""" AppSettings service DTO models"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import UploadFile, File
from pydantic import BaseModel


class AppSetting(BaseModel):
    """App settings entity."""
    id: int
    keyname: str
    value: str
    botid: Optional[int] = None
    iseditable: bool
    status: str
    createddate: datetime
    createdby: str
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    clientid: Optional[int] = None


class AppsettingCreate(BaseModel):
    """DTO for creating a new app setting."""
    keyname: str
    value: str
    botid: Optional[int] = None
    iseditable: bool
    clientid: Optional[int] = None
