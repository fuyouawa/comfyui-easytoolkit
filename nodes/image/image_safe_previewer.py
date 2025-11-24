from ... import register_node
from ...utils.format import static_image_formats
from ...utils.image import image_to_bytes
from ...utils.encoding import encode_bytes
import base64

@register_node(emoji="🖼️")
class ImageSafePreviewer:
    """
    A ComfyUI node that previews images in the frontend by converting them to base64.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "format": (static_image_formats, {
                    "default": static_image_formats[0],
                }),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"
    OUTPUT_NODE = True

    def run(self, image, format="image/png"):
        """
        Convert image to base64 and preview in frontend.
        """
        # Convert image to bytes
        image_bytes = image_to_bytes(image, format)

        # Convert bytes to base64
        base64_data = encode_bytes(image_bytes, "base64")

        # Return the base64 data for frontend preview
        return {
            "result": (),
            "ui": {
                "base64_preview": [{
                    "base64_data": base64_data,
                    "format": format
                }]
            }
        }