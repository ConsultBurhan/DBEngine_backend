"""Conversation service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import UploadFile, File
from pydantic import BaseModel

from models.common import MouthCue


class ConversationDto(BaseModel):
    """DTO for conversation."""
    Id: int
    Clientid: Optional[int] = None
    Botid: Optional[int] = None
    Userid: Optional[int] = None
    Threadid: Optional[str] = None
    Channelversion: Optional[str] = None
    Chatmetadata: Optional[str] = None
    Status: Optional[str] = None
    Lastmessage: Optional[str] = None
    Messagecount: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class GetResponse(BaseModel):
    """DTO for getting response."""
    RoleIds: str
    BotId: int
    MessageText: Optional[str] = None
    ConversationId: Optional[int] = None
    ResponseType: Optional[int] = None
    ResponseLanguage: int
    File: Optional[UploadFile] = File(...)
    BotType: int
    NeedLipSync: Optional[bool] = False


class GetResponseResult(BaseModel):
    """DTO for get response result."""
    ConversationId: int
    ResponseType: str
    ResponseText: Optional[str] = None
    ResponseUrl: Optional[str] = None
    SentMessageId: int
    ReceivedMessageId: int
    LipSyncJson: List[MouthCue]


class ChatApiResponse(BaseModel):
    """DTO for chat API response."""
    Response: str
    Thread_Id: str
    Bot_Id: str
    Role_Id: str
    Sources: List[str]
    Timestamp: datetime


class StreamingEventData(BaseModel):
    """DTO for streaming event data."""
    type: Optional[str] = None
    sql_query: Optional[str] = None
    Message: Optional[str] = None
    Stage: Optional[str] = None
    Request_Id: Optional[str] = None
    Thread_Id: Optional[str] = None
    Timestamp: Optional[str] = None
    Step: Optional[int] = None
    Total_Steps: Optional[int] = None
    Duration_Ms: Optional[int] = None
    Node: Optional[str] = None
    Summary: Optional["Summary"] = None
    Details: Optional[Dict[str, Any]] = None
    Views: Optional[List[str]] = None
    View_Name: Optional[str] = None
    Schema_Name: Optional[str] = None
    Needs_Join: Optional[bool] = None
    Success: Optional[bool] = None
    User_Query: Optional[str] = None
    sql_result: Optional["SqlResult"] = None
    Requires_Additional_Info: Optional[bool] = None
    Missing_Fields: Optional[List[str]] = None
    Sources: Optional[List[str]] = None
    Bot_Id: Optional[str] = None
    Role_Id: Optional[str] = None
    Usage: Optional[float] = None
    Data: Optional[float] = None


class StreamingEvent(BaseModel):
    """DTO for streaming event."""
    event: str = ""
    Content: Optional[str] = None
    Data: Optional[StreamingEventData] = None


class Summary(BaseModel):
    """DTO for summary."""
    Query_Expanded: Optional[bool] = None
    Expanded_Query: Optional[str] = None
    Has_Brand: Optional[bool] = None
    Has_Time: Optional[bool] = None
    Brand_Name: Optional[str] = None
    Time_Period: Optional[str] = None
    Validation_Passed: Optional[bool] = None
    Views_Found: Optional[int] = None
    View_Names: Optional[List[str]] = None
    Needs_Join: Optional[bool] = None


class SqlResult(BaseModel):
    """DTO for SQL result."""
    Success: Optional[bool] = None
    Error: Optional[str] = None
    Data: Optional[List[Dict[str, Any]]] = None
    formatted_message: str
    graph_data: "GraphData"


class GraphData(BaseModel):
    """DTO for graph data."""
    is_graphable: bool
    graph_type: Optional[str] = None
    title: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    data_points: List[Any]
