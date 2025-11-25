import base64
import torch
import numpy as np

def encode_steganography(
        data_bytes: bytes, 
        width: int = None, 
        height: int = None, 
        use_alpha: bool = True, 
        top_margin_ratio: float = 0.2, 
        bottom_margin_ratio: float = 0.2):
    """
    Encode bytes into a steganography image.

    Args:
        data_bytes: Bytes to encode
        width: Optional width of output image (auto-calculated if not provided)
        height: Optional height of output image (auto-calculated if not provided)
        use_alpha: Whether to use RGBA (4 channels) or RGB (3 channels) format
        top_margin_ratio: Ratio of top margin to reserve (default: 20%)
        bottom_margin_ratio: Ratio of bottom margin to reserve (default: 20%)

    Returns:
        Image tensor with encoded data
    """

    assert top_margin_ratio >= 0 and top_margin_ratio <= 1, "Top margin ratio must be between 0 and 1"
    assert bottom_margin_ratio >= 0 and bottom_margin_ratio <= 1, "Bottom margin ratio must be between 0 and 1"

    data_length = len(data_bytes)
    channels = 4 if use_alpha else 3

    middle_ratio = 1 - top_margin_ratio - bottom_margin_ratio
    assert middle_ratio > 0, "Middle ratio must be greater than 0"

    # Calculate image dimensions if not provided
    if width is None or height is None:
        # Calculate square-ish dimensions
        # We need 4 bytes per pixel (RGBA) or 3 bytes per pixel (RGB) to store data
        # Add header: 4 bytes for length
        total_bytes_needed = data_length + 4
        pixels_needed = (total_bytes_needed + channels - 1) // channels  # Round up

        if width is None and height is None:
            # Calculate square dimensions
            square_size = int(np.ceil(np.sqrt(pixels_needed / middle_ratio)))
            width = height = square_size
        elif width is None:
            width = (pixels_needed + height - 1) // height  # Round up
        else:  # height is None
            height = (pixels_needed + width - 1) // width  # Round up

    total_pixels = width * height
    total_capacity = total_pixels * channels

    # Check if data fits
    if data_length + 4 > total_capacity:
        raise ValueError(f"Data too large ({data_length} bytes) for image size {width}x{height} with {channels} channels (capacity: {total_capacity - 4} bytes)")

    # Calculate margin rows
    top_margin_rows = int(height * top_margin_ratio)
    bottom_margin_rows = int(height * bottom_margin_ratio)

    # Ensure we have at least 1 row for data
    available_rows = height - top_margin_rows - bottom_margin_rows
    if available_rows < 1:
        raise ValueError(f"Margins too large: top {top_margin_ratio}% + bottom {bottom_margin_ratio}% = {top_margin_rows + bottom_margin_rows} rows, leaving no space for data")

    # Create header with data length (4 bytes)
    header = data_length.to_bytes(4, byteorder='big')

    # Combine header and data
    full_data = header + data_bytes

    # Calculate capacity in data area (excluding margins)
    data_capacity = available_rows * width * channels

    # Check if data fits in data area
    if len(full_data) > data_capacity:
        raise ValueError(f"Data too large ({len(full_data)} bytes) for data area size {available_rows} rows x {width} width with {channels} channels (data capacity: {data_capacity} bytes)")

    # Create full image array with margins
    full_array = np.zeros(total_capacity, dtype=np.uint8)

    # Fill top margin with random noise
    top_margin_bytes = top_margin_rows * width * channels
    full_array[:top_margin_bytes] = np.random.randint(0, 256, top_margin_bytes, dtype=np.uint8)

    # Fill data area
    data_area_start = top_margin_bytes
    data_area_end = data_area_start + len(full_data)
    full_array[data_area_start:data_area_end] = np.frombuffer(full_data, dtype=np.uint8)

    # Fill remaining data area with random noise
    remaining_data_bytes = data_capacity - len(full_data)
    full_array[data_area_end:data_area_end + remaining_data_bytes] = np.random.randint(0, 256, remaining_data_bytes, dtype=np.uint8)

    # Fill bottom margin with random noise
    bottom_margin_start = data_area_start + data_capacity
    bottom_margin_bytes = bottom_margin_rows * width * channels
    full_array[bottom_margin_start:bottom_margin_start + bottom_margin_bytes] = np.random.randint(0, 256, bottom_margin_bytes, dtype=np.uint8)

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

def decode_steganography(image, top_margin_ratio: float = 0.2, bottom_margin_ratio: float = 0.2):
    """
    Decode bytes from a steganography image.

    Args:
        image: Image tensor with encoded data
        top_margin_ratio: Ratio of top margin to skip (default: 20%)
        bottom_margin_ratio: Ratio of bottom margin to skip (default: 20%)

    Returns:
        Decoded bytes
    """
    assert top_margin_ratio >= 0 and top_margin_ratio <= 1, "Top margin ratio must be between 0 and 1"
    assert bottom_margin_ratio >= 0 and bottom_margin_ratio <= 1, "Bottom margin ratio must be between 0 and 1"

    middle_ratio = 1 - top_margin_ratio - bottom_margin_ratio
    assert middle_ratio > 0, "Middle ratio must be greater than 0"
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
        channels = 3
    elif image_uint8.shape[2] == 4:
        # RGBA - use all 4 channels
        channels = 4
    else:
        raise ValueError(f"Unexpected number of channels: {image_uint8.shape[2]}")

    height, width = image_uint8.shape[:2]

    # Calculate margin rows
    top_margin_rows = int(height * top_margin_ratio)
    bottom_margin_rows = int(height * bottom_margin_ratio)

    # Ensure we have at least 1 row for data
    available_rows = height - top_margin_rows - bottom_margin_rows
    if available_rows < 1:
        raise ValueError(f"Margins too large: top {top_margin_ratio * 100}% + bottom {bottom_margin_ratio * 100}% = {top_margin_rows + bottom_margin_rows} rows, leaving no space for data")

    # Calculate byte positions
    top_margin_bytes = top_margin_rows * width * channels
    data_area_bytes = available_rows * width * channels

    # Extract data area from the flattened image
    flattened_image = image_uint8.flatten()
    data_area = flattened_image[top_margin_bytes:top_margin_bytes + data_area_bytes]

    # Read header (first 4 bytes = data length)
    data_length = int.from_bytes(data_area[:4].tobytes(), byteorder='big')

    # Validate data length
    if data_length < 0 or data_length > len(data_area) - 4:
        raise ValueError(f"Invalid data length in image header: {data_length}")

    # Extract data bytes
    data_bytes = data_area[4:4 + data_length].tobytes()

    return data_bytes


def encode_bytes(data: bytes, base: str) -> str:
    """
    Encode bytes data to string representation in specified base.

    Args:
        data: Bytes data to encode
        base: Base format ("binary", "octal", "decimal", "hexadecimal", "base64")

    Returns:
        Encoded string representation

    Raises:
        ValueError: If unsupported base is provided
    """
    if base == "binary":
        return ''.join(format(byte, '08b') for byte in data)
    elif base == "octal":
        return ''.join(format(byte, '03o') for byte in data)
    elif base == "decimal":
        return ' '.join(str(byte) for byte in data)
    elif base == "hexadecimal":
        return data.hex()
    elif base == "base64":
        return base64.b64encode(data).decode("utf-8")
    else:
        raise ValueError(f"Unsupported base: {base}")


def decode_bytes(encoded_string: str, base: str) -> bytes:
    """
    Decode string representation back to bytes data from specified base.

    Args:
        encoded_string: String representation of bytes data
        base: Base format ("binary", "octal", "decimal", "hexadecimal", "base64")

    Returns:
        Decoded bytes data

    Raises:
        ValueError: If unsupported base is provided or invalid input format
    """
    encoded_string = encoded_string.strip()

    if base == "binary":
        # Remove any spaces and ensure length is multiple of 8
        binary_string = encoded_string.replace(" ", "").replace("\n", "").replace("\t", "")
        if len(binary_string) % 8 != 0:
            raise ValueError("Binary string length must be multiple of 8")
        return bytes(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))

    elif base == "octal":
        # Remove any spaces and ensure length is multiple of 3
        octal_string = encoded_string.replace(" ", "").replace("\n", "").replace("\t", "")
        if len(octal_string) % 3 != 0:
            raise ValueError("Octal string length must be multiple of 3")
        return bytes(int(octal_string[i:i+3], 8) for i in range(0, len(octal_string), 3))

    elif base == "decimal":
        # Split by spaces and convert each number
        decimal_strings = encoded_string.split()
        return bytes(int(num) for num in decimal_strings)

    elif base == "hexadecimal":
        # Remove any spaces and ensure even length
        hex_string = encoded_string.replace(" ", "").replace("\n", "").replace("\t", "")
        if len(hex_string) % 2 != 0:
            raise ValueError("Hexadecimal string length must be even")
        return bytes.fromhex(hex_string)

    elif base == "base64":
        return base64.b64decode(encoded_string.encode("utf-8"))

    else:
        raise ValueError(f"Unsupported base: {base}")