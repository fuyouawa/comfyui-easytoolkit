from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.context import resolve_persistent_contexts_by_value_type, get_persistent_context, has_persistent_context
from .base64_context import Base64Context

routes = PromptServer.instance.routes

@register_node
class Base64ContextLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "hidden": {
                "key": ("STRING", {"default": "NONE"}),
                "mode": (["Builtin", "Dialog"], {"default": "Builtin"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("base64", "basename", "suffix")
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Misc"
    OUTPUT_NODE = True

    def run(self, key, mode):
        base64_context = get_persistent_context(key).get_value()
        if not base64_context or not isinstance(base64_context, Base64Context):
            raise Exception("There is no base64 data at all.")
        
        base64 = base64_context.get_base64()
        basename = base64_context.get_basename()
        suffix = base64_context.get_suffix()
        return {"result": (base64, basename, suffix,)}

@routes.post("/base64_context_previewer/get_keys")
async def handle_get_keys(request):
    """Get available base64 context keys"""
    base64_contexts = resolve_persistent_contexts_by_value_type(Base64Context)
    keys = [x.get_key() for x in base64_contexts]
    keys.insert(0, "NONE")
    return web.json_response({"success": True, "keys": keys})

@routes.post("/base64_context_previewer/get_data")
async def handle_get_data(request):
    """Get base64 data from context by key"""
    data = await request.json()
    key = data.get("key", None)

    if not key or key == "NONE":
        return web.json_response({"success": False, "error": "请选择一个有效的 key"})
    
    if not has_persistent_context(key):
        return web.json_response({"success": False, "error": f"未找到 key '{key}' 对应的上下文"})
    
    context = get_persistent_context(key).get_value()

    if not context or not isinstance(context, Base64Context):
        return web.json_response({"success": False, "error": "上下文数据不是 Base64Context 类型"})

    base64_data = context.get_base64()
    filename = context.get_filename()
    suffix = context.get_suffix()
    format_type = context.get_format()

    # Determine content type
    content_type = "unknown"
    image_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]
    text_extensions = ["txt", "json", "xml", "html", "css", "js", "py", "md"]
    
    if suffix.lower() in image_extensions:
        content_type = "image"
    elif suffix.lower() in text_extensions or format_type.startswith("text/"):
        content_type = "text"

    return web.json_response({
        "success": True,
        "base64": base64_data,
        "filename": filename,
        "suffix": suffix,
        "format": format_type,
        "content_type": content_type
    })