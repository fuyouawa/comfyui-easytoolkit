from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.image import image_to_base64
import datetime
import re
import time

routes = PromptServer.instance.routes

_last_image_cache: dict = None
_download_counter = 0

class FileNameFormatter:
    """
    文件名格式化器
    支持动态变量替换
    """

    @staticmethod
    def format_filename(template: str) -> str:
        """
        格式化文件名模板

        Args:
            template: 文件名模板，支持以下变量：
                %date:yyyy-MM-dd% - 日期
                %date:hh-mm-ss% - 时间
                %timestamp% - 时间戳
                %counter% - 下载计数器
                %random% - 随机数
                %width% - 图像宽度
                %height% - 图像高度
        """
        global _download_counter

        # 替换日期和时间变量
        now = datetime.datetime.now()

        def format_date(match):
            """将用户友好的日期格式转换为Python strftime格式"""
            user_format = match.group(1)
            # 格式映射：用户友好格式 -> Python strftime格式
            format_mapping = {
                'yyyy': '%Y',  # 四位年份
                'yy': '%y',    # 两位年份
                'MM': '%m',    # 两位月份
                'dd': '%d',    # 两位日期
                'HH': '%H',    # 24小时制小时
                'hh': '%I',    # 12小时制小时
                'mm': '%M',    # 分钟
                'ss': '%S',    # 秒
            }

            # 替换格式代码
            python_format = user_format
            for user_code, python_code in format_mapping.items():
                python_format = python_format.replace(user_code, python_code)

            return now.strftime(python_format)

        # 日期格式
        template = re.sub(
            r'%date:(.*?)%',
            format_date,
            template
        )

        # 时间戳
        template = template.replace('%timestamp%', str(int(time.time())))

        # 计数器
        if '%counter%' in template:
            _download_counter += 1
            template = template.replace('%counter%', str(_download_counter))

        # 随机数
        if '%random%' in template:
            import random
            template = template.replace('%random%', str(random.randint(1000, 9999)))

        # 确保文件扩展名
        if not template.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            template += '.png'

        return template

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
                "file_name": ("STRING", {
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

    def run(self, image, file_name):
        global _last_image_cache

        # 格式化文件名
        formatted_file_name = FileNameFormatter.format_filename(file_name)

        # 将图像缓存下来，供按钮下载使用
        _last_image_cache = {
            "base64_image": image_to_base64(image),
            "file_name": formatted_file_name
        }
        return ()
    
@routes.post("/image_downloader/download")
async def handle_download(request):
    global _last_image_cache

    if _last_image_cache is None:
        return web.json_response({"success": False, "error": "There is no image data at all."})
    return web.json_response({
            "success": True,
            "base64_image": _last_image_cache["base64_image"],
            "file_name": _last_image_cache["file_name"]
        })
