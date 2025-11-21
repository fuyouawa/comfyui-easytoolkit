from ... import register_node
from ...utils.format import static_image_formats

@register_node(emoji="🪲")
class ImageBase64Previewer:
    """
    A ComfyUI node that previews base64 encoded images in the frontend.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64": ("STRING", {
                    "default": ""
                }),
                "format": (static_image_formats, {
                    "default": static_image_formats[0],
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Debug"
    OUTPUT_NODE = True

    def run(self, base64, format="image/png"):
        """
        Preview base64 encoded image in frontend.
        """
        # Validate base64 string
        if not base64 or not base64.strip():
            return {
                "result": ("",),
                "ui": {
                    "base64_preview": [{
                        "base64_data": "",
                        "format": format,
                        "error": "Empty base64 image data"
                    }]
                }
            }

        # Clean the base64 string (remove data:image/... prefix if present)
        clean_base64 = base64.strip()
        if clean_base64.startswith("data:image/"):
            # Extract just the base64 part after the comma
            parts = clean_base64.split(",", 1)
            if len(parts) == 2:
                clean_base64 = parts[1]

        # Validate base64 format
        if not clean_base64:
            return {
                "result": (base64,),
                "ui": {
                    "base64_preview": [{
                        "base64_data": "",
                        "format": format,
                        "error": "Invalid base64 image format"
                    }]
                }
            }

        # Return the base64 data for frontend preview
        return {
            "result": (base64,),
            "ui": {
                "base64_preview": [{
                    "base64_data": clean_base64,
                    "format": format,
                    "error": ""
                }]
            }
        }