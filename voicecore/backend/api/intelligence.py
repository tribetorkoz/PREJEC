from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta


class CallIntelligenceEngine:
    """
    After every call, extract business intelligence.
    Build a data moat competitors can't replicate.
    
    This data makes your agents smarter over time.
    After 1M calls, your AI is unbeatable.
    """
    
    def __init__(self, db_session, llm_client):
        self.db = db_session
        self.llm = llm_client
    
    async def analyze_call(
        self,
        transcript: str,
        company_id: str,
        vertical: str,
        call_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        analysis_prompt = f"""
        Analyze this {vertical} business call transcript.
        Extract:
        
        1. INTENT: What did the customer want?
        2. OUTCOME: Was it resolved? (RESOLVED/TRANSFERRED/ABANDONED)
        3. SENTIMENT_JOURNEY: How did emotion change? (start→middle→end)
        4. KEY_TOPICS: Main subjects discussed
        5. UNMET_NEEDS: What did customer want that agent couldn't provide?
        6. BUSINESS_OPPORTUNITY: Any sales opportunities mentioned?
        7. COMPLAINT_RISK: Any risk of customer churning?
        8. IMPROVEMENT: What could have been handled better?
        9. COMPETITOR_MENTIONS: Did customer mention any competitor?
        10. URGENCY_SIGNALS: Anything requiring immediate follow-up?
        
        Transcript: {transcript}
        
        Return as JSON only.
        """
        
        try:
            analysis = await self.llm.complete(analysis_prompt)
            parsed = json.loads(analysis)
        except Exception:
            parsed = {
                "intent": "unknown",
                "outcome": "unknown",
                "sentiment_journey": "neutral",
                "key_topics": [],
                "unmet_needs": [],
                "business_opportunity": False,
                "complaint_risk": "low",
                "improvement": "",
                "competitor_mentions": [],
                "urgency_signals": []
            }
        
        await self.db.store_call_intelligence(company_id, parsed)
        
        await self._update_knowledge_base(company_id, vertical, parsed)
        
        if call_metadata:
            await self._correlate_with_metadata(company_id, parsed, call_metadata)
        
        return parsed
    
    async def _update_knowledge_base(
        self,
        company_id: str,
        vertical: str,
        analysis: Dict[str, Any]
    ):
        topics = analysis.get("key_topics", [])
        
        for topic in topics:
            await self.db.increment_topic_count(company_id, topic)
        
        if analysis.get("business_opportunity"):
            await self.db.increment_opportunity_count(company_id)
        
        if analysis.get("complaint_risk") == "high":
            await self.db.increment_risk_count(company_id)
    
    async def _correlate_with_metadata(
        self,
        company_id: str,
        analysis: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        await self.db.store_correlation({
            "company_id": company_id,
            "call_id": metadata.get("call_id"),
            "duration": metadata.get("duration"),
            "outcome": analysis.get("outcome"),
            "sentiment": analysis.get("sentiment_journey"),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def generate_daily_report(self, company_id: str) -> Dict[str, Any]:
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        yesterday_calls = await self.db.get_calls(
            company_id,
            start_date=yesterday
        )
        
        if not yesterday_calls:
            return {
                "total_calls": 0,
                "message": "No calls yesterday"
            }
        
        resolved = sum(1 for c in yesterday_calls if c.get("outcome") == "RESOLVED")
        
        total_duration = sum(
            c.get("duration", 0) for c in yesterday_calls
        )
        
        report = {
            "total_calls": len(yesterday_calls),
            "resolution_rate": resolved / len(yesterday_calls) if yesterday_calls else 0,
            "avg_duration_minutes": total_duration / len(yesterday_calls) if yesterday_calls else 0,
            "top_issues": await self._extract_top_issues(yesterday_calls),
            "missed_opportunities": sum(
                1 for c in yesterday_calls if c.get("business_opportunity")
            ),
            "sentiment_summary": self._sentiment_summary(yesterday_calls),
            "urgent_follow_ups": [
                c for c in yesterday_calls
                if c.get("urgency_signals")
            ],
            "recommendations": await self._generate_recommendations(yesterday_calls),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report
    
    def _extract_top_issues(self, calls: list) -> list:
        topics_count = {}
        
        for call in calls:
            for topic in call.get("key_topics", []):
                topics_count[topic] = topics_count.get(topic, 0) + 1
        
        sorted_topics = sorted(
            topics_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [{"topic": t[0], "count": t[1]} for t in sorted_topics[:5]]
    
    def _sentiment_summary(self, calls: list) -> Dict[str, int]:
        sentiment_counts = {}
        
        for call in calls:
            sentiment = call.get("sentiment_journey", "neutral")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        return sentiment_counts
    
    async def _generate_recommendations(self, calls: list) -> list:
        recommendations = []
        
        unresolved = sum(1 for c in calls if c.get("outcome") != "RESOLVED")
        if unresolved > len(calls) * 0.3:
            recommendations.append(
                "Consider improving resolution rate through better agent training"
            )
        
        complaint_risks = sum(1 for c in calls if c.get("complaint_risk") == "high")
        if complaint_risks > 0:
            recommendations.append(
                "Follow up with customers who showed high complaint risk"
            )
        
        return recommendations


class KnowledgeBaseManager:
    """
    Manage and update the knowledge base from call intelligence.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_common_questions(
        self,
        company_id: str,
        limit: int = 20
    ) -> list:
        return await self.db.get_common_questions(company_id, limit)
    
    async def get_common_objections(
        self,
        company_id: str,
        vertical: str
    ) -> list:
        return await self.db.get_common_objections(company_id, vertical)
    
    async def add_to_knowledge_base(
        self,
        company_id: str,
        topic: str,
        answer: str,
        confidence: float = 0.8
    ):
        await self.db.add_knowledge_entry({
            "company_id": company_id,
            "topic": topic,
            "answer": answer,
            "confidence": confidence,
            "source": "call_intelligence"
        })
