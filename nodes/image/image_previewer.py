from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.image import image_to_base64
from ...utils.context import get_persistent_context, has_persistent_context, update_persistent_context

routes = PromptServer.instance.routes

@register_node
class ImagePreviewer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "uuid": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"
    OUTPUT_NODE = True

    def run(self, image, uuid):
        # Convert image to base64
        base64_data = image_to_base64(image, format="image/png")
        
        # Store base64 data in persistent context
        get_persistent_context(uuid).set_value({
            "base64": base64_data,
            "format": "image/png"
        })
        
        return {"result": (image,), "ui": {"uuid": [uuid]}}


@routes.post("/image_previewer/get_image")
async def handle_get_image(request):
    """Get base64 image data from context by uuid"""
    data = await request.json()
    uuid = data.get("uuid", None)

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required"})
    
    if not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": f"Context not found for uuid '{uuid}'"})
    
    context = get_persistent_context(uuid).get_value()

    if not context or not isinstance(context, dict):
        return web.json_response({"success": False, "error": "Invalid context data"})

    base64_data = context.get("base64", "")
    format_type = context.get("format", "image/png")

    return web.json_response({
        "success": True,
        "base64": base64_data,
        "format": format_type
    })


@routes.post("/image_previewer/update_access")
async def handle_update_access(request):
    """Update the access time for a context to prevent it from being cleaned up"""
    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required."})

    if not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": "Context not found."})
    
    # Update access time
    update_persistent_context(uuid)
    return web.json_response({"success": True})

@routes.post("/image_previewer/clear")
async def handle_clear(request):
    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid or not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": "没有base64数据。"})
    
    # Clear the persistent context by setting it to None
    get_persistent_context(uuid).set_value(None)
    return web.json_response({"success": True})