import json
import os
from typing import Optional, Dict, Any
from .config import get_config

class ClientDisconnectedError(Exception):
    """Raised when client disconnects before AI request completes"""
    pass

class AIService:
    """
    AI service integration for prompt processing.
    Supports multiple AI providers (DeepSeek, OpenAI, Anthropic).
    """
    
    def __init__(self, service_name: Optional[str] = None):
        self.config = get_config()
        self.service_name = service_name or self.config.get('default_ai_service', 'deepseek')
        self.service_config = self._get_service_config()
    
    def _get_service_config(self) -> Dict[str, Any]:
        """Get configuration for the selected service"""
        services = self.config.get('ai_services', {})
        if self.service_name not in services:
            raise ValueError(f"AI service '{self.service_name}' not found in configuration")
        return services[self.service_name]
    
    def _get_api_key(self) -> str:
        """Get API key from config or environment variable"""
        # First try config
        api_key = self.service_config.get('api_key')
        if api_key and api_key.strip():
            return api_key.strip()
        
        # Try environment variable
        env_var_name = f"{self.service_name.upper()}_API_KEY"
        api_key = os.environ.get(env_var_name)
        if api_key and api_key.strip():
            return api_key.strip()
        
        raise ValueError(
            f"API key not found for {self.service_name}. "
            f"Please set it in config.yaml or as environment variable {env_var_name}"
        )
    
    def _create_request_payload(self, user_prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Create API request payload based on service type"""
        model = self.service_config.get('model', 'default')
        
        if self.service_name == 'anthropic':
            # Anthropic uses different message format
            return {
                "model": model,
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
        else:
            # OpenAI-compatible format (DeepSeek, OpenAI)
            return {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4096
            }
    
    def _extract_response_text(self, response_data: Dict[str, Any]) -> str:
        """Extract response text from API response"""
        if self.service_name == 'anthropic':
            # Anthropic response format
            content = response_data.get('content', [])
            if content and len(content) > 0:
                return content[0].get('text', '')
        else:
            # OpenAI-compatible format
            choices = response_data.get('choices', [])
            if choices and len(choices) > 0:
                message = choices[0].get('message', {})
                return message.get('content', '')
        
        raise ValueError("Failed to extract response text from API response")
    
    async def process_prompt(self, user_prompt: str, agent_name: Optional[str] = None, request=None) -> str:
        """
        Process a prompt using the AI service.
        
        Args:
            user_prompt: The user's input prompt
            agent_name: The agent preset to use (optional)
            request: The web request object for cancellation support (optional)
        
        Returns:
            Processed prompt from AI
        """
        # Get agent configuration
        agent_name = agent_name or self.config.get('default_ai_agent', 'video_prompt_expansion')
        agents = self.config.get('ai_agents', {})
        
        if agent_name not in agents:
            raise ValueError(f"AI agent '{agent_name}' not found in configuration")
        
        agent_config = agents[agent_name]
        system_prompt = agent_config.get('summary', '')
        
        if not system_prompt:
            raise ValueError(f"Agent '{agent_name}' has no system prompt configured")
        
        # Get API configuration
        base_url = self.service_config.get('base_url')
        api_key = self._get_api_key()
        timeout = self.service_config.get('timeout', 30)
        
        # Prepare request
        endpoint = f"{base_url}/chat/completions" if not base_url.endswith('/chat/completions') else base_url
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add authentication header based on service type
        if self.service_name == 'anthropic':
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        
        payload = self._create_request_payload(user_prompt, system_prompt)
        
        # Make request using aiohttp
        import aiohttp
        import asyncio
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create the API request task
                api_task = asyncio.create_task(
                    self._make_api_request(session, endpoint, headers, payload, timeout)
                )
                
                # If request object provided, monitor for disconnection
                if request:
                    disconnect_task = asyncio.create_task(
                        self._wait_for_client_disconnect(request)
                    )
                    
                    # Wait for either the API call to complete or client to disconnect
                    done, pending = await asyncio.wait(
                        [api_task, disconnect_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    
                    # Check which task completed
                    if disconnect_task in done:
                        api_task.cancel()
                        raise ClientDisconnectedError("Client disconnected - request cancelled")
                    
                    # Return the API result
                    return await api_task
                else:
                    # No request monitoring, just wait for API call
                    return await api_task
        
        except ClientDisconnectedError:
            # Re-raise client disconnection without wrapping
            raise
        except asyncio.CancelledError:
            raise ClientDisconnectedError("Request was cancelled")
        except Exception as e:
            raise Exception(f"Failed to process prompt with {self.service_name}: {str(e)}")
    
    async def _wait_for_client_disconnect(self, request) -> None:
        """
        Wait for client to disconnect by checking transport status periodically.
        This allows us to cancel the AI API request when the user clicks stop.
        """
        import asyncio
        
        while True:
            # Check if transport is closing or closed
            if request.transport is None:
                break
            
            # Check if transport is closing
            if hasattr(request.transport, 'is_closing') and request.transport.is_closing():
                break
            
            # For aiohttp, we can check the protocol
            try:
                if hasattr(request, 'protocol') and request.protocol is None:
                    break
                if hasattr(request, 'protocol') and hasattr(request.protocol, 'transport'):
                    if request.protocol.transport is None or request.protocol.transport.is_closing():
                        break
            except (AttributeError, RuntimeError):
                break
            
            # Sleep briefly before checking again
            await asyncio.sleep(0.1)
    
    async def _make_api_request(self, session, endpoint: str, headers: dict, payload: dict, timeout: int) -> str:
        """
        Make the actual API request to the AI service.
        Separated for easier cancellation handling.
        """
        import aiohttp
        
        async with session.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API request failed with status {response.status}: {error_text}")
            
            response_data = await response.json()
            return self._extract_response_text(response_data)

def get_ai_service(service_name: Optional[str] = None) -> AIService:
    """Factory function to create an AI service instance"""
    return AIService(service_name)

__all__ = ['AIService', 'ClientDisconnectedError', 'get_ai_service']

