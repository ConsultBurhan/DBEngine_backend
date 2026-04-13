"""Database table service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DatabasetableList(BaseModel):
    """DTO for database table list response."""
    Id: int
    Dbid: Optional[int] = None
    Tablename: Optional[str] = None
    Status: Optional[str] = None
    Embeddingdb: Optional[str] = None
    Embeddingdetails: Optional[str] = None
    Botid: Optional[int] = None
    Tablecount: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class DatabaseTableRoleMapList(BaseModel):
    """DTO for database table role mapping list."""
    DatabaseTableid: Optional[int] = None
    Clientid: Optional[int] = None
    Roleid: List[int]


class CreateDatabaseTableRole(BaseModel):
    """DTO for creating database table role mapping."""
    DatabaseTableId: int
    RolesId: Optional[str] = None


class DatabaseTablesColumnList(BaseModel):
    """DTO for database table column list response."""
    Id: int
    Tableid: Optional[int] = None
    Columnname: Optional[str] = None
    Dbtype: Optional[str] = None
    Embeddingdb: Optional[str] = None
    Embeddingdetails: Optional[str] = None
    Botid: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
