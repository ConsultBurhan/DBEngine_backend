"""Dbtype service models for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DbtypesList(BaseModel):
    """DTO for dbtype list response."""
    Id: int
    Dbprovider: Optional[str] = None
    Status: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class DbtypesCreate(BaseModel):
    """DTO for creating a new dbtype."""
    Dbprovider: Optional[str] = None
    Status: Optional[int] = None


class DbtypesUpdate(BaseModel):
    """DTO for updating an existing dbtype."""
    Id: int
    Dbprovider: Optional[str] = None
    Status: Optional[int] = None
