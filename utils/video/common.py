from PIL import Image
from typing import List, Tuple, Iterator, Optional
import itertools
import numpy as np
import torch

# Default downscale ratio for target size calculation
DEFAULT_DOWNSCALE_RATIO = 8


class VideoInfo:
    """
    Video information class for encapsulating video loading metadata.
    """
    def __init__(self, source_path: str, 
                source_width: int, source_height: int, source_fps: float, source_frame_count: int, 
                loaded_width: int, loaded_height: int, loaded_fps: float, loaded_frame_count: int,
                loaded_channels: int, 
                generator: str):
        """
        Initialize video information.

        Args:
            source_path: Video source file path
            source_fps: Original frame rate
            source_width: Original video width
            source_height: Original video height
            source_frame_count: Original frame count in source video
            loaded_width: Loaded width
            loaded_height: Loaded height
            loaded_channels: Loaded channels
            loaded_frame_count: Loaded frame count
            loaded_fps: Loaded frame rate
            generator: Generator type used
        """
        self.source_path = source_path
        self.loaded_width = loaded_width
        self.loaded_height = loaded_height
        self.loaded_channels = loaded_channels
        self.loaded_frame_count = loaded_frame_count
        self.generator = generator
        self.source_fps = source_fps
        self.source_frame_count = source_frame_count
        self.source_width = source_width
        self.source_height = source_height
        self.loaded_fps = loaded_fps

    @property
    def resolution(self) -> str:
        """Return resolution string."""
        return f"{self.loaded_width}x{self.loaded_height}"

    @property
    def aspect_ratio(self) -> float:
        """Return aspect ratio."""
        return self.loaded_width / self.loaded_height

    @property
    def total_duration(self) -> Optional[float]:
        """Calculate total duration in seconds from frame count and FPS."""
        if self.source_fps and self.source_fps > 0:
            return self.source_frame_count / self.source_fps
        return None

    @property
    def estimated_duration(self) -> Optional[float]:
        """Estimate video duration in seconds."""
        if self.source_fps and self.source_fps > 0:
            return self.loaded_frame_count / self.source_fps
        return None

    def __str__(self) -> str:
        """String representation."""
        duration_info = f", duration: {self.estimated_duration:.2f}s" if self.estimated_duration else ""
        fps_info = f", source fps: {self.source_fps}fps" if self.source_fps else ""
        loaded_fps_info = f", loaded fps: {self.loaded_fps}fps" if self.loaded_fps else ""
        source_res_info = f", source: {self.source_width}x{self.source_height}" if self.source_width and self.source_height else ""
        source_frames_info = f", source frames: {self.source_frame_count}" if self.source_frame_count else ""
        return f"VideoInfo(path: {self.source_path}, resolution: {self.resolution}, frames: {self.loaded_frame_count}{source_frames_info}{duration_info}{fps_info}{loaded_fps_info}{source_res_info})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"VideoInfo(source_path='{self.source_path}', loaded_width={self.loaded_width}, loaded_height={self.loaded_height}, loaded_channels={self.loaded_channels}, loaded_frame_count={self.loaded_frame_count}, generator='{self.generator}', source_fps={self.source_fps}, source_frame_count={self.source_frame_count}, source_width={self.source_width}, source_height={self.source_height}, loaded_fps={self.loaded_fps})"
    

def image_batch_to_pil_list(image_batch) -> List[Image.Image]:
    """
    Convert image_batch to PIL Image list and normalize.

    Supports multiple input formats:
    - ComfyUI tensor objects (converted via im.cpu().numpy())
    - PIL Image objects
    - numpy arrays (automatically converted to uint8 and clipped to [0, 255])

    Returns:
        List[Image.Image]: Normalized PIL Image list, all images converted to RGB format and ensured even dimensions
    """
    frames: List[Image.Image] = []
    for im in image_batch:
        try:
            # Handle ComfyUI tensor objects
            arr = (255.0 * im.cpu().numpy()).astype("uint8")
            img = Image.fromarray(arr)
        except Exception:
            # If image_batch is already PIL Image or numpy array, try direct processing
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


def pil_list_to_image_batch(pil_list: List[Image.Image]) -> torch.Tensor:
    """
    Convert PIL Image list to image batch in specified format.

    Args:
        pil_list: List of PIL Image objects
        output_format: Output format - "tensor" for PyTorch tensor or "numpy" for numpy array

    Returns:
        torch.Tensor or numpy.ndarray: Image batch in specified format
        - For tensor: shape (frames, height, width, channels) with values in [0, 1]
        - For numpy: shape (frames, height, width, channels) with values in [0, 1]
    """
    if not pil_list:
        raise ValueError("PIL list cannot be empty")

    # Get dimensions from first image
    first_img = pil_list[0]
    width, height = first_img.size

    # Convert all images to numpy arrays
    frames = []
    for img in pil_list:
        # Ensure consistent dimensions
        if img.size != (width, height):
            img = img.resize((width, height))

        # Convert to numpy array and normalize to [0, 1]
        arr = np.array(img).astype(np.float32) / 255.0
        frames.append(arr)

    # Stack frames
    batch = np.stack(frames)

    return torch.from_numpy(batch)



def frames_to_tensor(frame_generator: Iterator, width: int, height: int, channels: int = 3, max_frames: int = None) -> torch.Tensor:
    """
    Convert frame generator to PyTorch tensor.

    Args:
        frame_generator: Frame generator
        width: Frame width
        height: Frame height
        channels: Number of channels (3 for RGB, 4 for RGBA)
        max_frames: Maximum number of frames limit

    Returns:
        PyTorch tensor with shape (frames, height, width, channels)
    """
    if max_frames is not None:
        frame_generator = itertools.islice(frame_generator, max_frames)

    # Efficiently convert generator to numpy array, then to PyTorch tensor
    dtype = np.dtype((np.float32, (height, width, channels)))
    frames_array = np.fromiter(frame_generator, dtype)

    if len(frames_array) == 0:
        raise RuntimeError("No frames generated")

    return torch.from_numpy(frames_array)

def _ensure_even_dimensions(img: Image.Image) -> Image.Image:
    """Ensure width and height are even (some ffmpeg encoders don't like odd dimensions)."""
    w, h = img.size
    new_w = w + (w % 2)
    new_h = h + (h % 2)
    if new_w != w or new_h != h:
        return img.resize((new_w, new_h))
    return img


def combine_animated_image(frames: List[Image.Image], output_path: str, format_ext: str, frame_rate: int, loop_count: int) -> str:
    """
    Process image formats (GIF, WEBP, etc.) using Pillow and save to output_path.
    Returns output_path
    """
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
        frames[0].save(output_path, format="GIF", **save_kwargs)
    elif pil_format == "WEBP":
        save_kwargs.update({
            "save_all": True,
            "append_images": frames[1:],
            "duration": round(1000 / frame_rate),
            "loop": loop_count,
        })
        frames[0].save(output_path, format="WEBP", **save_kwargs)
    else:
        # Other pillow-supported multi-frame images
        frames[0].save(output_path, format=pil_format, save_all=True, append_images=frames[1:],
                      duration=round(1000/frame_rate), loop=loop_count)

    return output_path


def target_size(width: int, height: int, custom_width: int, custom_height: int, downscale_ratio: int = DEFAULT_DOWNSCALE_RATIO) -> tuple[int, int]:
    """
    Calculate target size while maintaining aspect ratio and scaling ratio.

    Args:
        width: Original width
        height: Original height
        custom_width: Custom width (0 means auto)
        custom_height: Custom height (0 means auto)
        downscale_ratio: Downscale ratio for alignment

    Returns:
        Tuple of (width, height)
    """
    if downscale_ratio is None:
        downscale_ratio = DEFAULT_DOWNSCALE_RATIO
    if custom_width == 0 and custom_height == 0:
        pass
    elif custom_height == 0:
        height *= custom_width/width
        width = custom_width
    elif custom_width == 0:
        width *= custom_height/height
        height = custom_height
    else:
        width = custom_width
        height = custom_height
    width = int(width/downscale_ratio + 0.5) * downscale_ratio
    height = int(height/downscale_ratio + 0.5) * downscale_ratio
    return (width, height)


def batched(iterable: Iterator, n: int) -> Iterator:
    """
    Batch an iterable into chunks of size n.

    Args:
        iterable: Input iterable
        n: Batch size

    Yields:
        Tuples of batch items
    """
    while batch := tuple(itertools.islice(iterable, n)):
        yield batch