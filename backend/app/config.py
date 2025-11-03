"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    
    # AWS-style credentials (if needed)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Proxy Configuration (ServiceNow Multi-Model Proxy)
    proxy_base_url: str = ""
    proxy_openai_endpoint: Optional[str] = None  # If different from default
    proxy_gemini_endpoint: Optional[str] = None  # If different from default
    proxy_claude_endpoint: Optional[str] = None  # If different from default
    
    # Proxy Custom Headers
    proxy_transaction_id: str = "stock-analysis-app"
    proxy_spoke_version: str = "v1.0"
    proxy_integration_source: str = "stock-researcher-app"
    
    # LLM provider settings
    # Controls which LLM is used for analysis (e.g., OpenAI, Gemini, Claude, local Ollama)
    default_llm_provider: str = "ollama-deepseek-r1"  # "openai", "gemini", "claude", "proxy-openai", "proxy-gemini", "proxy-claude", "ollama-llama3.1", "ollama-llama3.2", "ollama-deepseek-r1", "ollama-qwen2.5", "ollama-mixtral", "ollama-codellama"
    
    # Ollama Configuration (for local open-source models)
    ollama_base_url: str = "http://localhost:11434"
    
    # Frontend Configuration
    frontend_url: str = "http://localhost:5173"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    def validate_llm_config(self) -> bool:
        """Validate that at least one LLM provider is configured."""
        if self.default_llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if self.default_llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when using Gemini provider")
        if self.default_llm_provider.startswith("proxy"):
            # Proxy providers use the base URL
            if not self.proxy_base_url:
                raise ValueError("PROXY_BASE_URL is required when using proxy provider")
        if self.default_llm_provider.startswith("ollama"):
            # Ollama providers use the base URL (defaults to localhost:11434)
            if not self.ollama_base_url:
                raise ValueError("OLLAMA_BASE_URL is required when using Ollama provider")
        return True


# Global settings instance
settings = Settings()

