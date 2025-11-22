from ... import register_node

@register_node(emoji="🧮")
class BytesComparer:
    """
    Bytes comparison node
    Compare two BYTES data with different comparison methods
    content_equals provides detailed byte-by-byte analysis
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data1": ("BYTES", {}),
                "data2": ("BYTES", {}),
                "comparison_type": (["content_equals", "length_equals", "data1_longer", "data2_longer"], {
                    "default": "content_equals"
                }),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "INT", "INT", "STRING")
    RETURN_NAMES = ("result", "length1", "length2", "details")

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, data1, data2, comparison_type):
        """
        Compare two BYTES data based on the specified comparison type.
        """
        length1 = len(data1)
        length2 = len(data2)
        details = ""

        if comparison_type == "content_equals":
            result, details = self._compare_bytes_content(data1, data2)
        elif comparison_type == "length_equals":
            result = length1 == length2
            details = f"Length comparison: {length1} vs {length2} = {result}"
        elif comparison_type == "data1_longer":
            result = length1 > length2
            details = f"Length comparison: {length1} > {length2} = {result}"
        elif comparison_type == "data2_longer":
            result = length1 < length2
            details = f"Length comparison: {length1} < {length2} = {result}"
        else:
            result = False
            details = "Unknown comparison type"

        return (result, length1, length2, details)

    def _compare_bytes_content(self, data1, data2):
        """
        Compare two bytes objects byte by byte and return detailed results.
        """
        # Check if data1 and data2 are the same object (same pointer)
        if data1 is data2:
            return True, "Same object reference - data is identical"

        min_len = min(len(data1), len(data2))

        differences = []
        all_equal = True

        # Compare byte by byte up to the minimum length
        for i in range(min_len):
            if data1[i] != data2[i]:
                differences.append(f"Position {i}: 0x{data1[i]:02X} vs 0x{data2[i]:02X}")
                all_equal = False

        # Check for extra bytes in longer data
        if len(data1) > len(data2):
            for i in range(len(data2), len(data1)):
                differences.append(f"Position {i}: 0x{data1[i]:02X} vs (missing)")
                all_equal = False
        elif len(data2) > len(data1):
            for i in range(len(data1), len(data2)):
                differences.append(f"Position {i}: (missing) vs 0x{data2[i]:02X}")
                all_equal = False

        # Build detailed result
        if all_equal and len(data1) == len(data2):
            details = f"All {min_len} bytes match exactly"
        elif all_equal and len(data1) != len(data2):
            details = f"First {min_len} bytes match, but lengths differ ({len(data1)} vs {len(data2)})"
        else:
            diff_count = len(differences)
            sample_diffs = differences[:5]  # Show first 5 differences
            details = f"Found {diff_count} differences. Sample: {', '.join(sample_diffs)}"
            if diff_count > 5:
                details += f" ... and {diff_count - 5} more"

        return all_equal and len(data1) == len(data2), details