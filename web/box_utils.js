import { app } from "../../scripts/app.js";

/**
 * Utility functions for ComfyUI dialog and notification boxes
 * Provides a simplified and consistent API for showing messages to users
 */

/**
 * Dialog button types enumeration
 */
export const DialogButtonType = {
    OK_ONLY: 'ok_only',
    OK_CANCEL: 'ok_cancel'
};

/**
 * Dialog result enumeration
 */
export const DialogResult = {
    OK: 'ok',
    CANCEL: 'cancel'
};

/**
 * Begin a custom dialog box
 * Creates the overlay and dialog container with title
 * @param {string} title - Dialog title
 * @param {Object} [options] - Dialog options
 * @param {number} [options.minWidth=400] - Minimum dialog width in pixels
 * @param {number} [options.maxWidth=600] - Maximum dialog width in pixels
 * @param {number} [options.maxHeight=80] - Maximum dialog height as viewport percentage
 * @returns {Object} Dialog context containing overlay, dialog, and content elements
 */
export function beginDialogBox(title, options = {}) {
    const {
        minWidth = 400,
        maxWidth = 600,
        maxHeight = 80
    } = options;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.zIndex = '10000';

    // Create dialog
    const dialog = document.createElement('div');
    dialog.style.backgroundColor = '#1e1e1e';
    dialog.style.border = '1px solid #555';
    dialog.style.borderRadius = '8px';
    dialog.style.padding = '20px';
    dialog.style.minWidth = `${minWidth}px`;
    dialog.style.maxWidth = `${maxWidth}px`;
    dialog.style.maxHeight = `${maxHeight}vh`;
    dialog.style.display = 'flex';
    dialog.style.flexDirection = 'column';
    dialog.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';

    // Title
    const titleElement = document.createElement('h3');
    titleElement.textContent = title;
    titleElement.style.margin = '0 0 15px 0';
    titleElement.style.color = '#fff';
    titleElement.style.fontSize = '18px';
    dialog.appendChild(titleElement);

    // Content container for user controls
    const content = document.createElement('div');
    content.style.flex = '1';
    content.style.overflow = 'auto';
    content.style.marginBottom = '15px';
    dialog.appendChild(content);

    // Add dialog to overlay
    overlay.appendChild(dialog);

    // Add to body
    document.body.appendChild(overlay);

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    };

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    return {
        overlay,
        dialog,
        content,
        escapeHandler
    };
}

/**
 * End a custom dialog box
 * Adds buttons and handles cleanup
 * @param {Object} dialogContext - Dialog context from beginDialogBox
 * @param {DialogButtonType} buttonType - Type of buttons to show
 * @param {Function} onButtonClick - Callback when buttons are clicked
 * @param {Object} [options] - Button options
 * @param {string} [options.okText='Ok'] - Text for OK button
 * @param {string} [options.cancelText='Cancel'] - Text for Cancel button
 */
export function endDialogBox(dialogContext, buttonType, onButtonClick, options = {}) {
    const {
        overlay,
        dialog,
        escapeHandler
    } = dialogContext;

    const {
        okText = 'Ok',
        cancelText = 'Cancel'
    } = options;

    // Buttons container
    const buttonContainer = document.createElement('div');
    buttonContainer.style.display = 'flex';
    buttonContainer.style.justifyContent = 'flex-end';
    buttonContainer.style.gap = '10px';

    // Create button helper function
    const createButton = (text, isPrimary = false) => {
        const button = document.createElement('button');
        button.textContent = text;
        button.style.padding = '8px 20px';
        button.style.backgroundColor = isPrimary ? '#007acc' : '#555';
        button.style.color = '#fff';
        button.style.border = 'none';
        button.style.borderRadius = '4px';
        button.style.cursor = 'pointer';
        button.style.fontSize = '14px';

        // Hover effects
        button.onmouseover = () => {
            button.style.backgroundColor = isPrimary ? '#0098ff' : '#666';
        };
        button.onmouseout = () => {
            button.style.backgroundColor = isPrimary ? '#007acc' : '#555';
        };

        return button;
    };

    // Add buttons based on buttonType
    if (buttonType === DialogButtonType.OK_ONLY) {
        const okButton = createButton(okText, true);
        okButton.onclick = () => {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', escapeHandler);
            if (onButtonClick) {
                onButtonClick(DialogResult.OK);
            }
        };
        buttonContainer.appendChild(okButton);
    } else if (buttonType === DialogButtonType.OK_CANCEL) {
        const cancelButton = createButton(cancelText, false);
        cancelButton.onclick = () => {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', escapeHandler);
            if (onButtonClick) {
                onButtonClick(DialogResult.CANCEL);
            }
        };

        const okButton = createButton(okText, true);
        okButton.onclick = () => {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', escapeHandler);
            if (onButtonClick) {
                onButtonClick(DialogResult.OK);
            }
        };

        buttonContainer.appendChild(cancelButton);
        buttonContainer.appendChild(okButton);
    }

    dialog.appendChild(buttonContainer);
}

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
    DialogButtonType,
    DialogResult,
    beginDialogBox,
    endDialogBox,
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

