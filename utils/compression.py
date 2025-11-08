import base64
import gzip
import zlib
import bz2
import lzma


def compress_bytes(data_bytes: bytes, compression: str) -> bytes:
    """
    Compress bytes using specified compression algorithm.

    Args:
        data_bytes: Bytes to compress
        compression: Compression algorithm ('none', 'gzip', 'zlib', 'bz2', 'lzma')

    Returns:
        Compressed bytes
    """
    if compression == "none":
        return data_bytes

    # Apply compression
    if compression == "gzip":
        compressed = gzip.compress(data_bytes, compresslevel=9)
    elif compression == "zlib":
        compressed = zlib.compress(data_bytes, level=9)
    elif compression == "bz2":
        compressed = bz2.compress(data_bytes, compresslevel=9)
    elif compression == "lzma":
        compressed = lzma.compress(data_bytes, preset=9)
    else:
        raise ValueError(f"Unknown compression algorithm: {compression}")

    return compressed


def decompress_bytes(compressed_bytes: bytes, compression: str) -> bytes:
    """
    Decompress bytes using specified compression algorithm.

    Args:
        compressed_bytes: Compressed bytes
        compression: Compression algorithm used ('none', 'gzip', 'zlib', 'bz2', 'lzma')

    Returns:
        Decompressed bytes
    """
    if compression == "none":
        return compressed_bytes

    # Apply decompression
    if compression == "gzip":
        decompressed = gzip.decompress(compressed_bytes)
    elif compression == "zlib":
        decompressed = zlib.decompress(compressed_bytes)
    elif compression == "bz2":
        decompressed = bz2.decompress(compressed_bytes)
    elif compression == "lzma":
        decompressed = lzma.decompress(compressed_bytes)
    else:
        raise ValueError(f"Unknown compression算法: {compression}")

    return decompressed


def compress_base64(base64_data: str, compression: str) -> str:
    """
    Compress base64 string using specified compression algorithm.

    Args:
        base64_data: Base64 string to compress
        compression: Compression algorithm ('none', 'gzip', 'zlib', 'bz2', 'lzma')

    Returns:
        Compressed base64 string (base64 encoded compressed data)
    """
    if compression == "none":
        return base64_data

    # Convert base64 string to bytes
    data_bytes = base64_data.encode('utf-8')

    # Apply compression
    compressed = compress_bytes(data_bytes, compression)

    # Encode compressed data as base64
    return base64.b64encode(compressed).decode('utf-8')


def decompress_base64(compressed_data: str, compression: str) -> str:
    """
    Decompress base64 string using specified compression algorithm.

    Args:
        compressed_data: Compressed and base64 encoded data
        compression: Compression algorithm used ('none', 'gzip', 'zlib', 'bz2', 'lzma')

    Returns:
        Decompressed base64 string
    """
    if compression == "none":
        return compressed_data

    # Decode base64 to get compressed bytes
    compressed_bytes = base64.b64decode(compressed_data)

    # Apply decompression
    decompressed = decompress_bytes(compressed_bytes, compression)

    # Convert bytes back to string
    return decompressed.decode('utf-8')

