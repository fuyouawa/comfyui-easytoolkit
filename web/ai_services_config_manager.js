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

            nodeType.prototype.onNodeCreated = async function () {
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

                // Try to load cached configuration from field first
                const configDataWidget = this.widgets.find(w => w.name === "config_data");
                configDataWidget.hidden = true;

                // Add configure callback to handle config_data changes
                const originalConfigure = configDataWidget.configure;
                configDataWidget.configure = () => {
                    if (originalConfigure) {
                        originalConfigure.call(configDataWidget);
                    }

                    setTimeout(() => {
                        if (configDataWidget.value && configDataWidget.value !== "{}") {
                            try {
                                const cachedConfig = JSON.parse(configDataWidget.value);
                                if (cachedConfig.servicesData && Array.isArray(cachedConfig.servicesData)) {
                                    this.servicesData = cachedConfig.servicesData;
                                    console.log("[EasyToolkit] Loaded cached AI services configuration:", this.servicesData.length, "services");

                                    // Update service count widget
                                    if (serviceCountWidget) {
                                        serviceCountWidget.value = this.servicesData.length;
                                    }

                                    // Rebuild widgets with cached data
                                    this.updateServiceWidgets(this.servicesData.length);

                                    // Add action buttons
                                    this.addActionButtons();
                                    return;
                                }
                            } catch (error) {
                                console.warn("[EasyToolkit] Failed to parse cached configuration:", error);
                            }
                        }

                        // If no cached config or parsing failed, load from server
                        this.loadAIServices();

                        // Add action buttons
                        this.addActionButtons();
                    }, 0);
                };

                // Trigger configure callback to process initial value
                configDataWidget.configure();
            };
            
            /**
             * Load AI services from server
             */
            nodeType.prototype.loadAIServices = async function () {
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

                            // Update cached configuration
                            this.saveCachedConfig();

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
            nodeType.prototype.updateServiceWidgets = function (count) {
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

                // Create widgets for each service
                for (let i = 0; i < count; i++) {
                    const service = this.servicesData[i];

                    // Service ID
                    const idWidget = this.addWidget("text", `service_${i}_id`, service.id, (value) => {
                        this.servicesData[i].id = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    idWidget.label = `Service ${i + 1} - ID`;
                    this.dynamicWidgets.push(idWidget);

                    // Service Label
                    const labelWidget = this.addWidget("text", `service_${i}_label`, service.label, (value) => {
                        this.servicesData[i].label = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    labelWidget.label = `Service ${i + 1} - Label`;
                    this.dynamicWidgets.push(labelWidget);

                    // Base URL
                    const urlWidget = this.addWidget("text", `service_${i}_url`, service.base_url, (value) => {
                        this.servicesData[i].base_url = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    urlWidget.label = `Service ${i + 1} - Base URL`;
                    this.dynamicWidgets.push(urlWidget);

                    // API Key
                    const keyWidget = this.addWidget("text", `service_${i}_key`, service.api_key, (value) => {
                        this.servicesData[i].api_key = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    keyWidget.label = `Service ${i + 1} - API Key`;
                    this.dynamicWidgets.push(keyWidget);

                    // Model
                    const modelWidget = this.addWidget("text", `service_${i}_model`, service.model, (value) => {
                        this.servicesData[i].model = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    modelWidget.label = `Service ${i + 1} - Model`;
                    this.dynamicWidgets.push(modelWidget);

                    // Timeout
                    const timeoutWidget = this.addWidget("number", `service_${i}_timeout`, service.timeout, (value) => {
                        this.servicesData[i].timeout = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    timeoutWidget.label = `Service ${i + 1} - Timeout`;
                    timeoutWidget.options = { min: 1, max: 3600, step: 1 };
                    this.dynamicWidgets.push(timeoutWidget);

                    const separateWidget = this.addWidget("text", '', null, null);
                    separateWidget.value = '';
                    separateWidget.hidden = true;
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
            nodeType.prototype.removeDynamicWidgets = function () {
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
            nodeType.prototype.reorderWidgets = function () {
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
            nodeType.prototype.addActionButtons = function () {
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
            nodeType.prototype.saveAIServices = async function () {
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

                        // Update cached configuration
                        this.saveCachedConfig();
                    } else {
                        showError("Failed to save", new Error(data.error));
                    }
                } catch (error) {
                    showError("Error saving", error);
                }
            };

            /**
             * Save configuration to hidden field for persistence
             */
            nodeType.prototype.saveCachedConfig = function () {
                const configDataWidget = this.widgets.find(w => w.name === "config_data");
                if (configDataWidget) {
                    const cachedConfig = {
                        servicesData: this.servicesData,
                        timestamp: new Date().toISOString()
                    };
                    configDataWidget.value = JSON.stringify(cachedConfig);
                    console.log("[EasyToolkit] Cached configuration updated");
                }
            };
        }
    }
});

