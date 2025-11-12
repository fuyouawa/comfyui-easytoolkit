/**
 * UI Component Utility Functions
 * Provides utility functions for creating and managing dialog UI components
 */

/**
 * Create label element
 * @param {string} text - Label text
 * @param {Object} options - Configuration options
 * @param {string} options.color - Text color (default: '#fff')
 * @param {string} options.fontSize - Font size (default: '14px')
 * @param {string} options.fontWeight - Font weight (default: 'bold')
 * @returns {HTMLLabelElement} Label element
 */
export function createLabel(text, options = {}) {
    const label = document.createElement('label');
    label.textContent = text;
    label.style.color = options.color || '#fff';
    label.style.fontSize = options.fontSize || '14px';
    label.style.fontWeight = options.fontWeight || 'bold';

    return label;
}

/**
 * Create input element
 * @param {Object} options - Configuration options
 * @param {string} options.type - Input type (default: 'text')
 * @param {string} options.placeholder - Placeholder text
 * @param {string} options.value - Initial value
 * @param {string} options.backgroundColor - Background color (default: '#2d2d2d')
 * @param {string} options.color - Text color (default: '#fff')
 * @param {string} options.border - Border style (default: '1px solid #555')
 * @param {string} options.borderRadius - Border radius (default: '4px')
 * @param {string} options.fontSize - Font size (default: '14px')
 * @param {string} options.padding - Padding (default: '8px')
 * @returns {HTMLInputElement} Input element
 */
export function createInput(options = {}) {
    const input = document.createElement('input');
    input.type = options.type || 'text';

    if (options.placeholder) input.placeholder = options.placeholder;
    if (options.value) input.value = options.value;

    input.style.padding = options.padding || '8px';
    input.style.backgroundColor = options.backgroundColor || '#2d2d2d';
    input.style.color = options.color || '#fff';
    input.style.border = options.border || '1px solid #555';
    input.style.borderRadius = options.borderRadius || '4px';
    input.style.fontSize = options.fontSize || '14px';
    input.style.boxSizing = 'border-box';

    return input;
}

/**
 * Create textarea element
 * @param {Object} options - Configuration options
 * @param {string} options.placeholder - Placeholder text
 * @param {string} options.value - Initial value
 * @param {string} options.width - Width (default: '100%')
 * @param {string} options.height - Height (default: '150px')
 * @param {string} options.backgroundColor - Background color (default: '#2d2d2d')
 * @param {string} options.color - Text color (default: '#fff')
 * @param {string} options.border - Border style (default: '1px solid #555')
 * @param {string} options.borderRadius - Border radius (default: '4px')
 * @param {string} options.fontSize - Font size (default: '14px')
 * @param {string} options.fontFamily - Font family (default: 'monospace')
 * @param {string} options.padding - Padding (default: '8px')
 * @param {string} options.resize - Resize behavior (default: 'vertical')
 * @returns {HTMLTextAreaElement} Textarea element
 */
export function createTextarea(options = {}) {
    const textarea = document.createElement('textarea');

    if (options.placeholder) textarea.placeholder = options.placeholder;
    if (options.value) textarea.value = options.value;

    textarea.style.width = options.width || '100%';
    textarea.style.height = options.height || '150px';
    textarea.style.padding = options.padding || '8px';
    textarea.style.backgroundColor = options.backgroundColor || '#2d2d2d';
    textarea.style.color = options.color || '#fff';
    textarea.style.border = options.border || '1px solid #555';
    textarea.style.borderRadius = options.borderRadius || '4px';
    textarea.style.fontSize = options.fontSize || '14px';
    textarea.style.fontFamily = options.fontFamily || 'monospace';
    textarea.style.resize = options.resize || 'vertical';
    textarea.style.boxSizing = 'border-box';

    return textarea;
}

/**
 * Create form container
 * @param {Object} options - Configuration options
 * @param {string} options.display - Display mode (default: 'flex')
 * @param {string} options.flexDirection - Layout direction (default: 'column')
 * @param {string} options.gap - Element spacing (default: '15px')
 * @returns {HTMLDivElement} Form container element
 */
export function createFormContainer(options = {}) {
    const container = document.createElement('div');
    container.style.display = options.display || 'flex';
    container.style.flexDirection = options.flexDirection || 'column';
    container.style.gap = options.gap || '15px';

    return container;
}

/**
 * Create form field container
 * @param {Object} options - Configuration options
 * @param {string} options.display - Display mode (default: 'flex')
 * @param {string} options.flexDirection - Layout direction (default: 'column')
 * @param {string} options.gap - Element spacing (default: '5px')
 * @returns {HTMLDivElement} Field container element
 */
export function createFieldContainer(options = {}) {
    const container = document.createElement('div');
    container.style.display = options.display || 'flex';
    container.style.flexDirection = options.flexDirection || 'column';
    container.style.gap = options.gap || '5px';

    return container;
}

/**
 * Create complete form field (label + input/textarea)
 * @param {string} labelText - Label text
 * @param {string} fieldType - Field type ('input' or 'textarea')
 * @param {Object} fieldOptions - Field configuration options
 * @param {Object} containerOptions - Container configuration options
 * @returns {Object} Object containing container, label and field
 */
export function createFormField(labelText, fieldType, fieldOptions = {}, containerOptions = {}) {
    const container = createFieldContainer(containerOptions);
    const label = createLabel(labelText);
    let field;

    if (fieldType === 'textarea') {
        field = createTextarea(fieldOptions);
    } else {
        field = createInput(fieldOptions);
    }

    container.appendChild(label);
    container.appendChild(field);

    return {
        container,
        label,
        field
    };
}

/**
 * Create message element
 * @param {string} message - Message text
 * @param {Object} [options] - Configuration options
 * @param {string} [options.color="#fff"] - Text color
 * @param {string} [options.fontSize="14px"] - Font size
 * @param {string} [options.lineHeight="1.5"] - Line height
 * @param {string} [options.whiteSpace="pre-wrap"] - White space handling
 * @param {string} [options.wordBreak="break-word"] - Word breaking
 * @returns {HTMLElement} - Styled message element
 */
export function createMessage(message, options = {}) {
    const {
        color = "#fff",
        fontSize = "14px",
        lineHeight = "1.5",
        whiteSpace = "pre-wrap",
        wordBreak = "break-word"
    } = options;

    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.style.color = color;
    messageElement.style.fontSize = fontSize;
    messageElement.style.lineHeight = lineHeight;
    messageElement.style.whiteSpace = whiteSpace;
    messageElement.style.wordBreak = wordBreak;

    return messageElement;
}