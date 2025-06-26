"""Tests for SignalR client."""

from unittest.mock import MagicMock

import pytest

from cryptosenti.client import SentimentClient
from cryptosenti.config import CryptoSentiConfig
from cryptosenti.models import NewsSummary, SentimentData


@pytest.fixture
def client():
    """Create a test client."""
    config = CryptoSentiConfig(hub_url="https://test.example.com/hub")
    return SentimentClient(config)


def test_client_initialization(client):
    """Test client initialization."""
    assert client.config.hub_url == "https://test.example.com/hub"
    assert not client.is_connected
    assert len(client._summary_handlers) == 0
    assert len(client._sentiment_handlers) == 0


def test_event_handler_registration(client):
    """Test event handler registration."""
    summary_handler = MagicMock()
    sentiment_handler = MagicMock()
    connection_handler = MagicMock()

    client.on_summary_received(summary_handler)
    client.on_sentiment_received(sentiment_handler)
    client.on_connection_changed(connection_handler)

    assert len(client._summary_handlers) == 1
    assert len(client._sentiment_handlers) == 1
    assert len(client._connection_handlers) == 1


@pytest.mark.asyncio
async def test_summary_handler_call():
    """Test summary handler is called correctly."""
    client = SentimentClient()
    handler_called = False
    received_summary = None

    def summary_handler(summary):
        nonlocal handler_called, received_summary
        handler_called = True
        received_summary = summary

    client.on_summary_received(summary_handler)

    # Mock summary data
    summary_data = {
        "keyThemesTrends": ["Bitcoin", "Test"],
        "sentimentSummary": "Test summary",
        "importance": 5,
    }

    await client._on_summary_received(summary_data)

    assert handler_called
    assert isinstance(received_summary, NewsSummary)
    assert received_summary.key_themes_trends == ["Bitcoin", "Test"]


@pytest.mark.asyncio
async def test_sentiment_handler_call():
    """Test sentiment handler is called correctly."""
    client = SentimentClient()
    handler_called = False
    received_sentiment = None

    def sentiment_handler(sentiment):
        nonlocal handler_called, received_sentiment
        handler_called = True
        received_sentiment = sentiment

    client.on_sentiment_received(sentiment_handler)

    # Mock sentiment data
    sentiment_data = {
        "newsId": 123,
        "sentiment": "Bullish",
        "confidence": 85,
        "explanation": "Test explanation",
        "news": {
            "id": 123,
            "headline": "Test headline",
            "externalId": "ext-123",
            "source": "TestSource",
        },
    }

    await client._on_sentiment_received(sentiment_data)

    assert handler_called
    assert isinstance(received_sentiment, SentimentData)


@pytest.mark.asyncio
async def test_connection_handlers():
    """Test connection state change handlers."""
    client = SentimentClient()
    connection_states = []

    def connection_handler(connected):
        connection_states.append(connected)

    client.on_connection_changed(connection_handler)

    await client._on_connected()
    await client._on_disconnected()

    assert connection_states == [True, False]


@pytest.mark.asyncio
async def test_client_not_connected_error():
    """Test error when client is not connected."""
    client = SentimentClient()

    with pytest.raises(RuntimeError, match="Client not connected"):
        # This should be awaited in real usage, but we're testing the sync check
        await client.join_summary_group()
