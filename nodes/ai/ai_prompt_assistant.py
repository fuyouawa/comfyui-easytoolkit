from ... import register_node, register_route
from ...utils.config import get_config
from ...utils.ai_service import get_ai_service, ClientDisconnectedError
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
                "execute_ai_request": ("BOOLEAN", {"default": False}),
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
    
    def run(self, original_prompt, ai_service, ai_agent, execute_ai_request, processed_prompt=""):
        """
        Process the prompt through AI service.
        If execute_ai_request is True, automatically process the prompt using AI.
        Otherwise, pass through the values.
        """
        if execute_ai_request and original_prompt and original_prompt.strip():
            # Execute AI request synchronously
            try:
                processed_prompt = self._process_prompt_sync(original_prompt, ai_service, ai_agent)
            except Exception as e:
                print(f"AI request failed: {str(e)}")
                # If AI request fails, return original prompt and empty processed prompt
                return (original_prompt, "")

        return (original_prompt, processed_prompt)

    def _process_prompt_sync(self, original_prompt, ai_service, ai_agent):
        """
        Synchronously process prompt using AI service.
        This runs the same logic as the API endpoint but in a synchronous manner.
        """
        import asyncio

        # Create a new event loop for this synchronous call
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async process_prompt function
            service = get_ai_service(ai_service)
            processed_text = loop.run_until_complete(
                service.process_prompt(original_prompt, ai_agent, request=None)
            )

            return processed_text

        finally:
            loop.close()


@register_route("/easytoolkit_ai/process_prompt", method="POST")
async def process_prompt_api(request):
    """
    API endpoint for processing prompts with AI.
    Called by the frontend when the AI process button is clicked.
    Supports cancellation when client disconnects.
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
        
        # Process the prompt using AI service (with request for cancellation support)
        service = get_ai_service(ai_service)
        processed_text = await service.process_prompt(original_prompt, ai_agent, request=request)
        
        return web.json_response({
            "success": True,
            "processed_prompt": processed_text
        })
    
    except ClientDisconnectedError as e:
        # Client disconnected - this is expected behavior when user cancels
        print(f"AI request cancelled: {str(e)}")
        return web.json_response({
            "success": False,
            "error": "Request cancelled",
            "cancelled": True
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
            label = service_config.get('label', '')
            if not label:
                # Convert snake_case to Title Case
                label = ' '.join(word.capitalize() for word in service_name.split('_'))
            
            service_list.append({
                "name": service_name,
                "label": label,
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

