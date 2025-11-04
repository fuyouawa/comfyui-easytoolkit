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


def image_to_base64(image, format="image/png") -> str:
    # If it's a torch.Tensor, convert to numpy first
    if isinstance(image, torch.Tensor):
        image = image.detach().cpu().numpy()

    # Remove batch dimension (e.g., (1, H, W, C) -> (H, W, C))
    if image.ndim == 4:
        image = image[0]

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