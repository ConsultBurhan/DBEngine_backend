"""Pydantic models for bot response rating service DTOs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BotResponseRatingList(BaseModel):
    """Bot response rating list model."""
    Id: int
    ConversationId: Optional[int] = None
    ConversationMessageId: Optional[int] = None
    BotId: Optional[int] = None
    Ratings: Optional[str] = None
    ReviewMessage: Optional[str] = None
    QuestionText: Optional[str] = None
    AnswerText: Optional[str] = None
    CreatedDate: Optional[datetime] = None
    CreatedBy: int
    Status: Optional[int] = None  # 1 = Not Trained, 2 = Trained


class CreateBotResponseRating(BaseModel):
    """Create bot response rating model."""
    ConversationId: Optional[int] = None
    ConversationMessageId: Optional[int] = None
    BotId: Optional[int] = None
    Ratings: Optional[str] = None
    ReviewMessage: Optional[str] = None
