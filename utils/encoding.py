import base64
import torch
import numpy as np

def b64decode(data: str, encoding: str = "utf-8") -> bytes:
    return base64.b64decode(data.encode(encoding))

def b64encode(data: bytes, encoding: str = "utf-8") -> str:
    return base64.b64encode(data).decode(encoding)

def encode_steganography(data_bytes: bytes, width: int = None, height: int = None, use_alpha: bool = True):
    """
    Encode bytes into a steganography image.

    Args:
        data_bytes: Bytes to encode
        width: Optional width of output image (auto-calculated if not provided)
        height: Optional height of output image (auto-calculated if not provided)
        use_alpha: Whether to use RGBA (4 channels) or RGB (3 channels) format

    Returns:
        Image tensor with encoded data
    """
    data_length = len(data_bytes)
    channels = 4 if use_alpha else 3

    # Calculate image dimensions if not provided
    if width is None or height is None:
        # Calculate square-ish dimensions
        # We need 4 bytes per pixel (RGBA) or 3 bytes per pixel (RGB) to store data
        # Add header: 4 bytes for length
        total_bytes_needed = data_length + 4
        pixels_needed = (total_bytes_needed + channels - 1) // channels  # Round up

        if width is None and height is None:
            # Calculate square dimensions
            side = int(np.ceil(np.sqrt(pixels_needed)))
            width = height = side
        elif width is None:
            width = (pixels_needed + height - 1) // height  # Round up
        else:  # height is None
            height = (pixels_needed + width - 1) // width  # Round up

    total_pixels = width * height
    total_capacity = total_pixels * channels

    # Check if data fits
    if data_length + 4 > total_capacity:
        raise ValueError(f"Data too large ({data_length} bytes) for image size {width}x{height} with {channels} channels (capacity: {total_capacity - 4} bytes)")

    # Create header with data length (4 bytes)
    header = data_length.to_bytes(4, byteorder='big')

    # Combine header and data
    full_data = header + data_bytes

    # Pad with random noise to fill the image
    remaining_bytes = total_capacity - len(full_data)
    noise = np.random.randint(0, 256, remaining_bytes, dtype=np.uint8)
    full_data_array = np.frombuffer(full_data, dtype=np.uint8)
    full_array = np.concatenate([full_data_array, noise])

    # Reshape to image format
    if use_alpha:
        # RGBA format (height, width, 4 channels)
        image_array = full_array.reshape(height, width, 4)
    else:
        # RGB format (height, width, 3 channels)
        image_array = full_array.reshape(height, width, 3)

    # Convert to float32 [0, 1] range for ComfyUI
    image_tensor = torch.from_numpy(image_array.astype(np.float32) / 255.0)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor

def decode_steganography(image):
    """
    Decode bytes from a steganography image.

    Args:
        image: Image tensor with encoded data

    Returns:
        Decoded bytes
    """
    # Handle tensor input
    if isinstance(image, torch.Tensor):
        image = image.detach().cpu().numpy()

    # Remove batch dimension if present
    if image.ndim == 4:
        image = image[0]

    # Convert from float32 [0, 1] to uint8 [0, 255]
    if image.dtype == np.float32 or image.dtype == np.float64:
        image_uint8 = np.clip(image * 255, 0, 255).astype(np.uint8)
    else:
        image_uint8 = image.astype(np.uint8)

    # Handle different channel configurations
    if image_uint8.ndim == 2:
        # Grayscale - can't decode, need at least RGB
        raise ValueError("Cannot decode from grayscale image, need at least 3 channels")
    elif image_uint8.shape[2] == 3:
        # RGB - use 3 bytes per pixel
        pass
    elif image_uint8.shape[2] == 4:
        # RGBA - use all 4 channels
        pass
    else:
        raise ValueError(f"Unexpected number of channels: {image_uint8.shape[2]}")

    # Flatten the image to get byte array
    byte_array = image_uint8.flatten()

    # Read header (first 4 bytes = data length)
    data_length = int.from_bytes(byte_array[:4].tobytes(), byteorder='big')

    # Validate data length
    if data_length < 0 or data_length > len(byte_array) - 4:
        raise ValueError(f"Invalid data length in image header: {data_length}")

    # Extract data bytes
    data_bytes = byte_array[4:4 + data_length].tobytes()

    return data_bytes