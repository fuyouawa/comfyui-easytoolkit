import re
from server import PromptServer

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {}

def camel_to_spaced(s: str) -> str:
    return re.sub(r'(?<=[a-z0-9])([A-Z])', r' \1', s)

def register_node(c):
    NODE_CLASS_MAPPINGS[c.__name__] = c
    NODE_DISPLAY_NAME_MAPPINGS[c.__name__] = camel_to_spaced(c.__name__)
    return c

def register_route(path, method="POST"):
    """
    Decorator to register API routes more conveniently.
    
    Usage:
        @register_route("/my_endpoint", method="POST")
        async def my_handler(request):
            return web.json_response({"success": True})
    
    Args:
        path: The API endpoint path
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
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