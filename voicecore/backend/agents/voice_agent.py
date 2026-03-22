import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from agents.memory import CustomerMemoryManager, CustomerProfile, CallContext
from agents.emotions import SentimentAnalyzer, RealTimeEmotionEngine, EmotionState
from agents.fallback import FallbackHandler, ProviderHealthMonitor
from agents.pipeline import UltraLowLatencyPipeline
from agents.tools import AGENT_TOOLS, transfer_to_human, create_support_ticket
from db.models import Customer, Call
from db.database import AsyncSessionLocal
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ActiveCall:
    """Data class for active call information."""
    call_id: str
    call_sid: str
    caller_phone: str
    company_id: int
    agent_id: int
    start_time: datetime
    transcript: List[Dict[str, str]] = field(default_factory=list)
    sentiment_history: List[str] = field(default_factory=list)
    emotion_engine: RealTimeEmotionEngine = field(default_factory=RealTimeEmotionEngine)
    needs_transfer: bool = False
    transfer_reason: Optional[str] = None


@dataclass
class CallSummary:
    """Data class for call summary after completion."""
    call_id: str
    duration_seconds: int
    outcome: str
    sentiment: str
    sentiment_score: float
    transcript: str
    customer_name: Optional[str]
    was_transferred: bool
    escalation_recommended: bool


class VoiceAgent:
    """
    Main voice agent class that orchestrates all components.
    Handles the complete lifecycle of a voice call from start to end.
    """

    def __init__(
        self,
        agent_id: int,
        company_id: int,
        language: str = "en",
        voice_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        vertical: str = "general"
    ):
        self.agent_id = agent_id
        self.company_id = company_id
        self.language = language
        self.voice_id = voice_id
        self.system_prompt = system_prompt
        self.vertical = vertical
        
        self.memory = CustomerMemoryManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fallback_handler = FallbackHandler()
        self.health_monitor = ProviderHealthMonitor()
        
        self._current_call: Optional[ActiveCall] = None
        self._sentiment_history: List[str] = []
        self._angry_count: int = 0
        self._turn_count: int = 0
        
        self._pipeline: Optional[UltraLowLatencyPipeline] = None

    @property
    def current_call(self) -> Optional[ActiveCall]:
        """Get the current active call."""
        return self._current_call

    @property
    def sentiment_history(self) -> List[str]:
        """Get sentiment history for this call."""
        return self._sentiment_history

    @property
    def angry_count(self) -> int:
        """Get count of ANGRY emotion detections."""
        return self._angry_count

    async def on_call_start(
        self,
        call_sid: str,
        caller_phone: str,
        company_id: int,
        agent_id: int
    ) -> str:
        """
        Handle call start event.
        
        Args:
            call_sid: Twilio/LiveKit call SID
            caller_phone: Customer phone number
            company_id: Company identifier
            agent_id: Agent identifier
            
        Returns:
            Greeting message to play to customer
        """
        self._current_call = ActiveCall(
            call_id=f"{call_sid}_{int(datetime.utcnow().timestamp())}",
            call_sid=call_sid,
            caller_phone=caller_phone,
            company_id=company_id,
            agent_id=agent_id,
            start_time=datetime.utcnow(),
            emotion_engine=RealTimeEmotionEngine()
        )
        
        self._sentiment_history = []
        self._angry_count = 0
        self._turn_count = 0
        
        async with AsyncSessionLocal() as db:
            try:
                customer = await self.memory.get_customer_profile(
                    caller_phone,
                    company_id,
                    db
                )
                
                if customer and customer.name:
                    greeting = f"Hello {customer.name}, thank you for calling. How can I help you today?"
                elif customer and customer.is_vip:
                    greeting = "Hello, thank you for calling. I see you're a valued customer. How may I assist you today?"
                else:
                    greeting = "Thank you for calling. How can I help you today?"
                
                await self.memory.get_or_create_customer(
                    caller_phone,
                    company_id,
                    name="",
                    db=db
                )
                
                logger.info("Call started", extra={
                    "call_sid": call_sid,
                    "company_id": company_id,
                    "agent_id": agent_id,
                    "phone_hash": hash(caller_phone) % 10000
                })
                
                return greeting
                
            except Exception as e:
                logger.error(f"Error in on_call_start: {e}")
                return "Thank you for calling. How can I help you today?"

    async def on_audio_received(self, audio_frame: bytes) -> bytes:
        """
        Process received audio and return response audio.
        
        Args:
            audio_frame: Raw audio bytes from customer
            
        Returns:
            Audio bytes response to play to customer
        """
        if not self._current_call:
            logger.warning("Received audio but no active call")
            return b""
        
        self._turn_count += 1
        
        try:
            async with AsyncSessionLocal() as db:
                context = await self.memory.load_context_for_call(
                    self._current_call.caller_phone,
                    self._current_call.company_id,
                    self._current_call.call_id,
                    db
                )
                
                context_dict = {
                    "customer_name": context.customer.name if context.customer else None,
                    "total_calls": context.customer.total_calls if context.customer else 0,
                    "is_returning_customer": context.is_returning_customer,
                    "days_since_last_call": context.days_since_last_call,
                    "is_vip": context.customer.is_vip if context.customer else False,
                    "vip_reason": context.customer.vip_reason if context.customer else None,
                    "history_text": context.history_text,
                    "recent_topics": []
                }
                
                pipeline = UltraLowLatencyPipeline(
                    deepgram_client=None,
                    llm_client=None,
                    tts_client=None,
                    transport=None,
                    db_session=db
                )
                pipeline.memory_manager = self.memory
                
                audio_chunks = []
                async for chunk in pipeline.process(
                    audio_frame,
                    self._current_call.caller_phone,
                    self._current_call.company_id,
                    self._current_call.call_id,
                    self._current_call.transcript,
                    context_dict
                ):
                    audio_chunks.append(chunk)
                
                response_audio = b"".join(audio_chunks)
                
                self._current_call.transcript.append({
                    "role": "assistant",
                    "content": "audio_response",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                emotion = self._current_call.emotion_engine.detect_emotion(
                    transcript="",
                    speaking_pace=None,
                    volume_level=None
                )
                
                if emotion == EmotionState.ANGRY:
                    self._angry_count += 1
                    if self._angry_count >= 2:
                        await self._auto_transfer_if_angry()
                
                return response_audio
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return b""

    async def on_call_end(self, outcome: str) -> CallSummary:
        """
        Handle call end event.
        
        Args:
            outcome: Call outcome (completed, transferred, voicemail, etc.)
            
        Returns:
            CallSummary with call statistics
        """
        if not self._current_call:
            logger.warning("on_call_end called but no active call")
            return CallSummary(
                call_id="unknown",
                duration_seconds=0,
                outcome=outcome,
                sentiment="NEUTRAL",
                sentiment_score=0.5,
                transcript="",
                customer_name=None,
                was_transferred=False,
                escalation_recommended=False
            )
        
        duration = int((datetime.utcnow() - self._current_call.start_time).total_seconds())
        overall_sentiment = "NEUTRAL"
        sentiment_score = 0.5
        customer = None
        was_transferred = False
        
        async with AsyncSessionLocal() as db:
            try:
                customer = await self.memory.get_customer_profile(
                    self._current_call.caller_phone,
                    self._current_call.company_id,
                    db
                )
                
                if self._sentiment_history:
                    sentiment_counts = {}
                    for s in self._sentiment_history:
                        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
                    overall_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
                
                sentiment_score = await self._calculate_sentiment_score()
                
                summary_text = await self._generate_call_summary(outcome)
                
                was_transferred = self._current_call.needs_transfer
                
                await self.memory.save_call_summary(
                    self._current_call.caller_phone,
                    self._current_call.company_id,
                    self._current_call.call_id,
                    summary_text,
                    outcome,
                    overall_sentiment,
                    duration
                )
                
                await self.memory.update_customer_profile(
                    self._current_call.caller_phone,
                    self._current_call.company_id,
                    {
                        "total_calls": (customer.total_calls + 1) if customer else 1,
                        "last_call_at": datetime.utcnow()
                    },
                    db
                )
                
                logger.info("Call ended", extra={
                    "call_id": self._current_call.call_id,
                    "duration": duration,
                    "outcome": outcome,
                    "sentiment": overall_sentiment,
                    "was_transferred": was_transferred
                })
                
            except Exception as e:
                logger.error(f"Error in on_call_end: {e}")
        
        call_summary = CallSummary(
            call_id=self._current_call.call_id,
            duration_seconds=duration,
            outcome=outcome,
            sentiment=overall_sentiment,
            sentiment_score=sentiment_score,
            transcript=self._format_transcript(),
            customer_name=customer.name if customer else None,
            was_transferred=was_transferred,
            escalation_recommended=self._current_call.emotion_engine.get_emotion_summary().get("escalation_recommended", False)
        )
        
        self._current_call = None
        
        return call_summary

    async def _auto_transfer_if_angry(self) -> None:
        """
        Automatically transfer call after 2 ANGRY emotion detections.
        """
        if self._angry_count >= 2 and not self._current_call.needs_transfer:
            self._current_call.needs_transfer = True
            self._current_call.transfer_reason = "Customer expressed anger repeatedly"
            
            logger.warning("Auto-transfer triggered due to angry customer", extra={
                "call_id": self._current_call.call_id,
                "angry_count": self._angry_count
            })
            
            try:
                customer = await self.memory.get_customer_profile(
                    self._current_call.caller_phone,
                    self._current_call.company_id,
                    None
                )
                
                await self._execute_tool("transfer_to_human", {
                    "reason": "Customer anger escalation",
                    "customer_info": {
                        "phone": self._mask_phone(self._current_call.caller_phone),
                        "call_id": self._current_call.call_id,
                        "sentiment_history": self._sentiment_history[-5:]
                    }
                })
            except Exception as e:
                logger.error(f"Error during auto-transfer: {e}")

    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with a timeout.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            result = await asyncio.wait_for(
                self._run_tool(tool_name, parameters),
                timeout=3.0
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Tool {tool_name} timed out after 3 seconds")
            return {"status": "error", "message": "Tool execution timed out"}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"status": "error", "message": str(e)}

    async def _run_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a specific tool.
        
        Args:
            tool_name: Name of tool
            parameters: Tool parameters
            
        Returns:
            Tool result
        """
        if tool_name == "transfer_to_human":
            return await transfer_to_human(
                parameters.get("reason", "Unknown"),
                parameters.get("customer_info", {})
            )
        elif tool_name == "create_support_ticket":
            return await create_support_ticket(
                parameters.get("customer_phone", ""),
                parameters.get("issue", "")
            )
        elif tool_name == "get_business_hours":
            from agents.tools import get_business_hours
            return await get_business_hours()
        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    async def _generate_call_summary(self, outcome: str) -> str:
        """
        Generate a 1-2 sentence summary of the call using Claude.
        
        Args:
            outcome: Call outcome
            
        Returns:
            Summary text
        """
        transcript_text = self._format_transcript()
        
        if not transcript_text:
            return f"Call {outcome}. No conversation recorded."
        
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            
            prompt = f"""Summarize this customer service call in 1-2 sentences.
Focus on the customer's main issue and the resolution.

Outcome: {outcome}
Transcript excerpt:
{transcript_text[:2000]}

Summary:"""
            
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            summary = response.content[0].text if response.content else ""
            return summary.strip()
            
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            return f"Call {outcome}. Customer inquiry handled."

    async def _calculate_sentiment_score(self) -> float:
        """
        Calculate overall sentiment score for the call.
        
        Returns:
            Score from 0.0 to 1.0 (0 = negative, 1 = positive)
        """
        if not self._sentiment_history:
            return 0.5
        
        sentiment_values = {
            "POSITIVE": 1.0,
            "HAPPY": 1.0,
            "NEUTRAL": 0.5,
            "CONFUSED": 0.4,
            "URGENT": 0.3,
            "FRUSTRATED": 0.2,
            "ANGRY": 0.1
        }
        
        total = sum(
            sentiment_values.get(s, 0.5)
            for s in self._sentiment_history
        )
        
        return total / len(self._sentiment_history)

    def _format_transcript(self) -> str:
        """
        Format conversation transcript as text.
        
        Returns:
            Formatted transcript string
        """
        if not self._current_call or not self._current_call.transcript:
            return ""
        
        lines = []
        for turn in self._current_call.transcript:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            if content and role in ["user", "assistant"]:
                lines.append(f"{role}: {content}")
        
        return "\n".join(lines)

    def _mask_phone(self, phone: str) -> str:
        """
        Mask phone number for logging (keep last 4 digits).
        
        Args:
            phone: Full phone number
            
        Returns:
            Masked phone number
        """
        if len(phone) <= 4:
            return "****"
        return "*" * (len(phone) - 4) + phone[-4:]


async def create_voice_agent(
    agent_id: int,
    company_id: int,
    language: str = "en",
    voice_id: Optional[str] = None,
    system_prompt: Optional[str] = None,
    vertical: str = "general"
) -> VoiceAgent:
    """
    Factory function to create a VoiceAgent instance.
    
    Args:
        agent_id: Agent identifier
        company_id: Company identifier
        language: Language code
        voice_id: TTS voice ID
        system_prompt: Custom system prompt
        vertical: Industry vertical
        
    Returns:
        Configured VoiceAgent instance
    """
    agent = VoiceAgent(
        agent_id=agent_id,
        company_id=company_id,
        language=language,
        voice_id=voice_id,
        system_prompt=system_prompt,
        vertical=vertical
    )
    
    return agent


class AgentToolExecutor:
    """
    Executes tools available to voice agents.
    """

    def __init__(self, voice_agent: VoiceAgent):
        self.agent = voice_agent
        self.tools = {t["name"]: t for t in AGENT_TOOLS}

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name with parameters.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        return await self.agent._execute_tool(tool_name, parameters)

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools.
        
        Returns:
            List of tool definitions
        """
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool definition or None
        """
        return self.tools.get(name)
