/**
 * Node utility functions for ComfyUI
 * Shared utilities for node management and state handling
 */

/**
 * Check for duplicate UUID in the graph and regenerate if necessary
 * This function should be called in onConfigure to handle node copying
 * 
 * @param {object} node - LiteGraph node instance (usually 'this')
 * @param {object} app - ComfyUI app instance
 * @param {string} [widgetName="uuid"] - Name of the UUID widget (default: "uuid")
 * @returns {boolean} True if UUID was regenerated, false otherwise
 */
export function checkAndRegenerateUUID(node, app, widgetName = "uuid") {
    const uuid_widget = node.widgets?.find(w => w.name === widgetName);
    
    if (!uuid_widget || !uuid_widget.value) {
        return false;
    }
    
    // Find all nodes with the same UUID
    const duplicates = app.graph._nodes.filter(n => {
        const nodeUuidWidget = n.widgets?.find(w => w.name === widgetName);
        return nodeUuidWidget && 
               nodeUuidWidget.value === uuid_widget.value && 
               n !== node;
    });
    
    // If duplicates found, regenerate UUID for this node
    if (duplicates.length > 0) {
        const oldUUID = uuid_widget.value;
        uuid_widget.value = crypto.randomUUID();
        
        console.log(`[UUID Check] Duplicate UUID detected: ${oldUUID}`);
        console.log(`[UUID Check] New UUID generated: ${uuid_widget.value}`);
        
        return true;
    }
    
    return false;
}

/**
 * Initialize UUID widget if not present or empty
 * This function should be called in onNodeCreated
 * 
 * @param {object} node - LiteGraph node instance (usually 'this')
 * @param {string} [widgetName="uuid"] - Name of the UUID widget (default: "uuid")
 * @returns {boolean} True if UUID was initialized, false if already present
 */
export function initializeUUID(node, widgetName = "uuid") {
    const uuid_widget = node.widgets?.find(w => w.name === widgetName);
    
    if (!uuid_widget) {
        console.warn(`[UUID Init] Widget "${widgetName}" not found on node`);
        return false;
    }
    
    try {
        if (!uuid_widget.value || uuid_widget.value === "") {
            uuid_widget.value = crypto.randomUUID();
            console.log(`[UUID Init] UUID initialized: ${uuid_widget.value}`);
            return true;
        }
    } catch (error) {
        console.error("[UUID Init] Failed to generate UUID:", error);
        throw error;
    }
    
    return false;
}

/**
 * Setup UUID handling for a node (combines initialization and duplicate checking)
 * This is a convenience function that handles both onNodeCreated and onConfigure
 * 
 * @param {object} nodeType - Node type prototype
 * @param {object} app - ComfyUI app instance
 * @param {string} [widgetName="uuid"] - Name of the UUID widget (default: "uuid")
 * @param {Function} [onNodeCreatedCallback] - Optional callback after UUID initialization
 * @param {Function} [onConfigureCallback] - Optional callback after UUID check
 */
export function setupUUIDHandling(nodeType, app, widgetName = "uuid", onNodeCreatedCallback = null, onConfigureCallback = null) {
    // Hook into onNodeCreated for initialization
    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
        if (originalOnNodeCreated) {
            originalOnNodeCreated.apply(this, arguments);
        }
        
        initializeUUID(this, widgetName);
        
        if (onNodeCreatedCallback) {
            onNodeCreatedCallback.call(this);
        }
    };
    
    // Hook into onConfigure for duplicate checking
    const originalOnConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function(info) {
        if (originalOnConfigure) {
            originalOnConfigure.apply(this, arguments);
        }
        
        checkAndRegenerateUUID(this, app, widgetName);
        
        if (onConfigureCallback) {
            onConfigureCallback.call(this, info);
        }
    };
}

