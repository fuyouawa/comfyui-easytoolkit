from ... import register_node

@register_node(emoji="🧮")
class BytesMerger:
    """
    Bytes concatenation node
    Merge two BYTES data into one
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data1": ("BYTES", {}),
                "data2": ("BYTES", {}),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("merged_data",)

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, data1, data2):
        """
        Merge two BYTES data into one.
        """
        merged_data = data1 + data2
        return (merged_data,)