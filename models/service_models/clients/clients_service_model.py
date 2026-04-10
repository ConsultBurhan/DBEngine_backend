"""Client service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel


class ClientList(BaseModel):
    """DTO for client list response."""
    Id: int
    Clientname: Optional[str] = None
    Status: Optional[int] = None
    Logo: Optional[str] = None
    DefaultLanguageCode: Optional[str] = None
    ClientPrefix: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class ClientCreate(BaseModel):
    """DTO for creating a new client."""
    Clientname: Optional[str] = None
    DefaultLanguageCode: Optional[str] = None
    ClientPrefix: str
    Status: Optional[int] = None
    Logo: Optional[str] = None


class ClientUpdate(BaseModel):
    """DTO for updating an existing client."""
    ClientId: int
    Clientname: Optional[str] = None
    Status: Optional[int] = None
    Logo: Optional[str] = None
    DefaultLanguageCode: Optional[str] = None
