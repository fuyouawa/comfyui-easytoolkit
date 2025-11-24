from ... import register_node
from ...utils.format import mime_type_to_file_extension, all_resource_formats

@register_node(emoji="🔧")
class FormatTypeToFileExtension:
    """
    A ComfyUI node that converts MIME types to file extension.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "format": (all_resource_formats, {
                    "default": all_resource_formats[0],
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("extension",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Formatting"

    def run(self, format):
        """
        Convert MIME types to file extension.
        """
        extension = mime_type_to_file_extension(format)
        return {"result": (extension,)}