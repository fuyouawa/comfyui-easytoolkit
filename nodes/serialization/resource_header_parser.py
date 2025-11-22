from ... import register_node
from ...utils.serialization import ResourceHeader, CompressionMode, SerializationFormat, compression_modes, serialization_formats
from ...utils.format import all_resource_formats


@register_node(emoji="📦")
class ResourceHeaderParser:
    """
    ResourceHeader parser node.

    Parses a ResourceHeader object into its individual fields.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resource_header": ("RESOURCEHEADER",),
            },
        }

    RETURN_TYPES = (all_resource_formats, compression_modes, serialization_formats)
    RETURN_NAMES = ("format", "compression_mode", "serialization_format")
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"

    def run(self, resource_header: ResourceHeader):
        """
        Parse ResourceHeader into individual fields.
        """

        return (
            resource_header.mime_type,
            resource_header.compression_mode,
            resource_header.serialization_format,
            )