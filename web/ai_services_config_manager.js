import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { showError, showSuccess, showToastSuccess, showToastError } from "./box_utils.js";

/**
 * Extension for AIServicesConfigManager node
 * Dynamically generates widgets for managing AI services configuration
 */
app.registerExtension({
    name: "EasyToolkit.AIServicesConfigManager",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "AIServicesConfigManager") {
            
            // Store the original onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = async function() {
                // Call the original onNodeCreated if it exists
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                // Initialize services data storage
                this.servicesData = [];
                
                // Track dynamic widgets
                this.dynamicWidgets = [];
                
                // Find the service_count widget and add change listener
                const serviceCountWidget = this.widgets.find(w => w.name === "service_count");
                if (serviceCountWidget) {
                    const originalCallback = serviceCountWidget.callback;
                    serviceCountWidget.callback = (value) => {
                        if (originalCallback) {
                            originalCallback.call(serviceCountWidget, value);
                        }
                        this.updateServiceWidgets(value);
                    };
                }
                
                // Load current configuration
                await this.loadAIServices();
                
                // Add action buttons
                this.addActionButtons();
            };
            
            /**
             * Load AI services from server
             */
            nodeType.prototype.loadAIServices = async function() {
                try {
                    const response = await api.fetchApi("/easytoolkit_config/get_ai_services", {
                        method: "GET"
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            this.servicesData = data.services || [];
                            
                            // Update service count
                            const serviceCountWidget = this.widgets.find(w => w.name === "service_count");
                            if (serviceCountWidget) {
                                serviceCountWidget.value = this.servicesData.length;
                            }
                            
                            // Rebuild widgets
                            this.updateServiceWidgets(this.servicesData.length);
                            
                            console.log("[EasyToolkit] AI Services loaded:", this.servicesData.length, "services");
                            showToastSuccess("Load Successful", `Loaded ${this.servicesData.length} AI service(s)`);
                        } else {
                            showToastError("Load Failed", data.error || "Unknown error");
                        }
                    } else {
                        showToastError("Load Failed", `HTTP ${response.status}`);
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to load AI services:", error);
                    showToastError("Load Failed", error.message || "Failed to load AI services");
                }
            };
            
            /**
             * Update service widgets based on count
             */
            nodeType.prototype.updateServiceWidgets = function(count) {
                // Remove all dynamic widgets
                this.removeDynamicWidgets();
                
                // Ensure servicesData has enough entries
                while (this.servicesData.length < count) {
                    this.servicesData.push({
                        id: '',
                        label: '',
                        base_url: '',
                        api_key: '',
                        model: '',
                        timeout: 300
                    });
                }
                
                // Trim excess services
                if (this.servicesData.length > count) {
                    this.servicesData = this.servicesData.slice(0, count);
                }
                
                // Find insertion point (after service_count, before buttons)
                const serviceCountIndex = this.widgets.findIndex(w => w.name === "service_count");
                let insertIndex = serviceCountIndex + 1;

                const separateWidget = this.addWidget("text", '', null, null);
                separateWidget.value = '';
                separateWidget.disabled = true;
                this.dynamicWidgets.push(separateWidget);
                
                // Create widgets for each service
                for (let i = 0; i < count; i++) {
                    const service = this.servicesData[i];
                    
                    // Service ID
                    const idWidget = this.addWidget("text", `service_${i}_id`, service.id, (value) => {
                        this.servicesData[i].id = value;
                    });
                    idWidget.label = `Service ${i + 1} - ID`;
                    this.dynamicWidgets.push(idWidget);
                    
                    // Service Label
                    const labelWidget = this.addWidget("text", `service_${i}_label`, service.label, (value) => {
                        this.servicesData[i].label = value;
                    });
                    labelWidget.label = `Service ${i + 1} - Label`;
                    this.dynamicWidgets.push(labelWidget);
                    
                    // Base URL
                    const urlWidget = this.addWidget("text", `service_${i}_url`, service.base_url, (value) => {
                        this.servicesData[i].base_url = value;
                    });
                    urlWidget.label = `Service ${i + 1} - Base URL`;
                    this.dynamicWidgets.push(urlWidget);
                    
                    // API Key
                    const keyWidget = this.addWidget("text", `service_${i}_key`, service.api_key, (value) => {
                        this.servicesData[i].api_key = value;
                    });
                    keyWidget.label = `Service ${i + 1} - API Key`;
                    this.dynamicWidgets.push(keyWidget);
                    
                    // Model
                    const modelWidget = this.addWidget("text", `service_${i}_model`, service.model, (value) => {
                        this.servicesData[i].model = value;
                    });
                    modelWidget.label = `Service ${i + 1} - Model`;
                    this.dynamicWidgets.push(modelWidget);
                    
                    // Timeout
                    const timeoutWidget = this.addWidget("number", `service_${i}_timeout`, service.timeout, (value) => {
                        this.servicesData[i].timeout = value;
                    });
                    timeoutWidget.label = `Service ${i + 1} - Timeout`;
                    timeoutWidget.options = { min: 1, max: 3600, step: 1 };
                    this.dynamicWidgets.push(timeoutWidget);

                    const separateWidget = this.addWidget("text", '', null, null);
                    separateWidget.value = '';
                    separateWidget.disabled = true;
                    this.dynamicWidgets.push(separateWidget);
                }
                
                // Reorder widgets: service_count -> dynamic widgets -> buttons
                this.reorderWidgets();
                
                // Update node size (preserve width, only update height)
                const currentWidth = this.size[0];
                const newSize = this.computeSize();
                this.setSize([currentWidth, newSize[1]]);
            };
            
            /**
             * Remove all dynamic widgets
             */
            nodeType.prototype.removeDynamicWidgets = function() {
                for (const widget of this.dynamicWidgets) {
                    const index = this.widgets.indexOf(widget);
                    if (index > -1) {
                        this.widgets.splice(index, 1);
                    }
                }
                this.dynamicWidgets = [];
            };
            
            /**
             * Reorder widgets to maintain proper order
             */
            nodeType.prototype.reorderWidgets = function() {
                // Get button widgets
                const loadButton = this.widgets.find(w => w.name === "load_button");
                const saveButton = this.widgets.find(w => w.name === "save_button");
                
                if (loadButton) {
                    const index = this.widgets.indexOf(loadButton);
                    if (index > -1) {
                        this.widgets.splice(index, 1);
                        this.widgets.push(loadButton);
                    }
                }
                
                if (saveButton) {
                    const index = this.widgets.indexOf(saveButton);
                    if (index > -1) {
                        this.widgets.splice(index, 1);
                        this.widgets.push(saveButton);
                    }
                }
            };
            
            /**
             * Add action buttons
             */
            nodeType.prototype.addActionButtons = function() {
                // Button: Load
                const loadButton = this.addWidget("button", "Load AI Services", null, () => {
                    this.loadAIServices();
                });
                
                // Button: Save
                const saveButton = this.addWidget("button", "Save AI Services", null, () => {
                    this.saveAIServices();
                });
            };
            
            /**
             * Save AI services to server
             */
            nodeType.prototype.saveAIServices = async function() {
                try {
                    // Validate services
                    const validServices = this.servicesData.filter(s => s.id && s.id.trim());
                    
                    if (validServices.length === 0) {
                        showError("At least one service with valid ID is required");
                        return;
                    }
                    
                    // Check for duplicate IDs
                    const ids = validServices.map(s => s.id);
                    const uniqueIds = new Set(ids);
                    if (ids.length !== uniqueIds.size) {
                        showError("Duplicate service IDs found");
                        return;
                    }
                    
                    const response = await api.fetchApi("/easytoolkit_config/save_ai_services", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ services: validServices })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showSuccess(
                            `AI Services configuration saved successfully!\nSaved ${validServices.length} service(s).`
                        );
                        console.log("[EasyToolkit] AI Services saved");
                    } else {
                        showError("Failed to save", new Error(data.error));
                    }
                } catch (error) {
                    showError("Error saving", error);
                }
            };
        }
    }
});

