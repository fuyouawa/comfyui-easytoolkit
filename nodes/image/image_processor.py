from ... import register_node
from ...utils.image import process_image

@register_node
class ImageProcessor:
    """
    图像处理器节点
    提供多种图像处理功能：颜色翻转、异或加密/解密
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
                "operation": (["invert", "xor-16", "xor-32", "xor-64", "xor-128"], {
                    "default": "invert"
                }),
                "enable": ("BOOLEAN", {
                    "default": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"

    def run(self, image, enable, operation):
        """
        处理图像的主函数
        """
        if not enable:
            return (image,)

        processed_images = process_image(image, operation)
        return (processed_images,)