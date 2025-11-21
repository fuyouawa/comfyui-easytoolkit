from ... import register_node
from ...utils.image import bytes_to_image


@register_node(emoji="📦")
class ImageDeserializer:
    """
    Image deserializer node.

    Deserializes bytes data to ComfyUI image tensor and mask.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("BYTES", {
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK",)
    RETURN_NAMES = ("image", "mask",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"
    OUTPUT_NODE = True

    def run(self, data) -> dict:
        """
        Deserialize bytes data to image and mask.
        """
        image, mask = bytes_to_image(data)
        return {"result": (image, mask,)}
