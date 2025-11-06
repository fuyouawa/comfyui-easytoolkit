from aiohttp import web
from ... import register_node, register_route
from ...utils.image import image_to_base64
from ...utils.context import get_persistent_context, has_persistent_context
from ...utils.format import static_image_formats

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
                "format": (static_image_formats, {"default": "image/jpeg"}),
                "uuid": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"
    OUTPUT_NODE = True

    def run(self, image, format, uuid):
        # Convert image to base64
        base64_data = image_to_base64(image, format=format)
        
        # Store base64 data in persistent context
        get_persistent_context(uuid).set_value({
            "base64": base64_data,
            "format": format
        })
        
        return {"result": (image,), "ui": {"uuid": [uuid]}}


@register_route("/image_previewer/get_image")
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
