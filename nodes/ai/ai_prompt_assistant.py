from ... import register_node, register_route
from ...utils.config import get_config
from ...utils.ai_service import get_ai_service
from aiohttp import web
import traceback

@register_node
class AIPromptAssistant:
    """
    AI-powered prompt assistant for expanding, translating, and optimizing prompts.
    Integrates with multiple AI services (DeepSeek, OpenAI, Anthropic).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "dynamicPrompts": False
                }),
                "ai_service": ("COMBO", {"default": "deepseek"}),
                "ai_agent": ("COMBO", {"default": "video_prompt_expansion"}),
            },
            "optional": {
                "processed_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "dynamicPrompts": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("original_prompt", "processed_prompt")
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/AI"
    OUTPUT_NODE = True
    
    def run(self, original_prompt, ai_service, ai_agent, processed_prompt=""):
        """
        Process the prompt through AI service.
        Note: The actual AI processing is triggered from the frontend.
        This function mainly passes through the values.
        """
        return (original_prompt, processed_prompt)


@register_route("/easytoolkit_ai/process_prompt", method="POST")
async def process_prompt_api(request):
    """
    API endpoint for processing prompts with AI.
    Called by the frontend when the AI process button is clicked.
    """
    try:
        data = await request.json()
        
        original_prompt = data.get("original_prompt", "")
        ai_service = data.get("ai_service", "")
        ai_agent = data.get("ai_agent", "")
        
        if not original_prompt or not original_prompt.strip():
            return web.json_response({
                "success": False,
                "error": "Original prompt is empty"
            })
        
        if not ai_service:
            config = get_config()
            ai_service = config.get('default_ai_service', 'deepseek')
        
        if not ai_agent:
            config = get_config()
            ai_agent = config.get('default_ai_agent', 'video_prompt_expansion')
        
        # Process the prompt using AI service
        service = get_ai_service(ai_service)
        processed_text = await service.process_prompt(original_prompt, ai_agent)
        
        return web.json_response({
            "success": True,
            "processed_prompt": processed_text
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": error_msg
        })


@register_route("/easytoolkit_ai/get_config", method="GET")
async def get_ai_config(request):
    """
    API endpoint to get AI services and agents configuration.
    Used by frontend to populate dropdown options.
    """
    try:
        config = get_config()
        
        # Get AI services
        services = config.get('ai_services', {})
        service_list = []
        for service_name, service_config in services.items():
            service_list.append({
                "name": service_name,
                "label": service_name.title(),
                "model": service_config.get('model', '')
            })
        
        # Get AI agents
        agents = config.get('ai_agents', {})
        agent_list = []
        for agent_name, agent_config in agents.items():
            label = agent_config.get('label', '')
            if not label:
                # Convert snake_case to Title Case
                label = ' '.join(word.capitalize() for word in agent_name.split('_'))
            
            agent_list.append({
                "name": agent_name,
                "label": label
            })
        
        # Get defaults
        default_service = config.get('default_ai_service', 'deepseek')
        default_agent = config.get('default_ai_agent', 'video_prompt_expansion')
        
        return web.json_response({
            "success": True,
            "services": service_list,
            "agents": agent_list,
            "default_service": default_service,
            "default_agent": default_agent
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return web.json_response({
            "success": False,
            "error": error_msg
        })

