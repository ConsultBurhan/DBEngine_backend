"""Document group models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Documentgroup(_BaseDBModel):
    """Document group table."""
    Id: int
    Clientid: Optional[int] = None
    Botid: Optional[int] = None
    Documentgroupname: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    Status: Optional[int] = None


class Documentgrouprolemap(_BaseDBModel):
    """Document group to role mapping table."""
    Id: int
    Roleid: Optional[int] = None
    Documentgroupid: Optional[int] = None
    Clientid: Optional[int] = None
    Status: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
