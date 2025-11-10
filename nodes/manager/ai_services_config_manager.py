from aiohttp import web
from ... import register_node, register_route
from ...utils.config import get_config
import os
import yaml
import json

@register_node
class AIServicesConfigManager:
    """
    A ComfyUI node for managing AI Services configuration with dynamic controls.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "service_count": ("INT", {"default": 2, "min": 0, "max": 20, "step": 1}),
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Manager"
    OUTPUT_NODE = False

    def run(self, service_count):
        pass


@register_route("/easytoolkit_config/get_ai_services", method="GET")
async def handle_get_ai_services(request):
    """
    API endpoint to retrieve AI services configuration.
    """
    try:
        config = get_config()
        ai_services = config.get('ai_services', {})
        
        # Convert to list format for easier handling
        services_list = []
        for service_id, service_config in ai_services.items():
            services_list.append({
                'id': service_id,
                'label': service_config.get('label', ''),
                'base_url': service_config.get('base_url', ''),
                'api_key': service_config.get('api_key', ''),
                'model': service_config.get('model', ''),
                'timeout': service_config.get('timeout', 300)
            })
        
        return web.json_response({
            "success": True,
            "services": services_list
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@register_route("/easytoolkit_config/save_ai_services", method="POST")
async def handle_save_ai_services(request):
    """
    API endpoint to save AI services configuration to override file (JSON format).
    """
    try:
        data = await request.json()
        services_list = data.get("services", [])
        
        # Load current config
        config_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        override_path = os.path.join(config_dir, 'config.override.json')
        
        # Load existing configuration from override file if exists
        existing_config = {}
        if os.path.exists(override_path):
            try:
                with open(override_path, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load override config: {e}")
        
        # Convert list back to dict format
        ai_services = {}
        for service in services_list:
            service_id = service.get('id', '').strip()
            if service_id:  # Only add services with valid IDs
                ai_services[service_id] = {
                    'label': service.get('label', ''),
                    'base_url': service.get('base_url', ''),
                    'api_key': service.get('api_key', ''),
                    'model': service.get('model', ''),
                    'timeout': int(service.get('timeout', 300))
                }
        
        # Update only ai_services section
        existing_config['ai_services'] = ai_services
        
        # Write to override file as JSON
        with open(override_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        
        # Reload configuration
        config = get_config()
        config.reload()
        
        return web.json_response({
            "success": True,
            "message": f"AI services configuration saved to {override_path}",
            "path": override_path
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

