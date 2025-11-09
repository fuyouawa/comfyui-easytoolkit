import uuid
import os
from typing import List, Tuple, Optional
from PIL import Image
import cv2
import numpy as np

from .common import convert_image_batch_to_pil_list, process_image_format


def image_batch_to_video_bytes(
    image_batch,
    frame_rate: int,
    video_format: str = "image/gif",
    pingpong: bool = False,
    loop_count: int = 0,
    video_metadata: Optional[dict] = None
) -> Tuple[bytes, str]:
    """
    Convert image_batch to video and return bytes using OpenCV.
    Returns (video_bytes, extension_without_dot)

    Args:
        image_batch: List of images (PIL, numpy arrays, or ComfyUI tensors)
        frame_rate: Frame rate for the output video
        video_format: Format string like "image/gif", "video/mp4", etc.
        pingpong: Whether to create pingpong effect
        loop_count: Number of loops (for GIF/WEBP)
        video_metadata: Metadata for the video
        **kwargs: Additional arguments (ignored for OpenCV)

    Returns:
        Tuple[bytes, str]: Video bytes and file extension
    """
    # Convert image_batch to PIL Image list and normalize
    frames = convert_image_batch_to_pil_list(image_batch)

    if pingpong:
        if len(frames) >= 2:
            frames = frames + frames[-2:0:-1]

    format_type, format_ext = video_format.split("/")

    # image formats via Pillow (OpenCV doesn't handle GIF/WEBP well)
    if format_type == "image":
        return process_image_format(frames, format_ext, frame_rate, loop_count)

    # video formats via OpenCV
    return _process_video_format(frames, format_ext, frame_rate)


def _process_video_format(frames: List[Image.Image], format_ext: str, frame_rate: int) -> Tuple[bytes, str]:
    """
    Process video formats using OpenCV.
    """
    # Get video writer properties
    fourcc, extension = _get_opencv_format(format_ext)

    # Create temporary file for output
    import folder_paths

    tmp_dir = folder_paths.get_temp_directory()
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_out = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.{extension}")

    # Get frame dimensions
    width, height = frames[0].size

    # Initialize video writer
    fourcc_code = cv2.VideoWriter_fourcc(*fourcc)
    out = cv2.VideoWriter(tmp_out, fourcc_code, frame_rate, (width, height))

    try:
        # Write frames
        for frame in frames:
            # Convert PIL to OpenCV format (BGR)
            cv_frame = np.array(frame)
            cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_RGB2BGR)
            out.write(cv_frame)

        # Release video writer
        out.release()

        # Read output file
        with open(tmp_out, "rb") as f:
            video_bytes = f.read()

        return video_bytes, extension

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_out):
            os.remove(tmp_out)


def _get_opencv_format(format_ext: str) -> Tuple[str, str]:
    """
    Map format extension to OpenCV fourcc code and file extension.
    """
    format_mapping = {
        "mp4": ("mp4v", "mp4"),
        "avi": ("XVID", "avi"),
        "mov": ("mp4v", "mov"),
        "webm": ("VP80", "webm"),
        "mkv": ("X264", "mkv"),
        "wmv": ("WMV2", "wmv"),
    }

    if format_ext in format_mapping:
        return format_mapping[format_ext]

    # Default to MP4
    return ("mp4v", "mp4")


def is_opencv_available() -> bool:
    """
    Check if OpenCV is available and functional.
    """
    try:
        import cv2
        return True
    except ImportError:
        return False
