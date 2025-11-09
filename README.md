# ComfyUI EasyToolkit

## 📋 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [安装](#安装)
- [节点说明](#节点说明)
  - [算法节点](#算法节点)
  - [编码/解码节点](#编码解码节点)
  - [图像处理节点](#图像处理节点)
  - [管理工具节点](#管理工具节点)
- [许可证](#许可证)

## 简介

ComfyUI EasyToolkit 是一个功能丰富的 ComfyUI 扩展包，旨在简化工作流程中的常见操作。该工具包提供了三大类节点：算法计算、编码解码和图像处理，帮助用户更高效地完成各种任务。

## 功能特性

✨ **算法工具**
- 帧数计算器
- 文件后缀格式化

🔄 **编码/解码**
- 图像的 Base64 编码/解码（支持单图像和图像批次）
- 图像 Tensor 的 Base64 编码/解码（支持单图像和图像批次）
- 支持视频的 Base64 编码（GIF、WebM、MP4等格式）
- Base64 噪点图像编码/解码（将数据隐藏在像素值中）
- Base64 前缀修改器（自动添加/移除数据 URL 前缀）

🖼️ **图像处理**
- 图像批次选择器
- 图像加密/解密（支持单图像和图像批次）（支持反色、XOR加密）

⚙️ **管理工具**
- 可视化配置节点（EasyToolkitConfig）
- 支持配置覆盖机制
- 实时配置加载和保存

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

#### Base64 Noise Encoder（Base64 噪点编码器）

将 Base64 字符串编码为噪点图像，将数据隐藏在像素值中。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64`（字符串，多行）：要编码的 Base64 字符串
- `compression`（选择）：压缩算法（none、gzip、zlib、bz2、lzma），默认 gzip
- `width`（整数，可选）：图像宽度（0 = 自动计算）
- `height`（整数，可选）：图像高度（0 = 自动计算）

**输出：**
- `noise_image`（图像）：编码后的噪点图像
- `compression`（字符串）：使用的压缩算法

#### Base64 Noise Decoder（Base64 噪点解码器）

从噪点图像中解码 Base64 字符串。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `noise_image`（图像）：包含编码数据的噪点图像
- `compression`（选择）：压缩算法（none、gzip、zlib、bz2、lzma），默认 gzip

**输出：**
- `base64`（字符串）：解码后的 Base64 字符串

#### Base64 Prefix Modifier（Base64 前缀修改器）

修改或添加数据 URL 前缀到 Base64 字符串。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64`（字符串）：Base64 字符串
- `format`（选择）：资源格式（image/png、image/jpeg、video/mp4 等）

**输出：**
- `base64`（字符串）：带有正确前缀的 Base64 字符串

**功能：**
- 自动移除现有的数据 URL 前缀
- 根据指定格式添加正确的 `data:format;base64,` 前缀
- 支持所有常见资源格式

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

### 管理工具节点

#### EasyToolkitConfig（可视化配置编辑器）

可视化地编辑和管理 EasyToolkit 的 YAML 配置文件，无需手动编辑配置文件。

**分类：** `EasyToolkit/Manager`

**输入：**
- `config_yaml`（字符串，多行文本框）：YAML 格式的配置内容

**功能：**
- **自动加载配置**：节点创建时自动从 `config.override.yaml` 或 `config.yaml` 加载当前配置
- **实时编辑**：在文本框中编辑 YAML 配置，保留注释和格式
- **Save YAML按钮**：保存配置到 `config.override.yaml`（覆盖配置文件）
- **Restore YAML按钮**：删除覆盖配置文件，恢复到默认配置

**工作流：**
1. 添加 EasyToolkitConfigManager 节点到工作流
2. 节点自动加载当前配置到文本框
3. 在文本框中编辑配置
4. 点击 **Save YAML** 保存并应用修改
5. 如需恢复默认配置，点击 **Restore YAML**

**配置继承机制：**

配置系统采用类似继承的覆盖机制：
- `config.yaml`：基础配置文件（默认设置）
- `config.override.yaml`：覆盖配置文件（用户自定义设置）
- 最终配置 = 基础配置 + 覆盖配置

这样你可以在不修改原始配置文件的情况下自定义设置，便于版本控制和更新。使用 EasyToolkitConfigManager 节点可以轻松管理这些配置。

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 链接

- **GitHub 仓库：** [https://github.com/fuyouawa/comfyui-easytoolkit](https://github.com/fuyouawa/comfyui-easytoolkit)
- **ComfyUI 官网：** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

---

如果觉得这个项目对你有帮助，请给个 ⭐ Star 支持一下！
