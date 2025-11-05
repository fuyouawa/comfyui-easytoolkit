import { app } from "../../../scripts/app.js";
import { apiPost, apiSilent } from "./api_utils.js";
import { calculateAvailableSpace, drawImagePreview } from "./preview_utils.js";

app.registerExtension({
    name: "EasyToolkit.Image.ImagePreviewer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "ImagePreviewer") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Initialize UUID widget (hidden parameter)
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

            // Initialize access update timer
            this.accessUpdateTimer = null;
            this.previewImage = null;
            
            // Function to update access time - simplified with apiSilent
            const updateAccess = async () => {
                const currentUuid = this.widgets?.find(w => w.name === "uuid")?.value;
                if (!currentUuid) return;
                
                // Silent update, failure doesn't affect main flow
                await apiSilent("/image_previewer/update_access", {
                    method: "POST",
                    data: { uuid: currentUuid }
                });
            };
            
            // Start periodic access updates (every 30 seconds)
            const intervalMs = 30000;
            await updateAccess();
            this.accessUpdateTimer = setInterval(updateAccess, intervalMs);
            
            // Function to load and display image
            const loadPreviewImage = async () => {
                const currentUuid = this.widgets?.find(w => w.name === "uuid")?.value;
                if (!currentUuid) return;
                
                // Use silent mode since preview loading is optional
                const data = await apiSilent("/image_previewer/get_image", {
                    method: "POST",
                    data: { uuid: currentUuid }
                });
                
                if (data.success && data.base64) {
                    // Create image element
                    const img = new Image();
                    img.src = `data:${data.format};base64,${data.base64}`;
                    img.onload = () => {
                        this.previewImage = img;
                        this.setDirtyCanvas(true, true);
                    };
                }
            };
            
            // Store the load function for later use
            this.loadPreviewImage = loadPreviewImage;
        };

        // Override onExecuted to load image after execution
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (onExecuted) {
                onExecuted.apply(this, arguments);
            }
            
            // Load preview image after execution
            if (this.loadPreviewImage) {
                setTimeout(() => {
                    this.loadPreviewImage();
                }, 100);
            }
        };

        // Override onDrawForeground to draw the preview image on the node
        const onDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            if (onDrawForeground) {
                onDrawForeground.apply(this, arguments);
            }
            
            if (this.previewImage && this.previewImage.complete) {
                // Calculate available space using utility function
                const { margin, startY, availableWidth, availableHeight } = calculateAvailableSpace(this);
                
                // Draw image preview using utility function
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
            }
        };
        
        // Clean up timer when node is removed
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
            
            // Clear preview image
            this.previewImage = null;
            
            if (onRemoved) {
                return onRemoved.apply(this, arguments);
            }
        };
    },
});
