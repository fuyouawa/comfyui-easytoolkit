from ... import register_node
from ...utils.image import bytes_to_image
from ...utils.encoding import b64decode


@register_node(emoji="🔐")
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
                    "default": ""
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
        image_bytes = b64decode(base64)
        image, mask = bytes_to_image(image_bytes)
        return {"result": (image, mask,)}
