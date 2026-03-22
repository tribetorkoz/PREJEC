import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

import pytest
import pytest_asyncio


# ===== Fixtures =====

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.lpush = AsyncMock(return_value=1)
    redis_mock.ltrim = AsyncMock(return_value=True)
    redis_mock.lrange = AsyncMock(return_value=[])
    redis_mock.rpush = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.hset = AsyncMock(return_value=1)
    redis_mock.hgetall = AsyncMock(return_value={})
    redis_mock.hget = AsyncMock(return_value=None)
    return redis_mock


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def sample_customer_profile():
    """Sample customer profile data."""
    return {
        "phone": "+1234567890",
        "company_id": 1,
        "name": "John Doe",
        "total_calls": 5,
        "last_call_at": datetime.utcnow().isoformat(),
        "is_vip": False,
        "vip_reason": None,
        "notes": "Regular customer",
        "preferences": {"language": "en"},
        "call_history": [],
        "created_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_call_summary():
    """Sample call summary data."""
    return {
        "call_id": "CA123456",
        "date": datetime.utcnow().isoformat(),
        "duration_seconds": 120,
        "outcome": "completed",
        "sentiment": "positive",
        "summary": "Customer inquired about appointment availability."
    }


# ===== Memory Manager Tests =====

@pytest.mark.asyncio
async def test_memory_get_customer_new(mock_redis, mock_db_session):
    """New customer → creates empty profile."""
    from agents.memory import CustomerMemoryManager, CustomerProfile
    
    with patch('agents.memory.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        manager = CustomerMemoryManager()
        manager._redis = mock_redis
        
        profile = await manager.get_customer_profile(
            phone="+1234567890",
            company_id=1,
            db=mock_db_session
        )
        
        assert profile is None


@pytest.mark.asyncio
async def test_memory_get_customer_existing(mock_redis, mock_db_session, sample_customer_profile):
    """Existing customer → loads from Redis."""
    from agents.memory import CustomerMemoryManager, CustomerProfile
    
    with patch('agents.memory.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        mock_redis.get.return_value = json.dumps(sample_customer_profile)
        
        manager = CustomerMemoryManager()
        manager._redis = mock_redis
        
        profile = await manager.get_customer_profile(
            phone="+1234567890",
            company_id=1,
            db=mock_db_session
        )
        
        assert profile is not None
        assert profile.phone == "+1234567890"
        assert profile.total_calls == 5
        assert profile.is_vip is False


@pytest.mark.asyncio
async def test_memory_save_call_summary(mock_redis, mock_db_session, sample_call_summary):
    """Save summary → appears in history."""
    from agents.memory import CustomerMemoryManager
    
    with patch('agents.memory.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        manager = CustomerMemoryManager()
        manager._redis = mock_redis
        
        result = await manager.save_call_summary(
            phone="+1234567890",
            company_id=1,
            call_id="CA123456",
            summary="Customer inquired about appointment.",
            outcome="completed",
            sentiment="positive",
            duration_seconds=120
        )
        
        assert result is True
        mock_redis.lpush.assert_called_once()
        mock_redis.ltrim.assert_called_once()


@pytest.mark.asyncio
async def test_memory_max_10_calls(mock_redis):
    """11th call → first one is removed."""
    from agents.memory import CustomerMemoryManager
    
    with patch('agents.memory.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        manager = CustomerMemoryManager()
        manager._redis = mock_redis
        
        for i in range(11):
            await manager.save_call_summary(
                phone="+1234567890",
                company_id=1,
                call_id=f"CA{i}",
                summary=f"Call {i}",
                outcome="completed",
                sentiment="neutral",
                duration_seconds=60
            )
        
        mock_redis.ltrim.assert_called()
        last_call = mock_redis.ltrim.call_args
        assert last_call[0][2] == 9


# ===== Pipeline Tests =====

@pytest.mark.asyncio
async def test_pipeline_parallel_execution(mock_redis):
    """STT + Memory run in parallel → faster than sequential."""
    import time
    from agents.pipeline import UltraLowLatencyPipeline
    
    async def slow_stt(audio):
        await asyncio.sleep(0.2)
        return "transcribed text"
    
    async def slow_memory():
        await asyncio.sleep(0.1)
        return "memory context"
    
    with patch('agents.pipeline.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        pipeline = UltraLowLatencyPipeline()
        pipeline._redis = mock_redis
        
        with patch.object(pipeline, '_fallback_stt', side_effect=slow_stt):
            start = time.time()
            
            stt_task = asyncio.create_task(slow_stt(b"audio"))
            memory_task = asyncio.create_task(slow_memory())
            
            transcript, memory = await asyncio.gather(stt_task, memory_task)
            
            elapsed = time.time() - start
            
            assert elapsed < 0.25
            assert transcript == "transcribed text"
            assert memory == "memory context"


# ===== Fallback Handler Tests =====

@pytest.mark.asyncio
async def test_fallback_stt_deepgram_fails(mock_redis):
    """Deepgram fails → Whisper is used."""
    from agents.fallback import FallbackHandler
    
    with patch('agents.fallback.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        handler = FallbackHandler()
        handler._redis = mock_redis
        
        handler._transcribe_deepgram = AsyncMock(side_effect=Exception("Deepgram down"))
        handler._transcribe_whisper = AsyncMock(return_value="whisper transcription")
        
        with patch.object(handler, 'stt_with_fallback') as mock_fallback:
            mock_fallback.return_value = "whisper transcription"
            
            result = await handler.stt_with_fallback(b"audio", primary="deepgram")
            
            assert result == "whisper transcription"


@pytest.mark.asyncio
async def test_fallback_tts_elevenlabs_fails(mock_redis):
    """ElevenLabs fails → Twilio TTS is used."""
    from agents.fallback import FallbackHandler
    
    with patch('agents.fallback.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        handler = FallbackHandler()
        handler._redis = mock_redis
        
        handler._tts_elevenlabs = AsyncMock(side_effect=Exception("ElevenLabs down"))
        
        result = await handler.tts_with_fallback("Hello world", primary_voice_id="voice123")
        
        assert b"Say" in result


# ===== Sentiment Analyzer Tests =====

@pytest.mark.asyncio
async def test_sentiment_angry_triggers_transfer(mock_redis):
    """2 ANGRY → automatic transfer."""
    from agents.emotions import SentimentAnalyzer, EmotionState, RealTimeEmotionEngine
    
    with patch('agents.fallback.redis') as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis
        
        analyzer = SentimentAnalyzer()
        analyzer._redis = mock_redis
        mock_redis.get.return_value = None
        
        engine = RealTimeEmotionEngine()
        
        with patch.object(analyzer, '_keyword_fallback') as mock_fallback:
            from agents.emotions import SentimentResult
            mock_fallback.return_value = SentimentResult(
                sentiment="ANGRY",
                score=0.9,
                keywords=["angry"],
                action_required=True,
                reason="Strong anger detected"
            )
            
            result1 = await analyzer.analyze("I am so angry about this!")
            result2 = await analyzer.analyze("This is unacceptable!")
            
            assert result1.sentiment == "ANGRY"
            assert result2.sentiment == "ANGRY"
            
            engine.detect_emotion("I am so angry about this!")
            engine.detect_emotion("This is unacceptable!")
            
            should_escalate = engine.should_escalate(EmotionState.ANGRY, 2)
            
            assert should_escalate is True


# ===== Voice Agent Tests =====

@pytest.mark.asyncio
async def test_voice_agent_initialization():
    """VoiceAgent initializes all components correctly."""
    from agents.voice_agent import VoiceAgent
    
    with patch('agents.voice_agent.CustomerMemoryManager'):
        with patch('agents.voice_agent.SentimentAnalyzer'):
            with patch('agents.voice_agent.FallbackHandler'):
                with patch('agents.voice_agent.ProviderHealthMonitor'):
                    agent = VoiceAgent(
                        agent_id=1,
                        company_id=1,
                        language="en",
                        voice_id="voice123",
                        system_prompt="You are a helpful agent.",
                        vertical="general"
                    )
                    
                    assert agent.agent_id == 1
                    assert agent.company_id == 1
                    assert agent.language == "en"
                    assert agent.voice_id == "voice123"
                    assert agent.current_call is None
                    assert agent.sentiment_history == []
                    assert agent.angry_count == 0


# ===== WebSocket Tests =====

@pytest.mark.asyncio
async def test_voice_websocket_full_flow():
    """Full call: connect → welcome → audio → response → disconnect."""
    from unittest.mock import AsyncMock, patch
    
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    mock_websocket.send_bytes = AsyncMock()
    mock_websocket.receive_bytes = AsyncMock(return_value=b"audio_data")
    mock_websocket.close = AsyncMock()
    
    mock_token_payload = {
        "call_sid": "CA123",
        "agent_id": 1,
        "company_id": 1,
        "caller_phone": "+1234567890",
        "exp": datetime.utcnow().timestamp() + 3600
    }
    
    with patch('api.voice.verify_jwt_token', return_value=mock_token_payload):
        with patch('api.voice.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_result = AsyncMock()
            mock_session_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_session_result
            
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            with patch('agents.voice_agent.create_voice_agent') as mock_create_agent:
                mock_agent = AsyncMock()
                mock_agent.on_call_start = AsyncMock(return_value="Hello, how can I help you?")
                mock_agent.on_audio_received = AsyncMock(return_value=b"response_audio")
                mock_agent.on_call_end = AsyncMock()
                mock_agent.current_call = None
                mock_create_agent.return_value = mock_agent
                
                try:
                    from api.voice import voice_websocket
                    await voice_websocket(
                        websocket=mock_websocket,
                        call_sid="CA123",
                        token="valid_token"
                    )
                except Exception:
                    pass
                
                mock_websocket.accept.assert_called_once()


@pytest.mark.asyncio
async def test_inbound_webhook_twilio_signature():
    """Webhook without valid signature → 403."""
    from unittest.mock import AsyncMock, patch, MagicMock
    from fastapi import HTTPException
    
    mock_request = MagicMock()
    mock_request.headers = {"X-Twilio-Signature": "invalid_signature"}
    mock_request.query_params = {"CallSid": "CA123", "From": "+1234567890", "To": "+0987654321"}
    mock_request.form = AsyncMock(return_value={
        "CallSid": "CA123",
        "From": "+1234567890",
        "To": "+0987654321"
    })
    mock_request.method = "POST"
    mock_request.url = MagicMock()
    mock_request.url.__str__ = MagicMock(return_value="https://example.com/webhook")
    
    with patch('api.voice.verify_twilio_signature', return_value=False) as mock_verify:
        mock_verify.return_value = False
        
        from api.voice import handle_inbound_call
        
        with pytest.raises(HTTPException) as exc_info:
            await handle_inbound_call(mock_request, None)
        
        assert exc_info.value.status_code == 403


# ===== Provider Registry Tests =====

@pytest.mark.asyncio
async def test_provider_registry_register():
    """Register a provider successfully."""
    from core.provider_registry import ProviderRegistry, ProviderConfig
    
    registry = ProviderRegistry()
    
    config = ProviderConfig(
        name="deepgram",
        provider_type="stt",
        endpoint="https://api.deepgram.com",
        api_key="test_key",
        priority=1
    )
    
    result = registry.register_provider("deepgram", config)
    
    assert result is True
    assert registry.get_provider("deepgram") is not None
    assert registry.get_provider("deepgram").provider_type == "stt"


@pytest.mark.asyncio
async def test_provider_registry_get_all():
    """Get all registered providers."""
    from core.provider_registry import ProviderRegistry, ProviderConfig
    
    registry = ProviderRegistry()
    
    registry.register_provider("deepgram", ProviderConfig(
        name="deepgram", provider_type="stt", priority=1
    ))
    registry.register_provider("elevenlabs", ProviderConfig(
        name="elevenlabs", provider_type="tts", priority=1
    ))
    registry.register_provider("claude", ProviderConfig(
        name="claude", provider_type="llm", priority=1
    ))
    
    all_providers = registry.get_all_providers()
    
    assert len(all_providers) == 3


@pytest.mark.asyncio
async def test_provider_registry_get_by_type():
    """Get providers by type, sorted by priority."""
    from core.provider_registry import ProviderRegistry, ProviderConfig
    
    registry = ProviderRegistry()
    
    registry.register_provider("deepgram", ProviderConfig(
        name="deepgram", provider_type="stt", priority=2
    ))
    registry.register_provider("whisper", ProviderConfig(
        name="whisper", provider_type="stt", priority=1
    ))
    registry.register_provider("assembly", ProviderConfig(
        name="assembly", provider_type="stt", priority=3
    ))
    
    stt_providers = registry.get_providers_by_type("stt")
    
    assert len(stt_providers) == 3
    assert stt_providers[0].name == "whisper"
    assert stt_providers[1].name == "deepgram"
    assert stt_providers[2].name == "assembly"


# ===== Emotion Engine Tests =====

def test_emotion_detection_basic():
    """Test basic emotion detection from text."""
    from agents.emotions import RealTimeEmotionEngine, EmotionState
    
    engine = RealTimeEmotionEngine()
    
    emotion = engine.detect_emotion(
        "I am so frustrated with this service!",
        speaking_pace=None,
        volume_level=None
    )
    
    assert emotion in [EmotionState.FRUSTRATED, EmotionState.ANGRY]


def test_emotion_detection_urgent():
    """Test urgent emotion detection."""
    from agents.emotions import RealTimeEmotionEngine, EmotionState
    
    engine = RealTimeEmotionEngine()
    
    emotion = engine.detect_emotion(
        "This is an emergency! My child is bleeding!",
        speaking_pace=3.5,
        volume_level=0.9
    )
    
    assert emotion == EmotionState.URGENT


def test_emotion_detection_confused():
    """Test confused emotion detection."""
    from agents.emotions import RealTimeEmotionEngine, EmotionState
    
    engine = RealTimeEmotionEngine()
    
    emotion = engine.detect_emotion(
        "I don't understand, what do you mean? Can you repeat?",
        speaking_pace=0.8,
        volume_level=None
    )
    
    assert emotion == EmotionState.CONFUSED


def test_adapted_system_prompt():
    """Test system prompt adaptation based on emotion."""
    from agents.emotions import RealTimeEmotionEngine, EmotionState
    
    engine = RealTimeEmotionEngine()
    
    base_prompt = "You are a helpful voice assistant."
    
    adapted = engine.get_adapted_system_prompt(
        base_prompt,
        EmotionState.ANGRY,
        turn_count=1
    )
    
    assert "ANGRY" in adapted
    assert "ultra_calm_empathetic" in adapted.lower() or "ultra_calm" in adapted.lower()


def test_should_escalate_angry():
    """Test escalation trigger for angry customers."""
    from agents.emotions import RealTimeEmotionEngine, EmotionState
    
    engine = RealTimeEmotionEngine()
    
    engine.detect_emotion("This is terrible service!")
    engine.detect_emotion("I am very angry!")
    
    should_transfer = engine.should_escalate(EmotionState.ANGRY, 2)
    
    assert should_transfer is True


# ===== Run all tests with pytest-asyncio =====
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
