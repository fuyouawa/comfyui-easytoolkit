from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.format import format_filename

routes = PromptServer.instance.routes

_image_cache_by_uuid: dict[str, dict[str, any]] = {}
_download_counter = 0

@register_node
class Base64CacheDownloader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
        """
        return {
            "required": {
                "base64": ("STRING", {
                    "default": "",
                }),
                "filename": ("STRING", {
                    "default": "%date:yyyy-MM-dd%_%date:hh-mm-ss%"
                }),
                "format": (["image/png", "image/jpeg", "image/gif", "image/webp", "video/mp4", "video/webm"], {
                    "default": "image/png"
                }),
                "uuid": ("STRING", {
                    "default": "",
                }),
            },
        }
    

    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("filename","file_ext",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Misc"
    OUTPUT_NODE = True

    def run(self, base64, filename, format, uuid):
        global _image_cache_by_uuid

        formatted_filename = format_filename(filename)

        _image_cache_by_uuid[uuid] = {
            "base64_image": base64,
            "filename": formatted_filename,
            "format": format
        }
        return {"result": (formatted_filename, format.split("/")[-1],)}

    
@routes.post("/base64_cache_downloader/download")
async def handle_download(request):
    global _image_cache_by_uuid
    global _download_counter

    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid or uuid not in _image_cache_by_uuid:
        return web.json_response({"success": False, "error": "There is no base64 data at all."})
    
    last_image_cache = _image_cache_by_uuid[uuid]
    
    filename = last_image_cache["filename"]
    if '%counter%' in filename:
        _download_counter += 1
        filename = filename.replace('%counter%', str(_download_counter))

    return web.json_response({
            "success": True,
            "base64_image": last_image_cache["base64_image"],
            "filename": filename,
            "format": last_image_cache["format"]
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