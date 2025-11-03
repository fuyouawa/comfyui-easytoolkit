import io
import shutil
import uuid
import os
import subprocess
from typing import List, Tuple, Optional
from PIL import Image
import json

import folder_paths

ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path is None:
    print("ffmpeg could not be found. Using ffmpeg from imageio-ffmpeg.")
    from imageio_ffmpeg import get_ffmpeg_exe
    try:
        ffmpeg_path = get_ffmpeg_exe()
    except:
        print("ffmpeg could not be found. Outputs that require it have been disabled")

def convert_image_batch_to_pil_list(image_batch) -> List[Image.Image]:
    """
    将 image_batch 转为 PIL Image 列表并规范化。

    支持多种输入格式：
    - ComfyUI tensor objects (通过 im.cpu().numpy() 转换)
    - PIL Image 对象
    - numpy arrays (自动转换为 uint8 并裁剪到 [0, 255])

    返回:
        List[Image.Image]: 规范化后的 PIL Image 列表，所有图像已转换为 RGB 格式并确保偶数尺寸
    """
    frames: List[Image.Image] = []
    for im in image_batch:
        try:
            # 处理 ComfyUI tensor objects
            arr = (255.0 * im.cpu().numpy()).astype("uint8")
            img = Image.fromarray(arr)
        except Exception:
            # 如果 image_batch 已经是 PIL Image 或 numpy array，则尝试直接处理
            if isinstance(im, Image.Image):
                img = im
            else:
                import numpy as _np
                arr = _np.array(im)
                if arr.dtype != _np.uint8:
                    arr = _np.clip(arr, 0, 255).astype(_np.uint8)
                img = Image.fromarray(arr)
        img = img.convert("RGB")
        img = _ensure_even_dimensions(img)
        frames.append(img)
    return frames

# The code is based on ComfyUI-VideoHelperSuite modification.
def image_batch_to_video_bytes(
    image_batch,
    frame_rate: int,
    format: str = "image/gif",
    pingpong: bool = False,
    loop_count: int = 0,
    video_metadata: Optional[dict] = None,
    ffmpeg_bin: Optional[str] = None,
) -> Tuple[bytes, str]:
    """
    将 image_batch 转为视频并返回 bytes。
    返回 (video_bytes, extension_without_dot)
    - 对 image/* (gif, webp) 使用 Pillow 直接保存到 BytesIO。
    - 对 video/* 使用 ffmpeg，先输出到临时文件再读取字节。
    - 如果使用临时文件保存输出，第三个返回值是临时文件路径（调用者可决定是否保留或删除）。
    """
    # 将 image_batch 转为 PIL Image 列表并规范化
    frames = convert_image_batch_to_pil_list(image_batch)

    if pingpong:
        if len(frames) >= 2:
            frames = frames + frames[-2:0:-1]

    format_type, format_ext = format.split("/")
    # image formats via Pillow
    if format_type == "image":
        return _process_image_format(frames, format_ext, frame_rate, loop_count)

    # --- video path (ffmpeg) ---
    if ffmpeg_bin is None:
        # fallback: use global ffmpeg_path captured outside
        ffmpeg_bin = ffmpeg_path
    if ffmpeg_bin is None:
        raise ProcessLookupError("ffmpeg not found")

    # 找到对应 video_format json（保持与你原来一致）
    video_format_path = folder_paths.get_full_path("video_formats", format_ext + ".json")
    with open(video_format_path, "r") as f:
        video_format = json.load(f)

    # 生成临时输出文件
    tmp_dir = folder_paths.get_temp_directory()
    os.makedirs(tmp_dir, exist_ok=True)
    # out_suffix = "." + video_format["extension"]
    # tmp_out = os.path.join(tmp_dir, f"{uuid.uuid4().hex}{out_suffix}")
    tmp_out = os.path.join(tmp_dir, f"{uuid.uuid4().hex}")
    muxer = video_format.get("muxer", video_format["extension"])

    dimensions = f"{frames[0].width}x{frames[0].height}"
    metadata_json = json.dumps(video_metadata or {})

    # base args: read rawvideo from stdin
    args = [
        ffmpeg_bin, "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", dimensions, "-r", str(frame_rate), "-i", "-"
    ] + video_format.get("main_pass", [])

    # metadata handling - attempt to pass as -metadata comment=..., 若长度过长则回退到使用临时 metadata 文件
    metadata_args = ["-metadata", "comment=" + metadata_json]

    # estimate max arg length (copy from your original)
    if os.name == 'posix':
        max_arg_length = 4096 * 32
    else:
        # conservative estimate similar to your original
        max_arg_length = 32767 - len(" ".join(args + [metadata_args[0]] + [tmp_out])) - 1

    env = os.environ.copy()
    if "environment" in video_format:
        env.update(video_format["environment"])

    if len(metadata_args[1]) >= max_arg_length:
        # write metadata to temp file and use it as an extra input
        _run_ffmpeg_with_metadata_file(args, frames, metadata_json, tmp_dir, tmp_out, env, muxer)
    else:
        # normal path: pass metadata arg directly
        try:
            _run_ffmpeg_with_metadata_arg(args, metadata_args, frames, tmp_out, env, muxer)
        except (FileNotFoundError, OSError) as e:
            # replicate original fallback triggers for very long metadata on Windows/Errno
            # 回退到 metadata temp file approach
            _run_ffmpeg_with_metadata_file(args, frames, metadata_json, tmp_dir, tmp_out, env, muxer)

    # 读取 tmp_out 为 bytes
    with open(tmp_out, "rb") as f:
        data = f.read()

    # 删除临时文件
    os.remove(tmp_out)

    return data, video_format["extension"]


def _process_image_format(frames: List[Image.Image], format_ext: str, frame_rate: int, loop_count: int) -> Tuple[bytes, str]:
    """
    处理图像格式（GIF、WEBP等）的逻辑。
    返回 (video_bytes, extension_without_dot)
    """
    bio = io.BytesIO()
    pil_format = format_ext.upper()
    save_kwargs = {}
    # GIF / WEBP common args
    if pil_format == "GIF":
        save_kwargs.update({
            "save_all": True,
            "append_images": frames[1:],
            "duration": round(1000 / frame_rate),
            "loop": loop_count,
            "optimize": False,
        })
        frames[0].save(bio, format="GIF", **save_kwargs)
    elif pil_format == "WEBP":
        save_kwargs.update({
            "save_all": True,
            "append_images": frames[1:],
            "duration": round(1000 / frame_rate),
            "loop": loop_count,
        })
        frames[0].save(bio, format="WEBP", **save_kwargs)
    else:
        # 其他 pillow 支持的多帧 image
        frames[0].save(bio, format=pil_format, save_all=True, append_images=frames[1:], duration=round(1000/frame_rate), loop=loop_count)
    bio.seek(0)
    return bio.read(), format_ext


def _ensure_even_dimensions(img: Image.Image) -> Image.Image:
    """确保宽高为偶数（ffmpeg 有些编码器对奇数维度不友好）。"""
    w, h = img.size
    new_w = w + (w % 2)
    new_h = h + (h % 2)
    if new_w != w or new_h != h:
        return img.resize((new_w, new_h))
    return img

def _run_ffmpeg_with_metadata_file(
    args: List[str],
    frames: List[Image.Image],
    metadata_json: str,
    tmp_dir: str,
    tmp_out: str,
    env: dict,
    muxer: str
):
    """
    使用临时元数据文件运行 ffmpeg 的辅助函数。
    处理元数据文件的创建、转义、ffmpeg 执行和清理。
    """
    # 创建临时元数据文件
    md_tmp = os.path.join(tmp_dir, f"{uuid.uuid4().hex}_metadata.txt")
    with open(md_tmp, "w", encoding="utf-8") as mf:
        mf.write(";FFMETADATA1\n")
        # 转义危险字符
        md = metadata_json.replace("\\", "\\\\").replace(";", "\\;").replace("#", "\\#").replace("\n", "\\\n")
        mf.write(md)

    # 构建包含元数据文件的新参数
    new_args = [args[0]] + ["-i", md_tmp] + args[1:]

    try:
        with subprocess.Popen(new_args + ["-f", muxer, tmp_out], stdin=subprocess.PIPE, env=env) as proc:
            for fr in frames:
                proc.stdin.write(fr.tobytes())
            proc.stdin.close()
            proc.wait()
    finally:
        # 清理临时元数据文件
        if md_tmp and os.path.exists(md_tmp):
            os.remove(md_tmp)


def _run_ffmpeg_with_metadata_arg(
    args: List[str],
    meta_arg_list: List[str],
    frames: List[Image.Image],
    tmp_out: str,
    env: dict,
    muxer: str
):
    """
    使用元数据参数直接运行 ffmpeg 的辅助函数。
    """
    # run ffmpeg writing frames to stdin and create tmp_out
    try:
        with subprocess.Popen(args + meta_arg_list + ["-f", muxer, tmp_out], stdin=subprocess.PIPE, env=env) as proc:
            for fr in frames:
                # ensure rgb24 byte order
                proc.stdin.write(fr.tobytes())
            proc.stdin.close()
            proc.wait()
    except Exception:
        # bubble up, caller can decide
        raise
