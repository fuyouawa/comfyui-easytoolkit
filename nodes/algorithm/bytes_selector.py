from ... import register_node

@register_node(emoji="🧮")
class BytesSelector:
    """
    Bytes subarray extraction node
    Extract a subarray from BYTES data given start position and length
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("BYTES", {}),
                "start": ("INT", {
                    "default": 0,
                    "min": 0,
                    "step": 1
                }),
                "length": ("INT", {
                    "default": -1,
                    "min": -1,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("sub_data",)

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, data, start, length):
        """
        Extract a subarray from BYTES data.
        """
        data_length = len(data)

        # Validate start position
        if start >= data_length:
            return (b"",)

        # Calculate end position
        if length == -1:
            end = data_length
        else:
            end = min(start + length, data_length)

        # Extract subarray
        sub_data = data[start:end]

        return (sub_data,)