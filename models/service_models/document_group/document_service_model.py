"""Document service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentDeleteResponse(BaseModel):
    """DTO for document deletion response."""
    Message: str
    DocumentId: str
    BotId: str
    ClientId: str
    SupabaseDeleted: bool
    SupabaseChunksDeleted: int
    RedisChunksDeleted: int
    RedisDocumentDeleted: bool
    Status: str
    DeletedFrom: List[str]


class DocumentList(BaseModel):
    """DTO for document list response."""
    Id: int
    Documentname: Optional[str] = None
    Url: Optional[str] = None
    Documentgroupid: Optional[int] = None
    DocumentGroupName: Optional[str] = None
    Clientid: Optional[int] = None
    Botid: Optional[int] = None
    Noofchunks: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    Status: Optional[int] = None
    Embeddingdb: Optional[str] = None
    Embeddingdetails: Optional[str] = None
    Fileextension: Optional[str] = None
    DocumentStatus: Optional[int] = None


class CreateDocument(BaseModel):
    """DTO for creating a new document."""
    Documentname: str
    Documentgroupid: int
    Botid: int


class UplopadTranslatedDocument(BaseModel):
    """DTO for uploading translated document."""
    Documentid: int