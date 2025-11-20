// import { app } from "../../scripts/app.js";
// import {
//     createMessage,
//     createDialogOverlay,
//     createDialogContainer,
//     createDialogTitle,
//     createDialogContent,
//     createButtonContainer,
//     createDialogButton,
//     setupDialogEvents
// } from "./ui_utils.js";

// /**
//  * Utility functions for ComfyUI dialog and notification boxes
//  * Provides a simplified and consistent API for showing messages to users
//  */

// /**
//  * Dialog button types enumeration
//  */
// export const DialogButtonType = {
//     OK_ONLY: 'ok_only',
//     OK_CANCEL: 'ok_cancel'
// };

// /**
//  * Dialog result enumeration
//  */
// export const DialogResult = {
//     OK: 'ok',
//     CANCEL: 'cancel'
// };

// /**
//  * Begin a custom dialog box
//  * Creates the overlay and dialog container with title
//  * @param {string} title - Dialog title
//  * @param {Object} [options] - Dialog options
//  * @param {number} [options.minWidth=400] - Minimum dialog width in pixels
//  * @param {number} [options.maxWidth=600] - Maximum dialog width in pixels
//  * @param {number} [options.maxHeight=80] - Maximum dialog height as viewport percentage
//  * @returns {Object} Dialog context containing overlay, dialog, and content elements
//  */
// export function beginDialogBox(title, options = {}) {
//     const {
//         minWidth = 400,
//         maxWidth = 600,
//         maxHeight = 80
//     } = options;

//     // Create overlay
//     const overlay = createDialogOverlay();

//     // Create dialog
//     const dialog = createDialogContainer({ minWidth, maxWidth, maxHeight });

//     // Title
//     const titleElement = createDialogTitle(title);
//     dialog.appendChild(titleElement);

//     // Content container for user controls
//     const content = createDialogContent();
//     dialog.appendChild(content);

//     // Add dialog to overlay
//     overlay.appendChild(dialog);

//     // Add to body
//     document.body.appendChild(overlay);

//     // Close on Escape key
//     const escapeHandler = (e) => {
//         if (e.key === 'Escape') {
//             document.body.removeChild(overlay);
//             document.removeEventListener('keydown', escapeHandler);
//         }
//     };

//     // Setup event handlers
//     const cleanupEvents = setupDialogEvents(overlay, escapeHandler);

//     return {
//         overlay,
//         dialog,
//         content,
//         escapeHandler,
//         cleanupEvents
//     };
// }

// /**
//  * End a custom dialog box
//  * Adds buttons and handles cleanup
//  * @param {Object} dialogContext - Dialog context from beginDialogBox
//  * @param {DialogButtonType} buttonType - Type of buttons to show
//  * @param {Function} onButtonClick - Callback when buttons are clicked
//  * @param {Object} [options] - Button options
//  * @param {string} [options.okText='Ok'] - Text for OK button
//  * @param {string} [options.cancelText='Cancel'] - Text for Cancel button
//  */
// export function endDialogBox(dialogContext, buttonType, onButtonClick, options = {}) {
//     const {
//         overlay,
//         escapeHandler,
//         cleanupEvents
//     } = dialogContext;

//     const {
//         okText = 'Ok',
//         cancelText = 'Cancel'
//     } = options;

//     // Buttons container
//     const buttonContainer = createButtonContainer();

//     // Cleanup function
//     const cleanup = () => {
//         document.body.removeChild(overlay);
//         if (cleanupEvents) {
//             cleanupEvents();
//         } else {
//             document.removeEventListener('keydown', escapeHandler);
//         }
//     };

//     // Add buttons based on buttonType
//     if (buttonType === DialogButtonType.OK_ONLY) {
//         const okButton = createDialogButton(okText, true);
//         okButton.onclick = () => {
//             cleanup();
//             if (onButtonClick) {
//                 onButtonClick(DialogResult.OK);
//             }
//         };
//         buttonContainer.appendChild(okButton);
//     } else if (buttonType === DialogButtonType.OK_CANCEL) {
//         const cancelButton = createDialogButton(cancelText, false);
//         cancelButton.onclick = () => {
//             cleanup();
//             if (onButtonClick) {
//                 onButtonClick(DialogResult.CANCEL);
//             }
//         };

//         const okButton = createDialogButton(okText, true);
//         okButton.onclick = () => {
//             cleanup();
//             if (onButtonClick) {
//                 onButtonClick(DialogResult.OK);
//             }
//         };

//         buttonContainer.appendChild(okButton);
//         buttonContainer.appendChild(cancelButton);
//     }

//     dialogContext.dialog.appendChild(buttonContainer);
// }


// /**
//  * Show a message dialog with customizable appearance
//  * @param {string} message - The message to display
//  * @param {Object} [options] - Message options
//  * @param {string} [options.title="Message"] - Dialog title
//  * @param {string} [options.color="#fff"] - Text color
//  * @param {number} [options.minWidth=300] - Minimum dialog width
//  * @param {number} [options.maxWidth=500] - Maximum dialog width
//  * @param {number} [options.maxHeight=80] - Maximum dialog height as viewport percentage
//  */
// export function showMessage(message, options = {}) {
//     const {
//         title = "Message",
//         color = "#fff",
//         minWidth = 300,
//         maxWidth = 500,
//         maxHeight = 80
//     } = options;

//     const dialogContext = beginDialogBox(title, {
//         minWidth,
//         maxWidth,
//         maxHeight
//     });

//     const messageElement = createMessage(message, { color });
//     dialogContext.content.appendChild(messageElement);

//     endDialogBox(dialogContext, DialogButtonType.OK_ONLY);
// }

// /**
//  * Show an error message dialog
//  * @param {string} message - The error message
//  * @param {Error} [error] - Optional error object for logging
//  */
// export function showError(message, error = null) {
//     const errorMsg = error ? `${message}: ${error.message}` : message;

//     showMessage(errorMsg, {
//         title: "❌ Error",
//         color: "#ff6b6b",
//         minWidth: 400,
//         maxWidth: 600
//     });

//     if (error) {
//         console.error("[Error]", message, error);
//     } else {
//         console.error("[Error]", message);
//     }
// }

// /**
//  * Show a success message dialog
//  * @param {string} message - The success message
//  */
// export function showSuccess(message) {
//     showMessage(message, {
//         title: "✅ Success",
//         color: "#4caf50",
//         minWidth: 300,
//         maxWidth: 500
//     });
// }

// /**
//  * Show a warning message dialog
//  * @param {string} message - The warning message
//  */
// export function showWarning(message) {
//     showMessage(message, {
//         title: "⚠️ Warning",
//         color: "#ff9800",
//         minWidth: 400,
//         maxWidth: 600
//     });
// }

// /**
//  * Show an info message dialog
//  * @param {string} message - The info message
//  */
// export function showInfo(message) {
//     showMessage(message, {
//         title: "ℹ️ Information",
//         color: "#2196f3",
//         minWidth: 300,
//         maxWidth: 500
//     });
// }

// /**
//  * Show a confirmation dialog with custom yes/no text
//  * @param {string} message - The confirmation message
//  * @param {string} [yesText="OK"] - Text for yes button
//  * @param {string} [noText="Cancel"] - Text for no button
//  * @returns {Promise<boolean>} - Promise that resolves to true if user confirmed, false if cancelled
//  */
// export function showConfirmDialog(message, yesText = "OK", noText = "Cancel") {
//     return new Promise((resolve) => {
//         const dialogContext = beginDialogBox("Confirmation", {
//             minWidth: 400,
//             maxWidth: 600
//         });

//         const messageElement = createMessage(message, { color: "#fff" });
//         messageElement.style.marginBottom = '15px';
//         dialogContext.content.appendChild(messageElement);

//         endDialogBox(dialogContext, DialogButtonType.OK_CANCEL, (result) => {
//             resolve(result === DialogResult.OK);
//         }, {
//             okText: yesText,
//             cancelText: noText
//         });
//     });
// }

// /**
//  * Show a toast notification
//  * @param {Object} options - Toast options
//  * @param {string} options.severity - Severity level: "info", "success", "warn", "error"
//  * @param {string} options.summary - Toast title/summary
//  * @param {string} options.detail - Toast detail message
//  * @param {number} [options.life=3000] - Duration in milliseconds (0 for persistent)
//  */
// export function showToast({ severity = "info", summary, detail, life = 3000 }) {
//     app.extensionManager.toast.add({
//         severity,
//         summary,
//         detail,
//         life
//     });
// }

// /**
//  * Show an info toast notification
//  * @param {string} summary - Toast title
//  * @param {string} detail - Toast detail message
//  * @param {number} [life=3000] - Duration in milliseconds
//  */
// export function showToastInfo(summary, detail, life = 3000) {
//     showToast({
//         severity: "info",
//         summary,
//         detail,
//         life
//     });
// }

// /**
//  * Show a success toast notification
//  * @param {string} summary - Toast title
//  * @param {string} detail - Toast detail message
//  * @param {number} [life=3000] - Duration in milliseconds
//  */
// export function showToastSuccess(summary, detail, life = 3000) {
//     showToast({
//         severity: "success",
//         summary,
//         detail,
//         life
//     });
// }

// /**
//  * Show an error toast notification
//  * @param {string} summary - Toast title
//  * @param {string} detail - Toast detail message
//  * @param {number} [life=5000] - Duration in milliseconds (longer default for errors)
//  */
// export function showToastError(summary, detail, life = 5000) {
//     showToast({
//         severity: "error",
//         summary,
//         detail,
//         life
//     });
// }

// /**
//  * Show a warning toast notification
//  * @param {string} summary - Toast title
//  * @param {string} detail - Toast detail message
//  * @param {number} [life=4000] - Duration in milliseconds
//  */
// export function showToastWarning(summary, detail, life = 4000) {
//     showToast({
//         severity: "warn",
//         summary,
//         detail,
//         life
//     });
// }

// // /**
// //  * Windows System Notification Functions
// //  * Provides system-level notifications using Web Notifications API
// //  */

// // /**
// //  * Check if system notifications are supported and permission is granted
// //  * @returns {Promise<boolean>} - Promise that resolves to true if notifications are available
// //  */
// // export async function checkNotificationSupport() {
// //     if (!('Notification' in window)) {
// //         console.warn('This browser does not support system notifications');
// //         return false;
// //     }

// //     if (Notification.permission === 'granted') {
// //         return true;
// //     }

// //     if (Notification.permission === 'denied') {
// //         console.warn('Notification permission has been denied');
// //         return false;
// //     }

// //     // Request permission
// //     const permission = await Notification.requestPermission();
// //     return permission === 'granted';
// // }

// // /**
// //  * Show a system notification
// //  * @param {string} title - Notification title
// //  * @param {Object} [options] - Notification options
// //  * @param {string} [options.body] - Notification body text
// //  * @param {string} [options.icon] - URL of notification icon
// //  * @param {string} [options.image] - URL of notification image
// //  * @param {string} [options.tag] - Notification tag for grouping
// //  * @param {boolean} [options.requireInteraction=false] - Whether notification requires user interaction
// //  * @param {number} [options.timeout=5000] - Auto-close timeout in milliseconds (0 for no auto-close)
// //  * @param {Array} [options.actions] - Array of action objects
// //  * @returns {Promise<Notification|null>} - Promise that resolves to Notification object or null if failed
// //  */
// // export async function showSystemNotification(title, options = {}) {
// //     const {
// //         body = '',
// //         icon = '',
// //         image = '',
// //         tag = '',
// //         requireInteraction = false,
// //         timeout = 5000,
// //         actions = []
// //     } = options;

// //     const hasSupport = await checkNotificationSupport();
// //     if (!hasSupport) {
// //         console.warn('System notifications not available, falling back to toast');
// //         showToastInfo(title, body);
// //         return null;
// //     }

// //     const notificationOptions = {
// //         body,
// //         icon,
// //         image,
// //         tag,
// //         requireInteraction,
// //         actions
// //     };

// //     const notification = new Notification(title, notificationOptions);

// //     // Auto-close if timeout is specified
// //     if (timeout > 0) {
// //         setTimeout(() => {
// //             notification.close();
// //         }, timeout);
// //     }

// //     return notification;
// // }

// /**
//  * Windows-style notification utilities
//  * Provides Windows-specific notification patterns
//  */

// // /**
// //  * Request notification permission with user-friendly dialog
// //  * @returns {Promise<boolean>} - Promise that resolves to true if permission granted
// //  */
// // export async function requestNotificationPermission() {
// //     if (!('Notification' in window)) {
// //         showError('System notifications are not supported in this browser');
// //         return false;
// //     }

// //     if (Notification.permission === 'granted') {
// //         return true;
// //     }

// //     if (Notification.permission === 'denied') {
// //         showError('Notification permission has been denied. Please enable notifications in your browser settings.');
// //         return false;
// //     }

// //     // Show a friendly permission request dialog
// //     const granted = await showConfirmDialog(
// //         'Would you like to receive system notifications for workflow updates?',
// //         'Allow Notifications',
// //         'Not Now'
// //     );

// //     if (granted) {
// //         const permission = await Notification.requestPermission();
// //         if (permission === 'granted') {
// //             showSuccess('Notification permission granted! You will now receive system notifications.');
// //             return true;
// //         } else {
// //             showWarning('Notification permission was not granted. You can enable it later in browser settings.');
// //             return false;
// //         }
// //     }

// //     return false;
// // }

// // Default export with all functions
// export default {
//     DialogButtonType,
//     DialogResult,
//     beginDialogBox,
//     endDialogBox,
//     showMessage,
//     showError,
//     showSuccess,
//     showWarning,
//     showInfo,
//     showConfirmDialog,
//     showToast,
//     showToastInfo,
//     showToastSuccess,
//     showToastError,
//     showToastWarning,
//     // // Windows System Notification Functions
//     // checkNotificationSupport,
//     // showSystemNotification,
//     // closeNotificationsByTag,
//     // requestNotificationPermission
// };

