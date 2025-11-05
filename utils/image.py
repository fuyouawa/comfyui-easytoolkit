import torch
import cv2
import numpy as np
from PIL import Image
import base64
import io


def invert_colors(image):
    return 1.0 - image


def xor_operation(image, key):
    images_uint8 = (image * 255).to(torch.uint8)

    processed_images = images_uint8 ^ key

    return processed_images.to(torch.float32) / 255.0


def encrypt_image(image, operation):
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
    """
    Convert a single image (numpy array) to base64 string
    
    Args:
        image: numpy array with shape (H, W, C)
        format: Image format (e.g., "image/png", "image/jpeg")
    
    Returns:
        Base64 encoded string
    """
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
    """
    Convert an image to base64 string
    
    Args:
        image: torch.Tensor or numpy array with shape (H, W, C) or (1, H, W, C)
        format: Image format (e.g., "image/png", "image/jpeg")
    
    Returns:
        Base64 encoded string
    """
    # If it's a torch.Tensor, convert to numpy first
    if isinstance(image, torch.Tensor):
        image = image.detach().cpu().numpy()

    # Remove batch dimension (e.g., (1, H, W, C) -> (H, W, C))
    if image.ndim == 4:
        image = image[0]

    return _single_image_to_base64(image, format)

def base64_to_image(base64_data):
    nparr = np.frombuffer(base64.b64decode(base64_data), np.uint8)

    result = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    channels = cv2.split(result)
    if len(channels) > 3:
      mask = channels[3].astype(np.float32) / 255.0
      mask = torch.from_numpy(mask)
    else:
      mask = torch.ones(channels[0].shape, dtype=torch.float32, device="cpu")

    result = _convert_color(result)
    result = result.astype(np.float32) / 255.0
    new_images = torch.from_numpy(result)[None,]
    return new_images, mask

def _convert_color(image):
    if len(image.shape) > 2 and image.shape[2] >= 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def image_batch_to_base64_list(images, format="image/png"):
    """
    Convert a batch of images to a list of base64 strings
    
    Args:
        images: torch.Tensor with shape (N, H, W, C) where N is batch size
        format: Image format (e.g., "image/png", "image/jpeg")
    
    Returns:
        List of base64 encoded strings
    """
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
    """
    Convert a list of base64 strings to a batch of images
    
    Args:
        base64_list: List of base64 encoded strings
    
    Returns:
        Tuple of (images, masks) where:
        - images: torch.Tensor with shape (N, H, W, C)
        - masks: torch.Tensor with shape (N, H, W)
    """
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