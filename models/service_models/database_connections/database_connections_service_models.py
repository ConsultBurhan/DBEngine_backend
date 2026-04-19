"""Service models for the Database connection service."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DatabaseConnectionList(BaseModel):
    """DTO for database connection list response."""
    Id: int
    Connectiontype: Optional[int] = None
    Server: Optional[str] = None
    Username: Optional[str] = None
    Password: Optional[str] = None
    Dbname: Optional[str] = None
    Connectionstring: Optional[str] = None
    Clientid: Optional[int] = None
    Botid: Optional[int] = None
    BotName: Optional[str] = None
    Tablecount: Optional[int] = None
    Status: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class CreateDatabaseConnection(BaseModel):
    """DTO for creating a new database connection."""
    Connectiontype: str
    Server: str
    Username: str
    Password: str
    Dbname: str
    Connectionstring: str
    Botid: int
    Tablecount: Optional[int] = None


class UpdateDatabaseConnection(BaseModel):
    """DTO for updating an existing database connection."""
    Id: int
    Connectiontype: Optional[str] = None
    Server: Optional[str] = None
    Username: Optional[str] = None
    Password: Optional[str] = None
    Dbname: Optional[str] = None
    Connectionstring: Optional[str] = None
    Botid: Optional[int] = None
    Tablecount: Optional[int] = None
    Status: Optional[str] = None


class ColumnInfo(BaseModel):
    """DTO for column information."""
    ColumnName: str
    DataType: str
    IsPrimary: bool
    IsNullable: bool


class TableInfo(BaseModel):
    """DTO for table information."""
    SchemaName: str
    TableName: str
    Columns: List[ColumnInfo]


class DatabaseCheckResult(BaseModel):
    """DTO for database connection check result."""
    IsConnected: bool
    Tables: List[TableInfo]
