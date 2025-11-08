# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComfyUI EasyToolkit is a comprehensive ComfyUI extension package that provides nodes for algorithm calculations, Base64 encoding/decoding, image processing, and workflow utilities to streamline ComfyUI workflows.

## Architecture

### Node Categories
The toolkit is organized into several categories of nodes:

- **Algorithm Nodes** (`EasyToolkit/Algorithm`): Frame calculator, file suffix formatter
- **Encoding Nodes** (`EasyToolkit/Encoding`): Base64 encoding/decoding for images, image batches, and video
- **Image Processing Nodes** (`EasyToolkit/Image`): Batch selector, encryptor/decryptor, previewer
- **Miscellaneous Tools** (`EasyToolkit/Misc`): Base64 uploader, downloader, context loader
- **Manager Nodes** (`EasyToolkit/Manager`): Configuration management

### Core Components

1. **Node Registration System** (`__init__.py`): Uses custom decorators `@register_node` and `@register_route` for clean node and API registration
2. **Configuration Management** (`utils/config.py`): Singleton config loader with override support via `config.yaml` and `config.override.yaml`
3. **Persistent Context System** (`utils/context/`): Disk-based caching system with automatic cleanup and size management
4. **Utility Modules** (`utils/`): Shared functionality for image processing, video encoding, and format handling

## Development Setup

### Installation
```bash
# Clone and install dependencies
cd ComfyUI/custom_nodes
git clone https://github.com/fuyouawa/comfyui-easytoolkit.git
cd comfyui-easytoolkit
pip install -r requirements.txt
```

### Dependencies
- `numpy`, `imageio-ffmpeg`, `pyyaml`, `Pillow`, `opencv-python`

## Configuration System

The toolkit uses a hierarchical configuration system:

- `config.yaml`: Base configuration with default settings
- `config.override.yaml`: User-specific overrides (created via EasyToolkitConfigManager)
- Configuration is loaded via singleton `Config` class with deep merge capabilities

### Key Configuration Sections

```yaml
persistent_context:
  lazy_initialization: true    # Load cache on first API call
  auto_save: false             # Experimental auto-save feature
  cache_directory: 'input'     # 'input', 'output', or 'temp'
  max_cache_size_mb: 100       # Maximum cache size
  old_data_threshold_hours: 24 # Data older than this is cleaned

base64_uploader:
  max_upload_file_size_mb: 100 # Maximum upload file size
```

## Node Development Patterns

### Creating New Nodes
1. Use the `@register_node` decorator from the root `__init__.py`
2. Define `INPUT_TYPES()`, `RETURN_TYPES`, `RETURN_NAMES`, `FUNCTION`, and `CATEGORY` class attributes
3. Implement the `run()` method with parameters matching input types

### Example Node Structure
```python
from ... import register_node

@register_node
class MyNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_param": ("STRING", {"default": "value"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Category"

    def run(self, input_param):
        return (processed_value,)
```

### API Route Registration
Use `@register_route` decorator for adding custom API endpoints:
```python
from ... import register_route

@register_route("/my_endpoint", method="POST")
async def my_handler(request):
    return web.json_response({"success": True})
```

## Persistent Context System

The toolkit includes a sophisticated persistent context caching system:

- **Storage**: Contexts are saved as individual files in `{cache_directory}/comfyui-easytoolkit/persistent_context/`
- **Management**: Automatic cleanup based on size limits and access time
- **Usage**: Used by nodes like Base64 uploader/downloader and image previewer for data persistence

### Context Cache Key Features
- Lazy initialization to avoid startup overhead
- Size-based cleanup with configurable thresholds
- Support for different storage directories (input, output, temp)
- Automatic cleanup of old/unused data

## Testing and Development

### Adding New Nodes
1. Create node file in appropriate category directory under `nodes/`
2. Import and register in the category's `__init__.py`
3. Test in ComfyUI to ensure proper integration

### Configuration Changes
- Use the EasyToolkitConfigManager node for visual configuration editing
- Changes are saved to `config.override.yaml` to preserve base configuration
- Configuration reloads automatically when changes are saved

## File Structure

```
comfyui-easytoolkit/
├── nodes/                    # All node implementations
│   ├── algorithm/           # Frame calculator, file suffix formatter
│   ├── encoding/           # Base64 encoding/decoding nodes
│   ├── image/              # Image processing nodes
│   ├── misc/               # Uploader, downloader, context loader
│   ├── manager/            # Configuration management
│   └── video/              # Video encoding nodes
├── utils/                  # Shared utility modules
│   ├── config.py          # Configuration management
│   ├── image.py           # Image processing utilities
│   ├── video.py           # Video encoding utilities
│   ├── format.py          # Format handling utilities
│   └── context/           # Persistent context system
├── config.yaml            # Base configuration
├── config.override.yaml   # User overrides (auto-generated)
└── pyproject.toml         # Package metadata
```

## Common Development Tasks

### Adding New Configuration Options
1. Update default values in `utils/config.py` Config class
2. Add documentation to `config.yaml` with comments
3. Update EasyToolkitConfigManager if needed for UI support

### Extending Persistent Context
- Use `utils.context.persistent_context.PersistentContext` class
- Integrate with `utils.context.context_cache.ContextCache` for management
- Follow existing patterns in nodes like Base64 uploader

### Creating New Utility Functions
- Add to appropriate utility module in `utils/`
- Ensure compatibility with ComfyUI's image tensor format
- Use existing patterns for Base64 encoding/decoding and image processing

## Code Documentation Guidelines

### Commenting Rules

When adding or modifying code comments, follow these guidelines:

1. **Keep comments concise and focused** - Avoid verbose explanations of obvious code
2. **Remove unnecessary comments** - Don't describe:
   - `INPUT_TYPES()` return values (the return statement is self-explanatory)
   - `__init__` functions (unless they have complex initialization logic)
   - ComfyUI built-in fields (`RETURN_TYPES`, `RETURN_NAMES`, `FUNCTION`, etc.)
   - `run()` function return values (the return statement is clear)

3. **Focus on the "why", not the "what"** - Explain complex logic or non-obvious decisions
4. **Use docstrings for public functions** - Keep them brief, 1-3 lines maximum
5. **Preserve configuration documentation** - `config.yaml` comments are important for user understanding
