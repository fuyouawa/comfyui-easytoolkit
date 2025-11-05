import { app } from "../../../scripts/app.js";
import { apiPost } from "./api_utils.js";

app.registerExtension({
    name: "EasyToolkit.Misc.Base64ContextLoader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64ContextLoader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Add mode selector
            let modeWidget = this.addWidget("combo", "mode", "Builtin", (value) => {
                // Update preview visibility based on mode
                if (value === "Builtin" && this.previewData) {
                    this.updateBuiltinPreview(this.previewData);
                } else if (value === "Dialog") {
                    // Hide builtin preview
                    this.previewImage = null;
                    this.previewText = null;
                    this.setSize(this.computeSize());
                }
            }, { values: ["Builtin", "Dialog"] });

            // Create key combo widget dynamically
            // This widget name matches the hidden parameter "key" in backend
            let keyWidget = this.addWidget("combo", "key", "NONE", (value) => {
                // The widget will automatically sync to backend's hidden parameter
                // because the name matches
            }, { values: ["NONE"] });

            // Add preview container widget (read-only text display)
            let previewWidget = this.addWidget("text", "preview_info", "Waiting for preview...", () => {});
            previewWidget.disabled = true;

            // Store preview data
            this.previewData = null;
            this.previewImage = null;
            this.previewText = null;

            // Function to refresh keys from backend
            const refreshKeys = async () => {
                try {
                    const data = await apiPost("/base64_context_previewer/get_keys");
                    
                    if (data.success && data.keys) {
                        keyWidget.options.values = data.keys;
                        // Preserve current selection if still valid
                        if (!data.keys.includes(keyWidget.value)) {
                            keyWidget.value = data.keys[0] || "NONE";
                        }
                    }
                } catch (error) {
                    console.error("Failed to get keys:", error);
                }
            };

            // Initial load of keys
            await refreshKeys();

            // Add preview button
            this.addWidget("button", "Preview Data", null, async () => {
                try {
                    if (!keyWidget.value || keyWidget.value === "NONE") {
                        alert("Please select a valid key first");
                        previewWidget.value = "No key selected";
                        return;
                    }

                    previewWidget.value = "Loading...";

                    const data = await apiPost("/base64_context_previewer/get_data", {
                        key: keyWidget.value
                    });
                    
                    if (!data.success) {
                        alert(data.error);
                        previewWidget.value = `Error: ${data.error}`;
                        return;
                    }

                    // Update preview info
                    const fileInfo = `${data.filename}`;
                    previewWidget.value = fileInfo;

                    // Store preview data
                    this.previewData = data;

                    // Show preview based on mode
                    if (modeWidget.value === "Builtin") {
                        this.updateBuiltinPreview(data);
                    } else {
                        this.showPreviewDialog(data);
                    }

                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "Load successful",
                        detail: `Loaded ${data.filename}`,
                        life: 3000
                    });
                } catch (error) {
                    console.error("Preview data failed:", error);
                    alert(`Preview data failed: ${error.message}`);
                    previewWidget.value = `Error: ${error.message}`;
                }
            });

            // Add refresh button to reload available keys
            this.addWidget("button", "Refresh Key List", null, async () => {
                try {
                    await refreshKeys();
                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "Refresh successful",
                        detail: "Key list refreshed",
                        life: 3000
                    });
                } catch (error) {
                    console.error("Failed to refresh list:", error);
                    alert(`Failed to refresh list: ${error.message}`);
                }
            });
        };

        // Add builtin preview update method
        nodeType.prototype.updateBuiltinPreview = function(data) {
            if (data.content_type === "image") {
                // Load image
                const img = new Image();
                img.onload = () => {
                    this.previewImage = img;
                    this.previewText = null;
                    this.setSize(this.computeSize());
                };
                img.src = `data:${data.format};base64,${data.base64}`;
            } else if (data.content_type === "text") {
                // Decode text if needed
                let textContent = data.base64;
                if (!data.format.startsWith("text/")) {
                    try {
                        textContent = atob(data.base64);
                    } catch (e) {
                        textContent = data.base64;
                    }
                }
                this.previewText = textContent;
                this.previewImage = null;
                this.setSize(this.computeSize());
            } else {
                this.previewImage = null;
                this.previewText = null;
                this.setSize(this.computeSize());
            }
        };

        // Override onDrawForeground to render preview on node
        const onDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            if (onDrawForeground) {
                onDrawForeground.apply(this, arguments);
            }

            // Only draw builtin preview if mode is "Builtin"
            const modeWidget = this.widgets?.find(w => w.name === "mode");
            if (!modeWidget || modeWidget.value !== "Builtin") {
                return;
            }

            if (this.previewImage) {
                // Draw image preview
                const [w, h] = this.size;
                const previewHeight = 300;
                const previewY = h - previewHeight - 10;
                
                // Calculate image dimensions to fit in preview area
                const maxWidth = w - 20;
                const maxHeight = previewHeight;
                let imgWidth = this.previewImage.width;
                let imgHeight = this.previewImage.height;
                
                const aspectRatio = imgWidth / imgHeight;
                if (imgWidth > maxWidth) {
                    imgWidth = maxWidth;
                    imgHeight = imgWidth / aspectRatio;
                }
                if (imgHeight > maxHeight) {
                    imgHeight = maxHeight;
                    imgWidth = imgHeight * aspectRatio;
                }
                
                const imgX = (w - imgWidth) / 2;
                const imgY = previewY + (maxHeight - imgHeight) / 2;
                
                ctx.save();
                ctx.drawImage(this.previewImage, imgX, imgY, imgWidth, imgHeight);
                ctx.restore();
            } else if (this.previewText) {
                // Draw text preview
                const [w, h] = this.size;
                const previewHeight = 200;
                const previewY = h - previewHeight - 10;
                
                ctx.save();
                ctx.fillStyle = "#2d2d2d";
                ctx.fillRect(10, previewY, w - 20, previewHeight);
                
                ctx.strokeStyle = "#444";
                ctx.strokeRect(10, previewY, w - 20, previewHeight);
                
                ctx.fillStyle = "#d4d4d4";
                ctx.font = "12px monospace";
                
                // Split text into lines and draw
                const lines = this.previewText.split('\n');
                const lineHeight = 14;
                const maxLines = Math.floor((previewHeight - 20) / lineHeight);
                const visibleLines = lines.slice(0, maxLines);
                
                visibleLines.forEach((line, idx) => {
                    // Truncate long lines
                    const maxChars = Math.floor((w - 40) / 7);
                    const truncatedLine = line.length > maxChars ? line.substring(0, maxChars) + "..." : line;
                    ctx.fillText(truncatedLine, 15, previewY + 15 + idx * lineHeight);
                });
                
                if (lines.length > maxLines) {
                    ctx.fillText("...", 15, previewY + 15 + maxLines * lineHeight);
                }
                
                ctx.restore();
            }
        };

        // Override computeSize to account for preview area
        const computeSize = nodeType.prototype.computeSize;
        nodeType.prototype.computeSize = function(out) {
            const size = computeSize ? computeSize.apply(this, arguments) : [this.size[0], this.size[1]];
            
            const modeWidget = this.widgets?.find(w => w.name === "mode");
            if (modeWidget && modeWidget.value === "Builtin") {
                let requiredExtraHeight = 0;
                let requiredMinWidth = size[0];
                
                if (this.previewImage) {
                    requiredExtraHeight = 310; // Space for image preview
                    // Calculate minimum width based on image aspect ratio
                    const imgAspect = this.previewImage.width / this.previewImage.height;
                    const previewHeight = 300;
                    requiredMinWidth = Math.max(requiredMinWidth, Math.min(this.previewImage.width, previewHeight * imgAspect) + 40);
                } else if (this.previewText) {
                    requiredExtraHeight = 210; // Space for text preview
                    requiredMinWidth = Math.max(requiredMinWidth, 300); // Minimum width for text preview
                }
                
                // Calculate minimum required height (base height + preview area)
                const minRequiredHeight = size[1] + requiredExtraHeight;
                
                // Allow user to resize, but enforce minimum dimensions
                // Use the larger of: computed minimum size or user's manual resize
                size[0] = Math.max(size[0], requiredMinWidth);
                size[1] = Math.max(size[1], minRequiredHeight);
            }
            
            return size;
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
            title.textContent = `Preview: ${data.filename}`;
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
                message.textContent = `Unsupported content type: ${data.content_type}`;
                message.style.color = "#ff6b6b";
                message.style.fontSize = "16px";
                contentContainer.appendChild(message);

                const info = document.createElement("p");
                info.textContent = `File format: ${data.format}\nExtension: ${data.suffix}`;
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
