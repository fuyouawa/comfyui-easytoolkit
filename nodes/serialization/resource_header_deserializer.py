from ... import register_node
from ...utils.serialization import ResourceHeader


@register_node(emoji="📦")
class ResourceHeaderDeserializer:
    """
    ResourceHeader deserializer node.

    Converts bytes representation back to a ResourceHeader object.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "header_bytes": ("BYTES",),
            },
        }

    RETURN_TYPES = ("EASYTOOLKIT_RESOURCEHEADER",)
    RETURN_NAMES = ("resource_header",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"

    def run(self, header_bytes: bytes):
        """
        Convert bytes to ResourceHeader.
        """
        resource_header = ResourceHeader.from_bytes(header_bytes)
        return (resource_header,)