"""Database table models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Databasetable(_BaseDBModel):
    """Database table entity."""
    id: int
    dbid: Optional[int] = None
    tablename: Optional[str] = None
    status: Optional[str] = None
    embeddingdb: Optional[str] = None
    embeddingdetails: Optional[str] = None
    botid: Optional[int] = None
    tablecount: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None


class Databasetablerolemap(_BaseDBModel):
    """Database table role mapping entity."""
    id: int
    roleid: Optional[int] = None
    databasetableid: Optional[int] = None
    clientid: Optional[int] = None
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None


class Databasetablescolumn(_BaseDBModel):
    """Database table column entity."""
    id: int
    tableid: Optional[int] = None
    columnname: Optional[str] = None
    dbtype: Optional[str] = None
    embeddingdb: Optional[str] = None
    embeddingdetails: Optional[str] = None
    botid: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    isprimary: Optional[bool] = None
    isnullable: Optional[bool] = None
    sampledata: Optional[str] = None
