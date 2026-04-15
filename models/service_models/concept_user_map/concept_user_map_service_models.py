"""User concept map service DTOs for API requests and responses."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class UserConceptMapDto(BaseModel):
    """DTO for user concept mapping."""
    UserId: int
    ConceptIds: List[int]
    StoreIds: List[int]
