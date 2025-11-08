from aiohttp import web
from ... import register_node, register_route
from ...utils.image import image_to_base64
from ...utils.context import get_persistent_context, has_persistent_context
from ...utils.format import static_image_formats, mime_type_to_file_suffix
from ..misc.base64_context import Base64Context

@register_node
class ImagePreviewer:
    """
    Single image previewer for ComfyUI workflows.
    
    Converts images to base64 format and stores in persistent context for web preview.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        """
        Process single image and store in persistent context for preview.
        """
        base64_data = image_to_base64(image, format=format)

        suffix = mime_type_to_file_suffix(format)
        filename = f"TEMPORARY.{suffix}"

        context = Base64Context(base64_data, filename)
        get_persistent_context(uuid).set_value(context)

        return {"result": (image,), "ui": {"uuid": [uuid]}}


@register_route("/image_previewer/get_image")
async def handle_get_image(request):
    """API endpoint to retrieve single image data from persistent context."""
    data = await request.json()
    uuid = data.get("uuid", None)

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required"})
    
    if not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": f"Context not found for uuid '{uuid}'"})
    
    context = get_persistent_context(uuid).get_value()

    if not context or not isinstance(context, Base64Context):
        return web.json_response({"success": False, "error": "Invalid context data"})

    base64_data = context.get_base64()
    format_type = context.get_format()

    return web.json_response({
        "success": True,
        "base64": base64_data,
        "format": format_type
    })
