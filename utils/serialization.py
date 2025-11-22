"""
Serialization utilities for byte stream operations.
"""

import struct
from enum import StrEnum
from .format import all_resource_formats


class SerializationFormat(StrEnum):
    """Enumeration for serialization data formats."""
    NONE = "none"  # No special format
    BYTES_WITH_HEADERS = "bytes_with_headers"  # Data is bytes stream array format with size headers


class CompressionMode(StrEnum):
    """Enumeration for compression modes."""
    NO_COMPRESSION = "no_compression"  # No compression
    ZLIB_COMPRESSION = "zlib_compression"  # Zlib compression

serialization_formats = [SerializationFormat.NONE, SerializationFormat.BYTES_WITH_HEADERS]
compression_modes = [CompressionMode.NO_COMPRESSION, CompressionMode.ZLIB_COMPRESSION]


class ResourceHeader:
    """
    Resource header structure for serialized resources.

    Fixed 4-byte structure:
    - Byte 0: Resource format number (0-255)
    - Byte 1: Compression mode (0=no compression, 1=zlib compression)
    - Byte 2: Serialization format (0=none, 1=bytes_with_headers)
    - Byte 3: Reserved for future use

    Serialization formats:
    - NONE: Standard single data stream
    - BYTES_WITH_HEADERS: Data is a concatenated array of byte streams, each preceded by a 4-byte big-endian size header
    """

    def __init__(self, format_number: int = 0, compression_mode: CompressionMode = CompressionMode.NO_COMPRESSION, serialization_format: SerializationFormat = SerializationFormat.NONE):
        """
        Initialize ResourceHeader with format number, compression mode, and serialization format.

        Args:
            format_number: Resource format number (0-{max_format}), where 0=application/octet-stream
            compression_mode: Compression mode enum
            serialization_format: Serialization format enum
        """
        max_format = len(all_resource_formats)
        if not (0 <= format_number <= max_format):
            raise ValueError(f"Format number must be between 0-{max_format}, got {format_number}")

        self.format_number = format_number
        self.compression_mode = compression_mode
        self.serialization_format = serialization_format
        self.mime_type = all_resource_formats[format_number - 1] if format_number > 0 else "application/octet-stream"

    def to_bytes(self) -> bytes:
        """
        Convert ResourceHeader to 4-byte bytes representation.

        Returns:
            bytes: 4-byte header representation

        Raises:
            ValueError: If format_number, compression_mode, or serialization_format are out of valid range
        """
        max_format = len(all_resource_formats)
        if not (0 <= self.format_number <= max_format):
            raise ValueError(f"Format number must be between 0-{max_format}, got {self.format_number}")

        # Convert compression mode enum to index
        try:
            compression_index = compression_modes.index(self.compression_mode)
        except ValueError:
            raise ValueError(f"Invalid compression mode: {self.compression_mode}")

        # Convert serialization format enum to index
        try:
            serialization_index = serialization_formats.index(self.serialization_format)
        except ValueError:
            raise ValueError(f"Invalid serialization format: {self.serialization_format}")

        # Pack into 4 bytes: format_number, compression_mode, serialization_format, reserved
        return struct.pack('BBBB',
                          self.format_number,
                          compression_index,
                          serialization_index,
                          0)  # reserved byte

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ResourceHeader':
        """
        Create ResourceHeader from 4-byte bytes representation.

        Args:
            data: 4-byte header data

        Returns:
            ResourceHeader: Parsed header object

        Raises:
            ValueError: If data length is not exactly 4 bytes
        """
        if len(data) != 4:
            raise ValueError(f"ResourceHeader data must be exactly 4 bytes, got {len(data)} bytes")

        # Unpack 4 bytes: format_number, compression_mode_index, serialization_format_index, reserved
        format_number, compression_mode_index, serialization_format_index, _ = struct.unpack('BBBB', data)

        # Convert indices back to enum types
        try:
            compression_mode = compression_modes[compression_mode_index]
        except IndexError:
            raise ValueError(f"Invalid compression mode index: {compression_mode_index}")

        try:
            serialization_format = serialization_formats[serialization_format_index]
        except IndexError:
            raise ValueError(f"Invalid serialization format index: {serialization_format_index}")

        return cls(format_number, compression_mode, serialization_format)

    @classmethod
    def from_mime_type(cls, mime_type: str, compression_mode: CompressionMode = CompressionMode.NO_COMPRESSION, serialization_format: SerializationFormat = SerializationFormat.NONE) -> 'ResourceHeader':
        """
        Create ResourceHeader from MIME type.

        Args:
            mime_type: MIME type string
            compression_mode: Compression mode enum
            serialization_format: Serialization format enum

        Returns:
            ResourceHeader: Header object with corresponding format number

        Raises:
            ValueError: If MIME type is not supported
        """
        try:
            format_number = all_resource_formats.index(mime_type) + 1
        except ValueError:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

        return cls(format_number, compression_mode, serialization_format)

    def __repr__(self) -> str:
        """Return string representation of ResourceHeader."""
        return f"ResourceHeader(format_number={self.format_number}, mime_type='{self.mime_type}', compression_mode={self.compression_mode}, serialization_format={self.serialization_format})"

    def __eq__(self, other) -> bool:
        """Check equality with another ResourceHeader."""
        if not isinstance(other, ResourceHeader):
            return False
        return (self.format_number == other.format_number and
                self.compression_mode == other.compression_mode and
                self.serialization_format == other.serialization_format and
                self.mime_type == other.mime_type)


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