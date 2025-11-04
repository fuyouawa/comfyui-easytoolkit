from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.format import format_filename, all_resource_formats, file_format_to_suffix
from ...utils.context import get_persistent_context, has_persistent_context
from .base64_context import Base64Context

routes = PromptServer.instance.routes

_download_counter = 0

@register_node
class Base64Downloader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "base64": ("STRING", {
                    "default": "",
                }),
                "basename": ("STRING", {
                    "default": "%date:yyyy-MM-dd%_%date:hh-mm-ss%"
                }),
                "format": (all_resource_formats, {
                    "default": all_resource_formats[0]
                }),
                "uuid": ("STRING", {
                    "default": "",
                }),
            },
        }
    

    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("base64","uuid",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Misc"
    OUTPUT_NODE = True

    def run(self, base64, basename, format, uuid):
        # Create filename from basename and format
        filename = f"{basename}.{file_format_to_suffix(format)}"
        # Save to persistent context using Base64Context
        context = Base64Context(base64, filename)
        get_persistent_context(uuid).set_value(context)

        return {"result": (base64,uuid,)}

    
@routes.post("/base64_cache_downloader/download")
async def handle_download(request):
    global _download_counter

    data = await request.json()
    uuid = data.get("uuid", None)
    basename = data.get("basename", None)
    format = data.get("format", None)

    if not uuid or not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": "There is no base64 data at all."})
    
    context = get_persistent_context(uuid).get_value()

    if not context or not isinstance(context, Base64Context):
        return web.json_response({"success": False, "error": "There is no base64 data at all."})

    # Use basename and format from request, or fall back to context values
    if not basename:
        basename = context.get_basename()
    if not format:
        format = context.get_format()
    
    basename = format_filename(basename)
    if '%counter%' in basename:
        _download_counter += 1
        basename = basename.replace('%counter%', str(_download_counter))

    return web.json_response({
            "success": True,
            "base64": context.get_base64(),
            "basename": basename,
            "format": format
        })

    
@routes.post("/base64_cache_downloader/clear")
async def handle_clear(request):
    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid or not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": "There is no base64 data at all."})
    
    # Clear the persistent context by setting it to None
    get_persistent_context(uuid).set_value(None)
    return web.json_response({"success": True})