import { app } from "../../../scripts/app.js";
import { apiPost } from "../api_utils.js";
import { checkAndRegenerateUUID } from "../node_utils.js";

function downloadBase64(b64, basename, format) {
    try {
        // Format to suffix mapping, consistent with format.py's file_format_to_suffix
        const formatMapping = {
            "image/png": "png",
            "image/jpeg": "jpeg",
            "image/gif": "gif",
            "image/webp": "webp",
            "video/mp4": "mp4",
            "video/webm": "webm",
            "text/plain": "txt",
            "application/octet-stream": "bin"
        };
        
        // Get suffix from mapping, fallback to splitting format or default to "bin"
        let suffix = formatMapping[format.toLowerCase()];
        if (!suffix) {
            // Fallback: try to extract suffix from format string (e.g., "image/png" -> "png")
            suffix = format.split("/").pop() || "bin";
        }
        
        let blob = null;
        if (format === "text/plain") {
            // For plain text, treat b64 as raw text content
            blob = new Blob([b64], { type: format });
        }
        else {
            // For all other formats, decode base64 to binary
            const byteCharacters = atob(b64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            blob = new Blob([byteArray], { type: format });
        }

        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = basename + "." + suffix;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
    } catch (error) {
        console.error("Download failed:", error);
        alert(`Download failed: ${error.message}`);
        throw error;
    }
}

app.registerExtension({
    name: "EasyToolkit.Misc.Base64Downloader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Downloader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            let uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && (!uuid_widget.value || uuid_widget.value === "")) {
                uuid_widget.value = crypto.randomUUID();
            }

            uuid_widget.disabled = true;

            this.addWidget("button", "Download", null, async () => {
                try {
                    uuid_widget = this.widgets?.find(w => w.name === "uuid");
                    let basename_widget = this.widgets?.find(w => w.name === "basename");
                    let format_widget = this.widgets?.find(w => w.name === "format");
                    if (!uuid_widget || !basename_widget || !format_widget) {
                        alert("Cannot find uuid or basename or format widget.");
                        return;
                    }

                    // Simplified download request with apiPost
                    const data = await apiPost("/base64_cache_downloader/download", {
                        uuid: uuid_widget.value,
                        basename: basename_widget.computedDisabled ? null : basename_widget.value,
                        format: format_widget.computedDisabled ? null : format_widget.value
                    });
                    
                    if (data.success) {
                        downloadBase64(data.base64, data.basename, data.format);
                        app.extensionManager.toast.add({
                            severity: "info",
                            summary: "Download successful",
                            detail: `File ${data.basename} downloaded`,
                            life: 3000
                        });
                    } else {
                        alert(data.error);
                    }
                } catch (error) {
                    console.error("Download failed:", error);
                    alert(`Download failed: ${error.message}`);
                }
            });
        };

        // Override onConfigure to check for duplicate UUID
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function(info) {
            if (onConfigure) {
                onConfigure.apply(this, arguments);
            }
            
            // Check for duplicate UUID and regenerate if necessary
            checkAndRegenerateUUID(this, app);
        };

    },
});
