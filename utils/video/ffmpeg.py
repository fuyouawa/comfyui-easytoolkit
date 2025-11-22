import io
import shutil
import uuid
import os
import subprocess
from typing import List, Tuple, Optional
from PIL import Image

from .common import convert_image_batch_to_pil_list, process_image_format_to_file
from .formats import get_video_format
from .plantform import get_temp_directory

ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path is None:
    print("ffmpeg could not be found. Using ffmpeg from imageio-ffmpeg.")
    from imageio_ffmpeg import get_ffmpeg_exe
    try:
        ffmpeg_path = get_ffmpeg_exe()
    except:
        print("ffmpeg could not be found. Outputs that require it have been disabled")

# The code is based on ComfyUI-VideoHelperSuite modification.
def image_batch_to_video_file(
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
    frames = convert_image_batch_to_pil_list(image_batch)

    if pingpong:
        if len(frames) >= 2:
            frames = frames + frames[-2:0:-1]

    format_type, format_ext = video_format.split("/")
    # image formats via Pillow
    if format_type == "image":
        return process_image_format_to_file(frames, output_path, format_ext, frame_rate, loop_count)

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