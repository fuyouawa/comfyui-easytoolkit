# ComfyUI EasyToolkit

一个简单易用的 ComfyUI 工具包，提供各种实用的图像处理、算法计算等节点，旨在简化工作流程并提高效率。

## 功能特性

- 🖼️ **图像处理** - 颜色反转、异或加密/解密等图像操作
- 🔢 **算法计算** - 帧数计算等实用算法
- 🎯 **批量处理** - 支持单张图像和图像批次的灵活处理
- ⚡ **高效性能** - 基于 PyTorch 的高性能图像处理
- 🔧 **易于使用** - 直观的节点接口和参数配置

## 安装方法

### 方法一：直接复制
1. 将整个 `comfyui-easytoolkit` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录下
2. 重启 ComfyUI

### 方法二：Git 克隆
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-repo/comfyui-easytoolkit.git
```

## 节点列表

### 图像处理节点 (EasyToolkit/Image)

#### ImageProcessor - 图像处理器
**功能**: 对单张图像进行各种处理操作

**输入参数**:
- `image` (IMAGE): 输入图像
- `operation` (下拉菜单): 处理操作类型
  - `invert`: 颜色反转
  - `xor-16`: 异或加密 (密钥 16)
  - `xor-32`: 异或加密 (密钥 32)
  - `xor-64`: 异或加密 (密钥 64)
  - `xor-128`: 异或加密 (密钥 128)
- `enable` (BOOLEAN): 启用/禁用处理

**输出**:
- `image` (IMAGE): 处理后的图像

#### ImageBatchProcessor - 图像批次处理器
**功能**: 对图像批次进行批量处理操作

**输入参数**:
- `image_batch` (IMAGE): 输入图像批次
- `operation` (下拉菜单): 处理操作类型 (同 ImageProcessor)
- `enable` (BOOLEAN): 启用/禁用处理

**输出**:
- `image_batch` (IMAGE): 处理后的图像批次

#### ImageBatchSelector - 图像批次选择器
**功能**: 从图像批次中选择指定索引的单张图像

**输入参数**:
- `images` (IMAGE): 输入图像批次
- `select` (INT): 要选择的图像索引 (0-1000)

**输出**:
- `image` (IMAGE): 选择出的单张图像

### 算法节点 (EasyToolkit/Algorithm)

#### FrameCalculator - 帧数计算器
**功能**: 根据持续时间、帧率和附加帧数计算总帧数

**计算公式**: `总帧数 = 持续时间 × 帧率 + 附加帧数`

**输入参数**:
- `duration` (FLOAT): 持续时间 (秒), 范围: 0.0-1000.0
- `frame_rate` (FLOAT): 帧率 (fps), 范围: 1.0-120.0
- `extra_frames` (INT): 附加帧数, 范围: 0-1000

**输出**:
- `total_frames` (INT): 计算得到的总帧数

## 使用示例

### 基本图像处理工作流
```
加载图像 → ImageProcessor → 保存图像
```

### 批量图像处理工作流
```
加载图像批次 → ImageBatchProcessor → ImageBatchSelector → 保存单张图像
```

### 视频帧数计算工作流
```
FrameCalculator → 其他视频处理节点
```

## 操作说明

### 颜色反转 (invert)
将图像颜色进行反转，实现负片效果。

### 异或加密 (xor)
使用 XOR 操作对图像进行简单的加密/解密处理：
- `xor-16`: 使用密钥 16 进行异或操作
- `xor-32`: 使用密钥 32 进行异或操作
- `xor-64`: 使用密钥 64 进行异或操作
- `xor-128`: 使用密钥 128 进行异或操作

**注意**: 异或加密是可逆操作，使用相同的密钥再次操作可以恢复原始图像。

### 图像批次选择
当输入图像批次包含多张图像时，可以通过 `ImageBatchSelector` 节点选择特定索引的图像进行处理。

## 技术细节

- **图像格式**: 支持标准的 ComfyUI IMAGE 张量格式 (B, H, W, C)
- **数据类型**: 使用 PyTorch 张量进行高效计算
- **性能优化**: 批量处理支持并行计算

## 更新日志

### v1.0.0
- 初始版本发布
- 包含图像处理和帧数计算功能

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具包！

## 许可证

MIT License

## 支持

如果在使用过程中遇到问题，请通过以下方式联系：
- 提交 GitHub Issue
- 查看项目文档

---

**ComfyUI EasyToolkit** - 让 ComfyUI 工作流程更简单！