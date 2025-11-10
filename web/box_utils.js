import { app } from "../../scripts/app.js";

/**
 * Utility functions for ComfyUI dialog and notification boxes
 * Provides a simplified and consistent API for showing messages to users
 */

/**
 * Show a simple message dialog
 * @param {string} message - The message to display
 */
export function showMessage(message) {
    app.ui.dialog.show(message);
}

/**
 * Show an error message dialog
 * @param {string} message - The error message
 * @param {Error} [error] - Optional error object for logging
 */
export function showError(message, error = null) {
    const errorMsg = error ? `${message}: ${error.message}` : message;
    app.ui.dialog.show(`❌ Error: ${errorMsg}`);
    
    if (error) {
        console.error("[Error]", message, error);
    } else {
        console.error("[Error]", message);
    }
}

/**
 * Show a success message dialog
 * @param {string} message - The success message
 */
export function showSuccess(message) {
    app.ui.dialog.show(`✅ ${message}`);
}

/**
 * Show a warning message dialog
 * @param {string} message - The warning message
 */
export function showWarning(message) {
    app.ui.dialog.show(`⚠️ Warning: ${message}`);
}

/**
 * Show an info message dialog
 * @param {string} message - The info message
 */
export function showInfo(message) {
    app.ui.dialog.show(`ℹ️ ${message}`);
}

/**
 * Show a confirmation dialog
 * @param {string} message - The confirmation message
 * @returns {boolean} - True if user confirmed, false if cancelled
 */
export function showConfirm(message) {
    return confirm(message);
}

/**
 * Show a confirmation dialog with custom yes/no text (using native confirm)
 * @param {string} message - The confirmation message
 * @param {string} [yesText] - Text for yes button (not used in native confirm, but kept for API consistency)
 * @param {string} [noText] - Text for no button (not used in native confirm, but kept for API consistency)
 * @returns {boolean} - True if user confirmed, false if cancelled
 */
export function showConfirmDialog(message, yesText = "OK", noText = "Cancel") {
    // Native confirm doesn't support custom button text, but we keep the API for future enhancement
    return confirm(message);
}

/**
 * Show a toast notification
 * @param {Object} options - Toast options
 * @param {string} options.severity - Severity level: "info", "success", "warn", "error"
 * @param {string} options.summary - Toast title/summary
 * @param {string} options.detail - Toast detail message
 * @param {number} [options.life=3000] - Duration in milliseconds (0 for persistent)
 */
export function showToast({ severity = "info", summary, detail, life = 3000 }) {
    app.extensionManager.toast.add({
        severity,
        summary,
        detail,
        life
    });
}

/**
 * Show an info toast notification
 * @param {string} summary - Toast title
 * @param {string} detail - Toast detail message
 * @param {number} [life=3000] - Duration in milliseconds
 */
export function showToastInfo(summary, detail, life = 3000) {
    showToast({
        severity: "info",
        summary,
        detail,
        life
    });
}

/**
 * Show a success toast notification
 * @param {string} summary - Toast title
 * @param {string} detail - Toast detail message
 * @param {number} [life=3000] - Duration in milliseconds
 */
export function showToastSuccess(summary, detail, life = 3000) {
    showToast({
        severity: "success",
        summary,
        detail,
        life
    });
}

/**
 * Show an error toast notification
 * @param {string} summary - Toast title
 * @param {string} detail - Toast detail message
 * @param {number} [life=5000] - Duration in milliseconds (longer default for errors)
 */
export function showToastError(summary, detail, life = 5000) {
    showToast({
        severity: "error",
        summary,
        detail,
        life
    });
}

/**
 * Show a warning toast notification
 * @param {string} summary - Toast title
 * @param {string} detail - Toast detail message
 * @param {number} [life=4000] - Duration in milliseconds
 */
export function showToastWarning(summary, detail, life = 4000) {
    showToast({
        severity: "warn",
        summary,
        detail,
        life
    });
}

// Default export with all functions
export default {
    showMessage,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    showConfirm,
    showConfirmDialog,
    showToast,
    showToastInfo,
    showToastSuccess,
    showToastError,
    showToastWarning
};

