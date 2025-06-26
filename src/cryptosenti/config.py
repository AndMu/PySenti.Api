"""Configuration for CryptoSenti client."""

from typing import Optional
from pydantic import BaseModel, Field


class CryptoSentiConfig(BaseModel):
    """Configuration for CryptoSenti SignalR client."""
    
    hub_url: str = Field(default="https://crypto.pysenti.com/sentimenthub")
    connection_timeout: int = Field(default=30, description="Connection timeout in seconds")
    reconnect_attempts: int = Field(default=5, description="Number of reconnection attempts")
    reconnect_delay: float = Field(default=5.0, description="Delay between reconnection attempts")
    
    # No authentication required for public API
    
    # Subscription settings
    auto_subscribe_summary: bool = Field(default=True, description="Auto-subscribe to summary signals")
    auto_subscribe_sentiment: bool = Field(default=True, description="Auto-subscribe to sentiment signals")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    class Config:
        env_prefix = "CRYPTOSENTI_"
        case_sensitive = False