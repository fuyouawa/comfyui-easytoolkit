from ... import register_node
from ...utils.image import image_to_bytes
from ...utils.format import static_image_formats


@register_node(emoji="📦")
class ImageSerializer:
    """
    Image serializer node.

    Serializes ComfyUI image tensor to bytes data.
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

    RETURN_TYPES = ("BYTES", "STRING",)
    RETURN_NAMES = ("data", "suffix",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"
    OUTPUT_NODE = True

    def run(self, image, format: str = "image/png") -> dict:
        """
        Serialize image to bytes data.
        """
        image_bytes = image_to_bytes(image, format)
        suffix = format.split("/")[-1]
        return {"result": (image_bytes, suffix,)}
