import { app } from "../../../scripts/app.js";
import { apiPost } from "./api_utils.js";
import { 
    decodeBase64Text, 
    calculateAvailableSpace, 
    calculateImagePreviewDimensions,
    drawImagePreview, 
    drawTextPreview,
    createPreviewDialog
} from "./preview_utils.js";

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

            // Function to load preview data
            const loadPreview = async () => {
                try {
                    if (!keyWidget.value || keyWidget.value === "NONE") {
                        previewWidget.value = "No key selected";
                        return;
                    }

                    previewWidget.value = "Loading...";

                    const data = await apiPost("/base64_context_previewer/get_data", {
                        key: keyWidget.value
                    });
                    
                    if (!data.success) {
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
                    previewWidget.value = `Error: ${error.message}`;
                }
            };

            // Auto-load preview on initialization if in Builtin mode
            if (modeWidget.value === "Builtin" && keyWidget.value && keyWidget.value !== "NONE") {
                await loadPreview();
            }

            // Add preview button
            this.addWidget("button", "Preview Data", null, async () => {
                if (!keyWidget.value || keyWidget.value === "NONE") {
                    alert("Please select a valid key first");
                    return;
                }
                await loadPreview();
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
                    this.setDirtyCanvas(true, true);
                };
                img.src = `data:${data.format};base64,${data.base64}`;
            } else if (data.content_type === "text") {
                // Decode text using helper function
                this.previewText = decodeBase64Text(data.base64, data.format);
                this.previewImage = null;
                this.setDirtyCanvas(true, true);
            } else {
                this.previewImage = null;
                this.previewText = null;
                this.setDirtyCanvas(true, true);
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

            // Calculate available space for preview using helper function
            // Use extra spacing (30px) to prevent overlap with buttons
            const { margin, startY, availableWidth, availableHeight } = calculateAvailableSpace(this, 15, 30);

            if (this.previewImage && this.previewImage.complete) {
                // Draw image preview with auto-resize
                const { height: drawnHeight } = drawImagePreview(
                    ctx, 
                    this.previewImage, 
                    margin, 
                    startY, 
                    availableWidth, 
                    availableHeight
                );
                
                // Auto-resize node to fit image if needed
                const minHeight = startY + drawnHeight + margin;
                if (this.size[1] < minHeight) {
                    this.size[1] = minHeight;
                }
            } else if (this.previewText) {
                // Draw text preview with minimum height
                const textPreviewHeight = Math.max(200, Math.min(availableHeight, 400));
                drawTextPreview(
                    ctx, 
                    this.previewText, 
                    margin, 
                    startY, 
                    availableWidth, 
                    textPreviewHeight
                );
                
                // Auto-resize node to fit text preview if needed
                const minHeight = startY + textPreviewHeight + margin;
                if (this.size[1] < minHeight) {
                    this.size[1] = minHeight;
                }
            }
        };

        // Add preview dialog method to node prototype
        nodeType.prototype.showPreviewDialog = function(data) {
            // Create dialog using utility function
            const { contentContainer, overlay } = createPreviewDialog(
                `Preview: ${data.filename}`,
                null
            );

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
                // Display text using helper function to decode
                const textContent = decodeBase64Text(data.base64, data.format);

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

            document.body.appendChild(overlay);
        };
    },
});
