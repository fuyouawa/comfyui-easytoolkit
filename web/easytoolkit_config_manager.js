import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

/**
 * Extension for EasyToolkitConfigManager node
 * Adds buttons for managing YAML configuration
 */
app.registerExtension({
    name: "EasyToolkit.ConfigManager",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EasyToolkitConfigManager") {
            
            // Store the original onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = async function() {
                // Call the original onNodeCreated if it exists
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                
                // Load current configuration when node is created
                await this.loadCurrentConfig();
                
                // Add custom buttons
                this.addCustomButtons();
            };
            
            /**
             * Called when the node is loaded from the workflow
             */
            const origConfigure = nodeType.prototype.configure;
            nodeType.prototype.configure = async function(info) {
                // Call the original configure if it exists
                if (origConfigure) {
                    origConfigure.apply(this, arguments);
                }
                
                // Reload configuration when node is configured from workflow
                await this.loadCurrentConfig();
            };
            
            /**
             * Load current configuration from the server and populate the text widget
             */
            nodeType.prototype.loadCurrentConfig = async function() {
                try {
                    const response = await api.fetchApi("/easytoolkit_config/get_current_config", {
                        method: "GET"
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            this.setConfigYaml(data.config_yaml);
                            console.log("[EasyToolkit] Configuration loaded");
                        }
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to load configuration:", error);
                }
            };
            
            /**
             * Get the YAML text widget and set its value
             */
            nodeType.prototype.setConfigYaml = function(yamlText) {
                for (const widget of this.widgets) {
                    if (widget.name === "config_yaml") {
                        widget.value = yamlText;
                        break;
                    }
                }
            };
            
            /**
             * Get the YAML text from the widget
             */
            nodeType.prototype.getConfigYaml = function() {
                for (const widget of this.widgets) {
                    if (widget.name === "config_yaml") {
                        return widget.value;
                    }
                }
                return "";
            };
            
            /**
             * Add custom buttons to the node
             */
            nodeType.prototype.addCustomButtons = function() {
                // Button: Save (to override)
                this.addWidget("button", "Save YAML", null, () => {
                    this.saveOverride();
                });
                
                // Button: Restore (delete override)
                this.addWidget("button", "Restore YAML", null, () => {
                    this.deleteOverride();
                });
            };
            
            /**
             * Save configuration override
             */
            nodeType.prototype.saveOverride = async function() {
                try {
                    const yamlText = this.getConfigYaml();
                    
                    if (!yamlText || !yamlText.trim()) {
                        app.ui.dialog.show("Error: Configuration is empty");
                        return;
                    }
                    
                    const response = await api.fetchApi("/easytoolkit_config/save_override", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ config_yaml: yamlText })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        app.ui.dialog.show(
                            "Configuration saved successfully!"
                        );
                        console.log("[EasyToolkit] Configuration saved");
                    } else {
                        app.ui.dialog.show("Failed to save: " + data.error);
                        console.error("[EasyToolkit] Failed to save:", data.error);
                    }
                } catch (error) {
                    app.ui.dialog.show("Error saving: " + error.message);
                    console.error("[EasyToolkit] Error saving:", error);
                }
            };
            
            /**
             * Delete configuration override
             */
            nodeType.prototype.deleteOverride = async function() {
                if (!confirm("Restore to default configuration?")) {
                    return;
                }
                
                try {
                    const response = await api.fetchApi("/easytoolkit_config/delete_override", {
                        method: "DELETE"
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Wait for configuration to reload and update the display
                        await this.loadCurrentConfig();
                        app.ui.dialog.show(
                            "Configuration restored!\n" +
                            "Restart ComfyUI to apply changes."
                        );
                        console.log("[EasyToolkit] Configuration restored");
                    } else {
                        app.ui.dialog.show("Failed to restore: " + data.error);
                        console.error("[EasyToolkit] Failed to restore:", data.error);
                    }
                } catch (error) {
                    app.ui.dialog.show("Error restoring: " + error.message);
                    console.error("[EasyToolkit] Error restoring:", error);
                }
            };
        }
    }
});
