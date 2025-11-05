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

            // Initialize progress tracking
            this.uploadProgress = 0; // 0-100
            this.isUploading = false;
            this.uploadStatus = "待命中..."; // Status message

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
                            if (!uuid_widget || !filename_widget) {
                                alert("Cannot find uuid or filename widget.");
                                return;
                            }
                            filename_widget.value = file.name;

                            // 准备上传
                            this.uploadStatus = "正在准备上传...";
                            this.isUploading = true;
                            this.uploadProgress = 0;
                            app.canvas.setDirty(true);

                            try {
                                // 使用分块上传避免大文件卡死
                                await this.uploadFileInChunks(file, uuid_widget.value, file.name);
                                this.uploadStatus = "上传完成！";
                                this.isUploading = false;
                                this.uploadProgress = 100;
                                app.canvas.setDirty(true);
                                app.extensionManager.toast.add({
                                    severity: "info",
                                    summary: "上传成功",
                                    detail: `文件 ${file.name} 已上传`,
                                    life: 3000
                                });
                                // Reset progress after a delay
                                setTimeout(() => {
                                    this.uploadProgress = 0;
                                    this.uploadStatus = "待命中...";
                                    app.canvas.setDirty(true);
                                }, 2000);
                            } catch (error) {
                                console.error("Upload failed:", error);
                                this.uploadStatus = `上传失败: ${error.message}`;
                                this.isUploading = false;
                                this.uploadProgress = 0;
                                app.canvas.setDirty(true);
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

            // Draw progress bar
            const onDrawForeground = this.onDrawForeground;
            this.onDrawForeground = function(ctx) {
                if (onDrawForeground) {
                    onDrawForeground.apply(this, arguments);
                }

                if (this.isUploading && this.uploadProgress > 0) {
                    const margin = 15;
                    const barHeight = 20;
                    const statusTextHeight = 16;
                    const spacing = 8;
                    const totalHeight = statusTextHeight + spacing + barHeight;
                    const barY = this.size[1] - totalHeight - margin;
                    const statusY = barY - spacing;
                    const barWidth = this.size[0] - margin * 2;

                    // Draw status text
                    ctx.fillStyle = "#cccccc";
                    ctx.font = "12px Arial";
                    ctx.textAlign = "left";
                    ctx.textBaseline = "bottom";
                    ctx.fillText(this.uploadStatus || "", margin, statusY);

                    // Draw background
                    ctx.fillStyle = "#2a2a2a";
                    ctx.fillRect(margin, barY, barWidth, barHeight);

                    // Draw progress
                    const progressWidth = (barWidth * this.uploadProgress) / 100;
                    const gradient = ctx.createLinearGradient(margin, barY, margin + progressWidth, barY);
                    gradient.addColorStop(0, "#4a9eff");
                    gradient.addColorStop(1, "#2d7dd2");
                    ctx.fillStyle = gradient;
                    ctx.fillRect(margin, barY, progressWidth, barHeight);

                    // Draw border
                    ctx.strokeStyle = "#555";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(margin, barY, barWidth, barHeight);

                    // Draw percentage text
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "12px Arial";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(`${Math.round(this.uploadProgress)}%`, margin + barWidth / 2, barY + barHeight / 2);
                }
            };
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

        nodeType.prototype.uploadFileInChunks = async function(file, uuid, filename) {
            try {
                const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
                const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

                // 先初始化上传
                this.uploadProgress = 0;
                this.uploadStatus = "正在初始化上传...";
                app.canvas.setDirty(true);
                
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

                    // Update progress
                    this.uploadProgress = Math.round(((chunkIndex + 1) / totalChunks) * 100);
                    this.uploadStatus = `上传中... (${chunkIndex + 1}/${totalChunks})`;
                    app.canvas.setDirty(true);

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
                this.uploadProgress = 100;
                this.uploadStatus = "正在完成上传...";
                app.canvas.setDirty(true);
                
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
