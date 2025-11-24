from ... import register_node
from ...utils.format import file_extension_to_mime_type, all_resource_formats

@register_node(emoji="🔧")
class FileExtensionToFormatType:
    """
    A ComfyUI node that converts file extension to MIME types.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "extension": ("STRING", {
                    "default": "png",
                }),
            },
        }

    RETURN_TYPES = (all_resource_formats,)
    RETURN_NAMES = ("format",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Formatting"

    def run(self, extension):
        """
        Convert file extension to MIME type.
        """
        format = file_extension_to_mime_type(extension)
        return {"result": (format,)}