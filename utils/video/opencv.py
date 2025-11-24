import uuid
import os
from typing import List, Tuple, Optional, Iterator
from PIL import Image
import cv2
import numpy as np

from .common import image_batch_to_pil_list, combine_animated_image, pil_list_to_image_batch, VideoInfo
from .plantform import calculate_max_frames

FORMAT_MAPPING = {
    "mp4": ("mp4v", "mp4"),
    "avi": ("XVID", "avi"),
    "mov": ("mp4v", "mov"),
    "webm": ("VP80", "webm"),
    "mkv": ("X264", "mkv"),
    "wmv": ("WMV2", "wmv"),
}

def combine_video(
    image_batch,
    output_path: str,
    frame_rate: int,
    video_format: str = "image/gif",
    pingpong: bool = False,
    loop_count: int = 0,
    video_metadata: Optional[dict] = None
) -> Tuple[str, str]:
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
    frames = image_batch_to_pil_list(image_batch)

    if pingpong:
        if len(frames) >= 2:
            frames = frames + frames[-2:0:-1]

    format_type, format_ext = video_format.split("/")

    # image formats via Pillow (OpenCV doesn't handle GIF/WEBP well)
    if format_type == "image":
        return combine_animated_image(frames, output_path, format_ext, frame_rate, loop_count)

    # video formats via OpenCV
    return _process_video_format_to_file(frames, output_path, format_ext, frame_rate)


def _process_video_format_to_file(frames: List[Image.Image], output_path: str, format_ext: str, frame_rate: int):
    """
    Process video formats using OpenCV and save to output_path.

    Args:
        frames: List of PIL Image frames
        output_path: Output file path
        format_ext: Video format extension
        frame_rate: Frame rate for the output video

    Returns:
        Output file path
    """
    # Get video writer properties
    fourcc, extension = _get_opencv_format(format_ext)
    if not output_path.endswith(f".{extension}"):
        output_path = f"{output_path}.{extension}"

    # Get frame dimensions
    width, height = frames[0].size

    # Initialize video writer
    fourcc_code = cv2.VideoWriter_fourcc(*fourcc)
    out = cv2.VideoWriter(output_path, fourcc_code, frame_rate, (width, height))
    if not out.isOpened():
        print(cv2.getBuildInformation())
        print(cv2.__version__)
        raise ValueError(f"Failed to open video writer for {output_path}")

    try:
        # Write frames
        for frame in frames:
            # Convert PIL to OpenCV format (BGR)
            cv_frame = np.array(frame)
            cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_RGB2BGR)
            out.write(cv_frame)

        # Release video writer
        out.release()

        return output_path, extension

    except Exception:
        # Clean up output file if writing failed
        if os.path.exists(output_path):
            os.remove(output_path)
        raise


def _get_opencv_format(format_ext: str) -> Tuple[str, str]:
    """
    Map format extension to OpenCV fourcc code and file extension.

    Args:
        format_ext: Video format extension

    Returns:
        Tuple containing fourcc code and file extension
    """

    if format_ext in FORMAT_MAPPING:
        return FORMAT_MAPPING[format_ext]

    # Default to MP4
    return ("mp4v", "mp4")


def _cv_frame_generator(video_path: str, force_rate: int = 0, frame_load_cap: int = 0, skip_first_frames: int = 0,
                       select_every_nth: int = 1) -> Iterator[Image.Image]:
    """
    OpenCV video frame generator.

    Args:
        video_path: Video file path
        force_rate: Force frame rate (0 means use original frame rate)
        frame_load_cap: Maximum number of frames to load (0 means unlimited)
        skip_first_frames: Number of initial frames to skip
        select_every_nth: Select every nth frame

    Yields:
        Frame data as PIL Image objects
    """
    video_cap = cv2.VideoCapture(video_path)
    if not video_cap.isOpened() or not video_cap.grab():
        raise ValueError(f"Cannot load video with OpenCV: {video_path}")

    # Extract video metadata
    fps = video_cap.get(cv2.CAP_PROP_FPS)
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if width <= 0 or height <= 0:
        _, frame = video_cap.retrieve()
        height, width, _ = frame.shape

    # Frame rate control
    if force_rate == 0:
        target_frame_time = 1 / fps
    else:
        target_frame_time = 1 / force_rate

    base_frame_time = 1 / fps

    # Calculate number of frames that can be yielded
    if total_frames > 0:
        if force_rate != 0:
            yieldable_frames = int(total_frames / fps * force_rate)
        else:
            yieldable_frames = total_frames
        if select_every_nth > 1:
            yieldable_frames //= select_every_nth
        if frame_load_cap > 0:
            yieldable_frames = min(frame_load_cap, yieldable_frames)
    else:
        yieldable_frames = 0

    time_offset = target_frame_time
    frames_added = 0
    total_frame_count = 0
    total_frames_evaluated = -1

    while video_cap.isOpened():
        if time_offset < target_frame_time:
            is_returned = video_cap.grab()
            if not is_returned:
                break
            time_offset += base_frame_time
        if time_offset < target_frame_time:
            continue
        time_offset -= target_frame_time

        total_frame_count += 1
        if total_frame_count <= skip_first_frames:
            continue
        else:
            total_frames_evaluated += 1

        if total_frames_evaluated % select_every_nth != 0:
            continue

        # Get and process frame
        _, frame = video_cap.retrieve()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        pil_image = Image.fromarray(frame)
        yield pil_image
        frames_added += 1

        if frame_load_cap > 0 and frames_added >= frame_load_cap:
            break

    video_cap.release()


def _get_video_info(video_path: str) -> Tuple[int, int, float, int]:
    """
    Get video information using OpenCV.

    Args:
        video_path: Path to the video file

    Returns:
        Tuple containing:
        - source_width: Original video width
        - source_height: Original video height
        - source_fps: Original frame rate
        - source_frame_count: Original frame count
    """
    video_cap = cv2.VideoCapture(video_path)
    if not video_cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    # Extract video metadata
    source_fps = video_cap.get(cv2.CAP_PROP_FPS)
    source_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    source_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    source_frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))

    video_cap.release()

    return source_width, source_height, source_fps, source_frame_count


import itertools


def load_video(video_path, force_rate: int = 0, frame_load_cap: int = 0, start_time: int = 0,
                       select_every_nth: int = 1, memory_limit_mb=None):
    """
    Load video frames using OpenCV and convert them to tensor format.

    Args:
        video_path: Path to the video file
        force_rate: Force frame rate (0 for original rate)
        frame_load_cap: Maximum number of frames to load (0 for no limit)
        start_time: Start time in seconds (0 for beginning)
        select_every_nth: Select every nth frame
        memory_limit_mb: Memory limit in megabytes for frame loading

    Returns:
        Tuple containing:
        - frames_tensor: Video frames as tensor (float32, [0,1] range)
        - frame_count: Number of loaded frames
        - video_info: VideoInfo object with metadata
    """
    # Get video information first
    source_width, source_height, source_fps, source_frame_count = _get_video_info(video_path)

    # Calculate skip_first_frames from start_time (seconds to frames)
    skip_first_frames = int(start_time * source_fps)
    # Ensure skip_first_frames doesn't exceed total frame count
    if skip_first_frames >= source_frame_count:
        skip_first_frames = max(0, source_frame_count - 1)

    # Get frame generator
    frame_gen = _cv_frame_generator(
        video_path=video_path,
        force_rate=force_rate,
        frame_load_cap=frame_load_cap,
        skip_first_frames=skip_first_frames,
        select_every_nth=select_every_nth
    )

    # For OpenCV, we need to get the first frame to determine dimensions
    try:
        first_frame = next(frame_gen)
        width, height = first_frame.size
        channels = len(first_frame.getbands())
        # Recreate generator including the first frame
        frame_gen = itertools.chain([first_frame], frame_gen)
    except StopIteration:
        # No frames available
        height = source_height
        width = source_width
        channels = 3  # OpenCV typically loads RGB frames

    # Calculate memory limit
    memory_limit = None
    if memory_limit_mb is not None:
        memory_limit = memory_limit_mb * 1024 * 1024

    max_frames = calculate_max_frames(width, height, memory_limit)

    # Ensure at least one frame is loaded even with strict memory limits
    if max_frames == 0 and memory_limit_mb is not None:
        max_frames = 1

    # Convert frames to tensor using PIL list to image batch with memory limit
    pil_frames = []
    for i, frame in enumerate(frame_gen):
        if max_frames is not None and i >= max_frames:
            break
        pil_frames.append(frame)

    image_batch = pil_list_to_image_batch(pil_frames)
    frame_count = image_batch.shape[0]

    # Calculate loaded frame rate
    loaded_fps = force_rate if force_rate > 0 else source_fps

    # Build video information object
    video_info = VideoInfo(
        source_fps=source_fps,
        source_width=source_width,
        source_height=source_height,
        loaded_width=width,
        loaded_height=height,
        loaded_channels=channels,
        loaded_frame_count=frame_count,
        loaded_fps=loaded_fps,
        source_frame_count=source_frame_count,
        generator="opencv",
    )

    return image_batch, video_info