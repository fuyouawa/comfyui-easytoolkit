import io
import shutil
import uuid
import os
import subprocess
import re
import time
import itertools
from typing import List, Tuple, Optional, Iterator
from PIL import Image
import numpy as np

from .common import image_batch_to_pil_list, combine_animated_image, target_size, pil_list_to_image_batch, VideoInfo
from .plantform import get_temp_directory, calculate_max_frames

ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path is None:
    print("ffmpeg could not be found. Using ffmpeg from imageio-ffmpeg.")
    from imageio_ffmpeg import get_ffmpeg_exe
    try:
        ffmpeg_path = get_ffmpeg_exe()
    except:
        print("ffmpeg could not be found. Outputs that require it have been disabled")

# Encoding parameters for subprocess communication
ENCODE_ARGS = ('utf-8', 'ignore')

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


# The code is based on ComfyUI-VideoHelperSuite modification.
def combine_video(
    image_batch,
    output_path: str,
    frame_rate: int,
    video_format: str = "image/gif",
    pingpong: bool = False,
    loop_count: int = 0,
    video_metadata: Optional[dict] = None,
    ffmpeg_bin: Optional[str] = None,
) -> str:
    """
    Convert image_batch to video and save to output_path.
    Returns output_path
    - For image/* (gif, webp) use Pillow to save directly to output_path.
    - For video/* use ffmpeg, output directly to output_path.
    """
    # Convert image_batch to PIL Image list and normalize
    frames = image_batch_to_pil_list(image_batch)

    if pingpong:
        if len(frames) >= 2:
            frames = frames + frames[-2:0:-1]

    format_type, format_ext = video_format.split("/")
    # image formats via Pillow
    if format_type == "image":
        return combine_animated_image(frames, output_path, format_ext, frame_rate, loop_count)

    # --- video path (ffmpeg) ---
    if ffmpeg_bin is None:
        # fallback: use global ffmpeg_path captured outside
        ffmpeg_bin = ffmpeg_path
    if ffmpeg_bin is None:
        raise ProcessLookupError("ffmpeg not found")

    # Get video format configuration from Python module
    video_format = get_video_format(format_ext)
    muxer = video_format.get("muxer", video_format["extension"])

    dimensions = f"{frames[0].width}x{frames[0].height}"
    metadata_json = str(video_metadata or {})

    # base args: read rawvideo from stdin
    args = [
        ffmpeg_bin, "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", dimensions, "-r", str(frame_rate), "-i", "-"
    ] + video_format.get("main_pass", [])

    # metadata handling - attempt to pass as -metadata comment=..., if too long fall back to using temporary metadata file
    metadata_args = ["-metadata", "comment=" + metadata_json]

    # estimate max arg length (copy from your original)
    if os.name == 'posix':
        max_arg_length = 4096 * 32
    else:
        # conservative estimate similar to your original
        max_arg_length = 32767 - len(" ".join(args + [metadata_args[0]] + [output_path])) - 1

    env = os.environ.copy()
    if "environment" in video_format:
        env.update(video_format["environment"])

    if len(metadata_args[1]) >= max_arg_length:
        # write metadata to temp file and use it as an extra input
        _run_ffmpeg_with_metadata_file(args, frames, metadata_json, output_path, env, muxer)
    else:
        # normal path: pass metadata arg directly
        try:
            _run_ffmpeg_with_metadata_arg(args, metadata_args, frames, output_path, env, muxer)
        except (FileNotFoundError, OSError) as e:
            # replicate original fallback triggers for very long metadata on Windows/Errno
            # fall back to metadata temp file approach
            _run_ffmpeg_with_metadata_file(args, frames, metadata_json, output_path, env, muxer)

    return output_path

def _run_ffmpeg_with_metadata_file(
    args: List[str],
    frames: List[Image.Image],
    metadata_json: str,
    output_path: str,
    env: dict,
    muxer: str
):
    """
    Helper function to run ffmpeg with temporary metadata file.
    Handles metadata file creation, escaping, ffmpeg execution, and cleanup.
    """
    # Create temporary metadata file
    tmp_dir = get_temp_directory()
    md_tmp = os.path.join(tmp_dir, f"{uuid.uuid4().hex}_metadata.txt")
    with open(md_tmp, "w", encoding="utf-8") as mf:
        mf.write(";FFMETADATA1\n")
        # Escape dangerous characters
        md = metadata_json.replace("\\", "\\\\").replace(";", "\\;").replace("#", "\\#").replace("\n", "\\\n")
        mf.write(md)

    # Build new arguments including metadata file
    new_args = [args[0]] + ["-i", md_tmp] + args[1:]

    try:
        with subprocess.Popen(new_args + ["-f", muxer, output_path], stdin=subprocess.PIPE, env=env) as proc:
            for fr in frames:
                #TODO Error occurs when format is video/av1-webm
                proc.stdin.write(fr.tobytes())
            proc.stdin.close()
            proc.wait()
    finally:
        # Clean up temporary metadata file
        if md_tmp and os.path.exists(md_tmp):
            os.remove(md_tmp)


def _run_ffmpeg_with_metadata_arg(
    args: List[str],
    meta_arg_list: List[str],
    frames: List[Image.Image],
    output_path: str,
    env: dict,
    muxer: str
):
    """
    Helper function to run ffmpeg with metadata arguments directly.
    """
    # run ffmpeg writing frames to stdin and create output file
    try:
        with subprocess.Popen(args + meta_arg_list + ["-f", muxer, output_path], stdin=subprocess.PIPE, env=env) as proc:
            for fr in frames:
                # ensure rgb24 byte order
                proc.stdin.write(fr.tobytes())
            proc.stdin.close()
            proc.wait()
    except Exception:
        # bubble up, caller can decide
        raise

def _ffmpeg_frame_generator(video_path: str, force_rate: int = 0, frame_load_cap: int = 0, start_time: int = 0,
                           custom_width: int = 0, custom_height: int = 0, downscale_ratio: int = 8, ffmpeg_bin: Optional[str] = None, select_every_nth: int = 1) -> Iterator[Image.Image]:
    """
    FFmpeg video frame generator (supports complex processing).

    Args:
        video_path: Video file path
        force_rate: Force frame rate
        frame_load_cap: Maximum number of frames to load
        start_time: Start time in seconds
        custom_width: Custom width
        custom_height: Custom height
        downscale_ratio: Downscale ratio
        ffmpeg_bin: Custom ffmpeg executable path
        select_every_nth: Select every nth frame

    Yields:
        Frame data as PIL Image objects
    """

    # --- video path (ffmpeg) ---
    if ffmpeg_bin is None:
        # fallback: use global ffmpeg_path captured outside
        ffmpeg_bin = ffmpeg_path
    if ffmpeg_bin is None:
        raise ProcessLookupError("ffmpeg not found")

    # Get video information
    args_input = ["-i", video_path]
    args_dummy = [ffmpeg_bin] + args_input + ['-c', 'copy', '-frames:v', '1', "-f", "null", "-"]

    try:
        dummy_res = subprocess.run(args_dummy, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("FFmpeg subprocess error:\n" + e.stderr.decode(*ENCODE_ARGS))

    lines = dummy_res.stderr.decode(*ENCODE_ARGS)

    # Parse video information
    size_base = None
    fps_base = None
    alpha = False

    for line in lines.split('\n'):
        match = re.search("^ *Stream .* Video.*, ([1-9]|\\d{2,})x(\\d+)", line)
        if match is not None:
            size_base = [int(match.group(1)), int(match.group(2))]
            fps_match = re.search(", ([\\d\\.]+) fps", line)
            if fps_match:
                fps_base = float(fps_match.group(1))
            else:
                fps_base = 1
            alpha = re.search("(yuva|rgba|bgra)", line) is not None
            break
    else:
        raise Exception("Cannot parse video information. FFmpeg output:\n" + lines)

    # Build FFmpeg command
    if start_time > 0:
        if start_time > 4:
            post_seek = ['-ss', '4']
            args_input = ['-ss', str(start_time - 4)] + args_input
        else:
            post_seek = ['-ss', str(start_time)]
    else:
        post_seek = []

    args_all_frames = [ffmpeg_bin, "-v", "error", "-an"] + args_input + ["-pix_fmt", "rgba64le"] + post_seek

    # Video filters
    vfilters = []
    if force_rate != 0:
        vfilters.append("fps=fps="+str(force_rate))
    if custom_width != 0 or custom_height != 0:
        size = target_size(size_base[0], size_base[1], custom_width, custom_height, downscale_ratio)
        ar = float(size[0])/float(size[1])
        if abs(size_base[0]*ar-size_base[1]) >= 1:
            vfilters.append(f"crop=if(gt({ar}\\,a)\\,iw\\,ih*{ar}):if(gt({ar}\\,a)\\,iw/{ar}\\,ih)")
        size_arg = ':'.join(map(str,size))
        vfilters.append(f"scale={size_arg}")
    else:
        size = size_base

    if len(vfilters) > 0:
        args_all_frames += ["-vf", ",".join(vfilters)]

    if frame_load_cap > 0:
        args_all_frames += ["-frames:v", str(frame_load_cap)]

    args_all_frames += ["-f", "rawvideo", "-"]

    # Process frame data
    bpi = size[0] * size[1] * 8  # bytes per image

    try:
        with subprocess.Popen(args_all_frames, stdout=subprocess.PIPE) as proc:
            current_bytes = bytearray(bpi)
            current_offset = 0
            frame_count = 0

            while True:
                bytes_read = proc.stdout.read(bpi - current_offset)
                if bytes_read is None:
                    time.sleep(.1)
                    continue
                if len(bytes_read) == 0:
                    break

                current_bytes[current_offset:len(bytes_read)] = bytes_read
                current_offset += len(bytes_read)

                if current_offset == bpi:
                    frame_count += 1

                    # Skip frames based on select_every_nth parameter
                    if (frame_count - 1) % select_every_nth == 0:
                        frame = np.frombuffer(current_bytes, dtype=np.dtype(np.uint16).newbyteorder("<")).reshape(size[1], size[0], 4) / (2**16-1)
                        if not alpha:
                            frame = frame[:, :, :-1]
                        # Convert to PIL Image
                        frame_uint8 = (frame * 255).astype(np.uint8)
                        pil_image = Image.fromarray(frame_uint8)
                        yield pil_image

                    current_offset = 0

    except BrokenPipeError as e:
        raise Exception("FFmpeg subprocess error:\n" + proc.stderr.read().decode(*ENCODE_ARGS))


def _get_video_info(video_path: str, ffmpeg_bin: Optional[str] = None) -> Tuple[int, int, float, int, bool]:
    """
    Get video information using FFmpeg.

    Args:
        video_path: Path to the video file
        ffmpeg_bin: Custom FFmpeg executable path

    Returns:
        Tuple containing:
        - source_width: Original video width
        - source_height: Original video height
        - source_fps: Original frame rate
        - source_frame_count: Original frame count
        - has_alpha: Whether video has alpha channel
    """
    if ffmpeg_bin is None:
        ffmpeg_bin = ffmpeg_path
    if ffmpeg_bin is None:
        raise ProcessLookupError("ffmpeg not found")

    # Get video information
    args_input = ["-i", video_path]
    args_dummy = [ffmpeg_bin] + args_input + ['-c', 'copy', '-frames:v', '1', "-f", "null", "-"]

    try:
        dummy_res = subprocess.run(args_dummy, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("FFmpeg subprocess error:\n" + e.stderr.decode(*ENCODE_ARGS))

    lines = dummy_res.stderr.decode(*ENCODE_ARGS)

    # Parse video information
    source_width = 0
    source_height = 0
    source_fps = 0
    source_frame_count = 0
    has_alpha = False

    for line in lines.split('\n'):
        match = re.search("^ *Stream .* Video.*, ([1-9]|\\d{2,})x(\\d+)", line)
        if match is not None:
            source_width = int(match.group(1))
            source_height = int(match.group(2))
            fps_match = re.search(", ([\\d\\.]+) fps", line)
            if fps_match:
                source_fps = float(fps_match.group(1))
            else:
                source_fps = 1
            has_alpha = re.search("(yuva|rgba|bgra)", line) is not None
            break

    # Try to extract frame count from duration information
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", lines)
    if duration_match and source_fps > 0:
        hours = int(duration_match.group(1))
        minutes = int(duration_match.group(2))
        seconds = float(duration_match.group(3))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        source_frame_count = int(total_seconds * source_fps)

    if source_width == 0 or source_height == 0:
        raise Exception("Cannot parse video information. FFmpeg output:\n" + lines)

    return source_width, source_height, source_fps, source_frame_count, has_alpha


def load_video(video_path, force_rate: int = 0, frame_load_cap: int = 0, start_time: int = 0,
                           custom_width: int = 0, custom_height: int = 0, downscale_ratio: int = 8, select_every_nth: int = 1, ffmpeg_bin: Optional[str] = None, use_alpha = False, memory_limit_mb=None):
    """
    Load video frames using FFmpeg and convert them to tensor format.

    Args:
        video_path: Path to the video file
        force_rate: Force frame rate (0 for original rate)
        frame_load_cap: Maximum number of frames to load (0 for no limit)
        start_time: Start time in seconds from beginning of video
        custom_width: Custom output width (0 for original width)
        custom_height: Custom output height (0 for original height)
        downscale_ratio: Downscale ratio for automatic sizing
        ffmpeg_bin: Custom FFmpeg executable path (None for auto-detection)
        use_alpha: Whether to include alpha channel (RGBA vs RGB)
        memory_limit_mb: Memory limit in megabytes for frame loading
        select_every_nth: Select every nth frame

    Returns:
        Tuple containing:
        - frames_tensor: Video frames as tensor (float32, [0,1] range)
        - frame_count: Number of loaded frames
        - video_info: VideoInfo object with metadata
    """
    # Get video information first
    source_width, source_height, source_fps, source_frame_count, has_alpha = _get_video_info(video_path, ffmpeg_bin)

    # Get actual frame dimensions from the generator
    frame_gen = _ffmpeg_frame_generator(
        video_path=video_path,
        force_rate=force_rate,
        frame_load_cap=frame_load_cap,
        start_time=start_time,
        custom_width=custom_width,
        custom_height=custom_height,
        downscale_ratio=downscale_ratio,
        ffmpeg_bin=ffmpeg_bin,
        select_every_nth=select_every_nth
    )

    # Get first frame to determine actual dimensions
    try:
        first_frame = next(frame_gen)
        width, height = first_frame.size
        channels = len(first_frame.getbands())

        # Recreate generator including the first frame
        frame_gen = itertools.chain([first_frame], frame_gen)
    except StopIteration:
        # No frames available
        width = custom_width if custom_width != 0 else 512
        height = custom_height if custom_height != 0 else 512
        channels = 4 if use_alpha else 3

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
        generator="ffmpeg",
    )

    return image_batch, video_info