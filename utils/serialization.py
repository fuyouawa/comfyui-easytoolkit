"""
Serialization utilities for byte stream operations.
"""


def merge_bytes_with_headers(bytes_list):
    """
    Merge a list of bytes objects into a single bytes object with size headers.

    Format: [4-byte size][data][4-byte size][data]...
    Each size is stored as big-endian 32-bit integer.

    Args:
        bytes_list: List of bytes objects to merge

    Returns:
        bytes: Merged bytes object with size headers
    """
    merged_bytes = b""

    for data_bytes in bytes_list:
        # Convert size to 4-byte big-endian
        size_bytes = len(data_bytes).to_bytes(4, byteorder='big')
        # Append size header and data
        merged_bytes += size_bytes + data_bytes

    return merged_bytes


def split_bytes_with_headers(merged_bytes):
    """
    Split merged bytes object with size headers into individual bytes objects.

    Format: [4-byte size][data][4-byte size][data]...
    Each size is stored as big-endian 32-bit integer.

    Args:
        merged_bytes: Merged bytes object with size headers

    Returns:
        list: List of individual bytes objects
    """
    bytes_list = []
    offset = 0
    total_length = len(merged_bytes)

    while offset < total_length:
        # Check if we have enough bytes for a size header
        if offset + 4 > total_length:
            break

        # Read size header (4 bytes big-endian)
        size_bytes = merged_bytes[offset:offset+4]
        data_size = int.from_bytes(size_bytes, byteorder='big')
        offset += 4

        # Check if we have enough bytes for the data
        if offset + data_size > total_length:
            break

        # Extract the data bytes
        data_bytes = merged_bytes[offset:offset+data_size]
        bytes_list.append(data_bytes)
        offset += data_size

    return bytes_list