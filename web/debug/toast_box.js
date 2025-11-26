import { app } from "../../../scripts/app.js";
import {
    showToastInfo,
    showToastSuccess,
    showToastWarning,
    showToastError,
    showWindowsNotification,
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

                const notifications = output?.notifications;
                if (notifications && notifications.length > 0) {
                    const notification = notifications[0];
                    // Show notification based on node parameters
                    this.showNotification(
                        notification.type,
                        notification.message,
                        notification.duration,
                        notification.mode
                    );
                }
            };

            // Add method to show notification (toast or system)
            nodeType.prototype.showNotification = function(type, message, duration, mode = "comfyui") {
                try {
                    // Validate inputs
                    if (!message || message.trim() === "") {
                        console.warn("[ToastBox] Empty message");
                        return;
                    }

                    const trimmedMessage = message.trim();
                    const clampedDuration = Math.max(1000, Math.min(10000, duration)); // Clamp duration between 1-10 seconds

                    console.log(`[ToastBox] Showing ${type} notification (${mode}): ${trimmedMessage}`);

                    // Choose notification method based on mode
                    if (mode === "system") {
                        // Use system notifications
                        this.showSystemNotification(type, trimmedMessage, clampedDuration);
                    } else {
                        // Use ComfyUI toast notifications (default)
                        this.showComfyUIToast(type, trimmedMessage, clampedDuration);
                    }
                } catch (error) {
                    console.error("[ToastBox] Error showing notification:", error);
                    // Fallback to error toast
                    showToastError("ToastBox Error", "Failed to display notification", 5000);
                }
            };

            // Method to show ComfyUI toast notifications
            nodeType.prototype.showComfyUIToast = function(type, message, duration) {
                const toastOptions = {
                    summary: "ToastBox Notification",
                    detail: message,
                    life: duration
                };

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
            };

            // Method to show system notifications
            nodeType.prototype.showSystemNotification = function(type, message, duration) {
                const titleMap = {
                    "info": "Info",
                    "success": "Success",
                    "warn": "Warning",
                    "error": "Error"
                };

                const title = titleMap[type] || titleMap.info;

                // Use Windows-style system notification
                showWindowsNotification(title, message, type, {
                    timeout: duration,
                    requireInteraction: type === "error"
                }).catch(error => {
                    console.warn("[ToastBox] System notification failed, falling back to toast:", error);
                    // Fallback to ComfyUI toast
                    this.showComfyUIToast(type, message, duration);
                });
            };
        }
    }
});