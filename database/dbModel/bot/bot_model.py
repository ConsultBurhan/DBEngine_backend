"""Bot models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Botrolemap(_BaseDBModel):
    """Bot-to-role mapping table."""
    id: int
    roleid: Optional[int] = None
    botid: Optional[int] = None
    clientid: Optional[int] = None
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None


class Bot(_BaseDBModel):
    """Bot entity."""
    id: int
    botname: Optional[str] = None
    logo: Optional[str] = None
    clientid: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    status: Optional[int] = None
    bottype: Optional[int] = None


class BotResponseRating(_BaseDBModel):
    """Bot response rating entity."""
    Id: int
    ConversationId: Optional[int] = None
    ConverstaionMessageId: Optional[int] = None
    BotId: Optional[int] = None
    Ratings: Optional[str] = None
    ReviewMessage: Optional[str] = None
    CreatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    ClientId: Optional[int] = None
    Status: Optional[int] = None
