"""Bot service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile, File
from pydantic import BaseModel


class BotsList(BaseModel):
    """DTO for bot list response."""
    Id: int
    Botname: Optional[str] = None
    Logo: Optional[str] = None
    Clientid: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    Status: Optional[int] = None


class CreateBot(BaseModel):
    """DTO for creating a new bot."""
    Botname: str
    Logo: Optional[UploadFile] = File(None)


class UpdateBot(BaseModel):
    """DTO for updating an existing bot."""
    BotId: int
    Botname: str
    Logo: Optional[UploadFile] = File(None)


class BotRoleMapList(BaseModel):
    """DTO for bot role mapping list."""
    BotId: Optional[int] = None
    Clientid: Optional[int] = None
    Roleid: List[int]


class CreateBotRole(BaseModel):
    """DTO for creating bot role mapping."""
    BotId: int
    RolesId: Optional[str] = None


class BotDropDto(BaseModel):
    """DTO for bot dropdown."""
    Id: int
    Name: str
    Type: int
