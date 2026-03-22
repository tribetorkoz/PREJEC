import hashlib
from typing import Optional, Dict, Any
import json


class VoiceResponseCache:
    """
    Cache AI responses for common questions.
    "What are your hours?" → cached, responds in 50ms not 800ms
    80% of calls ask the same 20 questions.
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def _make_cache_key(self, question: str, company_id: str) -> str:
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return f"voice:{company_id}:{question_hash}"
    
    async def get_cached_response(
        self,
        question: str,
        company_id: str
    ) -> Optional[str]:
        cache_key = self._make_cache_key(question, company_id)
        try:
            cached = await self.redis.get(cache_key)
            return cached
        except Exception:
            return None
    
    async def cache_response(
        self,
        question: str,
        response: str,
        company_id: str,
        ttl: int = 3600
    ):
        cache_key = self._make_cache_key(question, company_id)
        try:
            await self.redis.setex(cache_key, ttl, response)
        except Exception:
            pass
    
    async def warm_cache(self, company_id: str, faq: Dict[str, str]):
        for question, answer in faq.items():
            await self.cache_response(question, answer, company_id)
    
    async def invalidate_cache(self, company_id: str, pattern: str = "*"):
        try:
            keys = await self.redis.keys(f"voice:{company_id}:{pattern}")
            for key in keys:
                await self.redis.delete(key)
        except Exception:
            pass


class SemanticCache:
    """
    More advanced caching using semantic similarity.
    If similar question exists, return cached response.
    """
    
    def __init__(self, redis_client, embedding_model):
        self.redis = redis_client
        self.embedding = embedding_model
    
    async def get_or_compute(
        self,
        question: str,
        company_id: str,
        compute_fn,
        similarity_threshold: float = 0.85
    ) -> str:
        question_embedding = await self.embedding.embed(question)
        
        cached_key = f"voice_sem:{company_id}"
        
        try:
            cached_questions = await self.redis.hgetall(cached_key)
            
            for cached_q, cached_response in cached_questions.items():
                cached_emb = await self.redis.get(f"voice_emb:{company_id}:{cached_q}")
                if cached_emb:
                    similarity = self.embedding.cosine_similarity(
                        question_embedding,
                        json.loads(cached_emb)
                    )
                    if similarity >= similarity_threshold:
                        return cached_response
        except Exception:
            pass
        
        response = await compute_fn(question)
        
        await self.cache_response(
            question,
            response,
            company_id,
            question_embedding
        )
        
        return response
    
    async def cache_response(
        self,
        question: str,
        response: str,
        company_id: str,
        embedding: list
    ):
        question_hash = hashlib.md5(question.encode()).hexdigest()
        
        await self.redis.hset(
            f"voice_sem:{company_id}",
            question_hash,
            response
        )
        await self.redis.set(
            f"voice_emb:{company_id}:{question_hash}",
            json.dumps(embedding),
            ex=86400
        )
