from ... import register_node
from ...utils.image import data_image_to_bytes
import zlib


@register_node(emoji="📦")
class DataImageDeserializer:
    """
    Data image deserializer node.

    Deserializes bytes data from a noise-like image where the data
    is hidden in the pixel values.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise_image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("data",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"
    OUTPUT_NODE = True

    def run(self, noise_image) -> dict:
        """
        Deserialize bytes data from noise image with optional decompression.
        """
        # Extract bytes from noise image
        data_bytes = data_image_to_bytes(noise_image)

        # Apply decompression if requested
        if data_bytes.startswith((b"\x78\x01", b"\x78\x9c", b"\x78\xda")):
            data_bytes = zlib.decompress(data_bytes)

        return {"result": (data_bytes,)}

