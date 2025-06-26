"""Tests for configuration."""

from cryptosenti.config import CryptoSentiConfig


def test_default_config():
    """Test default configuration values."""
    config = CryptoSentiConfig()

    assert config.hub_url == "https://crypto.pysenti.com/sentimentHub"
    assert config.connection_timeout == 30
    assert config.reconnect_attempts == 5
    assert config.reconnect_delay == 5.0
    assert config.log_level == "INFO"


def test_custom_config():
    """Test custom configuration values."""
    config = CryptoSentiConfig(
        hub_url="https://custom.example.com/hub",
        connection_timeout=60,
        reconnect_attempts=3,
        log_level="DEBUG",
    )

    assert config.hub_url == "https://custom.example.com/hub"
    assert config.connection_timeout == 60
    assert config.reconnect_attempts == 3
    assert config.log_level == "DEBUG"
