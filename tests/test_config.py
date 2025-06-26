"""Tests for configuration."""

import os
from cryptosenti.config import CryptoSentiConfig


def test_default_config():
    """Test default configuration values."""
    config = CryptoSentiConfig()
    
    assert config.hub_url == "https://crypto.pysenti.com/sentimenthub"
    assert config.connection_timeout == 30
    assert config.reconnect_attempts == 5
    assert config.reconnect_delay == 5.0
    assert config.auto_subscribe_summary is True
    assert config.auto_subscribe_sentiment is True
    assert config.log_level == "INFO"


def test_custom_config():
    """Test custom configuration values."""
    config = CryptoSentiConfig(
        hub_url="https://custom.example.com/hub",
        connection_timeout=60,
        reconnect_attempts=3,
        log_level="DEBUG"
    )
    
    assert config.hub_url == "https://custom.example.com/hub"
    assert config.connection_timeout == 60
    assert config.reconnect_attempts == 3
    assert config.log_level == "DEBUG"


def test_config_from_env():
    """Test configuration from environment variables."""
    # Set environment variables
    os.environ["CRYPTOSENTI_HUB_URL"] = "https://env.example.com/hub"
    os.environ["CRYPTOSENTI_CONNECTION_TIMEOUT"] = "45"
    os.environ["CRYPTOSENTI_LOG_LEVEL"] = "WARNING"
    
    try:
        config = CryptoSentiConfig()
        
        assert config.hub_url == "https://env.example.com/hub"
        assert config.connection_timeout == 45
        assert config.log_level == "WARNING"
        
    finally:
        # Clean up environment variables
        for key in ["CRYPTOSENTI_HUB_URL", "CRYPTOSENTI_CONNECTION_TIMEOUT", "CRYPTOSENTI_LOG_LEVEL"]:
            if key in os.environ:
                del os.environ[key]