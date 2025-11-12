from ... import register_node
from ...utils.image import image_to_bytes
from ...utils.encoding import b64encode
from ...utils.format import static_image_formats


@register_node(emoji="🔐")
class ImageBase64Encoder:
    """
    Base64 image encoder node.

    Encodes ComfyUI image tensor to base64 string.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "format": (static_image_formats, {
                    "default": static_image_formats[0],
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("base64", "suffix",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, image, format: str = "image/png") -> dict:
        """
        Encode image to base64.
        """
        image_bytes = image_to_bytes(image, format)
        b64 = b64encode(image_bytes)
        suffix = format.split("/")[-1]
        return {"result": (b64, suffix,)}
