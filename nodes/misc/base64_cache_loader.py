from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.persistent_context import get_persistent_context, has_persistent_context

routes = PromptServer.instance.routes

@register_node
class Base64CacheLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
        """
        return {
            "required": {
                "filename": ("STRING", {
                    "default": "",
                }),
                "uuid": ("STRING", {
                    "default": "",
                }),
            },
        }
    

    RETURN_TYPES = ("STRING","STRING","STRING",)
    RETURN_NAMES = ("base64","basename","suffix")
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Misc"
    OUTPUT_NODE = True

    def run(self, filename: str, uuid):
        last_data_cache = get_persistent_context(uuid).get_value()
        if not last_data_cache:
            raise Exception("There is no base64 data at all.")

        base64 = last_data_cache["base64"]
        basename = filename.split(".").pop().join(".")
        suffix = filename.split(".")[-1]
        return {"result": (base64, basename, suffix,)}


@routes.post("/base64_cache_loader/update")
async def handle_update(request):
    data = await request.json()
    uuid = data.get("uuid", None)
    if not uuid:
        return web.json_response({"success": False, "error": "uuid is required."})
    
    format = data.get("format", None)
    if not format:
        return web.json_response({"success": False, "error": "format is required."})
    
    base64 = data.get("base64", None)
    if not base64:
        return web.json_response({"success": False, "error": "base64 is required."})

    filename = data.get("filename", None)
    if not filename:
        return web.json_response({"success": False, "error": "filename is required."})

    get_persistent_context(uuid).set_value({
        "base64": base64,
        "filename": filename,
        "format": format
    })

    return web.json_response({"success": True})