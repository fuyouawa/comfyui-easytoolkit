"""
Video format configurations for ffmpeg.
These configurations replace the previous JSON files.
"""

# AV1 WebM format
AV1_WEBM = {
    "main_pass": [
        "-n", "-c:v", "libsvtav1",
        "-pix_fmt", "yuv420p10le",
        "-crf", "23"
    ],
    "extension": "webm",
    "environment": {"SVT_LOG": "1"}
}

# H.264 MP4 format
H264_MP4 = {
    "main_pass": [
        "-n", "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "19"
    ],
    "extension": "mp4"
}

# H.265 MP4 format
H265_MP4 = {
    "main_pass": [
        "-n", "-c:v", "libx265",
        "-pix_fmt", "yuv420p10le",
        "-preset", "medium",
        "-crf", "22",
        "-x265-params", "log-level=quiet"
    ],
    "extension": "mp4"
}

# WebM format (VP8/VP9)
WEBM = {
    "main_pass": [
        "-n",
        "-pix_fmt", "yuv420p",
        "-crf", "23"
    ],
    "extension": "webm"
}

# Format mapping dictionary for easy lookup
FORMAT_MAPPING = {
    "av1-webm": AV1_WEBM,
    "h264-mp4": H264_MP4,
    "h265-mp4": H265_MP4,
    "webm": WEBM
}

def get_video_format(format_name: str):
    """
    Get video format configuration by name.

    Args:
        format_name: Format name (e.g., "av1-webm", "h264-mp4")

    Returns:
        Dictionary with video format configuration

    Raises:
        KeyError: If format name is not found
    """
    if format_name not in FORMAT_MAPPING:
        raise KeyError(f"Video format '{format_name}' not found. Available formats: {list(FORMAT_MAPPING.keys())}")

    return FORMAT_MAPPING[format_name]

def list_available_formats():
    """
    List all available video formats.

    Returns:
        List of format names
    """
    return list(FORMAT_MAPPING.keys())