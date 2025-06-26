"""CryptoSenti - Python client for PySenti crypto sentiment analysis SignalR API."""

from .client import SentimentClient
from .config import CryptoSentiConfig
from .models import NewsSummary, SentimentData, WorldNews

__version__ = "0.1.0"
__all__ = [
    "SentimentClient",
    "NewsSummary",
    "SentimentData",
    "WorldNews",
    "CryptoSentiConfig",
]
