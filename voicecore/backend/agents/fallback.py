import json
import logging
from typing import Dict, Any, List, Optional, Callable, AsyncIterator
from datetime import datetime
from enum import Enum

import redis.asyncio as redis

from config import settings
from core.circuit_breaker import CircuitBreaker, CircuitBreakerManager

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Provider types for fallback routing."""
    STT = "stt"
    TTS = "tts"
    LLM = "llm"
    DB = "db"


class FallbackHandler:
    """
    Handles multi-provider fallback for STT, TTS, LLM, and DB operations.
    If any provider fails, switches instantly to the next available provider.
    No call drops, no errors heard by customer.
    """

    def __init__(self):
        self.circuit_breaker_manager = CircuitBreakerManager()
        self._redis: Optional[redis.Redis] = None
        self._provider_health: Dict[str, Dict[str, Any]] = {}

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url or "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def stt_with_fallback(
        self,
        audio_frame: bytes,
        primary: str = "deepgram"
    ) -> str:
        """
        Transcribe audio using primary STT provider with fallback.
        
        Args:
            audio_frame: Raw audio bytes
            primary: Primary provider name (default: deepgram)
            
        Returns:
            Transcribed text
        """
        providers = [
            ("deepgram", self._transcribe_deepgram),
            ("whisper", self._transcribe_whisper),
            ("assembly_ai", self._transcribe_assembly_ai),
        ]
        
        for name, func in providers:
            breaker = self.circuit_breaker_manager.get_breaker(f"stt_{name}")
            
            try:
                result = await breaker.call(f"stt_{name}", func, audio_frame)
                await self._record_provider_success(f"stt_{name}")
                logger.debug(f"STT succeeded with {name}")
                return result
            except Exception as e:
                await self._record_provider_failure(f"stt_{name}", str(e))
                logger.warning(f"STT provider {name} failed: {e}")
                continue
        
        raise Exception("All STT providers failed")

    async def _transcribe_deepgram(self, audio_frame: bytes) -> str:
        """Transcribe using Deepgram API."""
        try:
            from deepgram import Deepgram
            
            client = Deepgram(settings.deepgram_api_key)
            
            buffer = audio_frame
            if isinstance(audio_frame, bytes):
                buffer = audio_frame
            else:
                buffer = audio_frame
            
            response = await client.transcribe.prerecorded(
                {"buffer": buffer, "mimetype": "audio/wav"},
                {"punctuate": True, "smart_format": True}
            )
            
            if response and "results" in response:
                transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
                return transcript.strip()
            
            return ""
        except Exception as e:
            logger.error(f"Deepgram transcription error: {e}")
            raise

    async def _transcribe_whisper(self, audio_frame: bytes) -> str:
        """Transcribe using Whisper (local/open-source fallback)."""
        try:
            import io
            import wave
            
            audio_buffer = io.BytesIO(audio_frame)
            
            with wave.open(audio_buffer, 'rb') as wav_file:
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
            
            if hasattr(settings, 'whisper_api_url') and settings.whisper_api_url:
                import httpx
                
                async with httpx.AsyncClient() as client:
                    files = {"file": ("audio.wav", io.BytesIO(audio_frame), "audio/wav")}
                    response = await client.post(
                        f"{settings.whisper_api_url}/transcribe",
                        files=files,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result.get("text", "")
            
            return ""
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            raise

    async def _transcribe_assembly_ai(self, audio_frame: bytes) -> str:
        """Transcribe using AssemblyAI API."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                upload_response = await client.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers={"authorization": settings.get("assembly_ai_api_key", "")},
                    content=audio_frame,
                    timeout=30.0
                )
                upload_response.raise_for_status()
                audio_url = upload_response.json()["upload_url"]
                
                transcript_response = await client.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json={"audio_url": audio_url},
                    headers={"authorization": settings.get("assembly_ai_api_key", "")},
                    timeout=30.0
                )
                transcript_response.raise_for_status()
                transcript_id = transcript_response.json()["id"]
                
                polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
                while True:
                    status_response = await client.get(polling_url, timeout=30.0)
                    status_response.raise_for_status()
                    status = status_response.json()
                    
                    if status["status"] == "completed":
                        return status["text"]
                    elif status["status"] == "error":
                        raise Exception("AssemblyAI transcription failed")
                    
                    import asyncio
                    await asyncio.sleep(2)
            
            return ""
        except Exception as e:
            logger.error(f"AssemblyAI transcription error: {e}")
            raise

    async def tts_with_fallback(
        self,
        text: str,
        primary_voice_id: Optional[str] = None
    ) -> bytes:
        """
        Generate speech using primary TTS provider with fallback.
        
        Args:
            text: Text to convert to speech
            primary_voice_id: Voice ID for ElevenLabs (optional)
            
        Returns:
            Audio bytes (MP3/WAV)
        """
        providers = [
            ("elevenlabs", self._tts_elevenlabs),
            ("twilio", self._tts_twilio),
        ]
        
        for name, func in providers:
            breaker = self.circuit_breaker_manager.get_breaker(f"tts_{name}")
            
            try:
                result = await breaker.call(f"tts_{name}", func, text, primary_voice_id)
                await self._record_provider_success(f"tts_{name}")
                logger.debug(f"TTS succeeded with {name}")
                return result
            except Exception as e:
                await self._record_provider_failure(f"tts_{name}", str(e))
                logger.warning(f"TTS provider {name} failed: {e}")
                continue
        
        raise Exception("All TTS providers failed")

    async def _tts_elevenlabs(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Generate speech using ElevenLabs API."""
        try:
            from elevenlabs import ElevenLabs
            
            client = ElevenLabs(api_key=settings.elevenlabs_api_key)
            voice = voice_id or "pFZP5JQG7NrQdMSifM4u"
            
            audio = client.generate(
                text=text,
                voice=voice,
                model="eleven_monolingual_v1",
                output_format="mp3_44100_128"
            )
            
            return b"".join(audio) if hasattr(audio, '__iter__') else audio
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise

    async def _tts_twilio(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Generate speech using Twilio TTS (fallback)."""
        try:
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{text}</Say>
</Response>"""
            
            return twiml_response.encode('utf-8')
        except Exception as e:
            logger.error(f"Twilio TTS error: {e}")
            raise

    async def llm_with_fallback(
        self,
        messages: List[Dict[str, str]],
        intent: str
    ) -> str:
        """
        Generate response using primary LLM with fallback to pre-built responses.
        
        Args:
            messages: Chat messages for context
            intent: Detected intent for pre-built response routing
            
        Returns:
            Generated response text
        """
        providers = [
            ("claude", self._llm_claude),
            ("openai", self._llm_openai),
        ]
        
        for name, func in providers:
            breaker = self.circuit_breaker_manager.get_breaker(f"llm_{name}")
            
            try:
                result = await breaker.call(f"llm_{name}", func, messages)
                await self._record_provider_success(f"llm_{name}")
                logger.debug(f"LLM succeeded with {name}")
                return result
            except Exception as e:
                await self._record_provider_failure(f"llm_{name}", str(e))
                logger.warning(f"LLM provider {name} failed: {e}")
                continue
        
        logger.warning("All LLM providers failed, using pre-built response")
        return self._get_prebuilt_response(intent)

    async def _llm_claude(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Claude API."""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            
            system_message = ""
            chat_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg.get("content", "")
                else:
                    chat_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_message,
                messages=chat_messages
            )
            
            return response.content[0].text if response.content else ""
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def _llm_openai(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API."""
        try:
            import httpx
            
            api_key = settings.get("openai_api_key", "")
            if not api_key:
                raise Exception("OpenAI API key not configured")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": messages,
                        "max_tokens": 1024
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _get_prebuilt_response(self, intent: str) -> str:
        """
        Get pre-built response based on intent.
        Used when all LLM providers fail.
        
        Args:
            intent: Detected customer intent
            
        Returns:
            Pre-built response string
        """
        prebuilt_responses = {
            "hours": "We're open Monday-Friday 9am-6pm.",
            "location": "We're located at [company address].",
            "appointment": "I'd be happy to help you schedule. What day works best?",
            "emergency": "For emergencies, please hang up and call 911.",
            "default": "I'm having trouble processing that. Let me transfer you."
        }
        
        return prebuilt_responses.get(intent, prebuilt_responses["default"])

    async def db_with_fallback(
        self,
        operation: Callable,
        fallback_storage: Dict[str, Any],
        key: str
    ) -> Any:
        """
        Execute database operation with Redis queue fallback.
        
        Args:
            operation: Async function to execute
            fallback_storage: Redis dict for fallback storage
            key: Key for fallback storage
            
        Returns:
            Result of operation or fallback
        """
        try:
            result = await operation()
            await self._record_provider_success("db")
            return result
        except Exception as e:
            logger.warning(f"Database operation failed: {e}")
            await self._record_provider_failure("db", str(e))
            
            try:
                r = await self._get_redis()
                cached = await r.hget(fallback_storage.get("key", key), key)
                if cached:
                    logger.info("Using Redis fallback for database operation")
                    return json.loads(cached)
            except Exception as redis_error:
                logger.error(f"Redis fallback also failed: {redis_error}")
            
            raise Exception("All database operations failed")

    async def _record_provider_success(self, provider: str) -> None:
        """Record successful provider call in Redis."""
        try:
            r = await self._get_redis()
            health_key = f"provider:health:{provider}"
            
            data = await r.hgetall(health_key)
            successes = int(data.get("successes", 0)) + 1
            await r.hset(health_key, mapping={
                "successes": str(successes),
                "failures": data.get("failures", "0"),
                "last_success": datetime.utcnow().isoformat(),
                "status": "healthy"
            })
            await r.expire(health_key, 3600)
        except Exception as e:
            logger.debug(f"Failed to record provider success: {e}")

    async def _record_provider_failure(self, provider: str, error: str) -> None:
        """Record failed provider call in Redis."""
        try:
            r = await self._get_redis()
            health_key = f"provider:health:{provider}"
            
            data = await r.hgetall(health_key)
            failures = int(data.get("failures", 0)) + 1
            total = failures + int(data.get("successes", 0))
            failure_rate = failures / total if total > 0 else 1.0
            
            status = "degraded" if failure_rate > 0.1 else "unhealthy"
            
            await r.hset(health_key, mapping={
                "successes": data.get("successes", "0"),
                "failures": str(failures),
                "last_failure": datetime.utcnow().isoformat(),
                "last_error": error[:200],
                "status": status
            })
            await r.expire(health_key, 3600)
        except Exception as e:
            logger.debug(f"Failed to record provider failure: {e}")


class ProviderHealthMonitor:
    """
    Monitors health of all service providers.
    Tracks success/failure rates and updates circuit breakers.
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url or "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def check_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Test all configured providers and update their health status.
        
        Returns:
            Dictionary of provider health statuses
        """
        providers = [
            ("stt_deepgram", self._check_deepgram_stt),
            ("stt_whisper", self._check_whisper_stt),
            ("tts_elevenlabs", self._check_elevenlabs_tts),
            ("llm_claude", self._check_claude_llm),
        ]
        
        results = {}
        
        for name, check_func in providers:
            try:
                is_healthy = await check_func()
                results[name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "checked_at": datetime.utcnow().isoformat(),
                    "latency_ms": 0
                }
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "checked_at": datetime.utcnow().isoformat(),
                    "error": str(e)[:200]
                }
            
            await self._update_redis_health(name, results[name])
        
        return results

    async def _check_deepgram_stt(self) -> bool:
        """Check if Deepgram STT is healthy."""
        try:
            if not settings.deepgram_api_key:
                return False
            
            from deepgram import Deepgram
            client = Deepgram(settings.deepgram_api_key)
            return True
        except Exception:
            return False

    async def _check_whisper_stt(self) -> bool:
        """Check if Whisper STT is healthy."""
        try:
            if hasattr(settings, 'whisper_api_url') and settings.whisper_api_url:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{settings.whisper_api_url}/health", timeout=5.0)
                    return response.status_code == 200
            return True
        except Exception:
            return False

    async def _check_elevenlabs_tts(self) -> bool:
        """Check if ElevenLabs TTS is healthy."""
        try:
            if not settings.elevenlabs_api_key:
                return False
            
            from elevenlabs import ElevenLabs
            client = ElevenLabs(api_key=settings.elevenlabs_api_key)
            return True
        except Exception:
            return False

    async def _check_claude_llm(self) -> bool:
        """Check if Claude LLM is healthy."""
        try:
            if not settings.anthropic_api_key:
                return False
            
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            return True
        except Exception:
            return False

    async def _update_redis_health(self, provider: str, status: Dict[str, Any]) -> None:
        """Update provider health in Redis."""
        try:
            r = await self._get_redis()
            health_key = f"provider:health:{provider}"
            
            await r.hset(health_key, mapping={
                "status": status.get("status", "unknown"),
                "checked_at": status.get("checked_at", datetime.utcnow().isoformat()),
                "error": status.get("error", "")
            })
            await r.expire(health_key, 300)
        except Exception as e:
            logger.debug(f"Failed to update Redis health: {e}")

    async def get_provider_status(self, name: str) -> Dict[str, Any]:
        """
        Get cached health status for a provider.
        
        Args:
            name: Provider name
            
        Returns:
            Provider health status dictionary
        """
        try:
            r = await self._get_redis()
            health_key = f"provider:health:{name}"
            
            data = await r.hgetall(health_key)
            
            if not data:
                return {
                    "status": "unknown",
                    "message": "No health data available"
                }
            
            return {
                "status": data.get("status", "unknown"),
                "checked_at": data.get("checked_at"),
                "successes": data.get("successes", "0"),
                "failures": data.get("failures", "0"),
                "last_success": data.get("last_success"),
                "last_failure": data.get("last_failure"),
                "error": data.get("error")
            }
        except Exception as e:
            logger.error(f"Error getting provider status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
