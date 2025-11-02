from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.image import image_to_base64
from ...utils.format import format_filename

routes = PromptServer.instance.routes

_last_image_cache: dict = None
_download_counter = 0

@register_node
class ImageDownloader:
    """
    图像下载器节点
    提供前端按钮来下载传入的图像
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING", {
                    "default": "%date:yyyy-MM-dd%_%date:hh-mm-ss%",
                    "multiline": False,
                    "dynamicPrompts": False,
                    "placeholder": "文件名模板，支持变量: %date:格式%, %timestamp%, %counter%, %random%"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"
    OUTPUT_NODE = True

    def run(self, image, filename):
        global _last_image_cache

        # 将图像缓存下来，供按钮下载使用
        _last_image_cache = {
            "base64_image": image_to_base64(image),
            "filename": format_filename(filename)
        }
        return ()
    
@routes.post("/image_downloader/download")
async def handle_download(request):
    global _last_image_cache
    global _download_counter

    if _last_image_cache is None:
        return web.json_response({"success": False, "error": "There is no image data at all."})
    
    filename = _last_image_cache["filename"]
    if '%counter%' in filename:
        _download_counter += 1
        filename = filename.replace('%counter%', str(_download_counter))

    return web.json_response({
            "success": True,
            "base64_image": _last_image_cache["base64_image"],
            "filename": filename
        })
