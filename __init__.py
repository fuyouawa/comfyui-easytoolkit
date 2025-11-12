import re
from server import PromptServer

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {}

def camel_to_spaced(s: str) -> str:
    # Common prefixes to treat as separate words
    common_prefixes = ['AI', 'ML', 'API', 'UI', 'UX', 'JSON', 'XML', 'HTML', 'CSS', 'HTTP', 'HTTPS']

    # Check if the string starts with any common prefix
    for prefix in common_prefixes:
        if s.startswith(prefix) and len(s) > len(prefix):
            # Split the prefix from the rest of the string
            rest = s[len(prefix):]
            # Convert the rest using the original camel case logic
            spaced_rest = re.sub(r'(?<=[a-z0-9])([A-Z])', r' \1', rest)
            return f"{prefix} {spaced_rest}"

    # If no common prefix found, use the original logic
    return re.sub(r'(?<=[a-z0-9])([A-Z])', r' \1', s)

def register_node(c=None, *, emoji=None):
    """
    Decorator to register a ComfyUI node class.

    Args:
        c: The node class to register
        emoji: Optional emoji to append to the display name
    """
    def decorator(cls):
        NODE_CLASS_MAPPINGS[cls.__name__] = cls
        display_name = camel_to_spaced(cls.__name__)
        if emoji:
            display_name = f"{display_name} {emoji}"
        NODE_DISPLAY_NAME_MAPPINGS[cls.__name__] = display_name
        return cls

    if c is None:
        return decorator
    else:
        return decorator(c)

def register_route(path, method="POST"):
    """
    Decorator to register API routes more conveniently.
    """
    def decorator(func):
        routes = PromptServer.instance.routes
        method_lower = method.lower()
        
        if method_lower == "get":
            routes.get(path)(func)
        elif method_lower == "post":
            routes.post(path)(func)
        elif method_lower == "put":
            routes.put(path)(func)
        elif method_lower == "delete":
            routes.delete(path)(func)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return func
    return decorator

# Import all nodes
from .nodes import *

# Set the web directory, any .js file in that directory will be loaded by the frontend as a frontend extension
WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']