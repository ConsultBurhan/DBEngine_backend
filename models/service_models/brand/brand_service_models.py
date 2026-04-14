"""Brand service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BrandCreateDto(BaseModel):
    """DTO for creating a new brand."""
    BrandId: int
    BrandName: str
    IsActive: bool


class BrandResponseDto(BaseModel):
    """DTO for brand response."""
    Id: int
    BrandId: int
    BrandName: str
    CreatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    RecordStatus: str
    IsActive: Optional[bool] = None


class BrandUpdateDto(BaseModel):
    """DTO for updating an existing brand."""
    Id: int
    BrandId: int
    BrandName: str
    IsActive: bool


class BrandStoreCreateDto(BaseModel):
    """DTO for creating a new brand store."""
    BrandId: int
    StoreName: str
    IsActive: bool


class BrandStoreResponseDto(BaseModel):
    """DTO for brand store response."""
    Id: int
    BrandId: int
    StoreName: str
    CreatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    RecordStatus: str
    IsActive: bool


class BrandStoreUpdateDto(BaseModel):
    """DTO for updating an existing brand store."""
    Id: int
    BrandId: int
    StoreName: str
    IsActive: bool
