from typing import Dict, Any, List, Optional
from datetime import datetime


class CompetitiveIntelligence:
    """
    Every time a customer mentions a competitor,
    automatically log it and alert the business owner.
    Build market intelligence across your entire network.
    """
    
    COMPETITOR_SIGNALS = [
        "other company",
        "competitor",
        "someone else",
        "better deal",
        "cheaper elsewhere",
        "switching",
        "compared to",
        "instead of",
        "other option",
    ]
    
    def __init__(self, db_session, notification_service):
        self.db = db_session
        self.notifications = notification_service
    
    async def detect_competitor_mention(
        self,
        transcript: str,
        company_id: str,
        call_id: str
    ) -> Optional[Dict[str, Any]]:
        transcript_lower = transcript.lower()
        
        for signal in self.COMPETITOR_SIGNALS:
            if signal in transcript_lower:
                competitor_info = await self._extract_competitor_context(
                    transcript, signal
                )
                
                await self._log_competitor_mention(
                    company_id,
                    call_id,
                    competitor_info
                )
                
                await self._alert_owner(company_id, competitor_info)
                
                return competitor_info
        
        return None
    
    async def _extract_competitor_context(
        self,
        transcript: str,
        signal: str
    ) -> Dict[str, Any]:
        signal_pos = transcript.lower().find(signal)
        
        context_start = max(0, signal_pos - 100)
        context_end = min(len(transcript), signal_pos + 100)
        
        context = transcript[context_start:context_end]
        
        return {
            "signal": signal,
            "context": context,
            "detected_at": datetime.utcnow().isoformat()
        }
    
    async def _log_competitor_mention(
        self,
        company_id: str,
        call_id: str,
        competitor_info: Dict[str, Any]
    ):
        await self.db.create_competitor_mention({
            "company_id": company_id,
            "call_id": call_id,
            "signal": competitor_info["signal"],
            "context": competitor_info["context"],
            "detected_at": competitor_info["detected_at"]
        })
    
    async def _alert_owner(
        self,
        company_id: str,
        competitor_info: Dict[str, Any]
    ):
        await self.notifications.send({
            "type": "competitor_mention",
            "company_id": company_id,
            "message": f"Competitor mentioned: {competitor_info['context']}",
            "priority": "normal"
        })
    
    async def get_competitor_mentions_report(
        self,
        company_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        mentions = await self.db.get_competitor_mentions(
            company_id,
            start_date=start_date,
            end_date=end_date
        )
        
        signal_counts = {}
        for mention in mentions:
            signal = mention.get("signal", "unknown")
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        return {
            "total_mentions": len(mentions),
            "signal_breakdown": signal_counts,
            "mentions": mentions[-10:]
        }


class MarketIntelligenceAggregator:
    """
    Aggregate competitive intelligence across all companies
    to build industry-wide insights.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_industry_competitors(
        self,
        vertical: str
    ) -> List[Dict[str, Any]]:
        return await self.db.get_industry_competitors(vertical)
    
    async def get_competitor_trends(
        self,
        vertical: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        competitors = await self.db.get_industry_competitors(vertical)
        
        trends = {}
        for comp in competitors:
            trends[comp["name"]] = {
                "mention_count": comp.get("mention_count", 0),
                "sentiment": comp.get("average_sentiment", "neutral"),
                "trend": comp.get("trend", "stable")
            }
        
        return {
            "vertical": vertical,
            "time_period_days": time_period_days,
            "competitor_trends": trends
        }
