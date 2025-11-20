// import { app } from "../../../scripts/app.js";
// import { api } from "../../../scripts/api.js";
// import { showError, showSuccess, showToastSuccess, showToastError, beginDialogBox, endDialogBox, DialogButtonType, DialogResult, showConfirmDialog } from "../box_utils.js";
// import { createFormContainer, createFormField, createTextarea } from "../ui_utils.js";

// /**
//  * Extension for AIAgentsConfig node
//  * Dynamically generates widgets for managing AI agents configuration
//  */
// app.registerExtension({
//     name: "EasyToolkit.AIAgentsConfig",

//     async beforeRegisterNodeDef(nodeType, nodeData, app) {
//         if (nodeData.name === "AIAgentsConfig") {

//             // Store the original onNodeCreated
//             const onNodeCreated = nodeType.prototype.onNodeCreated;

//             nodeType.prototype.onNodeCreated = async function () {
//                 // Call the original onNodeCreated if it exists
//                 if (onNodeCreated) {
//                     onNodeCreated.apply(this, arguments);
//                 }

//                 // Initialize agents data storage
//                 this.agentsData = [];
//                 this.defaultAgent = '';

//                 // Track dynamic widgets
//                 this.dynamicWidgets = [];


//                 // Try to load cached configuration from field first
//                 const configDataWidget = this.widgets.find(w => w.name === "config_data");
//                 configDataWidget.hidden = true;

//                 // Add configure callback to handle config_data changes
//                 const originalConfigure = configDataWidget.configure;
//                 configDataWidget.configure = () => {
//                     if (originalConfigure) {
//                         originalConfigure.call(configDataWidget);
//                     }

//                     setTimeout(() => {
//                         if (configDataWidget.value && configDataWidget.value !== "{}") {
//                             try {
//                                 const cachedConfig = JSON.parse(configDataWidget.value);
//                                 if (cachedConfig.agentsData && Array.isArray(cachedConfig.agentsData)) {
//                                     this.agentsData = cachedConfig.agentsData;
//                                     this.defaultAgent = cachedConfig.defaultAgent || '';
//                                     console.log("[EasyToolkit] Loaded cached AI agents configuration:", this.agentsData.length, "agents", "default:", this.defaultAgent);


//                                     // Rebuild widgets with cached data (includes action buttons)
//                                     this.updateAgentWidgets();
//                                     return;
//                                 }
//                             } catch (error) {
//                                 console.warn("[EasyToolkit] Failed to parse cached configuration:", error);
//                             }
//                         }

//                         // If no cached config or parsing failed, load from server
//                         this.loadAIAgents();
//                     }, 0);
//                 };

//                 // Trigger configure callback to process initial value
//                 configDataWidget.configure();
//             };

//             /**
//              * Load AI agents from server
//              */
//             nodeType.prototype.loadAIAgents = async function () {
//                 try {
//                     const response = await api.fetchApi("/easytoolkit_config/get_ai_agents", {
//                         method: "GET"
//                     });

//                     if (response.ok) {
//                         const data = await response.json();
//                         if (data.success) {
//                             this.agentsData = data.agents || [];
//                             this.defaultAgent = data.default_agent || '';


//                             // Rebuild widgets (includes action buttons)
//                             this.updateAgentWidgets();

//                             // Update cached configuration
//                             this.saveCachedConfig();

//                             console.log("[EasyToolkit] AI Agents loaded:", this.agentsData.length, "agents", "default:", this.defaultAgent);
//                             showToastSuccess("Load Successful", `Loaded ${this.agentsData.length} AI agent(s)`);
//                         } else {
//                             showToastError("Load Failed", data.error || "Unknown error");
//                         }
//                     } else {
//                         showToastError("Load Failed", `HTTP ${response.status}`);
//                     }
//                 } catch (error) {
//                     console.error("[EasyToolkit] Failed to load AI agents:", error);
//                     showToastError("Load Failed", error.message || "Failed to load AI agents");
//                 }
//             };

//             /**
//              * Update agent widgets based on current agents data
//              */
//             nodeType.prototype.updateAgentWidgets = function () {
//                 // Remove all dynamic widgets and action buttons
//                 this.removeDynamicWidgets();
//                 this.removeActionButtons();


//                 // Update default agent options
//                 this.updateDefaultAgentOptions();

//                 // Find insertion point (before buttons)
//                 let insertIndex = this.widgets.length;

//                 // Find default agent selection widget
//                 const defaultAgentWidget = this.widgets.find(w => w.name === "default_agent");
//                 if (defaultAgentWidget) {
//                     defaultAgentWidget.value = this.defaultAgent;
//                     defaultAgentWidget.callback = (value) => {
//                         this.defaultAgent = value;
//                         this.saveCachedConfig(); // Update cache on change
//                     };
//                     defaultAgentWidget.options = {
//                         values: ["", ...this.agentsData.map(a => a.id).filter(id => id)]
//                     };
//                 }

//                 // Create widgets for each agent
//                 for (let i = 0; i < this.agentsData.length; i++) {
//                     const agent = this.agentsData[i];

//                     // Agent ID
//                     const idWidget = this.addWidget("text", `agent_${i}_id`, agent.id, (value) => {
//                         this.agentsData[i].id = value;
//                         this.saveCachedConfig(); // Update cache on change
//                         this.updateDefaultAgentOptions(); // Update default agent options
//                     });
//                     idWidget.label = `Agent ${i + 1} - ID`;
//                     this.dynamicWidgets.push(idWidget);

//                     // Agent Label
//                     const labelWidget = this.addWidget("text", `agent_${i}_label`, agent.label, (value) => {
//                         this.agentsData[i].label = value;
//                         this.saveCachedConfig(); // Update cache on change
//                     });
//                     labelWidget.label = `Agent ${i + 1} - Label`;
//                     this.dynamicWidgets.push(labelWidget);

//                     // Summary (button to open dialog)
//                     const summaryWidget = this.addWidget("button", `agent_${i}_summary`, null, () => {
//                         this.showSummaryDialog(i);
//                     });
//                     summaryWidget.label = `📝 Open Agent ${i + 1} - Summary Editor`;
//                     this.dynamicWidgets.push(summaryWidget);

//                     // Delete button (only show for agents with valid IDs)
//                     const deleteWidget = this.addWidget("button", `agent_${i}_delete`, null, () => {
//                         this.deleteAgent(i);
//                     });
//                     deleteWidget.label = `❌ Delete Agent ${i + 1}`;
//                     this.dynamicWidgets.push(deleteWidget);

//                     const separateWidget = this.addWidget("text", '', null, null);
//                     separateWidget.value = '';
//                     separateWidget.hidden = true;
//                     this.dynamicWidgets.push(separateWidget);
//                 }

//                 // Add action buttons
//                 this.addActionButtons();

//                 // Update node size (preserve width, only update height)
//                 const currentWidth = this.size[0];
//                 const newSize = this.computeSize();
//                 this.setSize([currentWidth, newSize[1]]);
//             };

//             /**
//              * Update default agent widget options based on available agent IDs
//              */
//             nodeType.prototype.updateDefaultAgentOptions = function () {
//                 const defaultAgentWidget = this.widgets.find(w => w.name === "default_agent");
//                 if (defaultAgentWidget) {
//                     const availableIds = ["", ...this.agentsData.map(a => a.id).filter(id => id)];
//                     defaultAgentWidget.options.values = availableIds;

//                     // If current default agent is not in available IDs, reset it
//                     if (this.defaultAgent && !availableIds.includes(this.defaultAgent)) {
//                         this.defaultAgent = '';
//                         defaultAgentWidget.value = '';
//                         this.saveCachedConfig();
//                     }
//                 }
//             };

//             /**
//              * Remove all dynamic widgets
//              */
//             nodeType.prototype.removeDynamicWidgets = function () {
//                 for (const widget of this.dynamicWidgets) {
//                     const index = this.widgets.indexOf(widget);
//                     if (index > -1) {
//                         this.widgets.splice(index, 1);
//                     }
//                 }
//                 this.dynamicWidgets = [];
//             };

//             /**
//              * Add action buttons
//              */
//             nodeType.prototype.addActionButtons = function () {
//                 // Button: Add
//                 const addButton = this.addWidget("button", "add_ai_agent", null, () => {
//                     this.showAddAgentDialog();
//                 });
//                 addButton.label = "➕ Add New AI Agent";

//                 // Button: Load
//                 const loadButton = this.addWidget("button", "load_ai_agents", null, () => {
//                     this.loadAIAgents();
//                 });
//                 loadButton.label = "📥 Load AI Agents";

//                 // Button: Save
//                 const saveButton = this.addWidget("button", "save_ai_agents", null, () => {
//                     this.saveAIAgents();
//                 });
//                 saveButton.label = "💾 Save AI Agents";

//                 // Button: Reset
//                 const resetButton = this.addWidget("button", "reset_ai_agents", null, () => {
//                     this.resetAIAgents();
//                 });
//                 resetButton.label = "🔄 Reset AI Agents";
//             };

//             /**
//              * Show dialog for adding a new AI agent
//              */
//             nodeType.prototype.showAddAgentDialog = function () {
//                 // Begin dialog box
//                 const dialogContext = beginDialogBox("Add New AI Agent", {
//                     minWidth: 500,
//                     maxWidth: 700
//                 });

//                 // Create form container
//                 const formContainer = createFormContainer();

//                 // Create form fields using utility functions
//                 const idField = createFormField(
//                     'Agent ID *',
//                     'input',
//                     {
//                         placeholder: 'Enter unique agent ID'
//                     }
//                 );

//                 const labelField = createFormField(
//                     'Agent Label',
//                     'input',
//                     {
//                         placeholder: 'Enter agent display label'
//                     }
//                 );

//                 const summaryField = createFormField(
//                     'Agent Summary',
//                     'textarea',
//                     {
//                         placeholder: 'Enter agent description/summary',
//                         height: '150px'
//                     }
//                 );

//                 // Add all form elements to container
//                 formContainer.appendChild(idField.container);
//                 formContainer.appendChild(labelField.container);
//                 formContainer.appendChild(summaryField.container);

//                 // Add form to dialog content
//                 dialogContext.content.appendChild(formContainer);

//                 // End dialog box with OK/Cancel buttons
//                 endDialogBox(dialogContext, DialogButtonType.OK_CANCEL, (result) => {
//                     if (result === DialogResult.OK) {
//                         const newAgent = {
//                             id: idField.field.value.trim(),
//                             label: labelField.field.value.trim(),
//                             summary: summaryField.field.value.trim()
//                         };

//                         // Validate input
//                         if (!newAgent.id) {
//                             showToastError("Validation Error", "Agent ID is required");
//                             return;
//                         }

//                         // Check for duplicate ID
//                         const existingIds = this.agentsData.map(a => a.id);
//                         if (existingIds.includes(newAgent.id)) {
//                             showToastError("Validation Error", `Agent ID "${newAgent.id}" already exists`);
//                             return;
//                         }

//                         this.addNewAgent(newAgent);
//                     }
//                 });

//                 // Focus ID input
//                 setTimeout(() => idField.field.focus(), 0);
//             };

//             /**
//              * Remove action buttons
//              */
//             nodeType.prototype.removeActionButtons = function () {
//                 // Remove Add button
//                 const addButton = this.widgets.find(w => w.name === "add_ai_agent");
//                 if (addButton) {
//                     const index = this.widgets.indexOf(addButton);
//                     if (index > -1) {
//                         this.widgets.splice(index, 1);
//                     }
//                 }

//                 // Remove Load button
//                 const loadButton = this.widgets.find(w => w.name === "load_ai_agents");
//                 if (loadButton) {
//                     const index = this.widgets.indexOf(loadButton);
//                     if (index > -1) {
//                         this.widgets.splice(index, 1);
//                     }
//                 }

//                 // Remove Save button
//                 const saveButton = this.widgets.find(w => w.name === "save_ai_agents");
//                 if (saveButton) {
//                     const index = this.widgets.indexOf(saveButton);
//                     if (index > -1) {
//                         this.widgets.splice(index, 1);
//                     }
//                 }

//                 // Remove Reset button
//                 const resetButton = this.widgets.find(w => w.name === "reset_ai_agents");
//                 if (resetButton) {
//                     const index = this.widgets.indexOf(resetButton);
//                     if (index > -1) {
//                         this.widgets.splice(index, 1);
//                     }
//                 }
//             };

//             /**
//              * Add a new AI agent to the configuration
//              */
//             nodeType.prototype.addNewAgent = function (agent) {
//                 // Add the new agent to agentsData
//                 this.agentsData.push(agent);


//                 // Rebuild widgets with updated data
//                 this.updateAgentWidgets();

//                 // Update cached configuration
//                 this.saveCachedConfig();

//                 // Show success message
//                 showToastSuccess("Agent Added", `Agent "${agent.id}" has been added successfully`);
//                 console.log("[EasyToolkit] New AI Agent added:", agent.id);
//             };

//             /**
//              * Show dialog for editing agent summary
//              */
//             nodeType.prototype.showSummaryDialog = function (agentIndex) {
//                 const agent = this.agentsData[agentIndex];
//                 const agentLabel = agent.label || `Agent ${agentIndex + 1}`;

//                 // Begin dialog box
//                 const dialogContext = beginDialogBox(`Edit Summary - ${agentLabel}`, {
//                     minWidth: 600,
//                     maxWidth: 800
//                 });

//                 // Create textarea for summary editing using utility function
//                 const textarea = createTextarea({
//                     value: agent.summary || '',
//                     height: '400px',
//                     padding: '10px'
//                 });

//                 // Add textarea to dialog content
//                 dialogContext.content.appendChild(textarea);

//                 // End dialog box with OK/Cancel buttons
//                 endDialogBox(dialogContext, DialogButtonType.OK_CANCEL, (result) => {
//                     if (result === DialogResult.OK) {
//                         this.agentsData[agentIndex].summary = textarea.value;
//                         this.saveCachedConfig(); // Update cache on change
//                     }
//                 });

//                 // Focus textarea
//                 setTimeout(() => textarea.focus(), 0);
//             };

//             /**
//              * Delete a specific AI agent
//              */
//             nodeType.prototype.deleteAgent = async function (agentIndex) {
//                 const agent = this.agentsData[agentIndex];

//                 if (!agent.id || !agent.id.trim()) {
//                     showToastError("Cannot Delete", "Agent ID is empty. Please provide a valid agent ID.");
//                     return;
//                 }

//                 // Confirm deletion
//                 const confirmMessage = `Are you sure you want to delete agent "${agent.id}"?\n\nThis action cannot be undone.`;

//                 const confirmed = await showConfirmDialog(confirmMessage);
//                 if (!confirmed) {
//                     return;
//                 }

//                 try {
//                     const response = await api.fetchApi("/easytoolkit_config/delete_ai_agent", {
//                         method: "POST",
//                         headers: {
//                             "Content-Type": "application/json"
//                         },
//                         body: JSON.stringify({
//                             agent_id: agent.id
//                         })
//                     });

//                     const data = await response.json();

//                     if (data.success) {
//                         showToastSuccess("Agent Deleted", `Agent "${agent.id}" has been deleted successfully.`);
//                         console.log("[EasyToolkit] AI Agent deleted:", agent.id);
//                     } else {
//                         showToastError("Delete Failed", data.error || "Failed to delete agent");
//                     }
//                 } catch (error) {
//                     console.error("[EasyToolkit] Failed to delete AI agent:", error);
//                     showToastError("Delete Failed", error.message || "Failed to delete agent");
//                 } finally {
//                     // Remove agent from local data
//                     this.agentsData.splice(agentIndex, 1);

//                     // Rebuild widgets with updated data
//                     this.updateAgentWidgets();

//                     // Update cached configuration
//                     this.saveCachedConfig();
//                 }
//             };

//             /**
//              * Save AI agents to server
//              */
//             nodeType.prototype.saveAIAgents = async function () {
//                 try {
//                     // Validate agents
//                     const validAgents = this.agentsData.filter(a => a.id && a.id.trim());

//                     if (validAgents.length === 0) {
//                         showError("At least one agent with valid ID is required");
//                         return;
//                     }

//                     // Check for duplicate IDs
//                     const ids = validAgents.map(a => a.id);
//                     const uniqueIds = new Set(ids);
//                     if (ids.length !== uniqueIds.size) {
//                         showError("Duplicate agent IDs found");
//                         return;
//                     }

//                     const response = await api.fetchApi("/easytoolkit_config/save_ai_agents", {
//                         method: "POST",
//                         headers: {
//                             "Content-Type": "application/json"
//                         },
//                         body: JSON.stringify({
//                             agents: validAgents,
//                             default_agent: this.defaultAgent
//                         })
//                     });

//                     const data = await response.json();

//                     if (data.success) {
//                         showSuccess(
//                             `AI Agents configuration saved successfully!\nSaved ${validAgents.length} agent(s).`
//                         );
//                         console.log("[EasyToolkit] AI Agents saved");

//                         // Update cached configuration
//                         this.saveCachedConfig();
//                     } else {
//                         showError("Failed to save", new Error(data.error));
//                     }
//                 } catch (error) {
//                     showError("Error saving", error);
//                 }
//             };

//             /**
//              * Reset AI agents configuration
//              */
//             nodeType.prototype.resetAIAgents = async function () {
//                 try {
//                     const response = await api.fetchApi("/easytoolkit_config/reset_ai_agents", {
//                         method: "POST",
//                         headers: {
//                             "Content-Type": "application/json"
//                         },
//                         body: JSON.stringify({})
//                     });

//                     const data = await response.json();

//                     if (data.success) {
//                         showSuccess(
//                             "AI Agents configuration reset successfully!\n" +
//                             "Override configuration has been removed and default settings restored."
//                         );
//                         console.log("[EasyToolkit] AI Agents reset");

//                         // Clear cached configuration
//                         this.agentsData = [];
//                         this.defaultAgent = '';
//                         this.saveCachedConfig();

//                         // Reload agents to get default configuration
//                         this.loadAIAgents();
//                     } else {
//                         showError("Failed to reset", new Error(data.error));
//                     }
//                 } catch (error) {
//                     showError("Error resetting", error);
//                 }
//             };

//             /**
//              * Save configuration to hidden field for persistence
//              */
//             nodeType.prototype.saveCachedConfig = function () {
//                 const configDataWidget = this.widgets.find(w => w.name === "config_data");
//                 if (configDataWidget) {
//                     const cachedConfig = {
//                         agentsData: this.agentsData,
//                         defaultAgent: this.defaultAgent,
//                         timestamp: new Date().toISOString()
//                     };
//                     configDataWidget.value = JSON.stringify(cachedConfig);
//                     console.log("[EasyToolkit] Cached configuration updated");
//                 }
//             };
//         }
//     }
// });


