from ... import register_node
from ...utils.format import mime_type_to_file_suffix, all_resource_formats

@register_node(emoji="🔧")
class MimeTypeToFileSuffix:
    """
    A ComfyUI node that converts MIME types to file suffix.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mime_type": (all_resource_formats, {
                    "default": "png",
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("suffix",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Formatting"

    def run(self, mime_type):
        """
        Convert MIME types to file suffix.
        """
        format = mime_type_to_file_suffix(mime_type)
        return {"result": (format,)}