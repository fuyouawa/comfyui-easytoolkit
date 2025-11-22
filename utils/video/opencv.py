import uuid
import os
from typing import List, Tuple, Optional
from PIL import Image
import cv2
import numpy as np

from .common import convert_image_batch_to_pil_list, process_image_format_to_file


def image_batch_to_video_file(
    image_batch,
    output_path: str,
    frame_rate: int,
    video_format: str = "image/gif",
    pingpong: bool = False,
    loop_count: int = 0,
    video_metadata: Optional[dict] = None
) -> str:
    """
    Convert image_batch to video and save to output_path using OpenCV.
    Returns output_path

    Args:
        image_batch: List of images (PIL, numpy arrays, or ComfyUI tensors)
        output_path: Path where the video file will be saved
        frame_rate: Frame rate for the output video
        video_format: Format string like "image/gif", "video/mp4", etc.
        pingpong: Whether to create pingpong effect
        loop_count: Number of loops (for GIF/WEBP)
        video_metadata: Metadata for the video
        **kwargs: Additional arguments (ignored for OpenCV)

    Returns:
        str: Output file path
    """
    # Convert image_batch to PIL Image list and normalize
    frames = convert_image_batch_to_pil_list(image_batch)

    if pingpong:
        if len(frames) >= 2:
            frames = frames + frames[-2:0:-1]

    format_type, format_ext = video_format.split("/")

    # image formats via Pillow (OpenCV doesn't handle GIF/WEBP well)
    if format_type == "image":
        return process_image_format_to_file(frames, output_path, format_ext, frame_rate, loop_count)

    # video formats via OpenCV
    return _process_video_format_to_file(frames, output_path, format_ext, frame_rate)


def _process_video_format_to_file(frames: List[Image.Image], output_path: str, format_ext: str, frame_rate: int) -> str:
    """
    Process video formats using OpenCV and save to output_path.
    """
    # Get video writer properties
    fourcc, extension = _get_opencv_format(format_ext)

    # Get frame dimensions
    width, height = frames[0].size

    # Initialize video writer
    fourcc_code = cv2.VideoWriter_fourcc(*fourcc)
    out = cv2.VideoWriter(output_path, fourcc_code, frame_rate, (width, height))

    try:
        # Write frames
        for frame in frames:
            # Convert PIL to OpenCV format (BGR)
            cv_frame = np.array(frame)
            cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_RGB2BGR)
            out.write(cv_frame)

        # Release video writer
        out.release()

        return output_path

    except Exception:
        # Clean up output file if writing failed
        if os.path.exists(output_path):
            os.remove(output_path)
        raise


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
