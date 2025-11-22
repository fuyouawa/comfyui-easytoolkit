import torch
import cv2
import numpy as np
from PIL import Image
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


def _single_image_to_bytes(image, format="image/png"):
    """Convert single image (numpy array) to bytes."""
    # Convert to uint8
    if image.dtype != np.uint8:
        image = np.clip(image * 255, 0, 255).astype(np.uint8)

    # Convert to PIL image
    image_pil = Image.fromarray(image)

    # Save to memory as bytes
    buffer = io.BytesIO()
    image_pil.save(buffer, format=format.split("/")[-1])
    buffer.seek(0)
    return buffer.read()


def image_to_bytes(image, format="image/png") -> bytes:
    """Convert image (tensor or numpy) to bytes."""
    # Handle tensor input
    if isinstance(image, torch.Tensor):
        image = image.detach().cpu().numpy()

    # Remove batch dimension
    if image.ndim == 4:
        image = image[0]

    return _single_image_to_bytes(image, format)

def bytes_to_image(image_bytes):
    """Convert bytes to image tensor with alpha mask."""
    nparr = np.frombuffer(image_bytes, np.uint8)

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

def image_batch_to_bytes_list(images, format="image/png"):
    """Convert batch of images to list of bytes."""
    if isinstance(images, torch.Tensor):
        images = images.detach().cpu().numpy()

    bytes_list = []
    # Handle batch dimension
    if images.ndim == 4:
        for i in range(images.shape[0]):
            image = images[i]
            image_bytes = _single_image_to_bytes(image, format)
            bytes_list.append(image_bytes)
    elif images.ndim == 3:
        # Single image
        image_bytes = _single_image_to_bytes(images, format)
        bytes_list.append(image_bytes)

    return bytes_list

def bytes_list_to_image_batch(bytes_list):
    """Convert list of bytes to batch of images with masks."""
    images = []
    masks = []

    for image_bytes in bytes_list:
        image, mask = bytes_to_image(image_bytes)
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


def tensor_to_bytes(tensor):
    """Convert raw tensor to bytes (serialized tensor data)."""
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

    return buffer.read()


def bytes_to_tensor(tensor_bytes):
    """Convert bytes back to tensor (deserialize tensor data)."""
    buffer = io.BytesIO(tensor_bytes)

    # Load tensor
    tensor = torch.load(buffer)

    # Add batch dimension if not present
    if tensor.ndim == 3:
        tensor = tensor.unsqueeze(0)

    return tensor


def tensor_batch_to_bytes_list(tensors):
    """Convert batch of tensors to list of bytes."""
    if isinstance(tensors, torch.Tensor):
        tensors = tensors.detach().cpu()
    else:
        tensors = torch.from_numpy(tensors)

    bytes_list = []
    # Handle batch dimension
    if tensors.ndim == 4:
        for i in range(tensors.shape[0]):
            tensor = tensors[i]
            tensor_bytes = tensor_to_bytes(tensor)
            bytes_list.append(tensor_bytes)
    elif tensors.ndim == 3:
        # Single tensor
        tensor_bytes = tensor_to_bytes(tensors)
        bytes_list.append(tensor_bytes)

    return bytes_list


def bytes_list_to_tensor_batch(bytes_list):
    """Convert list of bytes to batch of tensors."""
    tensors = []

    for tensor_bytes in bytes_list:
        tensor = bytes_to_tensor(tensor_bytes)
        tensors.append(tensor)

    # Concatenate all tensors into a batch
    if len(tensors) > 0:
        tensors_batch = torch.cat(tensors, dim=0)
        return tensors_batch
    else:
        # Return empty tensor if no tensors
        return torch.empty(0)