"""
Configuration management for the FastAPI backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    frontend_url: str = "http://localhost:3000"
    
    # LLM Configuration
    llm_model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.1  # Very low temperature to minimize hallucination and ensure data accuracy
    max_tokens: Optional[int] = None
    
    # API Keys for additional services (optional)
    news_api_key: Optional[str] = None  # For news sentiment
    alpha_vantage_api_key: Optional[str] = None  # Primary stock data source (Alpha Vantage)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": ("settings_",)
    }


# Global settings instance
settings = Settings()

