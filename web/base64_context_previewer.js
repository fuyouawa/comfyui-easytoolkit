import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "EasyToolkit.Misc.Base64ContextPreviewer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64ContextPreviewer") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Create key combo widget dynamically
            // This widget name matches the hidden parameter "key" in backend
            let keyWidget = this.addWidget("combo", "key", "NONE", (value) => {
                // The widget will automatically sync to backend's hidden parameter
                // because the name matches
            }, { values: ["NONE"] });

            // Add preview container widget (read-only text display)
            let previewWidget = this.addWidget("text", "preview_info", "等待预览...", () => {});
            previewWidget.disabled = true;

            // Function to refresh keys from backend
            const refreshKeys = async () => {
                try {
                    const response = await fetch("/base64_context_previewer/get_keys", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    if (data.success && data.keys) {
                        keyWidget.options.values = data.keys;
                        // Preserve current selection if still valid
                        if (!data.keys.includes(keyWidget.value)) {
                            keyWidget.value = data.keys[0] || "NONE";
                        }
                    }
                } catch (error) {
                    console.error("获取 keys 失败:", error);
                }
            };

            // Initial load of keys
            await refreshKeys();

            // Add preview button
            this.addWidget("button", "预览数据", null, async () => {
                try {
                    if (!keyWidget.value || keyWidget.value === "NONE") {
                        alert("请先选择一个有效的 key");
                        previewWidget.value = "未选择 key";
                        return;
                    }

                    previewWidget.value = "正在加载...";

                    const response = await fetch("/base64_context_previewer/get_data", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ "key": keyWidget.value }),
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    if (!data.success) {
                        alert(data.error);
                        previewWidget.value = `错误: ${data.error}`;
                        return;
                    }

                    // Update preview info
                    const fileInfo = `${data.filename}`;
                    previewWidget.value = fileInfo;

                    // Create preview dialog
                    this.showPreviewDialog(data);

                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "加载成功",
                        detail: `已加载 ${data.filename}`,
                        life: 3000
                    });
                } catch (error) {
                    console.error("预览数据失败:", error);
                    alert(`预览数据失败: ${error.message}`);
                    previewWidget.value = `错误: ${error.message}`;
                }
            });

            // Add refresh button to reload available keys
            this.addWidget("button", "刷新列表", null, async () => {
                try {
                    await refreshKeys();
                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "刷新成功",
                        detail: "键列表已刷新",
                        life: 3000
                    });
                } catch (error) {
                    console.error("刷新列表失败:", error);
                    alert(`刷新列表失败: ${error.message}`);
                }
            });
        };

        // Add preview dialog method to node prototype
        nodeType.prototype.showPreviewDialog = function(data) {
            const dialog = document.createElement("div");
            dialog.style.position = "fixed";
            dialog.style.top = "50%";
            dialog.style.left = "50%";
            dialog.style.transform = "translate(-50%, -50%)";
            dialog.style.backgroundColor = "#1e1e1e";
            dialog.style.border = "2px solid #444";
            dialog.style.borderRadius = "8px";
            dialog.style.padding = "20px";
            dialog.style.zIndex = "10000";
            dialog.style.maxWidth = "80vw";
            dialog.style.maxHeight = "80vh";
            dialog.style.overflow = "auto";
            dialog.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.5)";

            // Title bar
            const titleBar = document.createElement("div");
            titleBar.style.display = "flex";
            titleBar.style.justifyContent = "space-between";
            titleBar.style.alignItems = "center";
            titleBar.style.marginBottom = "15px";
            titleBar.style.paddingBottom = "10px";
            titleBar.style.borderBottom = "1px solid #444";

            const title = document.createElement("h3");
            title.textContent = `预览: ${data.filename}`;
            title.style.margin = "0";
            title.style.color = "#fff";
            title.style.fontSize = "18px";

            const closeButton = document.createElement("button");
            closeButton.textContent = "×";
            closeButton.style.fontSize = "24px";
            closeButton.style.border = "none";
            closeButton.style.background = "none";
            closeButton.style.color = "#fff";
            closeButton.style.cursor = "pointer";
            closeButton.style.padding = "0 8px";
            closeButton.onclick = () => {
                document.body.removeChild(overlay);
            };

            titleBar.appendChild(title);
            titleBar.appendChild(closeButton);
            dialog.appendChild(titleBar);

            // Content container
            const contentContainer = document.createElement("div");
            contentContainer.style.color = "#fff";
            contentContainer.style.minWidth = "400px";

            if (data.content_type === "image") {
                // Display image
                const img = document.createElement("img");
                img.src = `data:${data.format};base64,${data.base64}`;
                img.style.maxWidth = "100%";
                img.style.maxHeight = "70vh";
                img.style.objectFit = "contain";
                img.style.display = "block";
                img.style.margin = "0 auto";
                contentContainer.appendChild(img);
            } else if (data.content_type === "text") {
                // Display text
                let textContent = data.base64;
                
                // If it's base64 encoded text, try to decode it
                if (!data.format.startsWith("text/")) {
                    try {
                        textContent = atob(data.base64);
                    } catch (e) {
                        // If decode fails, show as-is
                        textContent = data.base64;
                    }
                }

                const textArea = document.createElement("textarea");
                textArea.value = textContent;
                textArea.style.width = "100%";
                textArea.style.minHeight = "300px";
                textArea.style.maxHeight = "60vh";
                textArea.style.backgroundColor = "#2d2d2d";
                textArea.style.color = "#d4d4d4";
                textArea.style.border = "1px solid #444";
                textArea.style.borderRadius = "4px";
                textArea.style.padding = "10px";
                textArea.style.fontFamily = "monospace";
                textArea.style.fontSize = "14px";
                textArea.readOnly = true;
                contentContainer.appendChild(textArea);
            } else {
                // Unknown type
                const message = document.createElement("p");
                message.textContent = `不支持的内容类型: ${data.content_type}`;
                message.style.color = "#ff6b6b";
                message.style.fontSize = "16px";
                contentContainer.appendChild(message);

                const info = document.createElement("p");
                info.textContent = `文件格式: ${data.format}\n后缀: ${data.suffix}`;
                info.style.whiteSpace = "pre-wrap";
                info.style.fontSize = "14px";
                info.style.marginTop = "10px";
                contentContainer.appendChild(info);
            }

            dialog.appendChild(contentContainer);

            // Overlay background
            const overlay = document.createElement("div");
            overlay.style.position = "fixed";
            overlay.style.top = "0";
            overlay.style.left = "0";
            overlay.style.width = "100%";
            overlay.style.height = "100%";
            overlay.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
            overlay.style.zIndex = "9999";
            overlay.onclick = (e) => {
                if (e.target === overlay) {
                    document.body.removeChild(overlay);
                }
            };

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
        };
    },
});

