from ... import register_node
from ...utils.image import base64_to_image


@register_node
class ImageBase64Decoder:
    """
    Base64 image decoder node.

    Decodes base64 string to ComfyUI image tensor and mask.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64": ("STRING", {
                    "multiline": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK",)
    RETURN_NAMES = ("image", "mask",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64: str) -> dict:
        """
        Decode base64 to image and mask.
        """
        image, mask = base64_to_image(base64)
        return {"result": (image, mask,)}
