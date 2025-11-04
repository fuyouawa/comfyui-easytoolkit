import base64
import os
import tempfile
import time
import asyncio
from aiohttp import web
from server import PromptServer
from ... import register_node
from ...utils.persistent_context import get_persistent_context, has_persistent_context

routes = PromptServer.instance.routes

# 存储分块上传的临时数据
_chunk_uploads = {}

async def cleanup_expired_uploads():
    """清理超过1小时未完成的分块上传"""
    current_time = time.time()
    expired_uuids = []

    for uuid, upload_info in _chunk_uploads.items():
        # 如果超过1小时未完成，清理
        if current_time - upload_info.get("start_time", current_time) > 3600:
            expired_uuids.append(uuid)

    for uuid in expired_uuids:
        del _chunk_uploads[uuid]

    if expired_uuids:
        print(f"Cleaned up {len(expired_uuids)} expired chunk uploads")

# 启动定时清理任务
async def start_cleanup_task():
    while True:
        await asyncio.sleep(300)  # 每5分钟清理一次
        await cleanup_expired_uploads()

# 在应用启动时启动清理任务
asyncio.create_task(start_cleanup_task())

@register_node
class Base64CacheLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
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
        last_data_cache = get_persistent_context(uuid).get_value()
        if not last_data_cache:
            raise Exception("There is no base64 data at all.")

        base64 = last_data_cache["base64"]
        basename = filename.split(".")[0]
        suffix = filename.split(".")[-1]
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

    # 初始化分块上传
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

    # 检查上传是否已初始化
    if uuid not in _chunk_uploads:
        return web.json_response({"success": False, "error": "Upload not initialized."})

    upload_info = _chunk_uploads[uuid]
    chunk_index = int(chunk_index)

    # 读取分块数据 - 使用FileField的file属性
    chunk_bytes = chunk_data.file.read()

    # 存储分块
    upload_info["chunks"][chunk_index] = chunk_bytes
    upload_info["received_chunks"] += 1

    return web.json_response({"success": True, "received_chunks": upload_info["received_chunks"]})


@routes.post("/base64_cache_loader/finalize_upload")
async def handle_finalize_upload(request):
    data = await request.json()
    uuid = data.get("uuid", None)
    if not uuid:
        return web.json_response({"success": False, "error": "uuid is required."})

    # 检查上传是否已初始化
    if uuid not in _chunk_uploads:
        return web.json_response({"success": False, "error": "Upload not initialized."})

    upload_info = _chunk_uploads[uuid]

    # 检查是否所有分块都已接收
    if upload_info["received_chunks"] != upload_info["total_chunks"]:
        return web.json_response({"success": False, "error": f"Not all chunks received. Expected {upload_info['total_chunks']}, got {upload_info['received_chunks']}."})

    # 合并所有分块
    file_data = b""
    for i in range(upload_info["total_chunks"]):
        if i not in upload_info["chunks"]:
            return web.json_response({"success": False, "error": f"Missing chunk {i}."})
        file_data += upload_info["chunks"][i]

    # 转换为Base64
    base64_data = base64.b64encode(file_data).decode('utf-8')

    # 保存到持久化上下文
    get_persistent_context(uuid).set_value({
        "base64": base64_data,
        "filename": upload_info["filename"],
        "format": "application/octet-stream"  # 默认格式，实际使用时可能需要检测
    })

    # 清理临时数据
    del _chunk_uploads[uuid]

    return web.json_response({"success": True})