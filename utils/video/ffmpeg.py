# import io
# import shutil
# import uuid
# import os
# import subprocess
# from typing import List, Tuple, Optional
# from PIL import Image
# import json

# import folder_paths

# from .common import convert_image_batch_to_pil_list, process_image_format

# ffmpeg_path = shutil.which("ffmpeg")
# if ffmpeg_path is None:
#     print("ffmpeg could not be found. Using ffmpeg from imageio-ffmpeg.")
#     from imageio_ffmpeg import get_ffmpeg_exe
#     try:
#         ffmpeg_path = get_ffmpeg_exe()
#     except:
#         print("ffmpeg could not be found. Outputs that require it have been disabled")

# # The code is based on ComfyUI-VideoHelperSuite modification.
# def image_batch_to_video_bytes(
#     image_batch,
#     frame_rate: int,
#     video_format: str = "image/gif",
#     pingpong: bool = False,
#     loop_count: int = 0,
#     video_metadata: Optional[dict] = None,
#     ffmpeg_bin: Optional[str] = None,
# ) -> Tuple[bytes, str]:
#     """
#     Convert image_batch to video and return bytes.
#     Returns (video_bytes, extension_without_dot)
#     - For image/* (gif, webp) use Pillow to save directly to BytesIO.
#     - For video/* use ffmpeg, output to temporary file first then read bytes.
#     - If using temporary file for output, third return value is temporary file path (caller can decide whether to keep or delete).
#     """
#     # Convert image_batch to PIL Image list and normalize
#     frames = convert_image_batch_to_pil_list(image_batch)

#     if pingpong:
#         if len(frames) >= 2:
#             frames = frames + frames[-2:0:-1]

#     format_type, format_ext = video_format.split("/")
#     # image formats via Pillow
#     if format_type == "image":
#         return process_image_format(frames, format_ext, frame_rate, loop_count)

#     # --- video path (ffmpeg) ---
#     if ffmpeg_bin is None:
#         # fallback: use global ffmpeg_path captured outside
#         ffmpeg_bin = ffmpeg_path
#     if ffmpeg_bin is None:
#         raise ProcessLookupError("ffmpeg not found")

#     # Find corresponding video_format json (keeping consistent with original)
#     video_format_path = folder_paths.get_full_path("video_formats", format_ext + ".json")
#     with open(video_format_path, "r") as f:
#         video_format = json.load(f)

#     # Generate temporary output file
#     tmp_dir = folder_paths.get_temp_directory()
#     os.makedirs(tmp_dir, exist_ok=True)
#     # out_suffix = "." + video_format["extension"]
#     # tmp_out = os.path.join(tmp_dir, f"{uuid.uuid4().hex}{out_suffix}")
#     tmp_out = os.path.join(tmp_dir, f"{uuid.uuid4().hex}")
#     muxer = video_format.get("muxer", video_format["extension"])

#     dimensions = f"{frames[0].width}x{frames[0].height}"
#     metadata_json = json.dumps(video_metadata or {})

#     # base args: read rawvideo from stdin
#     args = [
#         ffmpeg_bin, "-v", "error",
#         "-f", "rawvideo", "-pix_fmt", "rgb24",
#         "-s", dimensions, "-r", str(frame_rate), "-i", "-"
#     ] + video_format.get("main_pass", [])

#     # metadata handling - attempt to pass as -metadata comment=..., if too long fall back to using temporary metadata file
#     metadata_args = ["-metadata", "comment=" + metadata_json]

#     # estimate max arg length (copy from your original)
#     if os.name == 'posix':
#         max_arg_length = 4096 * 32
#     else:
#         # conservative estimate similar to your original
#         max_arg_length = 32767 - len(" ".join(args + [metadata_args[0]] + [tmp_out])) - 1

#     env = os.environ.copy()
#     if "environment" in video_format:
#         env.update(video_format["environment"])

#     if len(metadata_args[1]) >= max_arg_length:
#         # write metadata to temp file and use it as an extra input
#         _run_ffmpeg_with_metadata_file(args, frames, metadata_json, tmp_dir, tmp_out, env, muxer)
#     else:
#         # normal path: pass metadata arg directly
#         try:
#             _run_ffmpeg_with_metadata_arg(args, metadata_args, frames, tmp_out, env, muxer)
#         except (FileNotFoundError, OSError) as e:
#             # replicate original fallback triggers for very long metadata on Windows/Errno
#             # fall back to metadata temp file approach
#             _run_ffmpeg_with_metadata_file(args, frames, metadata_json, tmp_dir, tmp_out, env, muxer)

#     # Read tmp_out as bytes
#     with open(tmp_out, "rb") as f:
#         data = f.read()

#     # Delete temporary file
#     os.remove(tmp_out)

#     return data, video_format["extension"]

# def _run_ffmpeg_with_metadata_file(
#     args: List[str],
#     frames: List[Image.Image],
#     metadata_json: str,
#     tmp_dir: str,
#     tmp_out: str,
#     env: dict,
#     muxer: str
# ):
#     """
#     Helper function to run ffmpeg with temporary metadata file.
#     Handles metadata file creation, escaping, ffmpeg execution, and cleanup.
#     """
#     # Create temporary metadata file
#     md_tmp = os.path.join(tmp_dir, f"{uuid.uuid4().hex}_metadata.txt")
#     with open(md_tmp, "w", encoding="utf-8") as mf:
#         mf.write(";FFMETADATA1\n")
#         # Escape dangerous characters
#         md = metadata_json.replace("\\", "\\\\").replace(";", "\\;").replace("#", "\\#").replace("\n", "\\\n")
#         mf.write(md)

#     # Build new arguments including metadata file
#     new_args = [args[0]] + ["-i", md_tmp] + args[1:]

#     try:
#         with subprocess.Popen(new_args + ["-f", muxer, tmp_out], stdin=subprocess.PIPE, env=env) as proc:
#             for fr in frames:
#                 #TODO Error occurs when format is video/av1-webm
#                 proc.stdin.write(fr.tobytes())
#             proc.stdin.close()
#             proc.wait()
#     finally:
#         # Clean up temporary metadata file
#         if md_tmp and os.path.exists(md_tmp):
#             os.remove(md_tmp)


# def _run_ffmpeg_with_metadata_arg(
#     args: List[str],
#     meta_arg_list: List[str],
#     frames: List[Image.Image],
#     tmp_out: str,
#     env: dict,
#     muxer: str
# ):
#     """
#     Helper function to run ffmpeg with metadata arguments directly.
#     """
#     # run ffmpeg writing frames to stdin and create tmp_out
#     try:
#         with subprocess.Popen(args + meta_arg_list + ["-f", muxer, tmp_out], stdin=subprocess.PIPE, env=env) as proc:
#             for fr in frames:
#                 # ensure rgb24 byte order
#                 proc.stdin.write(fr.tobytes())
#             proc.stdin.close()
#             proc.wait()
#     except Exception:
#         # bubble up, caller can decide
#         raise
