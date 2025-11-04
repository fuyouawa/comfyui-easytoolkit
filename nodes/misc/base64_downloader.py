from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.format import format_filename
from ...utils.context import get_persistent_context, has_persistent_context

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
                "format": (["image/png", "image/jpeg", "image/gif", "image/webp", "video/mp4", "video/webm", "text/plain"], {
                    "default": "image/png"
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
        get_persistent_context(uuid).set_value({
            "base64_image": base64,
            "basename": basename,
            "format": format
        })

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
    
    last_image_cache = get_persistent_context(uuid).get_value()

    if not last_image_cache:
        return web.json_response({"success": False, "error": "There is no base64 data at all."})

    if not basename:
        basename = last_image_cache["basename"]
    if not format:
        format = last_image_cache["format"]
    
    basename = format_filename(basename)
    if '%counter%' in basename:
        _download_counter += 1
        basename = basename.replace('%counter%', str(_download_counter))

    return web.json_response({
            "success": True,
            "base64_image": last_image_cache["base64_image"],
            "basename": basename,
            "format": format
        })

    
@routes.post("/base64_cache_downloader/clear")
async def handle_clear(request):
    global _image_cache_by_uuid

    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid or uuid not in _image_cache_by_uuid:
        return web.json_response({"success": False, "error": "There is no base64 data at all."})
    
    del _image_cache_by_uuid[uuid]
    return web.json_response({"success": True})