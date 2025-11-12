import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { showError, showSuccess, showToastSuccess, showToastError } from "../box_utils.js";

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
                
                // Set up link monitoring for real-time value sync
                this.setupLinkMonitoring();
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
                            showToastError("Load Failed", data.error || "Unknown error");
                        }
                    } else {
                        showToastError("Load Failed", `HTTP ${response.status}`);
                    }
                } catch (error) {
                    console.error("[EasyToolkit] Failed to load AI configuration:", error);
                    showToastError("Load Failed", error.message || "Failed to load AI configuration");
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
                this.animationTimer = null;
                this.processingStartTime = null;
                
                const processButton = this.addWidget("button", "ai_process", null, async () => {
                    if (this.isProcessing) {
                        // Stop processing
                        this.stopProcessing();
                    } else {
                        // Start processing
                        await this.processWithAI();
                    }
                });
                processButton.label = "🚀 AI Process";
                
                // Store button reference
                this.processButton = processButton;
                
                // Style the button (optional)
                processButton.serialize = false; // Don't save button state
            };
            
            /**
             * Start loading animation and timer
             */
            nodeType.prototype.startLoadingAnimation = function() {
                const cache = this.widgetCache;
                if (!cache.processedPrompt) return;
                
                // Loading spinner frames
                const spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
                let frameIndex = 0;
                
                // Record start time
                this.processingStartTime = Date.now();
                
                // Update animation every 100ms
                this.animationTimer = setInterval(() => {
                    const elapsed = Date.now() - this.processingStartTime;
                    const seconds = Math.floor(elapsed / 1000);
                    const minutes = Math.floor(seconds / 60);
                    const remainingSeconds = seconds % 60;
                    
                    const timeStr = minutes > 0 
                        ? `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
                        : `${remainingSeconds}s`;
                    
                    const spinner = spinnerFrames[frameIndex];
                    cache.processedPrompt.value = `${spinner} Processing with AI... (${timeStr})`;
                    
                    frameIndex = (frameIndex + 1) % spinnerFrames.length;
                    
                    // Force UI update
                    if (this.onResize) {
                        this.onResize(this.size);
                    }
                }, 100);
            };
            
            /**
             * Stop loading animation and timer
             */
            nodeType.prototype.stopLoadingAnimation = function() {
                if (this.animationTimer) {
                    clearInterval(this.animationTimer);
                    this.animationTimer = null;
                }
                this.processingStartTime = null;
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
                
                // Stop animation
                this.stopLoadingAnimation();
                
                // Reset button text
                if (this.processButton) {
                    this.processButton.label = "🚀 AI Process";
                }
                
                // Update processed prompt
                const cache = this.widgetCache;
                if (cache.processedPrompt) {
                    cache.processedPrompt.value = "⏹ Processing stopped by user";
                }
                
                console.log("[EasyToolkit] AI processing stopped by user");
            };
            
            /**
             * Set up link monitoring for real-time value synchronization
             */
            nodeType.prototype.setupLinkMonitoring = function() {
                // Store original onConnectionsChange if exists
                const originalOnConnectionsChange = this.onConnectionsChange;
                
                // Override onConnectionsChange to detect link changes
                this.onConnectionsChange = function(type, index, connected, link_info) {
                    // Call original handler if exists
                    if (originalOnConnectionsChange) {
                        originalOnConnectionsChange.apply(this, arguments);
                    }
                    
                    // Check if this is an input connection change (type === 1)
                    if (type === 1) {
                        // Update link sync immediately
                        this.updateLinkedValue();
                    }
                };
                
                // Set up periodic check for linked values
                this.setupPeriodicSync();
                
                // Initial check
                this.updateLinkedValue();
            };
            
            /**
             * Set up periodic synchronization with linked nodes
             */
            nodeType.prototype.setupPeriodicSync = function() {
                // Clear existing timer if any
                if (this.syncTimer) {
                    clearInterval(this.syncTimer);
                }
                
                // Check linked values every 100ms for real-time updates
                this.syncTimer = setInterval(() => {
                    if (!this.isProcessing) {
                        this.updateLinkedValue();
                    }
                }, 100);
            };
            
            /**
             * Update original_prompt value from linked node
             */
            nodeType.prototype.updateLinkedValue = function() {
                const cache = this.widgetCache;
                if (!cache.originalPrompt) return;
                
                // Find the input slot for original_prompt (usually slot 0)
                const inputSlot = this.inputs?.findIndex(input => input.name === "original_prompt");
                if (inputSlot === -1 || inputSlot === undefined) return;
                
                // Check if the input is connected
                const input = this.inputs[inputSlot];
                if (!input || !input.link) return;
                
                // Get the link information
                const graph = app.graph;
                if (!graph) return;
                
                const link = graph.links[input.link];
                if (!link) return;
                
                // Get the source node
                const sourceNode = graph.getNodeById(link.origin_id);
                if (!sourceNode) return;
                
                // Check if source node is AIPromptAssistant
                if (sourceNode.type !== "AIPromptAssistant") return;
                
                // Get the output slot index from the link
                const outputSlot = link.origin_slot;
                
                // Find which output is connected
                const sourceOutput = sourceNode.outputs?.[outputSlot];
                if (!sourceOutput) return;
                
                // Find the source node's widgets
                const sourceWidgets = sourceNode.widgets;
                if (!sourceWidgets) return;
                
                let sourceValue = "";
                
                // Determine which output is connected and get the corresponding value
                if (sourceOutput.name === "original_prompt") {
                    // Connected to original_prompt output
                    const sourceOriginalPrompt = sourceWidgets.find(w => w.name === "original_prompt");
                    if (sourceOriginalPrompt) {
                        sourceValue = sourceOriginalPrompt.value || "";
                    }
                } else if (sourceOutput.name === "processed_prompt") {
                    // Connected to processed_prompt output
                    const sourceProcessedPrompt = sourceWidgets.find(w => w.name === "processed_prompt");
                    if (sourceProcessedPrompt) {
                        sourceValue = sourceProcessedPrompt.value || "";
                    }
                }
                
                // Update the current node's original_prompt if value changed
                if (sourceValue && cache.originalPrompt.value !== sourceValue) {
                    cache.originalPrompt.value = sourceValue;
                    
                    // Force UI update
                    if (this.onResize) {
                        this.onResize(this.size);
                    }
                }
            };
            
            /**
             * Process prompt using AI
             */
            nodeType.prototype.processWithAI = async function() {
                const cache = this.widgetCache;
                
                if (!cache.originalPrompt || !cache.originalPrompt.value) {
                    showError("Original prompt is empty");
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
                    this.processButton.label = "⏹ Stop";
                }
                
                // Start loading animation with timer
                this.startLoadingAnimation();
                
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
                    
                    // Stop animation before updating final result
                    this.stopLoadingAnimation();
                    
                    if (data.success) {
                        // Calculate total processing time
                        const processingTime = this.processingStartTime 
                            ? ((Date.now() - this.processingStartTime) / 1000).toFixed(1)
                            : '?';
                        
                        // Update processed prompt widget
                        if (cache.processedPrompt) {
                            cache.processedPrompt.value = data.processed_prompt;
                        }
                        console.log(`[EasyToolkit] AI processing completed in ${processingTime}s`);
                        
                        // Trigger node update
                        if (this.onResize) {
                            this.onResize(this.size);
                        }
                    } else {
                        const errorMsg = data.error || "Unknown error";
                        if (cache.processedPrompt) {
                            cache.processedPrompt.value = `❌ Error: ${errorMsg}`;
                        }
                        showError("AI Processing Failed", new Error(errorMsg));
                    }
                } catch (error) {
                    // Stop animation on error
                    this.stopLoadingAnimation();
                    
                    // Check if it was aborted
                    if (error.name === 'AbortError') {
                        console.log("[EasyToolkit] AI processing was aborted");
                        return; // Don't show error dialog for user-initiated abort
                    }
                    
                    const errorMsg = error.message || "Network error";
                    if (cache.processedPrompt) {
                        cache.processedPrompt.value = `❌ Error: ${errorMsg}`;
                    }
                    showError("AI processing error", error);
                } finally {
                    // Reset processing state
                    this.isProcessing = false;
                    this.abortController = null;
                    
                    // Reset button text
                    if (this.processButton) {
                        this.processButton.label = "🚀 AI Process";
                    }
                }
            };
            
            /**
             * Clean up when node is removed
             */
            const origOnRemoved = nodeType.prototype.onRemoved;
            nodeType.prototype.onRemoved = function() {
                // Clean up sync timer
                if (this.syncTimer) {
                    clearInterval(this.syncTimer);
                    this.syncTimer = null;
                }
                
                // Clean up animation timer
                if (this.animationTimer) {
                    clearInterval(this.animationTimer);
                    this.animationTimer = null;
                }
                
                // Call original handler if exists
                if (origOnRemoved) {
                    origOnRemoved.apply(this, arguments);
                }
            };
        }
    }
});

