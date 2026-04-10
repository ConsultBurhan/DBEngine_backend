"""Common shared models for API responses and utilities."""
from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResult(BaseModel):
    """API response wrapper for endpoints."""
    Success: bool
    Result: Optional[Any] = None
    Message: str = ""
    StatusCode: int
    PageNo: Optional[int] = None
    PageSize: Optional[int] = None
    TotalCount: Optional[int] = None


class Metadata(BaseModel):
    """Metadata for lip sync API response."""
    soundFile: str
    duration: float


class MouthCue(BaseModel):
    """Mouth cue for lip sync animation."""
    Start: float
    End: float
    Value: str


class LipSyncApiResponse(BaseModel):
    """Lip sync API response with mouth cues."""
    metadata: Metadata
    MouthCues: List[MouthCue]


class ResponseData(BaseModel, Generic[T]):
    """Standard response wrapper with generic data type."""
    Success: bool
    Data: Optional[T] = None
    Message: str = ""
    PageNo: Optional[int] = None
    pageSize: Optional[int] = None
    totalCount: Optional[int] = None


class ErrorDetail(BaseModel):
    """Error detail for API error responses."""
    Loc: List[Any]
    Msg: str
    Type: str


class TranslationTextResponse(BaseModel):
    """Translation API response."""
    Translated_Content: str
    Source_Language: str
    Target_Language: str


class TranslationAPIErrorResponse(BaseModel):
    """Translation API error response."""
    Detail: List[ErrorDetail]


class UEntity(BaseModel):
    """Simple entity with ID and Name."""
    Id: int
    Name: str


class UResponse(BaseModel):
    """Simple response with status and message."""
    Status: int
    Message: str = ""

