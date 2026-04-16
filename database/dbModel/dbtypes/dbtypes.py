"""Dbtype model for dbtypes entites"""
from datetime import datetime
from typing import Optional
from config.DBbasemodel import _BaseDBModel


class Dbtypes(_BaseDBModel):
    id: int
    dbprovider: str
    status: str
    createddate: datetime
    createdby: str
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None