"""
Persistent context management system for ComfyUI EasyToolkit.

This module provides a persistent storage mechanism for contexts that can survive
across application restarts. It handles automatic serialization, caching, and cleanup.
"""
import threading

from .persistent_context import PersistentContext
from .context_cache import PersistentContextCache
from ..config import get_config

# Export main classes
__all__ = [
    'PersistentContext',
    'PersistentContextCache',
    'has_persistent_context',
    'remove_persistent_context',
    'get_persistent_context',
    'update_persistent_context',
    'resolve_persistent_contexts_by_value_type',
]

# Global context cache (initialized lazily)
_global_context_cache = None
_initialization_lock = threading.Lock()


def _ensure_initialized():
    """Ensure the global context cache is initialized (lazy initialization)"""
    global _global_context_cache
    
    if _global_context_cache is not None:
        return
    
    with _initialization_lock:
        # Double-check pattern
        if _global_context_cache is not None:
            return
        
        # Check if lazy initialization is enabled
        config = get_config().get_persistent_context_config()
        lazy_init = config.get('lazy_initialization', True)
        
        if not lazy_init:
            # This shouldn't happen in normal flow, but handle it anyway
            _global_context_cache = PersistentContextCache()
            return
        
        # Initialize the cache
        print("[comfyui-easytoolkit] Initializing persistent context cache (lazy initialization)...")
        _global_context_cache = PersistentContextCache()


def has_persistent_context(key: str) -> bool:
    _ensure_initialized()
    return _global_context_cache.has_context(key)


def remove_persistent_context(key: str):
    _ensure_initialized()
    return _global_context_cache.remove_context(key)


def get_persistent_context(key: str, default_value = None) -> PersistentContext:
    _ensure_initialized()
    if _global_context_cache.has_context(key):
        return _global_context_cache.get_context(key)
    return _global_context_cache.create_context(key, default_value)


def update_persistent_context(key: str):
    _ensure_initialized()
    return _global_context_cache.update_context_access_time(key)


def resolve_persistent_contexts_by_value_type(value_type: type) -> list[PersistentContext]:
    """Get all persistent contexts whose value is an instance of the specified type
    
    Args:
        value_type: The type to filter by (e.g., str, int, dict, list, or custom classes)
    
    Returns:
        List of PersistentContext objects whose values match the specified type
    
    Example:
        # Get all contexts with string values
        str_contexts = get_persistent_contexts_by_value_type(str)
        for ctx in str_contexts:
            print(f"Key: {ctx.get_key()}, Value: {ctx.get_value()}")
        
        # Get all contexts with dict values
        dict_contexts = get_persistent_contexts_by_value_type(dict)
    """
    _ensure_initialized()
    return _global_context_cache.resolve_contexts_by_value_type(value_type)


# Initialize immediately if lazy_initialization is disabled
config = get_config().get_persistent_context_config()
if not config.get('lazy_initialization', True):
    print("[comfyui-easytoolkit] Lazy initialization disabled, initializing persistent context cache immediately...")
    _global_context_cache = PersistentContextCache()

