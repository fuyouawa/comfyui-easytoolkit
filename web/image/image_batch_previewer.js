import { app } from "../../../scripts/app.js";
import { apiPost, apiSilent } from "../api_utils.js";
import { calculateAvailableSpace, drawImagePreview } from "../preview_utils.js";
import { checkAndRegenerateUUID } from "../node_utils.js";

app.registerExtension({
    name: "EasyToolkit.Image.ImageBatchPreviewer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "ImageBatchPreviewer") return;

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

            // Initialize preview state
            this.previewImages = [];
            this.currentFrameIndex = 0;
            this.animationTimer = null;
            this.fps = 8;
            
            // Function to start animation
            const startAnimation = () => {
                // Clear existing timer if any
                if (this.animationTimer) {
                    clearInterval(this.animationTimer);
                    this.animationTimer = null;
                }
                
                if (this.previewImages.length === 0) return;
                
                // Calculate interval based on fps
                const interval = 1000 / this.fps;
                
                // Start animation loop
                this.animationTimer = setInterval(() => {
                    if (this.previewImages.length === 0) return;
                    
                    // Move to next frame
                    this.currentFrameIndex = (this.currentFrameIndex + 1) % this.previewImages.length;
                    this.setDirtyCanvas(true, true);
                }, interval);
            };
            
            // Function to load and display images
            const loadPreviewImages = async () => {
                const currentUuid = this.widgets?.find(w => w.name === "uuid")?.value;
                if (!currentUuid) return;
                
                // Use silent mode since preview loading is optional
                const data = await apiSilent("/image_batch_previewer/get_images", {
                    method: "POST",
                    data: { uuid: currentUuid }
                });
                
                if (data.success && data.base64_list && data.base64_list.length > 0) {
                    // Store fps
                    this.fps = data.fps || 8;
                    
                    // Load all images
                    const imagePromises = data.base64_list.map((base64, index) => {
                        return new Promise((resolve, reject) => {
                            const img = new Image();
                            img.src = `data:${data.format};base64,${base64}`;
                            img.onload = () => resolve(img);
                            img.onerror = () => reject(new Error(`Failed to load image ${index}`));
                        });
                    });
                    
                    try {
                        this.previewImages = await Promise.all(imagePromises);
                        this.currentFrameIndex = 0;
                        this.setDirtyCanvas(true, true);
                        
                        // Start animation
                        startAnimation();
                    } catch (error) {
                        console.error("Failed to load preview images:", error);
                    }
                }
                else {
                    console.error("Failed to load preview images:", data.error || "Unknown error");
                }
            };
            
            // Store the load function for later use
            this.loadPreviewImages = loadPreviewImages;
        };

        // Override onConfigure to load preview when node is copied or loaded
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function(info) {
            if (onConfigure) {
                onConfigure.apply(this, arguments);
            }
            
            // Check for duplicate UUID and regenerate if necessary
            checkAndRegenerateUUID(this, app);
            
            // Load preview images after configuration (this ensures UUID is properly set)
            if (this.loadPreviewImages) {
                // Use setTimeout to ensure widget values are fully updated
                setTimeout(() => {
                    this.loadPreviewImages();
                }, 50);
            }
        };

        // Override onExecuted to load images after execution
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (onExecuted) {
                onExecuted.apply(this, arguments);
            }
            
            // Load preview images after execution
            if (this.loadPreviewImages) {
                setTimeout(() => {
                    this.loadPreviewImages();
                }, 100);
            }
        };

        // Override onDrawForeground to draw the current frame on the node
        const onDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            if (onDrawForeground) {
                onDrawForeground.apply(this, arguments);
            }
            
            if (this.previewImages.length > 0 && this.previewImages[this.currentFrameIndex]?.complete) {
                const currentImage = this.previewImages[this.currentFrameIndex];
                
                // Calculate available space using utility function
                const { margin, startY, availableWidth, availableHeight } = calculateAvailableSpace(this);
                
                // Draw image preview using utility function
                const { height: drawnHeight } = drawImagePreview(
                    ctx,
                    currentImage,
                    margin,
                    startY,
                    availableWidth,
                    availableHeight
                );
                
                // Draw frame info
                const frameInfoY = startY + drawnHeight + margin / 2;
                ctx.save();
                ctx.fillStyle = "#ffffff";
                ctx.font = "12px monospace";
                ctx.textAlign = "center";
                const frameText = `Frame ${this.currentFrameIndex + 1}/${this.previewImages.length} @ ${this.fps} FPS`;
                ctx.fillText(frameText, this.size[0] / 2, frameInfoY);
                ctx.restore();
                
                // Auto-resize node to fit image and frame info if needed
                const minHeight = frameInfoY + margin;
                if (this.size[1] < minHeight) {
                    this.size[1] = minHeight;
                }
            }
        };
        
        // Clean up timers when node is removed
        const onRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function () {
            // Clear the animation timer
            if (this.animationTimer) {
                clearInterval(this.animationTimer);
                this.animationTimer = null;
            }
            
            if (onRemoved) {
                return onRemoved.apply(this, arguments);
            }
        };
    },
});

