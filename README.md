# ComfyUI EasyToolkit

## 📋 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [安装](#安装)
- [节点说明](#节点说明)
  - [AI 工具节点](#ai-工具节点)
  - [配置管理节点](#配置管理节点)
  - [编码/解码节点](#编码解码节点)
  - [图像处理节点](#图像处理节点)
  - [调试工具节点](#调试工具节点)
  - [算法节点](#算法节点)
- [许可证](#许可证)

## 简介

ComfyUI EasyToolkit 是一个功能丰富的 ComfyUI 扩展包，旨在简化工作流程中的常见操作。该工具包提供了六大类节点：配置管理、调试工具、AI 工具、算法计算、编码解码和图像处理，帮助用户更高效地完成各种任务。

## 功能特性

🤖 **AI 工具**
- AI 提示词助手（支持 DeepSeek、OpenAI、Anthropic等）
- 提示词扩写、翻译、优化
- 多种预设 Agent
- 灵活的配置系统

⚙️ **配置管理**
- AI 服务配置管理器（支持添加、编辑、删除 AI 服务）
- AI Agent 配置管理器（支持自定义 Agent 预设）
- 动态配置界面，实时更新
- 配置持久化存储

🔐 **编码/解码**
- 图像的 Base64 编码/解码（支持单图像和图像批次）
- 图像 Tensor 的 Base64 编码/解码（支持单图像和图像批次）
- 支持视频的 Base64 编码（GIF、WebM、MP4等格式）
- Base64 噪点图像编码/解码（将数据隐藏在像素值中）
- Base64 前缀修改器（自动添加/移除数据 URL 前缀）

🖼️ **图像处理**
- 图像批次选择器
- 图像加密/解密（支持单图像和图像批次）（支持反色、XOR加密）

🪲 **调试工具**
- 对话框节点（支持信息、成功、警告、错误、确认对话框）
- 通知节点（支持 ComfyUI 和系统通知）
- 交互式调试，捕获用户响应

🧮 **算法工具**
- 帧数计算器
- 文件后缀格式化

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

### AI 工具节点

#### AI Prompt Assistant（AI 提示词助手）

使用 AI 服务对提示词进行扩写、翻译和优化处理。

**分类：** `EasyToolkit/AI`

**输入：**
- `original_prompt`（字符串，多行）：原始提示词输入
- `ai_service`（选择）：AI 服务提供商
- `ai_agent`（选择）：AI Agent 预设
- `processed_prompt`（字符串，多行，可选）：AI 处理结果显示

**输出：**
- `original_prompt`（字符串）：原始提示词
- `processed_prompt`（字符串）：AI 处理后的提示词

**功能：**
- 🚀 一键 AI 处理按钮
- 支持多个 AI 服务提供商
- 多种预设 Agent（扩写、翻译、优化、风格转换）
- 实时提示词传输，可以将一个AIPromptAssistant节点的输出连接到另一个AIPromptAssistant节点的输入，实现链式处理（比如先扩写后翻译）
- 实时配置更新

### 配置管理节点

#### AI Services Config（AI 服务配置管理器）

管理 AI 服务的配置，支持添加、编辑、删除 AI 服务。

**分类：** `EasyToolkit/Manager`

**功能：**
- 动态配置界面，实时更新
- 支持添加新的 AI 服务（DeepSeek、OpenAI、Anthropic 等）
- 编辑现有服务配置（API Key、Base URL、模型等）
- 删除不需要的服务
- 设置默认 AI 服务
- 配置持久化存储
- 重置配置到默认状态

**配置字段：**
- `Service ID`：服务唯一标识符
- `Service Label`：服务显示名称
- `Base URL`：API 基础地址
- `API Key`：API 密钥
- `Model`：默认模型名称
- `Timeout`：请求超时时间（秒）

#### AI Agents Config（AI Agent 配置管理器）

管理 AI Agent 的配置，支持自定义 Agent 预设。

**分类：** `EasyToolkit/Manager`

**功能：**
- 动态配置界面，实时更新
- 支持添加新的 AI Agent
- 编辑现有 Agent 配置
- 删除不需要的 Agent
- 设置默认 AI Agent
- 配置持久化存储
- 重置配置到默认状态

**配置字段：**
- `Agent ID`：Agent 唯一标识符
- `Agent Label`：Agent 显示名称
- `Summary`：Agent 功能描述

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

#### Image Base64 Previewer（Base64 图像预览器）

在前端预览 Base64 编码的图像数据。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64`（字符串）：Base64 编码的图像数据
- `format`（选择）：图像格式（PNG、JPEG、WebP、BMP、TIFF）

**输出：**
- `base64`（字符串）：Base64 编码的图像数据（原样输出）

#### Image Batch Base64 Previewer（批量 Base64 图像预览器）

在前端预览批量 Base64 编码的图像数据，支持动画播放。

**分类：** `EasyToolkit/Encoding`

**输入：**
- `base64_batch`（字符串）：换行符分隔的 Base64 字符串列表
- `format`（选择）：图像格式（PNG、JPEG、WebP、BMP、TIFF）
- `fps`（浮点数）：帧率（FPS），用于动画播放，范围 1.0-120.0

**输出：**
- `base64_batch`（字符串）：Base64 编码的图像数据列表（原样输出）

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

### 调试工具节点

#### Dialog Box（对话框节点）

在流程执行期间显示对话框，支持多种类型并捕获用户响应。

**分类：** `EasyToolkit/Debug`

**输入：**
- `dialog_type`（选择）：对话框类型（info、success、warn、error、confirm）
- `message`（字符串，多行）：对话框消息内容

**输出：**
- `message`（字符串）：用户响应消息

**功能：**
- 支持 5 种对话框类型：信息、成功、警告、错误、确认
- 确认对话框支持用户交互，返回确认或取消结果
- 非阻塞式显示，不影响流程执行
- 捕获用户响应用于后续流程控制

#### Toast Box（通知节点）

在流程执行期间显示通知消息，支持 ComfyUI 和系统通知。

**分类：** `EasyToolkit/Debug`

**输入：**
- `type`（选择）：通知类型（info、success、warn、error）
- `mode`（选择）：通知模式（comfyui、system）
- `message`（字符串，多行）：通知消息内容
- `duration`（整数）：显示持续时间（毫秒）

**输出：**
- `message`（字符串）：通知消息

**功能：**
- 支持 4 种通知类型：信息、成功、警告、错误
- 支持两种显示模式：ComfyUI 内置通知、系统原生通知
- 可自定义显示持续时间
- 非阻塞式显示，不影响流程执行

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

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 链接

- **GitHub 仓库：** [https://github.com/fuyouawa/comfyui-easytoolkit](https://github.com/fuyouawa/comfyui-easytoolkit)
- **ComfyUI 官网：** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

---

如果觉得这个项目对你有帮助，请给个 ⭐ Star 支持一下！
