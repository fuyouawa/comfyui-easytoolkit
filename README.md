# ComfyUI EasyToolkit

## 📋 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [安装](#安装)
- [节点说明](#节点说明)
  - [算法节点](#算法节点)
  - [编码/解码节点](#编码解码节点)
  - [图像处理节点](#图像处理节点)
  - [杂项工具节点](#杂项工具节点)
- [配置说明](#配置说明)
- [许可证](#许可证)

## 简介

ComfyUI EasyToolkit 是一个功能丰富的 ComfyUI 扩展包，旨在简化工作流程中的常见操作。该工具包提供了四大类节点：算法计算、编码解码、图像处理和杂项工具，帮助用户更高效地完成各种任务。

## 功能特性

✨ **算法工具**
- 帧数计算器
- 文件后缀格式化

🔄 **编码/解码**
- 图像的 Base64 编码/解码（支持单图像和图像批次）
- 图像 Tensor 的 Base64 编码/解码（支持单图像和图像批次）
- 支持视频的 Base64 编码（GIF、WebM、MP4等格式）

🖼️ **图像处理**
- 图像批次选择器
- 图像加密/解密（支持单图像和图像批次）（支持反色、XOR加密）
- 图像预览器（支持单图像和图像批次）

🛠️ **杂项工具**
- Base64 文件上传器（支持大文件分块上传）
- Base64 文件下载器
- Base64 上下文加载器（支持预览数据）

## 安装

1. 打开终端并进入 ComfyUI 的 `custom_nodes` 目录：
   ```bash
   cd ComfyUI/custom_nodes
   ```

2. 克隆本仓库：
   ```bash
   git clone https://github.com/fuyouawa/comfyui-easytoolkit.git
   ```

3. 进入项目目录并安装依赖：
   ```bash
   cd comfyui-easytoolkit
   pip install -r requirements.txt
   ```

4. 重启 ComfyUI

## 节点说明

### 算法节点

#### Frame Calculator（帧数计算器）

计算视频或动画的总帧数。

**分类：** `EasyToolkit/Algorithm`

**输入：**
- `duration`（浮点数）：持续时间（秒），默认 5.0
- `frame_rate`（浮点数）：帧率（FPS），默认 16.0
- `extra_frames`（整数）：额外添加的帧数，默认 1

**输出：**
- `total_frames`（整数）：计算得出的总帧数

**计算公式：** `total_frames = duration × frame_rate + extra_frames`

#### File Suffix Formatter（文件后缀格式化器）

将文件后缀名转换为标准格式。

**分类：** `EasyToolkit/Algorithm`

**输入：**
- `suffix`（字符串）：文件后缀名，例如 "png"、"jpg"

**输出：**
- `format`（字符串）：标准化的格式，例如 "image/png"

### 编码/解码节点

#### Image Base64 Encoder（图像 Base64 编码器）

将单个图像编码为 Base64 字符串。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `image`（图像）：要编码的图像
- `format`（选择）：输出格式（支持 PNG、JPEG、WebP、BMP、TIFF）

**输出：**
- `base64`（字符串）：Base64 编码的图像数据
- `suffix`（字符串）：文件后缀名

#### Image Base64 Decoder（图像 Base64 解码器）

将 Base64 字符串解码为图像。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64`（字符串）：Base64 编码的图像数据

**输出：**
- `image`（图像）：解码后的图像

#### Image Batch Base64 Encoder（批量图像 Base64 编码器）

将批量图像编码为 Base64 字符串列表。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `image_batch`（图像批次）：要编码的图像批次
- `format`（选择）：输出格式

**输出：**
- `base64_list`（字符串）：换行符分隔的 Base64 字符串列表
- `count`（整数）：图像数量
- `suffix`（字符串）：文件后缀名

#### Image Batch Base64 Decoder（批量图像 Base64 解码器）

将 Base64 字符串列表解码为图像批次。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64_list`（字符串）：换行符分隔的 Base64 字符串列表

**输出：**
- `images`（图像批次）：解码后的图像批次

#### Image Tensor Base64 Encoder（图像 Tensor Base64 编码器）

将图像的 Tensor 数据直接编码为 Base64（保留原始张量信息）。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `image`（图像）：要编码的图像

**输出：**
- `base64`（字符串）：Base64 编码的 Tensor 数据

#### Image Tensor Base64 Decoder（图像 Tensor Base64 解码器）

将 Base64 编码的 Tensor 数据解码为图像。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64`（字符串）：Base64 编码的 Tensor 数据

**输出：**
- `image`（图像）：解码后的图像

#### Image Batch Tensor Base64 Encoder（批量图像 Tensor Base64 编码器）

将批量图像的 Tensor 数据编码为 Base64。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `images`（图像批次）：要编码的图像批次

**输出：**
- `base64`（字符串）：Base64 编码的 Tensor 数据

#### Image Batch Tensor Base64 Decoder（批量图像 Tensor Base64 解码器）

将 Base64 编码的批量 Tensor 数据解码为图像批次。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64`（字符串）：Base64 编码的 Tensor 数据

**输出：**
- `images`（图像批次）：解码后的图像批次

#### Video Base64 Encoder（视频 Base64 编码器）

将图像批次编码为视频格式的 Base64 字符串。

**分类：** `EasyToolkit/Video`

**输入：**
- `image_batch`（图像批次）：要编码为视频的图像序列
- `frame_rate`（整数）：帧率（FPS），默认 8
- `loop_count`（整数）：循环次数，0 表示无限循环
- `video_format`（选择）：视频格式（GIF、WebM、MP4 等）
- `pingpong`（布尔）：是否启用乒乓效果（来回播放）
- `save_metadata`（布尔）：是否保存元数据

**输出：**
- `base64`（字符串）：Base64 编码的视频数据
- `suffix`（字符串）：文件后缀名

**支持的格式：**
- 动画图像：`image/gif`、`image/webp`
- 视频格式：`video/webm`、`video/h264-mp4`、`video/h265-mp4`（需要 FFmpeg）

### 图像处理节点

#### Image Batch Selector（图像批次选择器）

从图像批次中选择单个图像。

**分类：** `EasyToolkit/Image`

**输入：**
- `image_batch`（图像批次）：图像批次
- `select`（整数）：要选择的图像索引（从 0 开始）

**输出：**
- `image`（图像）：选中的图像

#### Image Encryptor（图像加密器）

对图像进行加密或反色处理。

**分类：** `EasyToolkit/Image`

**输入：**
- `image`（图像）：要处理的图像
- `operation`（选择）：操作类型
  - `invert`：反色
  - `xor-16`：16 位 XOR 加密
  - `xor-32`：32 位 XOR 加密
  - `xor-64`：64 位 XOR 加密
  - `xor-128`：128 位 XOR 加密
- `enable`（布尔）：是否启用处理，默认 True

**输出：**
- `image`（图像）：处理后的图像

**说明：** XOR 加密是可逆的，使用相同的操作可以解密。

#### Image Batch Encryptor（批量图像加密器）

对批量图像进行加密或反色处理。

**分类：** `EasyToolkit/Image`

**输入：**
- `images`（图像批次）：要处理的图像批次
- `operation`（选择）：操作类型（同上）
- `enable`（布尔）：是否启用处理

**输出：**
- `images`（图像批次）：处理后的图像批次

#### Image Previewer（图像预览器）

在工作流中预览图像，并将图像数据缓存到持久化上下文中。

**分类：** `EasyToolkit/Image`

**输入：**
- `image`（图像）：要预览的图像
- `format`（选择）：预览格式（JPEG、PNG 等）
- `uuid`（字符串）：唯一标识符，用于缓存

**输出：**
- `image`（图像）：原始图像（透传）

**功能：** 在节点上显示图像预览，同时将图像数据保存到持久化缓存中供其他节点使用。

#### Image Batch Previewer（批量图像预览器）

预览批量图像，并缓存数据。

**分类：** `EasyToolkit/Image`

**输入：**
- `images`（图像批次）：要预览的图像批次
- `format`（选择）：预览格式
- `uuid`（字符串）：唯一标识符

**输出：**
- `images`（图像批次）：原始图像批次（透传）

### 杂项工具节点

#### Base64 Uploader（Base64 上传器）

上传文件并将其转换为 Base64 格式。

**分类：** `EasyToolkit/Misc`

**输入：**
- `filename`（字符串）：文件名（可选）
- `uuid`（字符串）：唯一标识符

**输出：**
- `base64`（字符串）：Base64 编码的文件数据
- `basename`（字符串）：不含后缀的文件名
- `suffix`（字符串）：文件后缀名

**功能：**
- 支持大文件分块上传
- 可配置最大文件大小限制（默认 100 MB）
- 自动清理过期的上传数据（1小时未完成）

#### Base64 Downloader（Base64 下载器）

下载 Base64 编码的文件。

**分类：** `EasyToolkit/Misc`

**输入：**
- `base64`（字符串）：Base64 编码的数据
- `basename`（字符串）：文件名（不含后缀），支持格式化变量
- `format`（选择）：文件格式
- `uuid`（字符串）：唯一标识符

**输出：**
- `base64`（字符串）：Base64 数据（透传）
- `uuid`（字符串）：UUID（透传）

**文件名格式化变量：**
- `%date:yyyy-MM-dd%`：日期（年-月-日）
- `%date:hh-mm-ss%`：时间（时-分-秒）
- `%counter%`：递增计数器
- 示例：`image_%date:yyyy-MM-dd%_%date:hh-mm-ss%` → `image_2024-03-15_14-30-45`

**功能：** 点击节点上的下载按钮即可下载文件到本地。

#### Base64 Context Loader（Base64 上下文加载器）

从持久化上下文中加载 Base64 数据。

**分类：** `EasyToolkit/Misc`

**输入：**
- `key`（字符串，隐藏）：上下文键名
- `mode`（选择，隐藏）：加载模式（内置/对话框）

**输出：**
- `base64`（字符串）：Base64 数据
- `basename`（字符串）：文件名（不含后缀）
- `suffix`（字符串）：文件后缀名

**功能：**
- 在节点界面中选择已缓存的数据
- 支持预览缓存的文件内容
- 可查看所有可用的上下文键

## 配置说明

项目配置文件位于 `config.yaml`，包含以下配置项：

### 持久化上下文缓存设置

```yaml
persistent_context:
  # 启用延迟初始化（默认：true）
  # true：首次 API 调用时才开始加载缓存
  # false：模块导入时立即加载缓存
  lazy_initialization: true
  
  # 启用自动保存（默认：true）
  auto_save: true
  
  # 缓存目录：'input'、'output' 或 'temp'
  # 每个上下文将保存为单独的文件在：
  # <目录>/comfyui-easytoolkit/persistent_context/
  cache_directory: 'input'
  
  # 最大缓存总大小（MB），默认 100
  # 超出时将清理旧数据
  max_cache_size_mb: 100
  
  # 旧数据阈值（小时），默认 24
  # 超过此时间未访问的数据视为"旧数据"
  old_data_threshold_hours: 24
  
  # 绝对最大缓存大小（MB），默认 200
  # 超出时强制清理，即使未达到旧数据阈值
  # 设为 0 禁用强制清理
  absolute_max_cache_size_mb: 200
  
  # 单个上下文最大大小（MB），默认 50
  # 大于此大小的上下文不会保存到磁盘
  # 设为 0 禁用大小限制（不推荐）
  max_context_size_mb: 50
  
  # 最大键长度，默认 256
  # 超过此长度的键将被拒绝
  # 设为 0 禁用键长度限制（不推荐）
  max_key_length: 256
```

### Base64 上传器设置

```yaml
base64_uploader:
  # 最大上传文件大小（MB），默认 100
  # 大于此大小的文件将被拒绝
  # 设为 0 禁用文件大小限制
  max_upload_file_size_mb: 100
```

## 依赖项

- `numpy`：数值计算
- `imageio-ffmpeg`：视频编码（用于 FFmpeg 视频格式）
- `pyyaml`：配置文件解析

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 链接

- **GitHub 仓库：** [https://github.com/fuyouawa/comfyui-easytoolkit](https://github.com/fuyouawa/comfyui-easytoolkit)
- **ComfyUI 官网：** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

---

如果觉得这个项目对你有帮助，请给个 ⭐ Star 支持一下！
