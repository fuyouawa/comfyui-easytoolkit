from ... import register_node
from ...utils.image import noise_image_to_bytes
from ...utils.compression import decompress_bytes


@register_node
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
                "compression": (["none", "gzip", "zlib", "bz2", "lzma"], {
                    "default": "gzip"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, noise_image, compression: str = "none") -> dict:
        """
        Decode base64 string from noise image with optional decompression.

        Args:
            noise_image: Image tensor with encoded data
            compression: Compression algorithm used (none, gzip, zlib, bz2, lzma)
        """
        # Extract bytes from noise image
        data_bytes = noise_image_to_bytes(noise_image)

        # Apply decompression if requested
        if compression != "none":
            data_bytes = decompress_bytes(data_bytes, compression)

        # Convert bytes to base64 string
        base64_string = data_bytes.decode('utf-8')

        return {"result": (base64_string,)}

