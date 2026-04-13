"""Conversations service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConversationsList(BaseModel):
    """DTO for conversations list."""
    Id: int
    Clientid: Optional[int] = None
    Botid: Optional[int] = None
    Userid: Optional[int] = None
    Threadid: Optional[str] = None
    BotType: Optional[str] = None
    Chatmetadata: Optional[str] = None
    Status: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    Title: Optional[str] = None
    Lastmessage: Optional[str] = None
    Messagecount: Optional[int] = None


class ConversationMessages(BaseModel):
    """DTO for conversation messages."""
    Id: int
    Conversationid: Optional[int] = None
    Messagetype: Optional[str] = None
    Messagetext: Optional[str] = None
    Mediatype: Optional[str] = None
    Mediaurl: Optional[str] = None
    Responsesource: Optional[str] = None
    Voicetypeid: Optional[int] = None
    Checkpointers: Optional[str] = None
    State: Optional[str] = None
    Status: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
