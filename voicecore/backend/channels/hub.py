from typing import Dict, Any, Optional, List
from datetime import datetime


class OmnichannelHub:
    """
    One agent — every channel.
    Customer starts on WhatsApp,
    continues on phone,
    agent remembers everything.
    
    No competitor offers seamless cross-channel memory.
    """
    
    CHANNELS = ["phone", "whatsapp", "sms", "webchat", "email"]
    
    def __init__(self, db_session, voice_agent):
        self.db = db_session
        self.voice_agent = voice_agent
    
    async def handle_message(
        self,
        channel: str,
        company_id: str,
        customer_identifier: str,
        message: str
    ) -> Dict[str, Any]:
        history = await self.get_cross_channel_history(
            customer_identifier,
            company_id
        )
        
        context = self.build_omnichannel_context(history)
        
        if channel == "phone":
            return await self.handle_voice(
                message, context, company_id, customer_identifier
            )
        elif channel in ["whatsapp", "sms"]:
            return await self.handle_text(
                message, context, company_id, customer_identifier
            )
        elif channel == "webchat":
            return await self.handle_webchat(
                message, context, company_id, customer_identifier
            )
        
        return {"error": "Unsupported channel"}
    
    async def handle_voice(
        self,
        audio_message: str,
        context: str,
        company_id: str,
        customer_id: str
    ) -> Dict[str, Any]:
        response = await self.voice_agent.process(
            message=audio_message,
            company_id=company_id,
            customer_id=customer_id,
            context=context,
            channel="phone"
        )
        
        await self.log_interaction(
            company_id,
            customer_id,
            "phone",
            audio_message,
            response
        )
        
        return {"response": response, "channel": "phone"}
    
    async def handle_text(
        self,
        text_message: str,
        context: str,
        company_id: str,
        customer_id: str
    ) -> Dict[str, Any]:
        response = await self.voice_agent.process(
            message=text_message,
            company_id=company_id,
            customer_id=customer_id,
            context=context,
            channel="text"
        )
        
        await self.log_interaction(
            company_id,
            customer_id,
            "whatsapp",
            text_message,
            response
        )
        
        return {"response": response, "channel": "whatsapp"}
    
    async def handle_webchat(
        self,
        chat_message: str,
        context: str,
        company_id: str,
        customer_id: str
    ) -> Dict[str, Any]:
        response = await self.voice_agent.process(
            message=chat_message,
            company_id=company_id,
            customer_id=customer_id,
            context=context,
            channel="webchat"
        )
        
        await self.log_interaction(
            company_id,
            customer_id,
            "webchat",
            chat_message,
            response
        )
        
        return {"response": response, "channel": "webchat"}
    
    async def get_cross_channel_history(
        self,
        customer_id: str,
        company_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        return await self.db.query("""
            SELECT channel, message, response, timestamp
            FROM interactions
            WHERE customer_id = ? AND company_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, [customer_id, company_id, limit])
    
    def build_omnichannel_context(self, history: List[Dict]) -> str:
        if not history:
            return "New customer. No previous interactions."
        
        context_parts = ["Previous interactions:"]
        
        for interaction in history[-5:]:
            channel = interaction.get("channel", "unknown")
            message = interaction.get("message", "")
            response = interaction.get("response", "")
            timestamp = interaction.get("timestamp", "")
            
            context_parts.append(
                f"[{channel.upper()} - {timestamp}]: {message} → {response}"
            )
        
        return "\n".join(context_parts)
    
    async def log_interaction(
        self,
        company_id: str,
        customer_id: str,
        channel: str,
        message: str,
        response: str
    ):
        await self.db.create_interaction({
            "company_id": company_id,
            "customer_id": customer_id,
            "channel": channel,
            "message": message,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })


class ChannelRouter:
    """
    Route messages to appropriate channel handlers.
    """
    
    def __init__(self, omnichannel_hub: OmnichannelHub):
        self.hub = omnichannel_hub
    
    async def route(
        self,
        channel: str,
        company_id: str,
        customer_id: str,
        message: str
    ) -> Dict[str, Any]:
        return await self.hub.handle_message(
            channel=channel,
            company_id=company_id,
            customer_identifier=customer_id,
            message=message
        )
