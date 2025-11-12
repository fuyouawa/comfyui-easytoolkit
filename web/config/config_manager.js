import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { showError, showSuccess, showToastSuccess, showToastError, beginDialogBox, endDialogBox, DialogButtonType, DialogResult, showConfirmDialog } from "../box_utils.js";

/**
 * Extension for ConfigManager node
 * Provides configuration management with apply, export, and import functionality
 */
app.registerExtension({
    name: "EasyToolkit.ConfigManager",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ConfigManager") {

            // Store the original onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = async function () {
                // Call the original onNodeCreated if it exists
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                // Load current settings
                this.loadCurrentSettings();
            };

            /**
             * Load current configuration settings
             */
            nodeType.prototype.loadCurrentSettings = async function () {
                try {
                    const response = await api.fetchApi("/easytoolkit_config/get_current_settings", {
                        method: "GET"
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            // Update storage directory widget value
                            const storageWidget = this.widgets.find(w => w.name === "storage_directory");
                            if (storageWidget) {
                                storageWidget.value = data.storage_directory || "input";
                            }
                            console.log("[EasyToolkit] Current settings loaded:", data.storage_directory);
                        } else {
                            console.warn("[EasyToolkit] Failed to load current settings:", data.error);
                        }
                    } else {
                        console.warn("[EasyToolkit] Failed to load current settings: HTTP", response.status);
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to load current settings:", error);
                }
            };

            /**
             * Apply configuration settings
             */
            nodeType.prototype.applySettings = async function () {
                try {
                    const storageWidget = this.widgets.find(w => w.name === "storage_directory");
                    const storageDirectory = storageWidget ? storageWidget.value : "input";

                    const response = await api.fetchApi("/easytoolkit_config/apply_settings", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            storage_directory: storageDirectory
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        showToastSuccess("Settings Applied", data.message);
                        console.log("[EasyToolkit] Configuration settings applied:", storageDirectory);
                    } else {
                        showToastError("Apply Failed", data.error || "Failed to apply settings");
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to apply settings:", error);
                    showToastError("Apply Failed", error.message || "Failed to apply settings");
                }
            };

            /**
             * Export configuration to JSON file
             */
            nodeType.prototype.exportConfig = async function () {
                try {
                    const response = await api.fetchApi("/easytoolkit_config/export_config", {
                        method: "GET"
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            // Create and download JSON file
                            const configJson = JSON.stringify(data.config, null, 2);
                            const blob = new Blob([configJson], { type: "application/json" });
                            const url = URL.createObjectURL(blob);

                            const a = document.createElement("a");
                            a.href = url;
                            a.download = `comfyui-easytoolkit-config-${new Date().toISOString().split('T')[0]}.json`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);

                            showToastSuccess("Export Successful", data.message);
                            console.log("[EasyToolkit] Configuration exported successfully");
                        } else {
                            showToastError("Export Failed", data.error || "Failed to export configuration");
                        }
                    } else {
                        showToastError("Export Failed", `HTTP ${response.status}`);
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to export configuration:", error);
                    showToastError("Export Failed", error.message || "Failed to export configuration");
                }
            };

            /**
             * Import configuration from JSON file
             */
            nodeType.prototype.importConfig = async function () {
                try {
                    // Create file input element
                    const fileInput = document.createElement("input");
                    fileInput.type = "file";
                    fileInput.accept = ".json";
                    fileInput.style.display = "none";

                    fileInput.onchange = async (event) => {
                        const file = event.target.files[0];
                        if (!file) {
                            return;
                        }

                        try {
                            const fileContent = await this.readFileAsText(file);
                            const configData = JSON.parse(fileContent);

                            // Validate JSON structure
                            if (typeof configData !== "object" || configData === null) {
                                showToastError("Import Failed", "Invalid configuration file format");
                                return;
                            }

                            // Confirm import
                            const confirmMessage = `Are you sure you want to import this configuration?\n\nThis will replace your current configuration settings.`;
                            const confirmed = await showConfirmDialog(confirmMessage);
                            if (!confirmed) {
                                return;
                            }

                            // Send import request
                            const response = await api.fetchApi("/easytoolkit_config/import_config", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({
                                    config: configData
                                })
                            });

                            const data = await response.json();

                            if (data.success) {
                                showToastSuccess("Import Successful", data.message);
                                console.log("[EasyToolkit] Configuration imported successfully");

                                // Reload current settings to reflect changes
                                this.loadCurrentSettings();
                            } else {
                                showToastError("Import Failed", data.error || "Failed to import configuration");
                            }
                        } catch (error) {
                            console.error("[EasyToolkit] Failed to parse configuration file:", error);
                            showToastError("Import Failed", "Invalid JSON file format");
                        }

                        // Clean up file input
                        document.body.removeChild(fileInput);
                    };

                    // Trigger file selection
                    document.body.appendChild(fileInput);
                    fileInput.click();

                } catch (error) {
                    console.error("[EasyToolkit] Failed to import configuration:", error);
                    showToastError("Import Failed", error.message || "Failed to import configuration");
                }
            };

            /**
             * Read file as text
             */
            nodeType.prototype.readFileAsText = function (file) {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target.result);
                    reader.onerror = (e) => reject(e);
                    reader.readAsText(file);
                });
            };

            /**
             * Add action buttons after node creation
             */
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (originalOnNodeCreated) {
                    originalOnNodeCreated.apply(this, arguments);
                }

                // Add action buttons
                this.addActionButtons();
            };

            /**
             * Add action buttons
             */
            nodeType.prototype.addActionButtons = function () {
                // Button: Apply Settings
                const applyButton = this.addWidget("button", "apply_settings", null, () => {
                    this.applySettings();
                });
                applyButton.label = "✅ Apply Settings";

                // Button: Export Config
                const exportButton = this.addWidget("button", "export_config", null, () => {
                    this.exportConfig();
                });
                exportButton.label = "📤 Export Configuration";

                // Button: Import Config
                const importButton = this.addWidget("button", "import_config", null, () => {
                    this.importConfig();
                });
                importButton.label = "📥 Import Configuration";
            };
        }
    }
});