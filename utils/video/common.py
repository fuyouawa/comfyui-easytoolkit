# from PIL import Image
# from typing import List, Tuple

# def convert_image_batch_to_pil_list(image_batch) -> List[Image.Image]:
#     """
#     Convert image_batch to PIL Image list and normalize.

#     Supports multiple input formats:
#     - ComfyUI tensor objects (converted via im.cpu().numpy())
#     - PIL Image objects
#     - numpy arrays (automatically converted to uint8 and clipped to [0, 255])

#     Returns:
#         List[Image.Image]: Normalized PIL Image list, all images converted to RGB format and ensured even dimensions
#     """
#     frames: List[Image.Image] = []
#     for im in image_batch:
#         try:
#             # Handle ComfyUI tensor objects
#             arr = (255.0 * im.cpu().numpy()).astype("uint8")
#             img = Image.fromarray(arr)
#         except Exception:
#             # If image_batch is already PIL Image or numpy array, try direct processing
#             if isinstance(im, Image.Image):
#                 img = im
#             else:
#                 import numpy as _np
#                 arr = _np.array(im)
#                 if arr.dtype != _np.uint8:
#                     arr = _np.clip(arr, 0, 255).astype(_np.uint8)
#                 img = Image.fromarray(arr)
#         img = img.convert("RGB")
#         img = _ensure_even_dimensions(img)
#         frames.append(img)
#     return frames


# def _ensure_even_dimensions(img: Image.Image) -> Image.Image:
#     """Ensure width and height are even (some ffmpeg encoders don't like odd dimensions)."""
#     w, h = img.size
#     new_w = w + (w % 2)
#     new_h = h + (h % 2)
#     if new_w != w or new_h != h:
#         return img.resize((new_w, new_h))
#     return img


# def process_image_format(frames: List[Image.Image], format_ext: str, frame_rate: int, loop_count: int) -> Tuple[bytes, str]:
#     """
#     Logic for processing image formats (GIF, WEBP, etc.) using Pillow.
#     Returns (video_bytes, extension_without_dot)
#     """
#     import io

#     bio = io.BytesIO()
#     pil_format = format_ext.upper()
#     save_kwargs = {}

#     # GIF / WEBP common args
#     if pil_format == "GIF":
#         save_kwargs.update({
#             "save_all": True,
#             "append_images": frames[1:],
#             "duration": round(1000 / frame_rate),
#             "loop": loop_count,
#             "optimize": False,
#         })
#         frames[0].save(bio, format="GIF", **save_kwargs)
#     elif pil_format == "WEBP":
#         save_kwargs.update({
#             "save_all": True,
#             "append_images": frames[1:],
#             "duration": round(1000 / frame_rate),
#             "loop": loop_count,
#         })
#         frames[0].save(bio, format="WEBP", **save_kwargs)
#     else:
#         # Other pillow-supported multi-frame images
#         frames[0].save(bio, format=pil_format, save_all=True, append_images=frames[1:],
#                       duration=round(1000/frame_rate), loop=loop_count)

#     bio.seek(0)
#     return bio.read(), format_ext

