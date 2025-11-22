from ... import register_node
from ...utils.serialization import RESOURCE_HEADER_SIZE


@register_node(emoji="📦")
class ResourceHeaderSize:
    """
    ResourceHeader size node.

    Returns the fixed size of ResourceHeader objects (4 bytes).
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("header_size",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"

    def run(self):
        """
        Return the fixed ResourceHeader size.
        """
        return (RESOURCE_HEADER_SIZE,)