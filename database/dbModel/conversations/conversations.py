"""Conversation model for database entity."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Conversations(_BaseDBModel):
    """Conversation entity."""
    id: Optional[int] = None
    clientid: Optional[int] = None
    botid: Optional[int] = None
    userid: Optional[int] = None
    threadid: Optional[str] = None
    BotType: Optional[str] = None
    chatmetadata: Optional[str] = None
    status: Optional[str] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    title: Optional[str] = None
    lastmessage: Optional[str] = None
    messagecount: Optional[int] = None


    
class Conversationmessages(_BaseDBModel):
    """Conversation message entity."""
    id: Optional[int] = None
    conversationid: Optional[int] = None
    messagetype: Optional[str] = None
    messagetext: Optional[str] = None
    mediatype: Optional[str] = None
    mediaurl: Optional[str] = None
    responsesource: Optional[str] = None
    voicetypeid: Optional[int] = None
    checkpointers: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    orignaltext: Optional[str] = None


class ConversationHistory(_BaseDBModel):
    """Conversation history entity."""
    id: Optional[int] = None
    userquery: str
    sqlquery: Optional[str] = None
    answer: Optional[str] = None
    formatedquery: Optional[str] = None
    reasoningsteps: Optional[str] = None
    bot_id: int
    role_id: int
    clientid: int
    createdat: Optional[datetime] = None
    updatedat: Optional[datetime] = None
    recordstatus: Optional[int] = None
