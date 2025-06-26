"""Data models for CryptoSenti API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict


class SentimentValue(str, Enum):
    """Sentiment value enumeration."""
    Bearish = "Bearish"
    Bullish = "Bullish"
    Neutral = "Neutral"


class Temporal(str, Enum):
    """Temporal enumeration."""
    PAST = "Past"
    PRESENT = "Present"
    FUTURE = "Future"


class NewsSummary(BaseModel):
    """News summary data model."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    key_themes_trends: list[str] = Field(default_factory=list, alias="keyThemesTrends")
    impactful_events_and_implications: list[str] = Field(
        default_factory=list, alias="impactfulEventsAndImplications"
    )
    sentiment_summary: str = Field(default="", alias="sentimentSummary")
    actionable_insights: list[str] = Field(default_factory=list, alias="actionableInsights")
    importance: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())


class WorldNews(BaseModel):
    """World news data model."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    id: int
    headline: str
    attributes: list[str] = Field(default_factory=list)
    version: int = 1
    urgency: int = 0
    processed: Union[datetime, str] = Field(default_factory=lambda: datetime.utcnow())
    event_date: Union[datetime, str] = Field(default_factory=lambda: datetime.utcnow(), alias="eventDate")
    type: Optional[str] = None

    @classmethod
    def parse_datetime(cls, v: Union[str, datetime]) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.fromisoformat(v)
        return v


class SentimentTopic(BaseModel):
    """Sentiment topic data model."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[Union[str, int]] = None  # Made optional and allow int
    name: Optional[str] = None            # Made optional
    description: Optional[str] = None


class SentimentData(BaseModel):
    """Sentiment data model."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )

    processed: Union[datetime, str] = Field(default_factory=lambda: datetime.utcnow())
    sentiment: Optional[SentimentValue] = None
    stage: Optional[str] = None
    temporal: Optional[Temporal] = None
    emotion: Optional[str] = None
    strength: Optional[int] = None
    explanation: str
    news: WorldNews
    topic: Optional[SentimentTopic] = None
    topic_id: Optional[Union[str, int]] = Field(None, alias="topicId")  # Added missing field
    correlation_id: Union[uuid.UUID, str] = Field(default_factory=uuid.uuid4, alias="correlationId")
    confidence: Optional[int] = None
    version: int = 1
    has_changed: bool = Field(default=True, alias="hasChanged")
