import { app } from "../../../scripts/app.js";
import {
    calculateAvailableSpace,
    drawImagePreview
} from "../preview_utils.js";

/**
 * Extension for ImageBase64Previewer node
 * Displays base64 encoded images directly on the node during workflow execution
 */
app.registerExtension({
    name: "EasyToolkit.ImageBase64Previewer",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "ImageBase64Previewer") {
            // Add custom node behavior
            const originalOnExecuted = nodeType.prototype.onExecuted;

            this.previewImage = null;

            nodeType.prototype.onExecuted = function(output) {
                // Call original method if it exists
                if (originalOnExecuted) {
                    originalOnExecuted.call(this, output);
                }

                const previews = output?.base64_preview;
                if (previews && previews.length > 0) {
                    const preview = previews[0];

                    // Create image element
                    const img = new Image();
                    img.src = `data:${preview.format};base64,${preview.base64_data}`;
                    img.onload = () => {
                        this.previewImage = img;
                        this.setDirtyCanvas(true, true);
                    };
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
        }
    }
});