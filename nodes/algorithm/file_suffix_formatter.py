from ... import register_node
from ...utils.format import file_suffix_to_mime_type, all_resource_formats

@register_node
class FileSuffixFormatter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "suffix": ("STRING", {
                    "default": "png",
                }),
            },
        }
    
    RETURN_TYPES = (all_resource_formats,)
    RETURN_NAMES = ("format",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, suffix):
        format = file_suffix_to_mime_type(suffix)
        return {"result": (format,)}