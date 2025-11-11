from aiohttp import web
from ... import register_node, register_route
from ...utils.config import get_config
import os
import yaml
import json

@register_node
class AIAgentsConfigManager:
    """
    A ComfyUI node for managing AI Agents configuration with dynamic controls.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "agent_count": ("INT", {"default": 2, "min": 0, "max": 20, "step": 1}),
                "config_data": ("STRING", {"default": "{}"}),
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Manager"
    OUTPUT_NODE = False

    def run(self, agent_count):
        pass


@register_route("/easytoolkit_config/get_ai_agents", method="GET")
async def handle_get_ai_agents(request):
    """
    API endpoint to retrieve AI agents configuration.
    """
    try:
        config = get_config()
        ai_agents = config.get('ai_agents', {})
        
        # Convert to list format for easier handling
        agents_list = []
        for agent_id, agent_config in ai_agents.items():
            agents_list.append({
                'id': agent_id,
                'label': agent_config.get('label', ''),
                'summary': agent_config.get('summary', '')
            })
        
        return web.json_response({
            "success": True,
            "agents": agents_list
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


@register_route("/easytoolkit_config/save_ai_agents", method="POST")
async def handle_save_ai_agents(request):
    """
    API endpoint to save AI agents configuration to override file (JSON format).
    """
    try:
        data = await request.json()
        agents_list = data.get("agents", [])
        
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
        ai_agents = {}
        for agent in agents_list:
            agent_id = agent.get('id', '').strip()
            if agent_id:  # Only add agents with valid IDs
                ai_agents[agent_id] = {
                    'label': agent.get('label', ''),
                    'summary': agent.get('summary', '')
                }
        
        # Update only ai_agents section
        existing_config['ai_agents'] = ai_agents
        
        # Write to override file as JSON
        with open(override_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        
        # Reload configuration
        config = get_config()
        config.reload()
        
        return web.json_response({
            "success": True,
            "message": f"AI agents configuration saved to {override_path}",
            "path": override_path
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


