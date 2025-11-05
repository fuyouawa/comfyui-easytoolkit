from aiohttp import web
from ... import register_node, register_route
from ...utils.image import image_batch_to_base64_list
from ...utils.context import get_context, has_context, update_context

@register_node
class ImageBatchPreviewer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "fps": ("INT", {"default": 8, "min": 1, "max": 60, "step": 1}),
                "uuid": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_batch",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"
    OUTPUT_NODE = True

    def run(self, image_batch, fps, uuid):
        # Convert image batch to base64 list
        base64_list = image_batch_to_base64_list(image_batch, format="image/png")
        
        # Store base64 data list in persistent context
        get_context(uuid).set_value({
            "base64_list": base64_list,
            "format": "image/png",
            "fps": fps,
            "frame_count": len(base64_list)
        })
        
        return {"result": (image_batch,), "ui": {"uuid": [uuid], "frame_count": [len(base64_list)], "fps": [fps]}}


@register_route("/image_batch_previewer/get_images")
async def handle_get_images(request):
    """Get base64 image list data from context by uuid"""
    data = await request.json()
    uuid = data.get("uuid", None)

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required"})
    
    if not has_context(uuid):
        return web.json_response({"success": False, "error": f"Context not found for uuid '{uuid}'"})
    
    context = get_context(uuid).get_value()

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


@register_route("/image_batch_previewer/update_access")
async def handle_update_access(request):
    """Update the access time for a context to prevent it from being cleaned up"""
    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required."})

    if not has_context(uuid):
        return web.json_response({"success": False, "error": "Context not found."})
    
    # Update access time
    update_context(uuid)
    return web.json_response({"success": True})

