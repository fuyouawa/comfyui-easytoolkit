import base64
import time
import asyncio
from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.context import get_persistent_context, has_persistent_context, update_persistent_context
from ...utils.config import get_config
from .base64_context import Base64Context

routes = PromptServer.instance.routes

# Store temporary data for chunked uploads
_chunk_uploads = {}

async def cleanup_expired_uploads():
    """Clean up chunked uploads that have been inactive for over 1 hour"""
    current_time = time.time()
    expired_uuids = []

    for uuid, upload_info in _chunk_uploads.items():
        # If inactive for over 1 hour, clean up
        if current_time - upload_info.get("start_time", current_time) > 3600:
            expired_uuids.append(uuid)

    for uuid in expired_uuids:
        del _chunk_uploads[uuid]

    if expired_uuids:
        print(f"Cleaned up {len(expired_uuids)} expired chunk uploads")

# Start periodic cleanup task
async def start_cleanup_task():
    while True:
        await asyncio.sleep(300)  # Clean up every 5 minutes
        await cleanup_expired_uploads()

# Start cleanup task when application launches
asyncio.create_task(start_cleanup_task())

@register_node
class Base64Uploader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "filename": ("STRING", {
                    "default": "",
                }),
                "uuid": ("STRING", {
                    "default": "",
                }),
            },
        }
    

    RETURN_TYPES = ("STRING","STRING","STRING",)
    RETURN_NAMES = ("base64","basename","suffix")
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Misc"
    OUTPUT_NODE = True

    def run(self, filename: str, uuid):
        context = get_persistent_context(uuid).get_value()
        if not context or not isinstance(context, Base64Context):
            raise Exception("There is no base64 data at all.")

        base64 = context.get_base64()
        basename = context.get_basename()
        suffix = context.get_suffix()
        return {"result": (base64, basename, suffix,)}

@routes.post("/base64_cache_loader/init_upload")
async def handle_init_upload(request):
    data = await request.json()
    uuid = data.get("uuid", None)
    if not uuid:
        return web.json_response({"success": False, "error": "uuid is required."})

    filename = data.get("filename", None)
    if not filename:
        return web.json_response({"success": False, "error": "filename is required."})

    total_chunks = data.get("total_chunks", None)
    if total_chunks is None:
        return web.json_response({"success": False, "error": "total_chunks is required."})

    file_size = data.get("file_size", None)
    if file_size is None:
        return web.json_response({"success": False, "error": "file_size is required."})

    # Initialize chunked upload
    _chunk_uploads[uuid] = {
        "filename": filename,
        "total_chunks": total_chunks,
        "file_size": file_size,
        "received_chunks": 0,
        "chunks": {},
        "start_time": time.time()
    }

    return web.json_response({"success": True})


@routes.post("/base64_cache_loader/upload_chunk")
async def handle_upload_chunk(request):
    data = await request.post()
    uuid = data.get("uuid", None)
    if not uuid:
        return web.json_response({"success": False, "error": "uuid is required."})

    chunk_index = data.get("chunk_index", None)
    if chunk_index is None:
        return web.json_response({"success": False, "error": "chunk_index is required."})

    chunk_data = data.get("chunk_data", None)
    if not chunk_data:
        return web.json_response({"success": False, "error": "chunk_data is required."})

    # Check if upload has been initialized
    if uuid not in _chunk_uploads:
        return web.json_response({"success": False, "error": "Upload not initialized."})

    upload_info = _chunk_uploads[uuid]
    chunk_index = int(chunk_index)

    # Read chunk data - using FileField's file attribute
    chunk_bytes = chunk_data.file.read()

    # Store chunk
    upload_info["chunks"][chunk_index] = chunk_bytes
    upload_info["received_chunks"] += 1

    return web.json_response({"success": True, "received_chunks": upload_info["received_chunks"]})


@routes.post("/base64_cache_loader/finalize_upload")
async def handle_finalize_upload(request):
    data = await request.json()
    uuid = data.get("uuid", None)
    if not uuid:
        return web.json_response({"success": False, "error": "uuid is required."})

    # Check if upload has been initialized
    if uuid not in _chunk_uploads:
        return web.json_response({"success": False, "error": "Upload not initialized."})

    upload_info = _chunk_uploads[uuid]

    # Check if all chunks have been received
    if upload_info["received_chunks"] != upload_info["total_chunks"]:
        return web.json_response({"success": False, "error": f"Not all chunks received. Expected {upload_info['total_chunks']}, got {upload_info['received_chunks']}."})

    # Merge all chunks
    file_data = b""
    for i in range(upload_info["total_chunks"]):
        if i not in upload_info["chunks"]:
            return web.json_response({"success": False, "error": f"Missing chunk {i}."})
        file_data += upload_info["chunks"][i]

    # Convert to Base64
    base64_data = base64.b64encode(file_data).decode('utf-8')

    # Save to persistent context using Base64Context
    context = Base64Context(base64_data, upload_info["filename"])
    get_persistent_context(uuid).set_value(context)

    # Clean up temporary data
    del _chunk_uploads[uuid]

    return web.json_response({"success": True})


@routes.post("/base64_cache_loader/update_access")
async def handle_update_access(request):
    """Update the access time for a context to prevent it from being cleaned up"""
    data = await request.json()
    uuid = data.get("uuid", "")

    if not uuid:
        return web.json_response({"success": False, "error": "UUID is required."})

    if not has_persistent_context(uuid):
        return web.json_response({"success": False, "error": "Context not found."})
    
    # Update access time
    update_persistent_context(uuid)
    return web.json_response({"success": True})


@routes.get("/base64_cache_loader/config")
async def handle_get_config(request):
    """Get the access update interval configuration"""
    config = get_config().get_persistent_context_config()
    access_update_interval = config.get('access_update_interval', 60.0)
    return web.json_response({
        "success": True,
        "access_update_interval": access_update_interval
    })