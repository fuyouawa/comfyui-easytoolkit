import torch
from ... import register_node
from ...utils.image import encrypt_image

@register_node
class ImageBatchEncryptor:
    """
    图像批次处理器节点
    提供多种图像批次处理功能：颜色翻转、异或加密/解密
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
        """
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "operation": (["invert", "xor-16", "xor-32", "xor-64", "xor-128"], {
                    "default": "invert"
                }),
                "enable": ("BOOLEAN", {
                    "default": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_batch",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"

    def run(self, image_batch, operation, enable):
        """
        处理图像批次的主函数
        """
        if not enable:
            return (image_batch,)

        # 获取批次大小
        batch_size = image_batch.shape[0]

        # 创建一个列表来存储处理后的图像
        processed_batch = []

        # 遍历批次中的每张图像
        for i in range(batch_size):
            # 获取单张图像
            single_image = image_batch[i:i+1]  # 保持批次维度

            # 应用图像处理
            processed_image = encrypt_image(single_image, operation)

            # 添加到处理后的批次
            processed_batch.append(processed_image)

        # 将处理后的批次拼接成一个张量
        result_batch = torch.cat(processed_batch, dim=0)

        return (result_batch,)
