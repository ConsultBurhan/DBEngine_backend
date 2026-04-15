"""App settings models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Appsetting(_BaseDBModel):
    """App settings entity."""
    id: int
    keyname: str
    value: str
    botid: Optional[int] = None
    iseditable: bool
    status: str
    createddate: datetime
    createdby: str
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    clientid: Optional[int] = None
