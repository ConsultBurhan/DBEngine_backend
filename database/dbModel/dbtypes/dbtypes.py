"""Dbtype model for dbtypes entites"""
import datetime
from typing import Optional
from config.DBbasemodel import _BaseDBModel


class Dbtypes(_BaseDBModel):
    id: int
    dbprovider: Optional[str] = None
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None


    