from ... import register_node
from ...utils.format import static_image_formats

@register_node(emoji="🔐")
class ImageBatchBase64Previewer:
    """
    A ComfyUI node that previews batch of base64 encoded images in the frontend.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64_batch": ("STRING", {
                    "default": ""
                }),
                "format": (static_image_formats, {
                    "default": static_image_formats[0],
                }),
                "fps": ("FLOAT", {
                    "default": 24.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 1.0
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64_batch",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64_batch, format="image/png", fps=24.0):
        """
        Preview batch of base64 encoded images in frontend.
        """
        # Validate base64 string
        if not base64_batch or not base64_batch.strip():
            return {
                "result": ("",),
                "ui": {
                    "base64_batch_preview": [{
                        "base64_datas": [],
                        "format": format,
                        "fps": fps,
                        "error": "Empty base64 image data"
                    }]
                }
            }

        # Parse the base64 list (separated by newlines)
        base64_items = base64_batch.strip().split("\n")
        clean_base64_list = []

        for base64_item in base64_items:
            if not base64_item.strip():
                continue

            # Clean the base64 string (remove data:image/... prefix if present)
            clean_base64 = base64_item.strip()
            if clean_base64.startswith("data:image/"):
                # Extract just the base64 part after the comma
                parts = clean_base64.split(",", 1)
                if len(parts) == 2:
                    clean_base64 = parts[1]

            if clean_base64:
                clean_base64_list.append(clean_base64)

        # Validate base64 format
        if not clean_base64_list:
            return {
                "result": (base64_batch,),
                "ui": {
                    "base64_batch_preview": [{
                        "base64_datas": [],
                        "format": format,
                        "fps": fps,
                        "error": "No valid base64 images found"
                    }]
                }
            }

        # Return the base64 data for frontend preview
        return {
            "result": (base64_batch,),
            "ui": {
                "base64_batch_preview": [{
                    "base64_datas": clean_base64_list,
                    "format": format,
                    "fps": fps,
                    "error": ""
                }]
            }
        }