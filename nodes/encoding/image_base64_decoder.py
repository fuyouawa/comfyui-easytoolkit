from ... import register_node
from ...utils.image import base64_to_image


@register_node
class ImageBase64Decoder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "base64": ("STRING",),
            },
        }

    RETURN_TYPES = ("IMAGE","MASK",)
    RETURN_NAMES = ("image","mask",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64):
        image, mask = base64_to_image(base64)
        return {"result": (image, mask,)}
