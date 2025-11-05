/**
 * API Utilities - Fetch wrapper functions
 */

/**
 * Generic fetch request wrapper
 * @param {string} url - Request URL
 * @param {Object} options - Configuration options
 * @param {string} options.method - HTTP method (GET, POST, etc.)
 * @param {Object|FormData} options.data - Request data
 * @param {Object} options.headers - Custom headers
 * @param {boolean} options.silent - Whether to fail silently (no error thrown)
 * @param {number} options.timeout - Timeout in milliseconds
 * @returns {Promise<Object>} Parsed JSON response data
 */
export async function apiRequest(url, options = {}) {
    const {
        method = "GET",
        data = null,
        headers = {},
        silent = false,
        timeout = 30000
    } = options;

    const isFormData = data instanceof FormData;
    
    // Build fetch configuration
    const fetchOptions = {
        method: method.toUpperCase()
    };

    // Handle request body and headers
    if (data) {
        if (isFormData) {
            fetchOptions.body = data;
            // FormData will automatically set Content-Type
        } else {
            fetchOptions.body = JSON.stringify(data);
            fetchOptions.headers = {
                "Content-Type": "application/json",
                ...headers
            };
        }
    } else if (Object.keys(headers).length > 0) {
        fetchOptions.headers = headers;
    }

    try {
        // Add timeout control
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        fetchOptions.signal = controller.signal;

        const response = await fetch(url, fetchOptions);
        clearTimeout(timeoutId);

        if (!response.ok) {
            const error = new Error(`HTTP error! status: ${response.status}`);
            error.status = response.status;
            error.response = response;
            throw error;
        }

        const result = await response.json();
        
        // Check if business logic succeeded
        if (result.success === false && !silent) {
            const error = new Error(result.error || "Request failed");
            error.result = result;
            throw error;
        }

        return result;
    } catch (error) {
        if (error.name === 'AbortError') {
            const timeoutError = new Error(`Request timeout after ${timeout}ms`);
            timeoutError.isTimeout = true;
            if (!silent) throw timeoutError;
            return { success: false, error: timeoutError.message };
        }
        
        if (!silent) {
            console.error(`API request failed [${method} ${url}]:`, error);
            throw error;
        }
        
        return { success: false, error: error.message };
    }
}

/**
 * Simplified GET request
 * @param {string} url - Request URL
 * @param {Object} options - Additional configuration options
 * @returns {Promise<Object>}
 */
export async function apiGet(url, options = {}) {
    return apiRequest(url, { ...options, method: "GET" });
}

/**
 * Simplified POST request
 * @param {string} url - Request URL
 * @param {Object|FormData} data - Request data
 * @param {Object} options - Additional configuration options
 * @returns {Promise<Object>}
 */
export async function apiPost(url, data = null, options = {}) {
    return apiRequest(url, { ...options, method: "POST", data });
}

/**
 * Simplified PUT request
 * @param {string} url - Request URL
 * @param {Object|FormData} data - Request data
 * @param {Object} options - Additional configuration options
 * @returns {Promise<Object>}
 */
export async function apiPut(url, data = null, options = {}) {
    return apiRequest(url, { ...options, method: "PUT", data });
}

/**
 * Simplified DELETE request
 * @param {string} url - Request URL
 * @param {Object} options - Additional configuration options
 * @returns {Promise<Object>}
 */
export async function apiDelete(url, options = {}) {
    return apiRequest(url, { ...options, method: "DELETE" });
}

/**
 * Silent request - does not throw errors on failure
 * @param {string} url - Request URL
 * @param {Object} options - Configuration options
 * @returns {Promise<Object>}
 */
export async function apiSilent(url, options = {}) {
    return apiRequest(url, { ...options, silent: true });
}

