"""Tests for data models."""

import uuid
from datetime import datetime

from cryptosenti.models import NewsSummary, SentimentData, SentimentValue, WorldNews


def test_news_summary_creation():
    """Test NewsSummary model creation."""
    summary = NewsSummary(
        key_themes_trends=["Bitcoin", "Regulation"],
        sentiment_summary="Mixed sentiment",
        importance=7,
    )

    assert summary.key_themes_trends == ["Bitcoin", "Regulation"]
    assert summary.sentiment_summary == "Mixed sentiment"
    assert summary.importance == 7
    assert isinstance(summary.timestamp, datetime)


def test_news_summary_with_aliases():
    """Test NewsSummary with JSON aliases."""
    data = {
        "keyThemesTrends": ["DeFi", "NFT"],
        "impactfulEventsAndImplications": ["Market crash"],
        "sentimentSummary": "Negative outlook",
        "actionableInsights": ["Hold positions"],
        "importance": 8,
    }

    summary = NewsSummary.model_validate(data)
    assert summary.key_themes_trends == ["DeFi", "NFT"]
    assert summary.impactful_events_and_implications == ["Market crash"]
    assert summary.sentiment_summary == "Negative outlook"
    assert summary.actionable_insights == ["Hold positions"]
    assert summary.importance == 8


def test_world_news_creation():
    """Test WorldNews model creation."""
    news = WorldNews(id=123, headline="Bitcoin reaches new high", urgency=5)

    assert news.id == 123
    assert news.headline == "Bitcoin reaches new high"
    assert news.urgency == 5


def test_sentiment_data_creation():
    """Test SentimentData model creation."""
    news = WorldNews(id=456, headline="Ethereum upgrade delayed")

    sentiment = SentimentData(
        sentiment=SentimentValue.Bullish,
        confidence=85,
        explanation="Negative due to delays",
        news=news,
    )

    assert sentiment.sentiment == SentimentValue.Bullish
    assert sentiment.confidence == 85
    assert sentiment.explanation == "Negative due to delays"
    assert sentiment.news.headline == "Ethereum upgrade delayed"
    assert isinstance(sentiment.correlation_id, uuid.UUID)


def test_sentiment_enums():
    """Test sentiment enumerations."""
    assert SentimentValue.Bearish == "Bearish"
    assert SentimentValue.Bullish == "Bullish"
    assert SentimentValue.Neutral == "Neutral"


def test_model_json_serialization():
    """Test JSON serialization of models."""
    summary = NewsSummary(
        key_themes_trends=["Test"], sentiment_summary="Test summary", importance=5
    )

    # Should be able to serialize to JSON
    json_data = summary.model_dump()
    assert "key_themes_trends" in json_data
    assert "importance" in json_data

    # Should be able to serialize with aliases
    json_data_aliases = summary.model_dump(by_alias=True)
    assert "keyThemesTrends" in json_data_aliases


# Test function to verify the model works with your data
def test_deserialization():
    """Test function to deserialize the provided JSON data."""
    test_data = {
        "confidence": 8,
        "correlationId": "ca1cb3a5-e282-4036-96d1-6ede987b4360",
        "emotion": "Fear",
        "explanation": "The article discusses geopolitical tensions between Iran and the U.S., which may lead to uncertainty in global markets, including cryptocurrencies. Such uncertainty typically results in  sentiment for crypto prices.",
        "hasChanged": True,
        "news": {
            "attributes": [],
            "eventDate": "2025-06-26T11:40:16Z",
            "externalId": "",
            "headline": "Supreme leader, in first appearance since ceasefire, says Iran would strike back if attacked",
            "id": 11350,
            "isDeleted": False,
            "processed": "2025-06-26T11:40:22.921528Z",
            "source": "Reuters News",
            "type": "NewsStory",
            "urgency": 3,
            "version": 1,
        },
        "newsId": 11350,
        "processed": "2025-06-26T11:40:24.158992Z",
        "sentiment": "Bearish",
        "stage": "SentimentDetection",
        "strength": 6,
        "temporal": "Future",
        "version": 1,
    }

    sentiment_data = SentimentData(**test_data)
    assert sentiment_data.confidence == 8
