import { app } from "../../../scripts/app.js";
import { apiPost, apiSilent } from "./api_utils.js";

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
                console.error("Failed to generate UUID:", error);
                alert(`Failed to generate UUID: ${error.message}`);
            }

            uuid_widget.disabled = true;

            // Initialize progress tracking
            this.uploadProgress = 0; // 0-100
            this.isUploading = false;
            this.uploadStatus = "Standby..."; // Status message

            this.addWidget("button", "Upload File", null, async () => {
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

                            // Prepare upload
                            this.uploadStatus = "Preparing upload...";
                            this.isUploading = true;
                            this.uploadProgress = 0;
                            app.canvas.setDirty(true);

                            try {
                                // Use chunked upload to avoid freezing with large files
                                await this.uploadFileInChunks(file, uuid_widget.value, file.name);
                                this.uploadStatus = "Upload complete!";
                                this.isUploading = false;
                                this.uploadProgress = 100;
                                app.canvas.setDirty(true);
                                app.extensionManager.toast.add({
                                    severity: "info",
                                    summary: "Upload successful",
                                    detail: `File ${file.name} uploaded`,
                                    life: 3000
                                });
                                // Reset progress after a delay
                                setTimeout(() => {
                                    this.uploadProgress = 0;
                                    this.uploadStatus = "Standby...";
                                    app.canvas.setDirty(true);
                                }, 2000);
                            } catch (error) {
                                console.error("Upload failed:", error);
                                this.uploadStatus = `Upload failed: ${error.message}`;
                                this.isUploading = false;
                                this.uploadProgress = 0;
                                app.canvas.setDirty(true);
                                alert(`Upload failed: ${error.message}`);
                            }
                        } catch (error) {
                            console.error("File selection handling failed:", error);
                            alert(`File selection handling failed: ${error.message}`);
                        }
                    };

                    input.click(); // Open file selection dialog
                } catch (error) {
                    console.error("Failed to create file selector:", error);
                    alert(`Failed to create file selector: ${error.message}`);
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

        // Clean up context data when node is removed
        const onRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function () {
            // Clear the context data - simplified with apiSilent
            const uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && uuid_widget.value) {
                apiSilent("/persistent_context/remove_key", {
                    method: "POST",
                    data: { key: uuid_widget.value }
                });
            }
            
            if (onRemoved) {
                return onRemoved.apply(this, arguments);
            }
        };
    },
});

// Add chunked upload method to node prototype
app.registerExtension({
    name: "EasyToolkit.Misc.Base64Uploader.Upload",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Uploader") return;

        nodeType.prototype.uploadFileInChunks = async function(file, uuid, filename) {
            try {
                const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
                const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

                // Initialize upload - simplified with apiPost
                this.uploadProgress = 0;
                this.uploadStatus = "Initializing upload...";
                app.canvas.setDirty(true);
                
                const initResult = await apiPost("/base64_cache_loader/init_upload", {
                    uuid: uuid,
                    filename: filename,
                    total_chunks: totalChunks,
                    file_size: file.size
                });

                if (!initResult.success) {
                    throw new Error(initResult.error || "Initialization failed");
                }

                // Upload file in chunks
                for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
                    const start = chunkIndex * CHUNK_SIZE;
                    const end = Math.min(start + CHUNK_SIZE, file.size);
                    const chunk = file.slice(start, end);

                    // Update progress
                    this.uploadProgress = Math.round(((chunkIndex + 1) / totalChunks) * 100);
                    this.uploadStatus = `Uploading... (${chunkIndex + 1}/${totalChunks})`;
                    app.canvas.setDirty(true);

                    // Give UI a chance to update
                    await new Promise(resolve => setTimeout(resolve, 0));

                    // Upload chunk with FormData
                    const formData = new FormData();
                    formData.append("uuid", uuid);
                    formData.append("chunk_index", chunkIndex.toString());
                    formData.append("chunk_data", chunk);

                    const result = await apiPost("/base64_cache_loader/upload_chunk", formData);

                    if (!result.success) {
                        throw new Error(result.error || `Upload chunk ${chunkIndex + 1} failed`);
                    }
                }

                // Finalize upload - simplified with apiPost
                this.uploadProgress = 100;
                this.uploadStatus = "Finalizing upload...";
                app.canvas.setDirty(true);
                
                const finalizeResult = await apiPost("/base64_cache_loader/finalize_upload", {
                    uuid: uuid
                });

                if (!finalizeResult.success) {
                    throw new Error(finalizeResult.error || "Finalization failed");
                }
            } catch (error) {
                console.error("Chunked upload failed:", error);
                throw error; // Re-throw error for outer handling
            }
        };
    },
});
