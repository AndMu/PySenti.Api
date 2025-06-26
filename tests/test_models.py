"""Tests for data models."""

import uuid
from datetime import datetime
from cryptosenti.models import (
    NewsSummary,
    SentimentData,
    WorldNews,
    SentimentValue,
    NewsType,
    StageName,
    Temporal
)


def test_news_summary_creation():
    """Test NewsSummary model creation."""
    summary = NewsSummary(
        key_themes_trends=["Bitcoin", "Regulation"],
        sentiment_summary="Mixed sentiment",
        importance=7
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
        "importance": 8
    }
    
    summary = NewsSummary.model_validate(data)
    assert summary.key_themes_trends == ["DeFi", "NFT"]
    assert summary.impactful_events_and_implications == ["Market crash"]
    assert summary.sentiment_summary == "Negative outlook"
    assert summary.actionable_insights == ["Hold positions"]
    assert summary.importance == 8


def test_world_news_creation():
    """Test WorldNews model creation."""
    news = WorldNews(
        id=123,
        headline="Bitcoin reaches new high",
        external_id="ext-123",
        source="CryptoNews",
        urgency=5
    )
    
    assert news.id == 123
    assert news.headline == "Bitcoin reaches new high"
    assert news.external_id == "ext-123"
    assert news.source == "CryptoNews"
    assert news.urgency == 5
    assert news.type == NewsType.REGULAR
    assert not news.is_deleted


def test_sentiment_data_creation():
    """Test SentimentData model creation."""
    news = WorldNews(
        id=456,
        headline="Ethereum upgrade delayed",
        external_id="ext-456",
        source="TechCrypto"
    )
    
    sentiment = SentimentData(
        news_id=456,
        sentiment=SentimentValue.NEGATIVE,
        confidence=85,
        explanation="Negative due to delays",
        news=news
    )
    
    assert sentiment.news_id == 456
    assert sentiment.sentiment == SentimentValue.NEGATIVE
    assert sentiment.confidence == 85
    assert sentiment.explanation == "Negative due to delays"
    assert sentiment.news.headline == "Ethereum upgrade delayed"
    assert sentiment.stage == StageName.SENTIMENT_DETECTION
    assert isinstance(sentiment.correlation_id, uuid.UUID)


def test_sentiment_enums():
    """Test sentiment enumerations."""
    assert SentimentValue.POSITIVE == "positive"
    assert SentimentValue.NEGATIVE == "negative"
    assert SentimentValue.NEUTRAL == "neutral"
    
    assert Temporal.PAST == "past"
    assert Temporal.PRESENT == "present"
    assert Temporal.FUTURE == "future"
    
    assert NewsType.BREAKING == "breaking"
    assert NewsType.REGULAR == "regular"


def test_model_json_serialization():
    """Test JSON serialization of models."""
    summary = NewsSummary(
        key_themes_trends=["Test"],
        sentiment_summary="Test summary",
        importance=5
    )
    
    # Should be able to serialize to JSON
    json_data = summary.model_dump()
    assert "key_themes_trends" in json_data
    assert "importance" in json_data
    
    # Should be able to serialize with aliases
    json_data_aliases = summary.model_dump(by_alias=True)
    assert "keyThemesTrends" in json_data_aliases