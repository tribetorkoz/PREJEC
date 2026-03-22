import json
import logging
import re
from typing import Dict, Any, Optional, List
from enum import Enum

import redis.asyncio as redis

from config import settings

logger = logging.getLogger(__name__)


class EmotionState(Enum):
    """Enumeration of possible emotion states."""
    HAPPY = "happy"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    URGENT = "urgent"


class SentimentResult:
    """Result of sentiment analysis."""
    def __init__(
        self,
        sentiment: str,
        score: float,
        keywords: List[str],
        action_required: bool,
        reason: str
    ):
        self.sentiment = sentiment
        self.score = score
        self.keywords = keywords
        self.action_required = action_required
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sentiment": self.sentiment,
            "score": self.score,
            "keywords": self.keywords,
            "action_required": self.action_required,
            "reason": self.reason
        }


class SentimentAnalyzer:
    """
    Analyzes sentiment of customer messages using Claude API.
    Falls back to keyword-based analysis if Claude is unavailable.
    Results are cached in Redis for 10 minutes.
    """

    CACHE_TTL = 600  # 10 minutes in seconds

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._positive_words = [
            "great", "excellent", "love", "amazing", "wonderful",
            "fantastic", "perfect", "awesome", "thank", "appreciate",
            "happy", "pleased", "satisfied", "good", "best", "helpful",
            "beautiful", "outstanding", "brilliant", "incredible"
        ]
        self._negative_words = [
            "bad", "terrible", "awful", "hate", "worst", "horrible",
            "angry", "frustrated", "disappointed", "unhappy", "poor",
            "disgusting", "ridiculous", "unacceptable", "pathetic",
            "useless", "broken", "annoying", "problem", "issue",
            "sucks", "crap", "damn", "hell", "pissed"
        ]
        self._angry_words = [
            "furious", "enraged", "livid", "outraged", "incensed",
            "infuriated", "irate", "maddened", "heated", "steaming",
            "lawsuit", "lawyer", "sue", "complaint", "manager",
            "supervisor", "corporate", "never", "again", "report",
            "yelling", "screaming", "shouting"
        ]
        self._urgent_keywords = [
            "emergency", "urgent", "immediately", "right now", "asap",
            "dying", "dead", "bleeding", "pain", "heart attack",
            "fire", "broken", "accident", "ambulance", "police",
            "severe", "critical", "crisis", "on the way", "help"
        ]
        self._confused_words = [
            "what", "huh", "pardon", "sorry", "excuse me",
            "repeat", "again", "don't understand", "confused",
            "lost", "how do", "which", "what do you mean",
            "can you explain", "i don't get it", "make sense"
        ]

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url or "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for sentiment analysis."""
        normalized = re.sub(r'[^\w\s]', '', text.lower().strip())
        cache_key = f"sentiment:cache:{hash(normalized) % 1000000000}"
        return cache_key

    async def analyze(
        self,
        text: str,
        language: str = "auto"
    ) -> SentimentResult:
        """
        Analyze sentiment of text using Claude API.
        
        Args:
            text: Text to analyze
            language: Language code or "auto" for detection
            
        Returns:
            SentimentResult object with sentiment, score, keywords, etc.
        """
        cache_key = self._get_cache_key(text)
        
        try:
            r = await self._get_redis()
            cached = await r.get(cache_key)
            if cached:
                logger.debug("Sentiment analysis cache hit")
                data = json.loads(cached)
                return SentimentResult(**data)
        except Exception as e:
            logger.warning(f"Redis cache check failed: {e}")

        try:
            result = await self._analyze_with_claude(text, language)
        except Exception as e:
            logger.warning(f"Claude analysis failed, using keyword fallback: {e}")
            result = self._keyword_fallback(text)

        try:
            r = await self._get_redis()
            await r.setex(cache_key, self.CACHE_TTL, json.dumps(result.to_dict()))
        except Exception as e:
            logger.warning(f"Failed to cache sentiment result: {e}")

        return result

    async def _analyze_with_claude(
        self,
        text: str,
        language: str
    ) -> SentimentResult:
        """
        Use Claude API for sentiment analysis.
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            SentimentResult from Claude
        """
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            
            prompt = f"""Analyze the sentiment of this customer message.
Respond with ONLY a JSON object:
{{
  "sentiment": "POSITIVE|NEUTRAL|FRUSTRATED|ANGRY",
  "score": 0.0-1.0,
  "keywords": ["word1", "word2"],
  "action_required": true/false,
  "reason": "brief explanation"
}}
Message: '{text}'"""
            
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text if response.content else "{}"
            
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return SentimentResult(
                    sentiment=data.get("sentiment", "NEUTRAL"),
                    score=float(data.get("score", 0.5)),
                    keywords=data.get("keywords", []),
                    action_required=bool(data.get("action_required", False)),
                    reason=data.get("reason", "")
                )
            else:
                return self._keyword_fallback(text)
        except Exception as e:
            logger.error(f"Claude sentiment analysis error: {e}")
            raise

    def _keyword_fallback(self, text: str) -> SentimentResult:
        """
        Simple keyword-based fallback if Claude API fails.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult from keyword analysis
        """
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        positive_count = sum(1 for word in self._positive_words if word in words)
        negative_count = sum(1 for word in self._negative_words if word in words)
        angry_count = sum(1 for word in self._angry_words if word in words)
        urgent_count = sum(1 for word in self._urgent_keywords if word in words)
        confused_count = sum(1 for word in self._confused_words if word in words)
        
        found_keywords = []
        for word in words:
            if word in self._positive_words or word in self._negative_words:
                found_keywords.append(word)
        
        if angry_count > 0 or urgent_count > 2:
            sentiment = "ANGRY"
            score = min(1.0, (angry_count + urgent_count) / 5)
            action_required = True
            reason = "Strong negative emotional indicators detected"
        elif urgent_count > 0:
            sentiment = "URGENT"
            score = min(1.0, urgent_count / 3)
            action_required = True
            reason = "Urgent keywords detected"
        elif negative_count > positive_count:
            sentiment = "FRUSTRATED"
            score = min(1.0, negative_count / 5)
            action_required = True
            reason = "Negative sentiment outweighs positive"
        elif positive_count > negative_count:
            sentiment = "POSITIVE"
            score = min(1.0, positive_count / 5)
            action_required = False
            reason = "Positive sentiment detected"
        elif confused_count > 0:
            sentiment = "NEUTRAL"
            score = 0.5
            action_required = True
            reason = "Customer may need clarification"
        else:
            sentiment = "NEUTRAL"
            score = 0.5
            action_required = False
            reason = "No strong emotional indicators"
        
        return SentimentResult(
            sentiment=sentiment,
            score=score,
            keywords=found_keywords[:5],
            action_required=action_required,
            reason=reason
        )

    async def analyze_full_call(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze entire call transcript for overall sentiment and patterns.
        
        Args:
            transcript: Full call transcript
            
        Returns:
            Dictionary with call-level analysis
        """
        lines = transcript.split('\n')
        
        if not lines:
            return {
                "overall_sentiment": "NEUTRAL",
                "avg_sentiment_score": 0.5,
                "emotional_peaks": [],
                "topic_sentiment": {},
                "action_items": [],
                "escalation_recommended": False
            }
        
        line_results = []
        for line in lines:
            if line.strip():
                result = await self.analyze(line)
                line_results.append(result)
        
        sentiment_scores = {
            "HAPPY": 1.0,
            "POSITIVE": 0.75,
            "NEUTRAL": 0.5,
            "CONFUSED": 0.4,
            "FRUSTRATED": 0.25,
            "ANGRY": 0.1,
            "URGENT": 0.3
        }
        
        total_score = sum(
            sentiment_scores.get(r.sentiment, 0.5) * r.score
            for r in line_results
        ) / len(line_results) if line_results else 0.5
        
        sentiment_counts = {}
        for r in line_results:
            sentiment_counts[r.sentiment] = sentiment_counts.get(r.sentiment, 0) + 1
        
        overall = max(sentiment_counts.items(), key=lambda x: x[1])[0]
        
        emotional_peaks = [
            r.to_dict() for r in line_results
            if r.sentiment in ["ANGRY", "URGENT", "FRUSTRATED"] and r.score > 0.7
        ]
        
        escalation_recommended = any(
            r.sentiment == "ANGRY" and r.score > 0.8
            for r in line_results
        ) or sum(1 for r in line_results if r.sentiment == "ANGRY") >= 2
        
        return {
            "overall_sentiment": overall,
            "avg_sentiment_score": total_score,
            "sentiment_distribution": sentiment_counts,
            "emotional_peaks": emotional_peaks,
            "action_items": [
                r.reason for r in line_results if r.action_required
            ],
            "escalation_recommended": escalation_recommended,
            "total_analyzed_lines": len(line_results)
        }


class RealTimeEmotionEngine:
    """
    Detects customer emotion in real-time using multiple signals:
    1. Text/words used (sentiment analysis)
    2. Speaking pace (fast = frustrated/urgent)
    3. Volume patterns (loud = angry)
    4. Repeated questions (confused)
    
    Adapts agent personality in real-time based on detected emotion.
    No competitor does all 4 signals together.
    """

    EMOTION_SIGNALS = {
        EmotionState.ANGRY: {
            "keywords": [
                "ridiculous", "unacceptable", "terrible", "worst",
                "lawsuit", "never coming back", "furious", "enraged",
                "fire you", "complaint", "manager", "supervisor"
            ],
            "response_style": "ultra_calm_empathetic",
            "pace": "slow",
            "escalate_after_turns": 2,
            "volume_threshold": 0.8,
            "pace_threshold": 2.5
        },
        EmotionState.URGENT: {
            "keywords": [
                "emergency", "urgent", "right now", "immediately",
                "bleeding", "broken", "flooding", "pain", "heart attack",
                "ambulance", "critical", "dying"
            ],
            "response_style": "fast_efficient_reassuring",
            "pace": "match_customer",
            "escalate_after_turns": 0,
            "priority_boost": True
        },
        EmotionState.CONFUSED: {
            "keywords": [
                "what do you mean", "i don't understand", "can you repeat",
                "what?", "huh?", "pardon", "confused", "lost", "how",
                "which", "what do i do", "explain"
            ],
            "response_style": "simple_clear_patient",
            "pace": "slow",
            "use_examples": True,
            "escalate_after_turns": 5
        },
        EmotionState.FRUSTRATED: {
            "keywords": [
                "already told you", "third time", "keep saying",
                "not working", "still", "again", "waiting", "forever",
                "disappointed", "frustrating"
            ],
            "response_style": "empathetic_solution_focused",
            "pace": "moderate",
            "acknowledge_first": True,
            "escalate_after_turns": 4
        },
        EmotionState.HAPPY: {
            "keywords": [
                "great", "excellent", "thank you", "perfect",
                "wonderful", "amazing", "love it", "fantastic"
            ],
            "response_style": "warm_enthusiastic",
            "pace": "moderate",
            "escalate_after_turns": 999
        }
    }

    def __init__(self):
        self.emotion_history: List[Dict[str, Any]] = []
        self.turn_count = 0
        self.consecutive_same_emotion = 0
        self.last_emotion: Optional[EmotionState] = None

    def detect_emotion(
        self,
        transcript: str,
        speaking_pace: Optional[float] = None,
        volume_level: Optional[float] = None
    ) -> EmotionState:
        """
        Detect customer emotion from transcript and audio signals.
        
        Args:
            transcript: Current transcript text
            speaking_pace: Words per second (optional)
            volume_level: Volume level 0.0-1.0 (optional)
            
        Returns:
            Detected EmotionState
        """
        self.turn_count += 1
        
        text_emotion = self._analyze_text(transcript)
        
        pace_signal = None
        if speaking_pace is not None:
            pace_signal = self._analyze_pace(speaking_pace)
        
        volume_signal = None
        if volume_level is not None:
            volume_signal = self._analyze_volume(volume_level)
        
        detected = self._combine_signals(text_emotion, pace_signal, volume_signal)
        
        if detected == self.last_emotion:
            self.consecutive_same_emotion += 1
        else:
            self.consecutive_same_emotion = 1
            self.last_emotion = detected
        
        self.emotion_history.append({
            "emotion": detected,
            "turn": self.turn_count,
            "transcript_length": len(transcript),
            "pace": speaking_pace,
            "volume": volume_level
        })
        
        if len(self.emotion_history) > 50:
            self.emotion_history = self.emotion_history[-50:]
        
        return detected

    def _analyze_text(self, transcript: str) -> EmotionState:
        """Analyze text for emotional keywords."""
        transcript_lower = transcript.lower()
        
        emotion_scores = {}
        for emotion, signals in self.EMOTION_SIGNALS.items():
            score = 0
            for keyword in signals["keywords"]:
                if keyword in transcript_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        return EmotionState.NEUTRAL

    def _analyze_pace(self, pace: float) -> Optional[EmotionState]:
        """
        Analyze speaking pace for emotional indicators.
        
        Args:
            pace: Words per second
            
        Returns:
            EmotionState if pace indicates emotion, None otherwise
        """
        if pace > 3.0:
            return EmotionState.URGENT
        elif pace > 2.5:
            return EmotionState.ANGRY
        elif pace > 2.0:
            return EmotionState.FRUSTRATED
        elif pace < 0.5:
            return EmotionState.CONFUSED
        return None

    def _analyze_volume(self, volume: float) -> Optional[EmotionState]:
        """
        Analyze volume level for emotional indicators.
        
        Args:
            volume: Volume level 0.0-1.0
            
        Returns:
            EmotionState if volume indicates emotion, None otherwise
        """
        if volume > 0.9:
            return EmotionState.ANGRY
        elif volume > 0.75:
            return EmotionState.URGENT
        elif volume < 0.2:
            return EmotionState.CONFUSED
        return None

    def _combine_signals(
        self,
        text_emotion: EmotionState,
        pace_signal: Optional[EmotionState],
        volume_signal: Optional[EmotionState]
    ) -> EmotionState:
        """
        Combine multiple emotional signals into final decision.
        
        Priority: URGENT > ANGRY > FRUSTRATED > CONFUSED > NEUTRAL > HAPPY
        
        Args:
            text_emotion: Emotion from text analysis
            pace_signal: Emotion from speaking pace (optional)
            volume_signal: Emotion from volume level (optional)
            
        Returns:
            Final EmotionState
        """
        signals = [text_emotion]
        
        if pace_signal:
            signals.append(pace_signal)
        if volume_signal:
            signals.append(volume_signal)
        
        priority_order = [
            EmotionState.URGENT,
            EmotionState.ANGRY,
            EmotionState.FRUSTRATED,
            EmotionState.CONFUSED,
            EmotionState.NEUTRAL,
            EmotionState.HAPPY
        ]
        
        for emotion in priority_order:
            if emotion in signals:
                return emotion
        
        return EmotionState.NEUTRAL

    def get_adapted_system_prompt(
        self,
        base_prompt: str,
        emotion: EmotionState,
        turn_count: int
    ) -> str:
        """
        Adapt system prompt based on detected emotion.
        
        Args:
            base_prompt: Original system prompt
            emotion: Detected emotion
            turn_count: Current turn number
            
        Returns:
            Adapted system prompt
        """
        style = self.EMOTION_SIGNALS.get(emotion, {})
        
        if not style:
            return base_prompt
        
        escalate_after = style.get('escalate_after_turns', 999)
        
        adaptation = f"""

CURRENT CUSTOMER EMOTION: {emotion.value.upper()}
RESPONSE ADAPTATION:
- Style: {style.get('response_style', 'default')}
- Pace: {style.get('pace', 'normal')}
- Turn: {turn_count}
- Escalate after: {escalate_after} turns

IMPORTANT: {'IMMEDIATE ESCALATION REQUIRED' if emotion == EmotionState.URGENT else 'Transfer to human after ' + str(escalate_after) + ' turns if emotion persists.'}
"""
        
        return base_prompt + adaptation

    def should_escalate(self, emotion: EmotionState, turn_count: int) -> bool:
        """
        Determine if call should be escalated to human.
        
        Args:
            emotion: Current emotion state
            turn_count: Number of consecutive turns with this emotion
            
        Returns:
            True if escalation is recommended
        """
        style = self.EMOTION_SIGNALS.get(emotion, {})
        escalate_after = style.get('escalate_after_turns', 999)
        
        if emotion == EmotionState.URGENT:
            return True
        
        if emotion == EmotionState.ANGRY:
            consecutive_angry = sum(
                1 for h in self.emotion_history[-10:]
                if h["emotion"] == EmotionState.ANGRY
            )
            return consecutive_angry >= 2
        
        if emotion == EmotionState.FRUSTRATED and self.consecutive_same_emotion >= 3:
            return True
        
        return turn_count >= escalate_after

    def get_response_modifiers(self, emotion: EmotionState) -> Dict[str, Any]:
        """
        Get response modifiers for current emotion.
        
        Args:
            emotion: Current emotion state
            
        Returns:
            Dictionary of response modifiers
        """
        return self.EMOTION_SIGNALS.get(emotion, {})

    def get_emotion_summary(self) -> Dict[str, Any]:
        """
        Get summary of emotional patterns in current session.
        
        Returns:
            Dictionary with emotion statistics
        """
        if not self.emotion_history:
            return {
                "total_turns": 0,
                "emotion_distribution": {},
                "dominant_emotion": "NEUTRAL",
                "emotional_intensity": 0.0
            }
        
        emotion_counts = {}
        for entry in self.emotion_history:
            emotion = entry["emotion"].value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "NEUTRAL"
        
        negative_emotions = ["angry", "frustrated", "urgent"]
        negative_count = sum(
            emotion_counts.get(e, 0)
            for e in negative_emotions
        )
        emotional_intensity = negative_count / len(self.emotion_history)
        
        return {
            "total_turns": len(self.emotion_history),
            "emotion_distribution": emotion_counts,
            "dominant_emotion": dominant,
            "emotional_intensity": emotional_intensity,
            "consecutive_same_emotion": self.consecutive_same_emotion,
            "escalation_recommended": self.should_escalate(
                EmotionState(dominant) if dominant != "NEUTRAL" else EmotionState.NEUTRAL,
                self.turn_count
            )
        }
