import torch
import cv2
import numpy as np
from PIL import Image
import base64
import io


def invert_colors(image):
    """Invert image colors (1.0 - image)."""
    return 1.0 - image


def xor_operation(image, key):
    """Apply XOR operation to image pixels with given key."""
    # Convert normalized [0,1] image to uint8 [0,255] for bitwise operations
    images_uint8 = (image * 255).to(torch.uint8)

    # Apply XOR operation for basic encryption/obfuscation
    processed_images = images_uint8 ^ key

    # Convert back to normalized float32 [0,1]
    return processed_images.to(torch.float32) / 255.0


def encrypt_image(image, operation):
    """Apply encryption/obfuscation operation to image."""
    if operation == "invert":
        processed_image = invert_colors(image)
    elif operation == "xor-16":
        processed_image = xor_operation(image, 16)
    elif operation == "xor-32":
        processed_image = xor_operation(image, 32)
    elif operation == "xor-64":
        processed_image = xor_operation(image, 64)
    elif operation == "xor-128":
        processed_image = xor_operation(image, 128)
    else:
        processed_image = image

    return processed_image


def _single_image_to_base64(image, format="image/png"):
    """Convert single image (numpy array) to base64 string."""
    # Convert to uint8
    if image.dtype != np.uint8:
        image = np.clip(image * 255, 0, 255).astype(np.uint8)

    # Convert to PIL image
    image_pil = Image.fromarray(image)

    # Save to memory and convert to base64
    buffer = io.BytesIO()
    image_pil.save(buffer, format=format.split("/")[-1])
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def image_to_base64(image, format="image/png") -> str:
    """Convert image (tensor or numpy) to base64 string."""
    # Handle tensor input
    if isinstance(image, torch.Tensor):
        image = image.detach().cpu().numpy()

    # Remove batch dimension
    if image.ndim == 4:
        image = image[0]

    return _single_image_to_base64(image, format)

def base64_to_image(base64_data):
    """Convert base64 string to image tensor with alpha mask."""
    nparr = np.frombuffer(base64.b64decode(base64_data), np.uint8)

    result = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    channels = cv2.split(result)

    # Handle alpha channel if present
    if len(channels) > 3:
      mask = channels[3].astype(np.float32) / 255.0  # Normalize alpha to [0,1]
      mask = torch.from_numpy(mask)
    else:
      # Create solid white mask for images without alpha
      mask = torch.ones(channels[0].shape, dtype=torch.float32, device="cpu")

    result = _convert_color(result)
    result = result.astype(np.float32) / 255.0  # Normalize RGB to [0,1]
    new_images = torch.from_numpy(result)[None,]  # Add batch dimension
    return new_images, mask

def _convert_color(image):
    """Convert BGR/BGRA image to RGB format."""
    # OpenCV loads images as BGR, convert to RGB for consistency
    if len(image.shape) > 2 and image.shape[2] >= 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)  # BGRA to RGB (drop alpha)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR to RGB

def image_batch_to_base64_list(images, format="image/png"):
    """Convert batch of images to list of base64 strings."""
    if isinstance(images, torch.Tensor):
        images = images.detach().cpu().numpy()

    base64_list = []
    # Handle batch dimension
    if images.ndim == 4:
        for i in range(images.shape[0]):
            image = images[i]
            base64_str = _single_image_to_base64(image, format)
            base64_list.append(base64_str)
    elif images.ndim == 3:
        # Single image
        base64_str = _single_image_to_base64(images, format)
        base64_list.append(base64_str)

    return base64_list

def base64_list_to_image_batch(base64_list):
    """Convert list of base64 strings to batch of images with masks."""
    images = []
    masks = []

    for base64_data in base64_list:
        image, mask = base64_to_image(base64_data)
        images.append(image)
        masks.append(mask)

    # Concatenate all images into a batch
    if len(images) > 0:
        images_batch = torch.cat(images, dim=0)
        masks_batch = torch.stack(masks, dim=0)
        return images_batch, masks_batch
    else:
        # Return empty tensors if no images
        return torch.empty(0), torch.empty(0)


def tensor_to_base64(tensor):
    """Convert raw tensor to base64 string (serialized tensor data)."""
    # Handle tensor input
    if isinstance(tensor, torch.Tensor):
        tensor = tensor.detach().cpu()
    else:
        tensor = torch.from_numpy(tensor)

    # Remove batch dimension if present
    if tensor.ndim == 4 and tensor.shape[0] == 1:
        tensor = tensor[0]

    # Serialize tensor to bytes
    buffer = io.BytesIO()
    torch.save(tensor, buffer)
    buffer.seek(0)

    # Encode to base64
    return base64.b64encode(buffer.read()).decode("utf-8")


def base64_to_tensor(base64_data):
    """Convert base64 string back to tensor (deserialize tensor data)."""
    # Decode from base64
    tensor_bytes = base64.b64decode(base64_data)
    buffer = io.BytesIO(tensor_bytes)

    # Load tensor
    tensor = torch.load(buffer)

    # Add batch dimension if not present
    if tensor.ndim == 3:
        tensor = tensor.unsqueeze(0)

    return tensor


def tensor_batch_to_base64_list(tensors):
    """Convert batch of tensors to list of base64 strings."""
    if isinstance(tensors, torch.Tensor):
        tensors = tensors.detach().cpu()
    else:
        tensors = torch.from_numpy(tensors)

    base64_list = []
    # Handle batch dimension
    if tensors.ndim == 4:
        for i in range(tensors.shape[0]):
            tensor = tensors[i]
            base64_str = tensor_to_base64(tensor)
            base64_list.append(base64_str)
    elif tensors.ndim == 3:
        # Single tensor
        base64_str = tensor_to_base64(tensors)
        base64_list.append(base64_str)

    return base64_list


def base64_list_to_tensor_batch(base64_list):
    """Convert list of base64 strings to batch of tensors."""
    tensors = []

    for base64_data in base64_list:
        tensor = base64_to_tensor(base64_data)
        tensors.append(tensor)

    # Concatenate all tensors into a batch
    if len(tensors) > 0:
        tensors_batch = torch.cat(tensors, dim=0)
        return tensors_batch
    else:
        # Return empty tensor if no tensors
        return torch.empty(0)


def base64_to_noise_image(base64_data: str, width: int = None, height: int = None):
    """
    Encode base64 string into a noise-like image.
    
    Args:
        base64_data: Base64 string to encode
        width: Optional width of output image (auto-calculated if not provided)
        height: Optional height of output image (auto-calculated if not provided)
    
    Returns:
        Image tensor with encoded data
    """
    # Convert base64 string to bytes
    data_bytes = base64_data.encode('utf-8')
    data_length = len(data_bytes)
    
    # Calculate image dimensions if not provided
    if width is None or height is None:
        # Calculate square-ish dimensions
        # We need 4 bytes per pixel (RGBA) to store data
        # Add header: 4 bytes for length
        total_bytes_needed = data_length + 4
        pixels_needed = (total_bytes_needed + 3) // 4  # Round up, 4 bytes per pixel
        
        if width is None and height is None:
            # Calculate square dimensions
            side = int(np.ceil(np.sqrt(pixels_needed)))
            width = height = side
        elif width is None:
            width = (pixels_needed + height - 1) // height  # Round up
        else:  # height is None
            height = (pixels_needed + width - 1) // width  # Round up
    
    total_pixels = width * height
    total_capacity = total_pixels * 4  # 4 bytes per pixel (RGBA)
    
    # Check if data fits
    if data_length + 4 > total_capacity:
        raise ValueError(f"Data too large ({data_length} bytes) for image size {width}x{height} (capacity: {total_capacity - 4} bytes)")
    
    # Create header with data length (4 bytes)
    header = data_length.to_bytes(4, byteorder='big')
    
    # Combine header and data
    full_data = header + data_bytes
    
    # Pad with random noise to fill the image
    remaining_bytes = total_capacity - len(full_data)
    noise = np.random.randint(0, 256, remaining_bytes, dtype=np.uint8)
    full_data_array = np.frombuffer(full_data, dtype=np.uint8)
    full_array = np.concatenate([full_data_array, noise])
    
    # Reshape to image format (height, width, 4 channels)
    image_array = full_array.reshape(height, width, 4)
    
    # Convert to float32 [0, 1] range for ComfyUI
    image_tensor = torch.from_numpy(image_array.astype(np.float32) / 255.0)
    
    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)
    
    return image_tensor


def noise_image_to_base64(image):
    """
    Decode base64 string from a noise-like image.
    
    Args:
        image: Image tensor with encoded data
    
    Returns:
        Decoded base64 string
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
        # RGB - can only use 3 bytes per pixel
        raise ValueError("Cannot decode from RGB image without alpha channel, need 4 channels (RGBA)")
    elif image_uint8.shape[2] == 4:
        # RGBA - perfect, use all 4 channels
        channels = 4
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
    
    # Convert bytes to string
    base64_string = data_bytes.decode('utf-8')
    
    return base64_string