"""Bot training models for database entities."""
from datetime import datetime
from typing import Optional, List

from config.DBbasemodel import _BaseDBModel


class Bottraining(_BaseDBModel):
    """Bot training entity."""
    id: int
    type: Optional[int] = None
    subid: Optional[int] = None
    trainingtext: Optional[str] = None
    embeddingdb: Optional[str] = None
    embeddingdetails: Optional[str] = None
    botid: Optional[int] = None
    status: Optional[str] = None
    issqlquery: Optional[bool] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None


class Bottrainingmap(_BaseDBModel):
    """Bot training mapping entity."""
    id: int
    botid: int
    clientid: str
    content: str
    trainingtype: int
    title: Optional[str] = None
    keywords: Optional[List[str]] = None
    summary: Optional[str] = None
    metadata: Optional[str] = None
    createddate: Optional[datetime] = None
    updateddate: Optional[datetime] = None
    source: Optional[int] = None
    documentid: Optional[int] = None
    recordstatus: Optional[int] = None
