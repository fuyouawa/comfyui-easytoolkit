import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import {
    showToastInfo,
    showToastSuccess,
    showToastWarning,
    showToastError
} from "../box_utils.js";

/**
 * Extension for ToastBox node
 * Displays toast notifications during workflow execution
 */
app.registerExtension({
    name: "EasyToolkit.ToastBox",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "ToastBox") {
            // Add custom node behavior
            const originalOnExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(output) {
                // Call original method if it exists
                if (originalOnExecuted) {
                    originalOnExecuted.call(this, output);
                }

                const toasts = output?.toasts;
                if (toasts && toasts.length > 0) {
                    const toast = toasts[0];
                    // Show toast notification based on node parameters
                    this.showToastNotification(toast.type, toast.message, toast.duration);
                }
            };

            // Add method to show toast notification
            nodeType.prototype.showToastNotification = function(type, message, duration) {
                try {
                    // Validate inputs
                    if (!message || message.trim() === "") {
                        console.warn("[ToastBox] Empty message");
                        return;
                    }

                    const toastOptions = {
                        summary: "ToastBox Notification",
                        detail: message.trim(),
                        life: Math.max(1000, Math.min(10000, duration)) // Clamp duration between 1-10 seconds
                    };

                    console.log(`[ToastBox] Showing ${type} notification: ${toastOptions.detail}`);

                    // Use appropriate toast function based on type
                    switch (type) {
                        case "info":
                            showToastInfo(toastOptions.summary, toastOptions.detail, toastOptions.life);
                            break;
                        case "success":
                            showToastSuccess(toastOptions.summary, toastOptions.detail, toastOptions.life);
                            break;
                        case "warn":
                            showToastWarning(toastOptions.summary, toastOptions.detail, toastOptions.life);
                            break;
                        case "error":
                            showToastError(toastOptions.summary, toastOptions.detail, toastOptions.life);
                            break;
                        default:
                            console.warn(`[ToastBox] Unknown type: ${type}, defaulting to info`);
                            showToastInfo(toastOptions.summary, toastOptions.detail, toastOptions.life);
                    }
                } catch (error) {
                    console.error("[ToastBox] Error showing notification:", error);
                    showToastError("ToastBox Error", "Failed to display notification", 5000);
                }
            };
        }
    }
});