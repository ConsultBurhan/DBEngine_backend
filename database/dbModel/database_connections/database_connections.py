"""Database connection model for database connection entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Databaseconnections(_BaseDBModel):
    """Database connection model for database connection entities."""
    id: int
    connectiontype: Optional[str] = None
    server: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    dbname: Optional[str] = None
    connectionstring: Optional[str] = None
    clientid: Optional[int] = None
    botid: Optional[int] = None
    tablecount: Optional[int] = None
    status: Optional[str] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
