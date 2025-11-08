from aiohttp import web
from ... import register_node, register_route
from ...utils.image import image_batch_to_base64_list
from ...utils.context import get_persistent_context, has_persistent_context
from ...utils.format import static_image_formats

@register_node
class ImageBatchPreviewer:
    """
    Batch image previewer for ComfyUI workflows.
    
    Converts image batches to base64 format and stores in persistent context for web preview.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "format": (static_image_formats, {"default": "image/jpeg"}),
                "fps": ("INT", {"default": 16, "min": 1, "max": 60, "step": 1}),
                "uuid": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_batch",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"
    OUTPUT_NODE = True

    def run(self, image_batch, format, fps, uuid):
        """
        Process image batch and store in persistent context for preview.
        """
        base64_list = image_batch_to_base64_list(image_batch, format=format)

        get_persistent_context(uuid).set_value({
            "base64_list": base64_list,
            "format": format,
            "fps": fps,
            "frame_count": len(base64_list)
        })

        return {"result": (image_batch,), "ui": {"uuid": [uuid], "frame_count": [len(base64_list)], "fps": [fps]}}


@register_route("/image_batch_previewer/get_images")
async def handle_get_images(request):
    """API endpoint to retrieve batch image data from persistent context."""
    data = await request.json()
    uuid = data.get("uuid", None)

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required"})
    
    if not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": f"Context not found for uuid '{uuid}'"})
    
    context = get_persistent_context(uuid).get_value()

    if not context or not isinstance(context, dict):
        return web.json_response({"success": False, "error": "Invalid context data"})

    base64_list = context.get("base64_list", [])
    format_type = context.get("format", "image/png")
    fps = context.get("fps", 8)
    frame_count = context.get("frame_count", 0)

    return web.json_response({
        "success": True,
        "base64_list": base64_list,
        "format": format_type,
        "fps": fps,
        "frame_count": frame_count
    })
