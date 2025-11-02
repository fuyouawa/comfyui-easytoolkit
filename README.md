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

### 图像处理节点 (EasyToolkit/Image)

#### ImageBatchSelector - 图像批次选择器
**功能**: 从图像批次中选择指定索引的单张图像

**输入参数**:
- `images` (IMAGE): 输入图像批次
- `select` (INT): 要选择的图像索引 (0-1000)

**输出**:
- `image` (IMAGE): 选择出的单张图像

#### ImageEncryptor - 图像加密器
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

#### ImageBatchEncryptor - 图像批次加密器
**功能**: 对图像批次进行批量处理操作

**输入参数**:
- `image_batch` (IMAGE): 输入图像批次
- `operation` (下拉菜单): 处理操作类型 (同 ImageEncryptor)
- `enable` (BOOLEAN): 启用/禁用处理

**输出**:
- `image_batch` (IMAGE): 处理后的图像批次

#### ImageDownloader - 图像下载器
**功能**: 提供前端按钮来下载传入的图像，支持动态文件名模板

**输入参数**:
- `image` (IMAGE): 输入图像
- `file_name` (STRING): 文件名模板，支持以下变量：
  - `%date:yyyy-MM-dd%` - 日期 (2023-12-25)
  - `%date:hh-mm-ss%` - 时间 (14-30-45)
  - `%timestamp%` - 时间戳 (1703493045)
  - `%counter%` - 下载计数器 (自动递增)
  - `%random%` - 随机数 (1000-9999)

**输出**:
- `images` (IMAGE): 原始图像

**使用说明**:
1. 连接图像到节点
2. 设置文件名模板
3. 在 ComfyUI 界面中点击下载按钮下载图像

## 更新日志

### v1.0.0
- 初始版本发布

## 支持

如果在使用过程中遇到问题，请通过以下方式联系：
- 提交 GitHub Issue
- 查看项目文档

---

**ComfyUI EasyToolkit** - 让 ComfyUI 工作流程更简单！