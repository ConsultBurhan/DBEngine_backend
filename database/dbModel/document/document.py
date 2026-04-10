"""Document models for database entities."""
from datetime import datetime
from typing import Optional
import uuid

from config.DBbasemodel import _BaseDBModel


class Document(_BaseDBModel):
    """Document table."""
    Id: int
    Documentname: Optional[str] = None
    Url: Optional[str] = None
    Documentgroupid: Optional[int] = None
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
    TranslatedtextUrl: Optional[str] = None
    DocumentStatus: Optional[int] = None


class DocumentChatMessage(_BaseDBModel):
    """Document chat message table."""
    Id: int
    ThreadId: int
    Role: str
    Content: str
    Timestamp: Optional[datetime] = None
    MessageMetadata: Optional[str] = None


class DocumentChunk(_BaseDBModel):
    """Document chunk table."""
    Id: uuid.UUID
    DocumentId: uuid.UUID
    ChunkIndex: int
    Metadata: Optional[str] = None
    CreatedAt: Optional[datetime] = None
    Botid: Optional[str] = None
    Roleid: Optional[str] = None
    ClientId: Optional[str] = None
    FileExtension: Optional[str] = None
    DocumentContent: Optional[str] = None
    DatabaseContent: Optional[str] = None
    SchemaContent: Optional[str] = None
    ContentType: Optional[str] = None


class DocumentChatThread(_BaseDBModel):
    """Document chat thread table."""
    Id: int
    UserId: int
    Title: str
    Status: str
    CreatedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None