"""Brand models for database entities."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Brand(_BaseDBModel):
    """Brand entity."""
    Id: int
    BrandId: int
    BrandName: str
    CreatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    UpdatedDate: Optional[datetime] = None
    UpdatedBy: Optional[int] = None
    RecordStatus: Optional[str] = None
    IsActive: Optional[bool] = None


class BrandStore(_BaseDBModel):
    """Brand store entity."""
    Id: int
    BrandId: int
    StoreName: str
    CreatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    UpdatedDate: Optional[datetime] = None
    UpdatedBy: Optional[int] = None
    RecordStatus: Optional[str] = None
    IsActive: bool
