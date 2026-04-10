"""Role service models for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RoleWithBots(BaseModel):
    """Role with associated bot IDs."""
    Id: int
    Rolename: str
    Clientid: Optional[int] = None
    Status: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    BotsId: Optional[str] = Field(default=None, description="Comma-separated list of Bot IDs associated with this role")


class CreateRoleWithBots(BaseModel):
    """Create a new role with bots."""
    Rolename: Optional[str] = None
    Status: Optional[int] = None
    BotsId: Optional[str] = None


class UpdateRoleWithBots(BaseModel):
    """Update an existing role with bots."""
    Id: int
    Rolename: Optional[str] = None
    Status: Optional[int] = None
    BotsId: Optional[str] = None
    