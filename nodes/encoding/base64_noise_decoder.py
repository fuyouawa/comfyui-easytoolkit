from ... import register_node
from ...utils.image import noise_image_to_bytes
from ...utils.encoding import b64encode
import zlib


@register_node(emoji="🔐")
class Base64NoiseDecoder:
    """
    Base64 noise decoder node.

    Decodes base64 string from a noise-like image where the data
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

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, noise_image) -> dict:
        """
        Decode base64 string from noise image with optional decompression.
        """
        # Extract bytes from noise image
        data_bytes = noise_image_to_bytes(noise_image)

        # Apply decompression if requested
        if data_bytes.startswith((b"\x78\x01", b"\x78\x9c", b"\x78\xda")):
            data_bytes = zlib.decompress(data_bytes)

        # Convert bytes to base64 string
        base64_string = b64encode(data_bytes)

        return {"result": (base64_string,)}

