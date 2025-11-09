# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComfyUI EasyToolkit is a comprehensive ComfyUI extension package that provides nodes for algorithm calculations, Base64 encoding/decoding, image processing, and workflow utilities to streamline ComfyUI workflows.

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
