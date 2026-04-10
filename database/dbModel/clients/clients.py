"""Client models for database entities."""
from calendar import c
from datetime import datetime
from re import U
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Client(_BaseDBModel):
    """Client table."""
    id: int
    clientname: Optional[str] = None
    status: Optional[int] = None
    logo: Optional[str] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    DefaultLanguageCode: Optional[str] = None
    client_prefix: Optional[str] = None
