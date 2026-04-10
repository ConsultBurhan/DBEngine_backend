"""Bot models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Botrolemap(_BaseDBModel):
    """Bot-to-role mapping table."""
    id: int
    roleid: Optional[int] = None
    botid: Optional[int] = None
    clientid: Optional[int] = None
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
