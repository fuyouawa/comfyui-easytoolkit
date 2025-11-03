from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.format import format_filename

routes = PromptServer.instance.routes

_last_image_cache_by_uuid: dict[str, dict[str, any]] = {}
_download_counter = 0

@register_node
class Base64Downloader:
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
                "file_format": (["png", "jpeg", "gif", "webp", "mp4", "webm"], {
                    "default": "png"
                }),
                "uuid": ("STRING", {
                    "default": "",
                }),
            },
        }
    

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Misc"
    OUTPUT_NODE = True

    def run(self, base64, filename, file_format, uuid):
        global _last_image_cache_by_uuid

        formatted_filename = format_filename(filename)

        _last_image_cache_by_uuid[uuid] = {
            "base64_image": base64,
            "filename": formatted_filename,
            "file_format": file_format
        }
        return {"result": (formatted_filename + "." + file_format,)}

    
@routes.post("/base64_downloader/download")
async def handle_download(request):
    global _last_image_cache_by_uuid
    global _download_counter

    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid or uuid not in _last_image_cache_by_uuid:
        return web.json_response({"success": False, "error": "There is no base64 data at all."})
    
    last_image_cache = _last_image_cache_by_uuid[uuid]
    
    filename = last_image_cache["filename"]
    if '%counter%' in filename:
        _download_counter += 1
        filename = filename.replace('%counter%', str(_download_counter))

    return web.json_response({
            "success": True,
            "base64_image": last_image_cache["base64_image"],
            "filename": filename,
            "file_format": last_image_cache["file_format"]
        })
