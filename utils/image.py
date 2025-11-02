import torch

def invert_colors(image):
    return 1.0 - image


def xor_operation(image, key):
    images_uint8 = (image * 255).to(torch.uint8)

    processed_images = images_uint8 ^ key

    return processed_images.to(torch.float32) / 255.0


def process_image(image, operation):
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
