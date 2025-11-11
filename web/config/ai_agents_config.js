import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { showError, showSuccess, showToastSuccess, showToastError } from "../box_utils.js";

/**
 * Extension for AIAgentsConfig node
 * Dynamically generates widgets for managing AI agents configuration
 */
app.registerExtension({
    name: "EasyToolkit.AIAgentsConfig",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "AIAgentsConfig") {

            // Store the original onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = async function () {
                // Call the original onNodeCreated if it exists
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                // Initialize agents data storage
                this.agentsData = [];
                this.defaultAgent = '';

                // Track dynamic widgets
                this.dynamicWidgets = [];

                // Find the agent_count widget and add change listener
                const agentCountWidget = this.widgets.find(w => w.name === "agent_count");
                if (agentCountWidget) {
                    const originalCallback = agentCountWidget.callback;
                    agentCountWidget.callback = (value) => {
                        if (originalCallback) {
                            originalCallback.call(agentCountWidget, value);
                        }
                        this.updateAgentWidgets(value);
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
                                if (cachedConfig.agentsData && Array.isArray(cachedConfig.agentsData)) {
                                    this.agentsData = cachedConfig.agentsData;
                                    this.defaultAgent = cachedConfig.defaultAgent || '';
                                    console.log("[EasyToolkit] Loaded cached AI agents configuration:", this.agentsData.length, "agents", "default:", this.defaultAgent);

                                    // Update agent count widget
                                    if (agentCountWidget) {
                                        agentCountWidget.value = this.agentsData.length;
                                    }

                                    // Rebuild widgets with cached data (includes action buttons)
                                    this.updateAgentWidgets(this.agentsData.length);
                                    return;
                                }
                            } catch (error) {
                                console.warn("[EasyToolkit] Failed to parse cached configuration:", error);
                            }
                        }

                        // If no cached config or parsing failed, load from server
                        this.loadAIAgents();
                    }, 0);
                };

                // Trigger configure callback to process initial value
                configDataWidget.configure();
            };

            /**
             * Load AI agents from server
             */
            nodeType.prototype.loadAIAgents = async function () {
                try {
                    const response = await api.fetchApi("/easytoolkit_config/get_ai_agents", {
                        method: "GET"
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            this.agentsData = data.agents || [];
                            this.defaultAgent = data.default_agent || '';

                            // Update agent count
                            const agentCountWidget = this.widgets.find(w => w.name === "agent_count");
                            if (agentCountWidget) {
                                agentCountWidget.value = this.agentsData.length;
                            }

                            // Rebuild widgets (includes action buttons)
                            this.updateAgentWidgets(this.agentsData.length);

                            // Update cached configuration
                            this.saveCachedConfig();

                            console.log("[EasyToolkit] AI Agents loaded:", this.agentsData.length, "agents", "default:", this.defaultAgent);
                            showToastSuccess("Load Successful", `Loaded ${this.agentsData.length} AI agent(s)`);
                        } else {
                            showToastError("Load Failed", data.error || "Unknown error");
                        }
                    } else {
                        showToastError("Load Failed", `HTTP ${response.status}`);
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to load AI agents:", error);
                    showToastError("Load Failed", error.message || "Failed to load AI agents");
                }
            };

            /**
             * Update agent widgets based on count
             */
            nodeType.prototype.updateAgentWidgets = function (count) {
                // Remove all dynamic widgets and action buttons
                this.removeDynamicWidgets();
                this.removeActionButtons();

                // Ensure agentsData has enough entries
                while (this.agentsData.length < count) {
                    this.agentsData.push({
                        id: '',
                        label: '',
                        summary: ''
                    });
                }

                // Trim excess agents
                if (this.agentsData.length > count) {
                    this.agentsData = this.agentsData.slice(0, count);
                }

                // Update default agent options
                this.updateDefaultAgentOptions();

                // Find insertion point (after agent_count, before buttons)
                const agentCountIndex = this.widgets.findIndex(w => w.name === "agent_count");
                let insertIndex = agentCountIndex + 1;

                // Find default agent selection widget
                const defaultAgentWidget = this.widgets.find(w => w.name === "default_agent");
                if (defaultAgentWidget) {
                    defaultAgentWidget.value = this.defaultAgent;
                    defaultAgentWidget.callback = (value) => {
                        this.defaultAgent = value;
                        this.saveCachedConfig(); // Update cache on change
                    };
                    defaultAgentWidget.options = {
                        values: ["", ...this.agentsData.map(a => a.id).filter(id => id)]
                    };
                }

                // Create widgets for each agent
                for (let i = 0; i < count; i++) {
                    const agent = this.agentsData[i];

                    // Agent ID
                    const idWidget = this.addWidget("text", `agent_${i}_id`, agent.id, (value) => {
                        this.agentsData[i].id = value;
                        this.saveCachedConfig(); // Update cache on change
                        this.updateDefaultAgentOptions(); // Update default agent options
                    });
                    idWidget.label = `Agent ${i + 1} - ID`;
                    this.dynamicWidgets.push(idWidget);

                    // Agent Label
                    const labelWidget = this.addWidget("text", `agent_${i}_label`, agent.label, (value) => {
                        this.agentsData[i].label = value;
                        this.saveCachedConfig(); // Update cache on change
                    });
                    labelWidget.label = `Agent ${i + 1} - Label`;
                    this.dynamicWidgets.push(labelWidget);

                    // Summary (button to open dialog)
                    const summaryWidget = this.addWidget("button", `agent_${i}_summary`, "Edit Summary", () => {
                        this.showSummaryDialog(i);
                    });
                    summaryWidget.label = `Open Agent ${i + 1} - Summary Editor`;
                    this.dynamicWidgets.push(summaryWidget);

                    const separateWidget = this.addWidget("text", '', null, null);
                    separateWidget.value = '';
                    separateWidget.hidden = true;
                    this.dynamicWidgets.push(separateWidget);
                }

                // Add action buttons
                this.addActionButtons();

                // Reorder widgets: agent_count -> dynamic widgets -> buttons
                this.reorderWidgets();

                // Update node size (preserve width, only update height)
                const currentWidth = this.size[0];
                const newSize = this.computeSize();
                this.setSize([currentWidth, newSize[1]]);
            };

            /**
             * Update default agent widget options based on available agent IDs
             */
            nodeType.prototype.updateDefaultAgentOptions = function () {
                const defaultAgentWidget = this.widgets.find(w => w.name === "default_agent");
                if (defaultAgentWidget) {
                    const availableIds = ["", ...this.agentsData.map(a => a.id).filter(id => id)];
                    defaultAgentWidget.options.values = availableIds;

                    // If current default agent is not in available IDs, reset it
                    if (this.defaultAgent && !availableIds.includes(this.defaultAgent)) {
                        this.defaultAgent = '';
                        defaultAgentWidget.value = '';
                        this.saveCachedConfig();
                    }
                }
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
                const loadButton = this.addWidget("button", "Load AI Agents", null, () => {
                    this.loadAIAgents();
                });

                // Button: Save
                const saveButton = this.addWidget("button", "Save AI Agents", null, () => {
                    this.saveAIAgents();
                });

                // Button: Reset
                const resetButton = this.addWidget("button", "Reset AI Agents", null, () => {
                    this.resetAIAgents();
                });
            };

            /**
             * Remove action buttons
             */
            nodeType.prototype.removeActionButtons = function () {
                // Remove Load button
                const loadButton = this.widgets.find(w => w.name === "Load AI Agents");
                if (loadButton) {
                    const index = this.widgets.indexOf(loadButton);
                    if (index > -1) {
                        this.widgets.splice(index, 1);
                    }
                }

                // Remove Save button
                const saveButton = this.widgets.find(w => w.name === "Save AI Agents");
                if (saveButton) {
                    const index = this.widgets.indexOf(saveButton);
                    if (index > -1) {
                        this.widgets.splice(index, 1);
                    }
                }

                // Remove Reset button
                const resetButton = this.widgets.find(w => w.name === "Reset AI Agents");
                if (resetButton) {
                    const index = this.widgets.indexOf(resetButton);
                    if (index > -1) {
                        this.widgets.splice(index, 1);
                    }
                }
            };

            /**
             * Show dialog for editing agent summary
             */
            nodeType.prototype.showSummaryDialog = function (agentIndex) {
                const agent = this.agentsData[agentIndex];
                const agentLabel = agent.label || `Agent ${agentIndex + 1}`;

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
                dialog.style.minWidth = '600px';
                dialog.style.maxWidth = '800px';
                dialog.style.maxHeight = '80vh';
                dialog.style.display = 'flex';
                dialog.style.flexDirection = 'column';
                dialog.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';

                // Title
                const title = document.createElement('h3');
                title.textContent = `Edit Summary - ${agentLabel}`;
                title.style.margin = '0 0 15px 0';
                title.style.color = '#fff';
                title.style.fontSize = '18px';
                dialog.appendChild(title);

                // Textarea
                const textarea = document.createElement('textarea');
                textarea.value = agent.summary || '';
                textarea.style.width = '100%';
                textarea.style.height = '400px';
                textarea.style.padding = '10px';
                textarea.style.backgroundColor = '#2d2d2d';
                textarea.style.color = '#fff';
                textarea.style.border = '1px solid #555';
                textarea.style.borderRadius = '4px';
                textarea.style.fontSize = '14px';
                textarea.style.fontFamily = 'monospace';
                textarea.style.resize = 'vertical';
                textarea.style.marginBottom = '15px';
                textarea.style.boxSizing = 'border-box';
                dialog.appendChild(textarea);

                // Buttons container
                const buttonContainer = document.createElement('div');
                buttonContainer.style.display = 'flex';
                buttonContainer.style.justifyContent = 'flex-end';
                buttonContainer.style.gap = '10px';

                // Cancel button
                const cancelButton = document.createElement('button');
                cancelButton.textContent = 'Cancel';
                cancelButton.style.padding = '8px 20px';
                cancelButton.style.backgroundColor = '#555';
                cancelButton.style.color = '#fff';
                cancelButton.style.border = 'none';
                cancelButton.style.borderRadius = '4px';
                cancelButton.style.cursor = 'pointer';
                cancelButton.style.fontSize = '14px';
                cancelButton.onmouseover = () => {
                    cancelButton.style.backgroundColor = '#666';
                };
                cancelButton.onmouseout = () => {
                    cancelButton.style.backgroundColor = '#555';
                };
                cancelButton.onclick = () => {
                    document.body.removeChild(overlay);
                };

                // Ok button
                const okButton = document.createElement('button');
                okButton.textContent = 'Ok';
                okButton.style.padding = '8px 20px';
                okButton.style.backgroundColor = '#007acc';
                okButton.style.color = '#fff';
                okButton.style.border = 'none';
                okButton.style.borderRadius = '4px';
                okButton.style.cursor = 'pointer';
                okButton.style.fontSize = '14px';
                okButton.onmouseover = () => {
                    okButton.style.backgroundColor = '#0098ff';
                };
                okButton.onmouseout = () => {
                    okButton.style.backgroundColor = '#007acc';
                };
                okButton.onclick = () => {
                    this.agentsData[agentIndex].summary = textarea.value;
                    this.saveCachedConfig(); // Update cache on change
                    document.body.removeChild(overlay);
                };

                buttonContainer.appendChild(cancelButton);
                buttonContainer.appendChild(okButton);
                dialog.appendChild(buttonContainer);

                // Add dialog to overlay
                overlay.appendChild(dialog);

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

                // Add to body
                document.body.appendChild(overlay);

                // Focus textarea
                setTimeout(() => textarea.focus(), 0);
            };

            /**
             * Save AI agents to server
             */
            nodeType.prototype.saveAIAgents = async function () {
                try {
                    // Validate agents
                    const validAgents = this.agentsData.filter(a => a.id && a.id.trim());

                    if (validAgents.length === 0) {
                        showError("At least one agent with valid ID is required");
                        return;
                    }

                    // Check for duplicate IDs
                    const ids = validAgents.map(a => a.id);
                    const uniqueIds = new Set(ids);
                    if (ids.length !== uniqueIds.size) {
                        showError("Duplicate agent IDs found");
                        return;
                    }

                    const response = await api.fetchApi("/easytoolkit_config/save_ai_agents", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            agents: validAgents,
                            default_agent: this.defaultAgent
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        showSuccess(
                            `AI Agents configuration saved successfully!\nSaved ${validAgents.length} agent(s).`
                        );
                        console.log("[EasyToolkit] AI Agents saved");

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
             * Reset AI agents configuration
             */
            nodeType.prototype.resetAIAgents = async function () {
                try {
                    const response = await api.fetchApi("/easytoolkit_config/reset_ai_agents", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({})
                    });

                    const data = await response.json();

                    if (data.success) {
                        showSuccess(
                            "AI Agents configuration reset successfully!\n" +
                            "Override configuration has been removed and default settings restored."
                        );
                        console.log("[EasyToolkit] AI Agents reset");

                        // Clear cached configuration
                        this.agentsData = [];
                        this.defaultAgent = '';
                        this.saveCachedConfig();

                        // Reload agents to get default configuration
                        this.loadAIAgents();
                    } else {
                        showError("Failed to reset", new Error(data.error));
                    }
                } catch (error) {
                    showError("Error resetting", error);
                }
            };

            /**
             * Save configuration to hidden field for persistence
             */
            nodeType.prototype.saveCachedConfig = function () {
                const configDataWidget = this.widgets.find(w => w.name === "config_data");
                if (configDataWidget) {
                    const cachedConfig = {
                        agentsData: this.agentsData,
                        defaultAgent: this.defaultAgent,
                        timestamp: new Date().toISOString()
                    };
                    configDataWidget.value = JSON.stringify(cachedConfig);
                    console.log("[EasyToolkit] Cached configuration updated");
                }
            };
        }
    }
});


