from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ProviderConfig(BaseModel):
    """Configuration for an AI service provider."""
    name: str = Field(..., description="Provider name (e.g., deepgram, elevenlabs)")
    provider_type: str = Field(..., description="Provider type: stt, tts, llm")
    endpoint: str = Field(default="", description="API endpoint URL")
    api_key: Optional[str] = Field(default=None, description="API key (optional)")
    priority: int = Field(default=1, description="Priority for fallback (1 = highest)")
    is_active: bool = Field(default=True, description="Whether provider is enabled")


class ProviderRegistry:
    """
    Central registry for all AI service providers.
    Manages registration, retrieval, and health monitoring of providers.
    """

    def __init__(self):
        self._providers: Dict[str, ProviderConfig] = {}
        self._provider_instances: Dict[str, Any] = {}
        self._health_status: Dict[str, Dict[str, Any]] = {}

    def register_provider(self, name: str, provider_config: ProviderConfig) -> bool:
        """
        Register a new provider with the registry.
        
        Args:
            name: Provider identifier
            provider_config: Provider configuration
            
        Returns:
            True if registered successfully
        """
        try:
            if name in self._providers:
                logger.warning(f"Provider {name} already registered, updating")
            
            self._providers[name] = provider_config
            
            logger.info(f"Registered provider: {name}", extra={
                "name": name,
                "type": provider_config.provider_type,
                "priority": provider_config.priority
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to register provider {name}: {e}")
            return False

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """
        Get provider configuration by name.
        
        Args:
            name: Provider name
            
        Returns:
            ProviderConfig or None if not found
        """
        return self._providers.get(name)

    def get_provider_instance(self, name: str) -> Optional[Any]:
        """
        Get the instantiated provider instance.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None
        """
        return self._provider_instances.get(name)

    def set_provider_instance(self, name: str, instance: Any) -> None:
        """
        Set the instantiated provider instance.
        
        Args:
            name: Provider name
            instance: Provider instance
        """
        self._provider_instances[name] = instance

    def get_all_providers(self) -> List[ProviderConfig]:
        """
        Get all registered providers.
        
        Returns:
            List of ProviderConfig objects
        """
        return list(self._providers.values())

    def get_providers_by_type(self, provider_type: str) -> List[ProviderConfig]:
        """
        Get all providers of a specific type, sorted by priority.
        
        Args:
            provider_type: Type of provider (stt, tts, llm)
            
        Returns:
            List of providers sorted by priority
        """
        providers = [
            p for p in self._providers.values()
            if p.provider_type == provider_type and p.is_active
        ]
        return sorted(providers, key=lambda x: x.priority)

    def get_provider_status(self, name: str) -> Dict[str, Any]:
        """
        Get health status for a provider.
        
        Args:
            name: Provider name
            
        Returns:
            Health status dictionary
        """
        if name in self._health_status:
            return self._health_status[name]
        
        provider = self._providers.get(name)
        if not provider:
            return {
                "status": "not_registered",
                "name": name
            }
        
        return {
            "status": "active" if provider.is_active else "inactive",
            "name": name,
            "type": provider.provider_type,
            "priority": provider.priority
        }

    def update_provider_status(self, name: str, status: Dict[str, Any]) -> None:
        """
        Update health status for a provider.
        
        Args:
            name: Provider name
            status: Status dictionary
        """
        self._health_status[name] = status

    async def _health_check(self, name: str) -> Dict[str, Any]:
        """
        Perform health check on a provider.
        
        Args:
            name: Provider name
            
        Returns:
            Health check result
        """
        provider = self._providers.get(name)
        if not provider:
            return {
                "name": name,
                "status": "not_found",
                "healthy": False
            }
        
        try:
            instance = self._provider_instances.get(name)
            if not instance:
                return {
                    "name": name,
                    "status": "no_instance",
                    "healthy": False
                }
            
            if provider.provider_type == "stt":
                healthy = await self._check_stt_health(instance, provider)
            elif provider.provider_type == "tts":
                healthy = await self._check_tts_health(instance, provider)
            elif provider.provider_type == "llm":
                healthy = await self._check_llm_health(instance, provider)
            else:
                healthy = False
            
            return {
                "name": name,
                "status": "healthy" if healthy else "unhealthy",
                "healthy": healthy,
                "type": provider.provider_type
            }
        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            return {
                "name": name,
                "status": "error",
                "healthy": False,
                "error": str(e)
            }

    async def _check_stt_health(self, instance: Any, provider: ProviderConfig) -> bool:
        """Check STT provider health."""
        try:
            if provider.name == "deepgram":
                return bool(instance)
            elif provider.name == "whisper":
                return bool(instance)
            return True
        except Exception:
            return False

    async def _check_tts_health(self, instance: Any, provider: ProviderConfig) -> bool:
        """Check TTS provider health."""
        try:
            if provider.name == "elevenlabs":
                return bool(instance)
            return True
        except Exception:
            return False

    async def _check_llm_health(self, instance: Any, provider: ProviderConfig) -> bool:
        """Check LLM provider health."""
        try:
            if provider.name == "claude":
                return bool(instance)
            elif provider.name == "openai":
                return bool(instance)
            return True
        except Exception:
            return False

    def remove_provider(self, name: str) -> bool:
        """
        Remove a provider from the registry.
        
        Args:
            name: Provider name
            
        Returns:
            True if removed successfully
        """
        if name in self._providers:
            del self._providers[name]
            if name in self._provider_instances:
                del self._provider_instances[name]
            if name in self._health_status:
                del self._health_status[name]
            logger.info(f"Removed provider: {name}")
            return True
        return False

    def get_provider_summary(self) -> Dict[str, Any]:
        """
        Get summary of all providers.
        
        Returns:
            Dictionary with provider statistics
        """
        providers_by_type = {}
        for provider in self._providers.values():
            ptype = provider.provider_type
            if ptype not in providers_by_type:
                providers_by_type[ptype] = []
            providers_by_type[ptype].append({
                "name": provider.name,
                "priority": provider.priority,
                "is_active": provider.is_active
            })
        
        return {
            "total_providers": len(self._providers),
            "active_providers": sum(1 for p in self._providers.values() if p.is_active),
            "providers_by_type": providers_by_type,
            "health_status": self._health_status
        }


_global_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """
    Get the global provider registry instance.
    
    Returns:
        Global ProviderRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry


def register_stt_provider(
    name: str,
    endpoint: str = "",
    api_key: Optional[str] = None,
    priority: int = 1
) -> bool:
    """
    Register an STT provider.
    
    Args:
        name: Provider name
        endpoint: API endpoint
        api_key: API key
        priority: Priority for fallback
        
    Returns:
        True if registered
    """
    registry = get_provider_registry()
    config = ProviderConfig(
        name=name,
        provider_type="stt",
        endpoint=endpoint,
        api_key=api_key,
        priority=priority
    )
    return registry.register_provider(name, config)


def register_tts_provider(
    name: str,
    endpoint: str = "",
    api_key: Optional[str] = None,
    priority: int = 1
) -> bool:
    """
    Register a TTS provider.
    
    Args:
        name: Provider name
        endpoint: API endpoint
        api_key: API key
        priority: Priority for fallback
        
    Returns:
        True if registered
    """
    registry = get_provider_registry()
    config = ProviderConfig(
        name=name,
        provider_type="tts",
        endpoint=endpoint,
        api_key=api_key,
        priority=priority
    )
    return registry.register_provider(name, config)


def register_llm_provider(
    name: str,
    endpoint: str = "",
    api_key: Optional[str] = None,
    priority: int = 1
) -> bool:
    """
    Register an LLM provider.
    
    Args:
        name: Provider name
        endpoint: API endpoint
        api_key: API key
        priority: Priority for fallback
        
    Returns:
        True if registered
    """
    registry = get_provider_registry()
    config = ProviderConfig(
        name=name,
        provider_type="llm",
        endpoint=endpoint,
        api_key=api_key,
        priority=priority
    )
    return registry.register_provider(name, config)
