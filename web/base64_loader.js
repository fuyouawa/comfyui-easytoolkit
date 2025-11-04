import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "EasyToolkit.Misc.Base64Uploader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Uploader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            let uuid_widget = this.widgets?.find(w => w.name === "uuid");
            try {
                if (uuid_widget && (!uuid_widget.value || uuid_widget.value === "")) {
                    uuid_widget.value = crypto.randomUUID();
                }
            } catch (error) {
                console.error("生成UUID失败:", error);
                alert(`生成UUID失败: ${error.message}`);
            }

            uuid_widget.disabled = true;

            let progressWidget = this.addWidget("text", "upload_progress", "正在准备上传...", () => {});
            progressWidget.disabled = true;
            progressWidget.value = "待命中...";

            // Initialize access update timer
            this.accessUpdateTimer = null;
            
            // Function to update access time
            const updateAccess = async () => {
                try {
                    const currentUuid = this.widgets?.find(w => w.name === "uuid")?.value;
                    if (!currentUuid) return;
                    
                    const response = await fetch("/base64_cache_loader/update_access", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ "uuid": currentUuid }),
                    });
                    
                    // Silently update, only log errors
                    if (!response.ok) {
                        console.warn("Failed to update access time");
                    }
                } catch (error) {
                    console.warn("Access update error:", error);
                }
            };
            
            // Get configuration from backend
            try {
                const configResponse = await fetch("/base64_cache_loader/config");
                if (configResponse.ok) {
                    const configData = await configResponse.json();
                    if (configData.success && configData.access_update_interval > 0) {
                        const intervalMs = configData.access_update_interval * 1000;
                        
                        // Immediately update access time on initialization
                        await updateAccess();
                        
                        // Start periodic access updates
                        this.accessUpdateTimer = setInterval(updateAccess, intervalMs);
                    }
                }
            } catch (error) {
                console.error("Failed to get config for access updates:", error);
            }

            this.addWidget("button", "选择文件上传", null, async () => {
                try {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.accept = "*/*";
                    input.style.display = "none";

                    input.onchange = async (event) => {
                        try {
                            const file = event.target.files[0];
                            if (!file) return;

                            uuid_widget = this.widgets?.find(w => w.name === "uuid");
                            let filename_widget = this.widgets?.find(w => w.name === "filename");
                            progressWidget = this.widgets?.find(w => w.name === "upload_progress");
                            if (!uuid_widget || !filename_widget || !progressWidget) {
                                alert("Cannot find uuid or filename or progress widget.");
                                return;
                            }
                            filename_widget.value = file.name;

                            // 查找或创建进度显示
                            progressWidget.value = "正在准备上传...";

                            try {
                                // 使用分块上传避免大文件卡死
                                await this.uploadFileInChunks(file, uuid_widget.value, file.name, progressWidget);
                                progressWidget.value = "上传完成！";
                                app.extensionManager.toast.add({
                                    severity: "info",
                                    summary: "上传成功",
                                    detail: `文件 ${file.name} 已上传`,
                                    life: 3000
                                });
                            } catch (error) {
                                console.error("Upload failed:", error);
                                progressWidget.value = `上传失败: ${error.message}`;
                                alert(`上传失败: ${error.message}`);
                            }
                        } catch (error) {
                            console.error("文件选择处理失败:", error);
                            alert(`文件选择处理失败: ${error.message}`);
                        }
                    };

                    input.click(); // 打开文件选择对话框
                } catch (error) {
                    console.error("创建文件选择器失败:", error);
                    alert(`创建文件选择器失败: ${error.message}`);
                }
            });

            this.addWidget("button", "删除缓存", null, async () => {
                try {
                    uuid_widget = this.widgets?.find(w => w.name === "uuid");
                    const response = await fetch("/base64_cache_loader/clear", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ "uuid": uuid_widget.value }),
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    if (data.success) {
                        app.extensionManager.toast.add({
                            severity: "info",
                            summary: "删除成功",
                            detail: "缓存已清除",
                            life: 3000
                        });
                    } else {
                        alert(data.error);
                    }
                } catch (error) {
                    console.error("删除缓存失败:", error);
                    alert(`删除缓存失败: ${error.message}`);
                }
            });

            this.addWidget("button", "重新生成UUID", null, async () => {
                try {
                    uuid_widget = this.widgets?.find(w => w.name === "uuid");
                    uuid_widget.value = crypto.randomUUID();
                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "生成成功",
                        detail: "新的UUID已生成",
                        life: 3000
                    });
                } catch (error) {
                    console.error("生成UUID失败:", error);
                    alert(`生成UUID失败: ${error.message}`);
                }
            });

            this.addWidget("button", "复制UUID", null, async () => {
                try {
                    uuid_widget = this.widgets?.find(w => w.name === "uuid");
                    if (!uuid_widget || !uuid_widget.value) {
                        alert("UUID不存在");
                        return;
                    }
                    await navigator.clipboard.writeText(uuid_widget.value);
                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "复制成功",
                        detail: "UUID已复制到剪切板",
                        life: 3000
                    });
                } catch (error) {
                    console.error("复制UUID失败:", error);
                    alert(`复制UUID失败: ${error.message}`);
                }
            });
        };

        // Clean up timer and context data when node is removed
        const onRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function () {
            // Clear the timer
            if (this.accessUpdateTimer) {
                clearInterval(this.accessUpdateTimer);
                this.accessUpdateTimer = null;
            }
            
            // Clear the context data
            const uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && uuid_widget.value) {
                fetch("/base64_cache_loader/clear", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ "uuid": uuid_widget.value }),
                }).catch(error => {
                    console.warn("Failed to clear context on node removal:", error);
                });
            }
            
            if (onRemoved) {
                return onRemoved.apply(this, arguments);
            }
        };
    },
});

// 添加分块上传方法到节点原型
app.registerExtension({
    name: "EasyToolkit.Misc.Base64Uploader.Upload",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Uploader") return;

        nodeType.prototype.uploadFileInChunks = async function(file, uuid, filename, progressWidget) {
            try {
                const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
                const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

                // 先初始化上传
                progressWidget.value = "正在初始化上传...";
                const initResponse = await fetch("/base64_cache_loader/init_upload", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        "uuid": uuid,
                        "filename": filename,
                        "total_chunks": totalChunks,
                        "file_size": file.size
                    }),
                });

                if (!initResponse.ok) {
                    throw new Error(`HTTP error! status: ${initResponse.status}`);
                }

                const initResult = await initResponse.json();
                if (!initResult.success) {
                    throw new Error(initResult.error || "Initialization failed");
                }

                // 分块上传文件
                for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
                    const start = chunkIndex * CHUNK_SIZE;
                    const end = Math.min(start + CHUNK_SIZE, file.size);
                    const chunk = file.slice(start, end);

                    progressWidget.value = `上传中... ${Math.round(((chunkIndex + 1) / totalChunks) * 100)}% (${chunkIndex + 1}/${totalChunks})`;

                    // 给UI一个更新的机会
                    await new Promise(resolve => setTimeout(resolve, 0));

                    const formData = new FormData();
                    formData.append("uuid", uuid);
                    formData.append("chunk_index", chunkIndex.toString());
                    formData.append("chunk_data", chunk);

                    const response = await fetch("/base64_cache_loader/upload_chunk", {
                        method: "POST",
                        body: formData,
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    if (!result.success) {
                        throw new Error(result.error || `Upload chunk ${chunkIndex + 1} failed`);
                    }
                }

                // 完成上传
                progressWidget.value = "正在完成上传...";
                const finalizeResponse = await fetch("/base64_cache_loader/finalize_upload", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        "uuid": uuid
                    }),
                });

                if (!finalizeResponse.ok) {
                    throw new Error(`HTTP error! status: ${finalizeResponse.status}`);
                }

                const finalizeResult = await finalizeResponse.json();
                if (!finalizeResult.success) {
                    throw new Error(finalizeResult.error || "Finalization failed");
                }
            } catch (error) {
                console.error("分块上传失败:", error);
                throw error; // 重新抛出错误以便外层处理
            }
        };
    },
});
