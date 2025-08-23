from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Water Futures AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://water-futures-ai.web.app",
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/water_futures"
    )
    
    # GCP
    GCP_PROJECT_ID: str = "water-futures-ai"
    GCP_REGION: str = "us-central1"
    GCP_BUCKET_NAME: str = "water-futures-data"
    
    # Vertex AI
    VERTEX_AI_ENDPOINT: str = os.getenv("VERTEX_AI_ENDPOINT", "")
    MODEL_NAME: str = "water-futures-forecast-model"
    
    # Anthropic AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Alpaca Trading
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    # CME Group API
    CME_API_KEY: str = os.getenv("CME_API_KEY", "")
    
    # News API
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # MCP/Smithery
    SMITHERY_API_KEY: str = os.getenv("SMITHERY_API_KEY", "")
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:5000")
    
    # Crossmint
    CROSSMINT_API_KEY: str = os.getenv("CROSSMINT_API_KEY", "")
    UNCLE_SAM_WALLET_ADDRESS: str = os.getenv("UNCLE_SAM_WALLET_ADDRESS", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env

settings = Settings()