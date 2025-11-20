# from aiohttp import web
# from ... import register_node, register_route
# from ...utils.config import get_config

# @register_node(emoji="⚙️")
# class AIAgentsConfig:
#     """
#     A ComfyUI node for managing AI Agents configuration with dynamic controls.
#     """

#     def __init__(self):
#         pass

#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "default_agent": ("COMBO", {"default": ""}),
#                 "config_data": ("STRING", {"default": "{}"}),
#             },
#         }

#     RETURN_TYPES = ()
#     RETURN_NAMES = ()
#     FUNCTION = "run"
#     CATEGORY = "EasyToolkit/Config"
#     OUTPUT_NODE = False

#     def run(self, default_agent, config_data):
#         pass


# @register_route("/easytoolkit_config/get_ai_agents", method="GET")
# async def handle_get_ai_agents(request):
#     """
#     API endpoint to retrieve AI agents configuration.
#     """
#     try:
#         config = get_config()
#         ai_agents = config.get('ai_agents', {})
#         default_agent = config.get('default_ai_agent', '')

#         # Convert to list format for easier handling
#         agents_list = []
#         for agent_id, agent_config in ai_agents.items():
#             agents_list.append({
#                 'id': agent_id,
#                 'label': agent_config.get('label', ''),
#                 'summary': agent_config.get('summary', '')
#             })

#         return web.json_response({
#             "success": True,
#             "agents": agents_list,
#             "default_agent": default_agent
#         })
#     except Exception as e:
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)


# @register_route("/easytoolkit_config/save_ai_agents", method="POST")
# async def handle_save_ai_agents(request):
#     """
#     API endpoint to save AI agents configuration to override file (JSON format).
#     """
#     try:
#         data = await request.json()
#         agents_list = data.get("agents", [])
#         default_agent = data.get("default_agent", "")

#         # Convert list back to dict format
#         ai_agents = {}
#         for agent in agents_list:
#             agent_id = agent.get('id', '').strip()
#             if agent_id:  # Only add agents with valid IDs
#                 ai_agents[agent_id] = {
#                     'label': agent.get('label', ''),
#                     'summary': agent.get('summary', '')
#                 }

#         # Use config utility to set ai_agents
#         config = get_config()
#         config.set("ai_agents", ai_agents)

#         # Update default_ai_agent if provided
#         if default_agent:
#             config.set("default_ai_agent", default_agent)
#         else:
#             # Remove default_ai_agent if it's empty
#             config.delete("default_ai_agent")

#         return web.json_response({
#             "success": True,
#             "message": "AI agents configuration saved successfully",
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)


# @register_route("/easytoolkit_config/delete_ai_agent", method="POST")
# async def handle_delete_ai_agent(request):
#     """
#     API endpoint to delete a specific AI agent from configuration.
#     """
#     try:
#         data = await request.json()
#         agent_id = data.get("agent_id", "")

#         if not agent_id:
#             return web.json_response({
#                 "success": False,
#                 "error": "Agent ID is required"
#             }, status=400)

#         # Check if agent exists
#         config = get_config()
#         ai_agents = config.get("ai_agents", {})
#         if agent_id not in ai_agents:
#             return web.json_response({
#                 "success": False,
#                 "error": f"Agent '{agent_id}' not found"
#             }, status=404)

#         # Remove the agent using config.delete with dot notation
#         config.delete(f"ai_agents.{agent_id}")

#         # Update default agent if it was the deleted one
#         default_agent = config.get("default_ai_agent", "")
#         if default_agent == agent_id:
#             config.set("default_ai_agent", "")

#         return web.json_response({
#             "success": True,
#             "message": f"Agent '{agent_id}' deleted successfully",
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)


# @register_route("/easytoolkit_config/reset_ai_agents", method="POST")
# async def handle_reset_ai_agents(request):
#     """
#     API endpoint to reset AI agents configuration by removing ai_agents from override file.
#     """
#     try:
#         config = get_config()

#         # Remove ai_agents and default_ai_agent sections using config utility
#         config_changed = False

#         if config.get("ai_agents") is not None:
#             config.delete("ai_agents")
#             config_changed = True

#         if config.get("default_ai_agent") is not None:
#             config.delete("default_ai_agent")
#             config_changed = True

#         if config_changed:
#             return web.json_response({
#                 "success": True,
#                 "message": "AI agents configuration reset successfully",
#             })
#         else:
#             return web.json_response({
#                 "success": True,
#                 "message": "No AI agents configuration found to reset",
#             })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)

