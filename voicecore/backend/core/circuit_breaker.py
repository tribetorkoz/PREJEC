from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
import asyncio


class CircuitBreaker:
    """
    If a provider fails 3 times in 60 seconds,
    stop using it for 5 minutes automatically.
    Prevents cascade failures.
    Used by Netflix and Amazon for 99.99% uptime.
    """
    
    STATE_CLOSED = "CLOSED"
    STATE_OPEN = "OPEN"
    STATE_HALF_OPEN = "HALF_OPEN"
    
    def __init__(
        self,
        failure_threshold: int = 3,
        timeout: int = 300,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.failures: Dict[str, int] = {}
        self.state: Dict[str, str] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.successes: Dict[str, int] = {}
    
    async def call(
        self,
        provider_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        if self.state.get(provider_name) == self.STATE_OPEN:
            if self._should_try_reset(provider_name):
                self.state[provider_name] = self.STATE_HALF_OPEN
                self.successes[provider_name] = 0
            else:
                raise Exception(f"{provider_name} circuit is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success(provider_name)
            return result
            
        except Exception as e:
            self._on_failure(provider_name)
            raise e
    
    def _should_try_reset(self, provider_name: str) -> bool:
        last_failure = self.last_failure_time.get(provider_name)
        if not last_failure:
            return True
        
        return (datetime.utcnow() - last_failure).total_seconds() >= self.timeout
    
    def _on_success(self, provider_name: str):
        self.failures[provider_name] = 0
        
        if self.state.get(provider_name) == self.STATE_HALF_OPEN:
            self.successes[provider_name] = self.successes.get(provider_name, 0) + 1
            
            if self.successes[provider_name] >= self.success_threshold:
                self.state[provider_name] = self.STATE_CLOSED
    
    def _on_failure(self, provider_name: str):
        self.failures[provider_name] = self.failures.get(provider_name, 0) + 1
        self.last_failure_time[provider_name] = datetime.utcnow()
        
        if self.failures[provider_name] >= self.failure_threshold:
            self.state[provider_name] = self.STATE_OPEN
    
    def get_state(self, provider_name: str) -> str:
        return self.state.get(provider_name, self.STATE_CLOSED)
    
    def reset(self, provider_name: str):
        self.state[provider_name] = self.STATE_CLOSED
        self.failures[provider_name] = 0
        self.successes[provider_name] = 0
        self.last_failure_time.pop(provider_name, None)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            provider: {
                "state": self.state.get(provider, self.STATE_CLOSED),
                "failures": self.failures.get(provider, 0),
                "successes": self.successes.get(provider, 0),
                "last_failure": self.last_failure_time.get(provider)
            }
            for provider in set(list(self.state.keys()) + list(self.failures.keys()))
        }


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different services.
    """
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(
        self,
        name: str,
        failure_threshold: int = 3,
        timeout: int = 300
    ) -> CircuitBreaker:
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                timeout=timeout
            )
        return self.breakers[name]
    
    async def call(
        self,
        service: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        breaker = self.get_breaker(service)
        return await breaker.call(service, func, *args, **kwargs)
    
    def get_all_status(self) -> Dict[str, Any]:
        return {
            service: breaker.get_status()
            for service, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        for service_name, breaker in self.breakers.items():
            breaker.reset(service_name)
