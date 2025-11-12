from aiohttp import web
from ... import register_node, register_route
from ...utils.config import get_config

@register_node(emoji="⚙️")
class AIServicesConfig:
    """
    A ComfyUI node for managing AI Services configuration with dynamic controls.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "default_service": ("COMBO", {"default": ""}),
                "config_data": ("STRING", {"default": "{}"}),
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Config"
    OUTPUT_NODE = False

    def run(self, default_service, config_data):
        pass


@register_route("/easytoolkit_config/get_ai_services", method="GET")
async def handle_get_ai_services(request):
    """
    API endpoint to retrieve AI services configuration.
    """
    try:
        config = get_config()
        ai_services = config.get('ai_services', {})
        default_service = config.get('default_ai_service', '')

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
            "services": services_list,
            "default_service": default_service
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@register_route("/easytoolkit_config/save_ai_services", method="POST")
async def handle_save_ai_services(request):
    """
    API endpoint to save AI services configuration.
    """
    try:
        data = await request.json()
        services_list = data.get("services", [])
        default_service = data.get("default_service", "")

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

        # Use config utility to set ai_services
        config = get_config()
        config.set("ai_services", ai_services)

        # Update default_ai_service if provided
        if default_service:
            config.set("default_ai_service", default_service)
        else:
            # Remove default_ai_service if it's empty
            config.delete("default_ai_service")

        return web.json_response({
            "success": True,
            "message": "AI services configuration saved successfully",
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@register_route("/easytoolkit_config/delete_ai_service", method="POST")
async def handle_delete_ai_service(request):
    """
    API endpoint to delete a specific AI service from configuration.
    """
    try:
        data = await request.json()
        service_id = data.get("service_id", "")

        if not service_id:
            return web.json_response({
                "success": False,
                "error": "Service ID is required"
            }, status=400)

        # Check if service exists
        config = get_config()
        ai_services = config.get("ai_services", {})
        if service_id not in ai_services:
            return web.json_response({
                "success": False,
                "error": f"Service '{service_id}' not found"
            }, status=404)

        # Remove the service using config.delete with dot notation
        config.delete(f"ai_services.{service_id}")

        # Update default service if it was the deleted one
        default_service = config.get("default_ai_service", "")
        if default_service == service_id:
            config.set("default_ai_service", "")

        return web.json_response({
            "success": True,
            "message": f"Service '{service_id}' deleted successfully",
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@register_route("/easytoolkit_config/reset_ai_services", method="POST")
async def handle_reset_ai_services(request):
    """
    API endpoint to reset AI services configuration by removing ai_services from override file.
    """
    try:
        config = get_config()

        # Remove ai_services and default_ai_service sections using config utility
        config_changed = False

        if config.get("ai_services") is not None:
            config.delete("ai_services")
            config_changed = True

        if config.get("default_ai_service") is not None:
            config.delete("default_ai_service")
            config_changed = True

        if config_changed:
            return web.json_response({
                "success": True,
                "message": "AI services configuration reset successfully",
            })
        else:
            return web.json_response({
                "success": True,
                "message": "No AI services configuration found to reset",
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

