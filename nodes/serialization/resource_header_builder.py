from ... import register_node
from ...utils.serialization import ResourceHeader, CompressionMode, SerializationFormat, compression_modes, serialization_formats
from ...utils.format import all_resource_formats


@register_node(emoji="📦")
class ResourceHeaderBuilder:
    """
    ResourceHeader builder node.

    Creates a ResourceHeader object from format, compression mode, and serialization format inputs.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format": (all_resource_formats, {
                    "default": all_resource_formats[0],
                }),
                "compression_mode": (compression_modes, {
                    "default": compression_modes[0],
                }),
                "serialization_format": (serialization_formats, {
                    "default": serialization_formats[0],
                }),
            },
        }

    RETURN_TYPES = ("RESOURCEHEADER",)
    RETURN_NAMES = ("resource_header",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"

    def run(self, format: str, compression_mode, serialization_format):
        """
        Create ResourceHeader from input parameters.
        """
        resource_header = ResourceHeader.from_mime_type(format, compression_mode, serialization_format)
        return {"result": (resource_header,)}