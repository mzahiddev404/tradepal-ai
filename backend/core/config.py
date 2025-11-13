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
    finnhub_api_key: Optional[str] = None  # Primary stock data source (Finnhub - 60 calls/min)
    alpha_vantage_api_key: Optional[str] = None  # Fallback stock data source (Alpha Vantage - 25 calls/day)
    
    # AWS Bedrock Configuration (optional, for orchestrator)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"  # Claude 3 Haiku for routing
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": ("settings_",)
    }


# Global settings instance
settings = Settings()

