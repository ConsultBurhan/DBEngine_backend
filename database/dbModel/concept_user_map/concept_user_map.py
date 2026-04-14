"""Concept user map models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Conceptusermap(_BaseDBModel):
    """Concept user map entity."""
    id: int
    user_id: int
    concept_id: int
    concept_name: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    recordstatus: Optional[int] = None


class Storeusermap(_BaseDBModel):
    """Store user map entity."""
    id: int
    user_id: int
    store_id: int
    store_name: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    recordstatus: Optional[str] = None
