from ... import register_node
from ...utils.image import image_to_base64


@register_node
class ImageBase64Encoder:
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
                "format": (["image/png", "image/jpeg"], {
                    "default": "image/png"
                }),
            },
        }

    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("base64","file_ext",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, image, format="image/png"):
        b64 = image_to_base64(image, format)
        return {"result": (b64,format.split("/")[-1],)}
