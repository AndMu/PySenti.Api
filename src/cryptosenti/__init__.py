"""CryptoSenti - Python client for PySenti crypto sentiment analysis SignalR API."""

from .client import SentimentClient
from .models import NewsSummary, SentimentData, WorldNews
from .config import CryptoSentiConfig

__version__ = "0.1.0"
__all__ = [
    "SentimentClient",
    "NewsSummary", 
    "SentimentData",
    "WorldNews",
    "CryptoSentiConfig",
]