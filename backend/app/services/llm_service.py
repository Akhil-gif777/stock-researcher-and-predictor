"""LLM service supporting multiple providers (OpenAI, Gemini, Claude, Proxy, Ollama)."""
from typing import Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
import httpx


class LLMService:
    """Service for interacting with LLM providers."""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM service with specified provider.
        
        Args:
            provider: "ollama-llama3.1", "ollama-qwen2.5", "ollama-mixtral", or "ollama-codellama". If None, uses default from settings.
        """
        self.provider = provider or settings.default_llm_provider
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> BaseChatModel:
        """Initialize the appropriate LLM based on provider."""
        
        # Ollama providers (local open-source models)
        if self.provider == "ollama-llama3.1":
            return self._create_ollama_llm("llama3.1:8b")
        
        elif self.provider == "ollama-llama3.2":
            return self._create_ollama_llm("llama3.2:latest")
        
        elif self.provider == "ollama-deepseek-r1":
            return self._create_ollama_llm("deepseek-r1:latest")
        
        elif self.provider == "ollama-qwen2.5":
            return self._create_ollama_llm("qwen2.5:7b")
        
        elif self.provider == "ollama-mixtral":
            return self._create_ollama_llm("mixtral:8x7b")
        
        elif self.provider == "ollama-codellama":
            return self._create_ollama_llm("codellama:7b")
        
        elif self.provider == "ollama-llama3.1-70b":
            return self._create_ollama_llm("llama3.1:70b")
        
        elif self.provider == "ollama-qwen2.5-72b":
            return self._create_ollama_llm("qwen2.5:72b")
        
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _create_ollama_llm(self, model_name: str) -> BaseChatModel:
        """Create Ollama LLM connection for local open-source models."""
        base_url = settings.ollama_base_url or "http://localhost:11434"
        
        return ChatOllama(
            base_url=base_url,
            model=model_name,
            temperature=0.7,
            request_timeout=120,  # Longer timeout for local models
            # Additional parameters for better performance
            num_ctx=4096,  # Context window size
            num_predict=2048,  # Max tokens to generate
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.1,
        )
    
    def invoke(self, system_prompt: str, user_message: str) -> str:
        """
        Invoke the LLM with system and user messages.
        
        Args:
            system_prompt: System prompt for context
            user_message: User's message/query
            
        Returns:
            LLM response as string
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    async def ainvoke(self, system_prompt: str, user_message: str) -> str:
        """Async invoke the LLM with system and user messages."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def invoke_structured(self, system_prompt: str, user_message: str, 
                         response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Invoke LLM with structured output format.
        
        This is useful when you need JSON or specific format responses.
        """
        # For now, return plain text. Can be enhanced with JSON mode later.
        return self.invoke(system_prompt, user_message)


# Global instance
def get_llm_service(provider: Optional[str] = None) -> LLMService:
    """Factory function to get LLM service instance."""
    return LLMService(provider)

