import { app } from "../../../scripts/app.js";
import {
    showError
} from "../box_utils.js";
import {
    calculateAvailableSpace,
    drawImagePreview
} from "../preview_utils.js";

/**
 * Extension for ImageBatchBase64Previewer node
 * Displays batch of base64 encoded images directly on the node during workflow execution
 */
app.registerExtension({
    name: "EasyToolkit.ImageBatchBase64Previewer",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "ImageBatchBase64Previewer") {
            // Add custom node behavior
            const originalOnExecuted = nodeType.prototype.onExecuted;

            this.previewImages = [];
            this.currentFrame = 0;
            this.lastFrameTime = 0;
            this.animationFrameId = null;

            nodeType.prototype.onExecuted = function(output) {
                // Call original method if it exists
                if (originalOnExecuted) {
                    originalOnExecuted.call(this, output);
                }

                const previews = output?.base64_batch_preview;
                if (previews && previews.length > 0) {
                    const preview = previews[0];

                    // Clear previous images and animation
                    this.previewImages = [];
                    this.currentFrame = 0;
                    this.lastFrameTime = 0;

                    if (this.animationFrameId) {
                        cancelAnimationFrame(this.animationFrameId);
                        this.animationFrameId = null;
                    }

                    // Load all images
                    if (preview.base64_datas && preview.base64_datas.length > 0) {
                        let loadedCount = 0;
                        const totalImages = preview.base64_datas.length;

                        preview.base64_datas.forEach((base64Data, index) => {
                            const img = new Image();
                            img.src = `data:${preview.format};base64,${base64Data}`;
                            img.onload = () => {
                                this.previewImages[index] = img;
                                loadedCount++;

                                // Start animation when all images are loaded
                                if (loadedCount === totalImages && totalImages > 1) {
                                    this.startAnimation(preview.fps || 24.0);
                                }

                                this.setDirtyCanvas(true, true);
                            };
                            img.onerror = () => {
                                console.error(`Failed to load image ${index + 1}`);
                                loadedCount++;
                                if (loadedCount === totalImages) {
                                    this.setDirtyCanvas(true, true);
                                }
                            };
                        });
                    }
                }
            };

            // Start animation for multiple images
            nodeType.prototype.startAnimation = function(fps) {
                const frameInterval = 1000 / fps;

                const animate = (currentTime) => {
                    if (!this.lastFrameTime) {
                        this.lastFrameTime = currentTime;
                    }

                    const elapsed = currentTime - this.lastFrameTime;

                    if (elapsed > frameInterval) {
                        this.currentFrame = (this.currentFrame + 1) % this.previewImages.length;
                        this.lastFrameTime = currentTime;
                        this.setDirtyCanvas(true, true);
                    }

                    this.animationFrameId = requestAnimationFrame(animate);
                };

                this.animationFrameId = requestAnimationFrame(animate);
            };

            // Override onDrawForeground to draw the preview image(s) on the node
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function(ctx) {
                if (onDrawForeground) {
                    onDrawForeground.apply(this, arguments);
                }

                if (this.previewImages && this.previewImages.length > 0) {
                    // Calculate available space using utility function
                    const { margin, startY, availableWidth, availableHeight } = calculateAvailableSpace(this);

                    // Get current image to display
                    let currentImage;
                    if (this.previewImages.length === 1) {
                        currentImage = this.previewImages[0];
                    } else {
                        currentImage = this.previewImages[this.currentFrame];
                    }

                    if (currentImage && currentImage.complete) {
                        // Draw image preview using utility function
                        const { height: drawnHeight } = drawImagePreview(
                            ctx,
                            currentImage,
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

                        // Show frame info for multiple images
                        if (this.previewImages.length > 1) {
                            ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
                            ctx.fillRect(margin, startY - 20, 80, 18);
                            ctx.fillStyle = "white";
                            ctx.font = "12px Arial";
                            ctx.fillText(`Frame: ${this.currentFrame + 1}/${this.previewImages.length}`, margin + 5, startY - 5);
                        }
                    }
                }
            };

            // Clean up animation when node is removed
            const originalOnRemoved = nodeType.prototype.onRemoved;
            nodeType.prototype.onRemoved = function() {
                if (this.animationFrameId) {
                    cancelAnimationFrame(this.animationFrameId);
                    this.animationFrameId = null;
                }
                if (originalOnRemoved) {
                    originalOnRemoved.apply(this, arguments);
                }
            };
        }
    }
});