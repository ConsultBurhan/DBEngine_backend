"""Document group service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentGroupList(BaseModel):
    """DTO for document group list response."""
    Id: int
    Clientid: Optional[int] = None
    Botid: Optional[int] = None
    BotName: Optional[str] = None
    Documentgroupname: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    Status: Optional[int] = None


class DocumentGroupCreate(BaseModel):
    """DTO for creating a new document group."""
    Botid: Optional[int] = None
    Documentgroupname: Optional[str] = None
    Status: Optional[int] = None


class DocumentGroupUpdate(BaseModel):
    """DTO for updating an existing document group."""
    DocumentGroupId: int
    Botid: Optional[int] = None
    Documentgroupname: Optional[str] = None
    Status: Optional[int] = None


class DocumentGroupRoleMapList(BaseModel):
    """DTO for document group role mapping list."""
    Documentgroupid: Optional[int] = None
    Clientid: Optional[int] = None
    Roleid: List[int]


class CreateDocumentGroupRole(BaseModel):
    """DTO for creating document group role mapping."""
    DocumentGroupId: int
    RolesId: Optional[str] = None