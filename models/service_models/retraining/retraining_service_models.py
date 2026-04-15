"""Retraining service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BottrainingmapDto(BaseModel):
    """DTO for Bottrainingmap entity."""
    Id: int
    Botid: int
    Clientid: str
    Content: str
    Trainingtype: int
    Title: Optional[str] = None
    Keywords: Optional[List[str]] = None
    Summary: Optional[str] = None
    Metadata: Optional[str] = None
    Createddate: Optional[datetime] = None
    Updateddate: Optional[datetime] = None
    Source: Optional[int] = None
    Documentid: Optional[int] = None
    Recordstatus: Optional[int] = None


class CreateBottrainingmap(BaseModel):
    """DTO for creating a new Bottrainingmap."""
    Botid: int
    Clientid: str
    Content: str
    Trainingtype: int
    Title: Optional[str] = None
    Keywords: Optional[List[str]] = None
    Summary: Optional[str] = None
    Metadata: Optional[str] = None
    Source: Optional[int] = None
    Documentid: Optional[int] = None


class UpdateBottrainingmap(BaseModel):
    """DTO for updating an existing Bottrainingmap."""
    Id: int
    Botid: int
    Clientid: str
    Content: str
    Trainingtype: int
    Title: Optional[str] = None
    Keywords: Optional[List[str]] = None
    Summary: Optional[str] = None
    Metadata: Optional[str] = None
    Source: Optional[int] = None
    Documentid: Optional[int] = None
