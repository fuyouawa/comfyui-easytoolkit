/**
 * Preview utility functions for ComfyUI nodes
 * Shared utilities for image and text preview rendering
 */

/**
 * Decode base64 text content
 * @param {string} base64Content - Base64 encoded content or plain text
 * @param {string} format - MIME type format (e.g., "text/plain")
 * @returns {string} Decoded text content
 */
export function decodeBase64Text(base64Content, format) {
    // If it's already plain text format, return as-is
    if (format.startsWith("text/")) {
        return base64Content;
    }
    
    // Try to decode base64
    try {
        return atob(base64Content);
    } catch (e) {
        return base64Content;
    }
}

/**
 * Calculate available space for preview in a node
 * @param {object} node - LiteGraph node instance
 * @param {number} [customMargin=15] - Optional custom margin value
 * @param {number} [extraSpacing=0] - Optional extra spacing below widgets to prevent overlap
 * @returns {object} Object containing margin, startY, availableWidth, availableHeight
 */
export function calculateAvailableSpace(node, customMargin = 15, extraSpacing = 0) {
    const margin = customMargin;
    const widgetHeight = node.widgets?.reduce((sum, w) => sum + (w.computedHeight || 30), 0) || 0;
    const headerHeight = 30;
    const startY = headerHeight + widgetHeight + margin + extraSpacing;
    
    return {
        margin,
        startY,
        availableWidth: node.size[0] - 2 * margin,
        availableHeight: node.size[1] - startY - margin
    };
}

/**
 * Calculate image preview dimensions maintaining aspect ratio
 * @param {HTMLImageElement} img - Image element
 * @param {number} availableWidth - Available width for preview
 * @param {number} availableHeight - Available height for preview
 * @returns {object} Object containing width and height
 */
export function calculateImagePreviewDimensions(img, availableWidth, availableHeight) {
    const imgAspect = img.width / img.height;
    let drawWidth = availableWidth;
    let drawHeight = drawWidth / imgAspect;
    
    if (drawHeight > availableHeight) {
        drawHeight = availableHeight;
        drawWidth = drawHeight * imgAspect;
    }
    
    return { width: drawWidth, height: drawHeight };
}

/**
 * Draw image preview on canvas with automatic centering
 * @param {CanvasRenderingContext2D} ctx - Canvas 2D context
 * @param {HTMLImageElement} img - Image to draw
 * @param {number} x - X position (left edge)
 * @param {number} y - Y position (top edge)
 * @param {number} availableWidth - Available width
 * @param {number} availableHeight - Available height
 * @returns {object} Object containing drawn width and height
 */
export function drawImagePreview(ctx, img, x, y, availableWidth, availableHeight) {
    const { width, height } = calculateImagePreviewDimensions(img, availableWidth, availableHeight);
    
    // Center the image horizontally
    const centerX = x + (availableWidth - width) / 2;
    
    ctx.save();
    ctx.drawImage(img, centerX, y, width, height);
    ctx.restore();
    
    return { width, height };
}

/**
 * Draw text preview on canvas with background and border
 * @param {CanvasRenderingContext2D} ctx - Canvas 2D context
 * @param {string} text - Text content to display
 * @param {number} x - X position
 * @param {number} y - Y position
 * @param {number} width - Preview box width
 * @param {number} height - Preview box height
 * @param {object} [options] - Optional styling options
 * @param {string} [options.backgroundColor="#2d2d2d"] - Background color
 * @param {string} [options.borderColor="#444"] - Border color
 * @param {string} [options.textColor="#d4d4d4"] - Text color
 * @param {string} [options.fontFamily="monospace"] - Font family
 * @param {number} [options.fontSize=12] - Font size in pixels
 */
export function drawTextPreview(ctx, text, x, y, width, height, options = {}) {
    const {
        backgroundColor = "#2d2d2d",
        borderColor = "#444",
        textColor = "#d4d4d4",
        fontFamily = "monospace",
        fontSize = 12
    } = options;
    
    ctx.save();
    
    // Draw background
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(x, y, width, height);
    
    // Draw border
    ctx.strokeStyle = borderColor;
    ctx.strokeRect(x, y, width, height);
    
    // Draw text
    ctx.fillStyle = textColor;
    ctx.font = `${fontSize}px ${fontFamily}`;
    
    const lines = text.split('\n');
    const lineHeight = fontSize + 2;
    const maxLines = Math.floor((height - 20) / lineHeight);
    const visibleLines = lines.slice(0, maxLines);
    
    visibleLines.forEach((line, idx) => {
        const maxChars = Math.floor((width - 20) / 7);
        const truncatedLine = line.length > maxChars ? line.substring(0, maxChars) + "..." : line;
        ctx.fillText(truncatedLine, x + 5, y + 15 + idx * lineHeight);
    });
    
    if (lines.length > maxLines) {
        ctx.fillText("...", x + 5, y + 15 + maxLines * lineHeight);
    }
    
    ctx.restore();
}

/**
 * Create a modal dialog element with common styling
 * @param {string} title - Dialog title
 * @param {Function} onClose - Callback when dialog is closed
 * @returns {object} Object containing dialog, contentContainer, and overlay elements
 */
export function createPreviewDialog(title, onClose) {
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

    const titleElement = document.createElement("h3");
    titleElement.textContent = title;
    titleElement.style.margin = "0";
    titleElement.style.color = "#fff";
    titleElement.style.fontSize = "18px";

    const closeButton = document.createElement("button");
    closeButton.textContent = "×";
    closeButton.style.fontSize = "24px";
    closeButton.style.border = "none";
    closeButton.style.background = "none";
    closeButton.style.color = "#fff";
    closeButton.style.cursor = "pointer";
    closeButton.style.padding = "0 8px";

    titleBar.appendChild(titleElement);
    titleBar.appendChild(closeButton);
    dialog.appendChild(titleBar);

    // Content container
    const contentContainer = document.createElement("div");
    contentContainer.style.color = "#fff";
    contentContainer.style.minWidth = "400px";
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

    // Set up close handlers
    const closeDialog = () => {
        document.body.removeChild(overlay);
        if (onClose) onClose();
    };

    closeButton.onclick = closeDialog;
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            closeDialog();
        }
    };

    overlay.appendChild(dialog);

    return { dialog, contentContainer, overlay };
}

