import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "EasyToolkit.Misc.Base64Uploader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Uploader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            let uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && (!uuid_widget.value || uuid_widget.value === "")) {
                uuid_widget.value = crypto.randomUUID();
            }

            uuid_widget.disabled = true;

            let progressWidget = this.addWidget("text", "upload_progress", "正在准备上传...", () => {});
            progressWidget.disabled = true;
            progressWidget.value = "待命中...";

            this.addWidget("button", "选择文件上传", null, async () => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = "*/*";
                input.style.display = "none";

                input.onchange = async (event) => {
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
                    } catch (error) {
                        console.error("Upload failed:", error);
                        progressWidget.value = `上传失败: ${error.message}`;
                        alert(`Update failed: ${error.message}`);
                    }
                };

                input.click(); // 打开文件选择对话框
            });

            this.addWidget("button", "重新生成UUID", null, async () => {
                uuid_widget = this.widgets?.find(w => w.name === "uuid");
                uuid_widget.value = crypto.randomUUID();
            });
        };
    },
});

// 添加分块上传方法到节点原型
app.registerExtension({
    name: "EasyToolkit.Misc.Base64Uploader.Upload",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Uploader") return;

        nodeType.prototype.uploadFileInChunks = async function(file, uuid, filename, progressWidget) {
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

                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || `Update chunk ${chunkIndex + 1} failed`);
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

            const finalizeResult = await finalizeResponse.json();
            if (!finalizeResult.success) {
                throw new Error(finalizeResult.error || "Finalization failed");
            }
        };
    },
});
