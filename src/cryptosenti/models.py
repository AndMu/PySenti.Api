"""Data models for CryptoSenti API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SentimentValue(str, Enum):
    """Sentiment value enumeration."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Temporal(str, Enum):
    """Temporal enumeration."""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class StageName(str, Enum):
    """Stage name enumeration."""
    SENTIMENT_DETECTION = "SentimentDetection"
    ANALYSIS = "Analysis"
    PROCESSING = "Processing"
    COMPLETED = "Completed"


class NewsType(str, Enum):
    """News type enumeration."""
    BREAKING = "breaking"
    REGULAR = "regular"
    ANALYSIS = "analysis"
    OPINION = "opinion"


class NewsSummary(BaseModel):
    """News summary data model."""
    
    key_themes_trends: list[str] = Field(default_factory=list, alias="keyThemesTrends")
    impactful_events_and_implications: list[str] = Field(
        default_factory=list, alias="impactfulEventsAndImplications"
    )
    sentiment_summary: str = Field(default="", alias="sentimentSummary")
    actionable_insights: list[str] = Field(default_factory=list, alias="actionableInsights")
    importance: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorldNews(BaseModel):
    """World news data model."""
    
    id: int
    headline: str
    attributes: list[str] = Field(default_factory=list)
    external_id: str = Field(alias="externalId")
    version: int = 1
    source: str
    is_deleted: bool = Field(default=False, alias="isDeleted")
    urgency: int = 0
    processed: datetime = Field(default_factory=lambda: datetime.utcnow())
    event_date: datetime = Field(default_factory=lambda: datetime.utcnow(), alias="eventDate")
    type: NewsType = NewsType.REGULAR

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SentimentTopic(BaseModel):
    """Sentiment topic data model."""
    
    id: str
    name: str
    description: Optional[str] = None
    
    class Config:
        populate_by_name = True


class SentimentData(BaseModel):
    """Sentiment data model."""
    
    news_id: int = Field(alias="newsId")
    topic_id: Optional[str] = Field(default=None, alias="topicId")
    processed: datetime = Field(default_factory=lambda: datetime.utcnow())
    sentiment: Optional[SentimentValue] = None
    stage: StageName = StageName.SENTIMENT_DETECTION
    temporal: Optional[Temporal] = None
    emotion: Optional[str] = None
    strength: Optional[int] = None
    explanation: str
    news: WorldNews
    topic: Optional[SentimentTopic] = None
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="correlationId")
    confidence: Optional[int] = None
    version: int = 1
    has_changed: bool = Field(default=True, alias="hasChanged")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }