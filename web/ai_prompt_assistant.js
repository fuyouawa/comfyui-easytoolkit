import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

/**
 * Extension for AIPromptAssistant node
 * Adds AI processing button and dynamic dropdowns
 */
app.registerExtension({
    name: "EasyToolkit.AIPromptAssistant",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "AIPromptAssistant") {
            
            // Store the original onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = async function() {
                // Call the original onNodeCreated if it exists
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                // Load configuration and set up widgets
                await this.setupAIConfig();
                
                // Add AI process button
                this.addProcessButton();
                
                // Store widget references for easy access
                this.cacheWidgetReferences();
            };
            
            /**
             * Load AI configuration from server and update dropdowns
             */
            nodeType.prototype.setupAIConfig = async function() {
                try {
                    const response = await api.fetchApi("/easytoolkit_ai/get_config", {
                        method: "GET"
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            this.aiConfig = data;
                            this.updateServiceDropdown();
                            this.updateAgentDropdown();
                            console.log("[EasyToolkit] AI configuration loaded");
                        } else {
                            console.error("[EasyToolkit] Failed to load AI config:", data.error);
                        }
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to load AI configuration:", error);
                }
            };
            
            /**
             * Update AI service dropdown options
             */
            nodeType.prototype.updateServiceDropdown = function() {
                if (!this.aiConfig || !this.aiConfig.services) return;
                
                const serviceWidget = this.widgets.find(w => w.name === "ai_service");
                if (serviceWidget) {
                    // Create mappings between label and name
                    this.serviceLabelToName = {};
                    this.serviceNameToLabel = {};
                    this.aiConfig.services.forEach(s => {
                        this.serviceLabelToName[s.label] = s.name;
                        this.serviceNameToLabel[s.name] = s.label;
                    });
                    
                    // Update options with labels
                    serviceWidget.options.values = this.aiConfig.services.map(s => s.label);
                    
                    // Set default value (convert name to label for display)
                    const defaultName = this.aiConfig.default_service || "deepseek";
                    const defaultLabel = this.serviceNameToLabel[defaultName] || defaultName;
                    if (!serviceWidget.value || serviceWidget.value === "deepseek" || serviceWidget.value === "Deepseek") {
                        serviceWidget.value = defaultLabel;
                    } else if (this.serviceNameToLabel[serviceWidget.value]) {
                        // Convert existing name to label
                        serviceWidget.value = this.serviceNameToLabel[serviceWidget.value];
                    }
                }
            };
            
            /**
             * Update AI agent dropdown options
             */
            nodeType.prototype.updateAgentDropdown = function() {
                if (!this.aiConfig || !this.aiConfig.agents) return;
                
                const agentWidget = this.widgets.find(w => w.name === "ai_agent");
                if (agentWidget) {
                    // Create mappings between label and name
                    this.agentLabelToName = {};
                    this.agentNameToLabel = {};
                    this.aiConfig.agents.forEach(a => {
                        this.agentLabelToName[a.label] = a.name;
                        this.agentNameToLabel[a.name] = a.label;
                    });
                    
                    // Update options with labels
                    agentWidget.options.values = this.aiConfig.agents.map(a => a.label);
                    
                    // Set default value (convert name to label for display)
                    const defaultName = this.aiConfig.default_agent || "video_prompt_expansion";
                    const defaultLabel = this.agentNameToLabel[defaultName] || defaultName;
                    if (!agentWidget.value || agentWidget.value === "video_prompt_expansion" || agentWidget.value === "Video Prompt Expansion") {
                        agentWidget.value = defaultLabel;
                    } else if (this.agentNameToLabel[agentWidget.value]) {
                        // Convert existing name to label
                        agentWidget.value = this.agentNameToLabel[agentWidget.value];
                    }
                }
            };
            
            /**
             * Cache widget references for easy access
             */
            nodeType.prototype.cacheWidgetReferences = function() {
                this.widgetCache = {
                    originalPrompt: this.widgets.find(w => w.name === "original_prompt"),
                    aiService: this.widgets.find(w => w.name === "ai_service"),
                    aiAgent: this.widgets.find(w => w.name === "ai_agent"),
                    processedPrompt: this.widgets.find(w => w.name === "processed_prompt")
                };
            };
            
            /**
             * Add the AI process button
             */
            nodeType.prototype.addProcessButton = function() {
                // Initialize processing state
                this.isProcessing = false;
                this.abortController = null;
                
                const processButton = this.addWidget("button", "🚀 AI Process", null, async () => {
                    if (this.isProcessing) {
                        // Stop processing
                        this.stopProcessing();
                    } else {
                        // Start processing
                        await this.processWithAI();
                    }
                });
                
                // Store button reference
                this.processButton = processButton;
                
                // Style the button (optional)
                processButton.serialize = false; // Don't save button state
            };
            
            /**
             * Stop AI processing
             */
            nodeType.prototype.stopProcessing = function() {
                if (this.abortController) {
                    this.abortController.abort();
                    this.abortController = null;
                }
                this.isProcessing = false;
                
                // Reset button text
                if (this.processButton) {
                    this.processButton.name = "🚀 AI Process";
                }
                
                // Update processed prompt
                const cache = this.widgetCache;
                if (cache.processedPrompt) {
                    cache.processedPrompt.value = "⏹ Processing stopped by user";
                }
                
                console.log("[EasyToolkit] AI processing stopped by user");
            };
            
            /**
             * Process prompt using AI
             */
            nodeType.prototype.processWithAI = async function() {
                const cache = this.widgetCache;
                
                if (!cache.originalPrompt || !cache.originalPrompt.value) {
                    app.ui.dialog.show("Error: Original prompt is empty");
                    return;
                }
                
                const originalPrompt = cache.originalPrompt.value;
                
                // Get label values from widgets
                const aiServiceLabel = cache.aiService ? cache.aiService.value : "Deepseek";
                const aiAgentLabel = cache.aiAgent ? cache.aiAgent.value : "Video Prompt Expansion";
                
                // Convert labels to names for backend
                const aiService = this.serviceLabelToName && this.serviceLabelToName[aiServiceLabel] 
                    ? this.serviceLabelToName[aiServiceLabel] 
                    : aiServiceLabel.toLowerCase(); // fallback
                
                const aiAgent = this.agentLabelToName && this.agentLabelToName[aiAgentLabel]
                    ? this.agentLabelToName[aiAgentLabel]
                    : aiAgentLabel.toLowerCase().replace(/\s+/g, '_'); // fallback
                
                // Set processing state
                this.isProcessing = true;
                this.abortController = new AbortController();
                
                // Change button text
                if (this.processButton) {
                    this.processButton.name = "⏹ Stop";
                }
                
                // Show processing indicator
                if (cache.processedPrompt) {
                    cache.processedPrompt.value = "⏳ Processing with AI...";
                }
                
                try {
                    const response = await api.fetchApi("/easytoolkit_ai/process_prompt", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            original_prompt: originalPrompt,
                            ai_service: aiService,
                            ai_agent: aiAgent
                        }),
                        signal: this.abortController.signal
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Update processed prompt widget
                        if (cache.processedPrompt) {
                            cache.processedPrompt.value = data.processed_prompt;
                        }
                        console.log("[EasyToolkit] AI processing completed");
                        
                        // Trigger node update
                        if (this.onResize) {
                            this.onResize(this.size);
                        }
                    } else {
                        const errorMsg = data.error || "Unknown error";
                        if (cache.processedPrompt) {
                            cache.processedPrompt.value = `❌ Error: ${errorMsg}`;
                        }
                        app.ui.dialog.show("AI Processing Failed: " + errorMsg);
                        console.error("[EasyToolkit] AI processing failed:", errorMsg);
                    }
                } catch (error) {
                    // Check if it was aborted
                    if (error.name === 'AbortError') {
                        console.log("[EasyToolkit] AI processing was aborted");
                        return; // Don't show error dialog for user-initiated abort
                    }
                    
                    const errorMsg = error.message || "Network error";
                    if (cache.processedPrompt) {
                        cache.processedPrompt.value = `❌ Error: ${errorMsg}`;
                    }
                    app.ui.dialog.show("Error: " + errorMsg);
                    console.error("[EasyToolkit] AI processing error:", error);
                } finally {
                    // Reset processing state
                    this.isProcessing = false;
                    this.abortController = null;
                    
                    // Reset button text
                    if (this.processButton) {
                        this.processButton.name = "🚀 AI Process";
                    }
                }
            };
            
            /**
             * Serialize node data (save to workflow)
             */
            const origGetExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(_, options) {
                if (origGetExtraMenuOptions) {
                    origGetExtraMenuOptions.apply(this, arguments);
                }
                
                // Add menu option to reload config
                options.push({
                    content: "Reload AI Config",
                    callback: async () => {
                        await this.setupAIConfig();
                        app.ui.dialog.show("AI configuration reloaded");
                    }
                });
            };
        }
    }
});

