from aiohttp import web
from ... import register_node, register_route
from ...utils.config import get_config
import os
import yaml

@register_node
class EasyToolkitConfigManager:
    """
    A ComfyUI node for managing EasyToolkit configuration via YAML text.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config_yaml": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Manager"
    OUTPUT_NODE = False

    def run(self):
        pass


@register_route("/easytoolkit_config/get_current_config", method="GET")
async def handle_get_current_config(request):
    """
    API endpoint to retrieve current configuration as YAML text.
    """
    try:
        config_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        override_path = os.path.join(config_dir, 'config.override.yaml')
        config_path = os.path.join(config_dir, 'config.yaml')
        
        yaml_text = "# Edit configuration here\n"
        
        # Read YAML file directly to preserve comments
        # Prioritize override file
        if os.path.exists(override_path):
            try:
                with open(override_path, 'r', encoding='utf-8') as f:
                    yaml_text = f.read()
            except Exception as e:
                yaml_text = f"# Error reading config.override.yaml: {str(e)}\n"
        elif os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_text = f.read()
            except Exception as e:
                yaml_text = f"# Error reading config.yaml: {str(e)}\n"
        
        return web.json_response({
            "success": True,
            "config_yaml": yaml_text
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@register_route("/easytoolkit_config/save_override", method="POST")
async def handle_save_override(request):
    """
    API endpoint to save configuration override as YAML text.
    """
    try:
        data = await request.json()
        yaml_text = data.get("config_yaml", "")
        
        if not yaml_text or not yaml_text.strip():
            return web.json_response({
                "success": False,
                "error": "No configuration data provided"
            }, status=400)
        
        # Get the path to config.override.yaml
        config_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        override_path = os.path.join(config_dir, 'config.override.yaml')
        
        # Write YAML text directly
        with open(override_path, 'w', encoding='utf-8') as f:
            f.write(yaml_text)
        
        # Reload configuration to apply changes immediately
        config = get_config()
        config.reload()
        
        return web.json_response({
            "success": True,
            "message": f"Configuration override saved to {override_path}",
            "path": override_path
        })
        
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

@register_route("/easytoolkit_config/delete_override", method="DELETE")
async def handle_delete_override(request):
    """
    API endpoint to delete override configuration.
    """
    try:
        config_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        override_path = os.path.join(config_dir, 'config.override.yaml')
        
        if not os.path.exists(override_path):
            return web.json_response({
                "success": True,
                "message": "Override file does not exist"
            })
        
        os.remove(override_path)
        
        # Reload configuration to apply changes immediately
        config = get_config()
        config.reload()
        
        return web.json_response({
            "success": True,
            "message": "Override file deleted successfully"
        })
        
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

