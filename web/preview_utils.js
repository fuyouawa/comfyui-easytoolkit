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
