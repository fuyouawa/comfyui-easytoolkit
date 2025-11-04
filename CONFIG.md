# Configuration Guide / 配置指南

## 配置文件位置 / Configuration File Location

配置文件位于项目根目录：`config.yaml`

The configuration file is located at the project root: `config.yaml`

## 配置选项 / Configuration Options

### Persistent Context Cache Settings

持久化上下文缓存设置 - 用于配置数据缓存和自动保存行为。

#### `timeout` (默认: 300.0 秒)

Context 过期时间。超过这个时间没有被访问的 context 会被清理。

- 单位：秒
- 默认值：300.0（5分钟）
- 示例：`timeout: 600.0`（10分钟）

Time before a context is considered expired. Contexts not accessed within this time will be cleaned up.

#### `check_interval` (默认: 60.0 秒)

检查过期 context 的时间间隔。系统会定期检查并清理过期的 context。

- 单位：秒
- 默认值：60.0（1分钟）
- 示例：`check_interval: 120.0`（2分钟）

Interval between cleanup checks for expired contexts.

#### `auto_save_interval` (默认: 30.0 秒)

自动保存到磁盘的时间间隔。系统会定期将数据保存到磁盘。

- 单位：秒
- 默认值：30.0（30秒）
- 设置为 0 可以禁用定期自动保存（仅在创建和清理时保存）
- 示例：`auto_save_interval: 60.0`（1分钟）

Interval between automatic saves to disk. Set to 0 to disable automatic periodic saves (only saves on create/cleanup).

## 配置示例 / Example Configuration

```yaml
# comfyui-easytoolkit Configuration

# Persistent Context Cache Settings
persistent_context:
  # Context 过期时间（秒）
  timeout: 300.0
  
  # 清理检查间隔（秒）
  check_interval: 60.0
  
  # 自动保存间隔（秒），设置为 0 禁用定期自动保存
  auto_save_interval: 30.0
```

## 性能优化建议 / Performance Optimization Tips

### 短期项目 / Short-term Projects

如果你的工作流程持续时间较短（几分钟内），可以减少自动保存频率：

```yaml
persistent_context:
  timeout: 180.0  # 3分钟
  check_interval: 30.0  # 30秒
  auto_save_interval: 60.0  # 1分钟
```

### 长期项目 / Long-term Projects

如果你的工作流程需要长时间运行，可以增加超时时间并保持较频繁的自动保存：

```yaml
persistent_context:
  timeout: 1800.0  # 30分钟
  check_interval: 300.0  # 5分钟
  auto_save_interval: 30.0  # 30秒（频繁保存防止数据丢失）
```

### 禁用自动保存 / Disable Auto-save

如果你想完全手动控制保存时机，可以禁用自动保存：

```yaml
persistent_context:
  timeout: 300.0
  check_interval: 60.0
  auto_save_interval: 0  # 禁用自动保存
```

然后在代码中手动调用：

```python
from utils.persistent_context import save_persistent_context

# 在需要保存时调用
save_persistent_context()
```

## 数据存储位置 / Data Storage Location

持久化数据保存在：`ComfyUI\user\default\comfyui-easytoolkit\persistent_context.pkl`

系统会自动创建必要的目录。

Persistent data is saved at: `ComfyUI\user\default\comfyui-easytoolkit\persistent_context.pkl`

The system will automatically create necessary directories.

