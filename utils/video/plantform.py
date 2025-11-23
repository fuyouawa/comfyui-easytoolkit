import psutil

# Memory safety buffer (128MB)
MEMORY_SAFETY_BUFFER = 2 ** 27  # 128MB

# Default memory fallback (10GB)
DEFAULT_MEMORY_FALLBACK = 10 * 1024 * 1024 * 1024  # 10GB


def get_temp_directory() -> str:
    """
    Get temporary directory for video processing.

    Returns:
        Path to temporary directory
    """
    import folder_paths
    return folder_paths.get_temp_directory()
    # import tempfile
    # return tempfile.gettempdir()


def calculate_available_memory() -> int:
    """
    Calculate available memory (with 128MB safety buffer).

    Returns:
        Available memory in bytes
    """
    try:
        return (psutil.virtual_memory().available + psutil.swap_memory().free) - MEMORY_SAFETY_BUFFER
    except:
        # If memory calculation fails, return a large fallback value
        return DEFAULT_MEMORY_FALLBACK


def calculate_max_frames(width: int, height: int, memory_limit: int = None, vae: bool = None) -> int:
    """
    Calculate maximum number of frames that can be loaded.

    Args:
        width: Video width
        height: Video height
        memory_limit: Memory limit in bytes, None for automatic calculation
        vae: Whether VAE encoding is used

    Returns:
        Maximum number of frames that can be loaded
    """
    if memory_limit is None:
        memory_limit = calculate_available_memory()

    if vae is not None:
        # VAE encoding requires more memory: f32 image + latent space + decode buffer
        memory_per_frame = width * height * 3 * (4 + 4 + 1/10)  # bytes
    else:
        # Image loading only
        memory_per_frame = width * height * 3 * 4  # bytes (float32)

    return int(memory_limit // memory_per_frame)
