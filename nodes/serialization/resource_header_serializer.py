from ... import register_node
from ...utils.serialization import ResourceHeader


@register_node(emoji="📦")
class ResourceHeaderSerializer:
    """
    ResourceHeader serializer node.

    Converts a ResourceHeader object to bytes representation.
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

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("header_bytes",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"

    def run(self, resource_header: ResourceHeader):
        """
        Convert ResourceHeader to bytes.
        """
        header_bytes = resource_header.to_bytes()
        return (header_bytes,)