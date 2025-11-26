import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import {
    showInfo,
    showSuccess,
    showWarning,
    showError,
    showConfirmDialog,
    showMessage
} from "../box_utils.js";

/**
 * Extension for DialogBox node
 * Displays dialog boxes during workflow execution and captures user responses
 */
app.registerExtension({
    name: "EasyToolkit.DialogBox",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "DialogBox") {
            // Add custom node behavior
            const originalOnExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(output) {
                // Call original method if it exists
                if (originalOnExecuted) {
                    originalOnExecuted.call(this, output);
                }

                const dialogs = output?.dialogs;
                if (dialogs && dialogs.length > 0) {
                    const dialog = dialogs[0];
                    // Show dialog and capture user response
                    this.showDialog(dialog.type, dialog.message);
                }
            };

            // Add method to show dialog and capture response
            nodeType.prototype.showDialog = async function(type, message) {
                try {
                    // Validate inputs
                    if (!message || message.trim() === "") {
                        console.warn("[DialogBox] Empty message");
                        return;
                    }

                    const trimmedMessage = message.trim();
                    console.log(`[DialogBox] Showing ${type} dialog: ${trimmedMessage}`);

                    let userResponse = "";

                    // Use appropriate dialog function based on type
                    switch (type) {
                        case "info":
                            showInfo(trimmedMessage);
                            userResponse = "ok";
                            break;
                        case "success":
                            showSuccess(trimmedMessage);
                            userResponse = "ok";
                            break;
                        case "warn":
                            showWarning(trimmedMessage);
                            userResponse = "ok";
                            break;
                        case "error":
                            showError(trimmedMessage);
                            userResponse = "ok";
                            break;
                        case "confirm":
                            const confirmed = await showConfirmDialog(trimmedMessage);
                            userResponse = confirmed ? "ok" : "cancel";
                            break;
                        default:
                            console.warn(`[DialogBox] Unknown type: ${type}, defaulting to info`);
                            showMessage(trimmedMessage);
                            userResponse = "ok";
                    }

                    console.log(`[DialogBox] User response: ${userResponse}`);

                } catch (error) {
                    console.error("[DialogBox] Error showing dialog:", error);
                    showError("DialogBox Error", "Failed to display dialog");
                }
            };
        }
    }
});