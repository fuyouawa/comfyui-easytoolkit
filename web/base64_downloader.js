import { app } from "../../../scripts/app.js";
import { apiGet, apiPost, apiSilent } from "./api_utils.js";

function downloadBase64(b64, basename, format) {
    try {
        let suffix = format.split("/").pop();
        let blob = null;
        if (format == "text/plain") {
            suffix = "txt";
            blob = new Blob([b64], { type: format });
        }
        else {
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

            // Initialize access update timer
            this.accessUpdateTimer = null;
            
            // Function to update access time - simplified with apiSilent
            const updateAccess = async () => {
                const currentUuid = this.widgets?.find(w => w.name === "uuid")?.value;
                if (!currentUuid) return;
                
                // Silent update, failure doesn't affect main flow
                await apiSilent("/base64_cache_downloader/update_access", {
                    method: "POST",
                    data: { uuid: currentUuid }
                });
            };
            
            // Get configuration from backend - simplified with apiGet
            try {
                const configData = await apiGet("/base64_cache_downloader/config");
                
                if (configData.success && configData.access_update_interval > 0) {
                    const intervalMs = configData.access_update_interval * 1000;
                    
                    // Immediately update access time on initialization
                    await updateAccess();
                    
                    // Start periodic access updates
                    this.accessUpdateTimer = setInterval(updateAccess, intervalMs);
                }
            } catch (error) {
                console.error("Failed to get config for access updates:", error);
            }

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

        // Clean up timer and context data when node is removed
        const onRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function () {
            // Clear the timer
            if (this.accessUpdateTimer) {
                clearInterval(this.accessUpdateTimer);
                this.accessUpdateTimer = null;
            }
            
            // Clear the context data - simplified with apiSilent
            const uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && uuid_widget.value) {
                apiSilent("/context/remove_key", {
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
