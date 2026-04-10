"""Permission service models for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UpdatePermissionByRole(BaseModel):
    """Update permission by role DTO."""
    RoleId: int = Field(..., description="Role ID")
    PermissionTaskId: int = Field(..., description="Permission task ID")
    CanView: Optional[bool] = None
    CanCreate: Optional[bool] = None
    CanUpdate: Optional[bool] = None
    CanDelete: Optional[bool] = None
    IsActive: Optional[bool] = None
    UpdatedBy: Optional[str] = None


class PermissionList(BaseModel):
    """Permission list item for role permissions."""
    PermissionTaskName: str
    ParentId: Optional[int] = None
    PermissionTaskId: int
    CanView: bool
    CanCreate: bool
    CanUpdate: bool
    CanDelete: bool
    PermissionId: Optional[int] = None
    DisplayOrder: Optional[int] = None
    Icon: Optional[str] = None


class SavePermissions(BaseModel):
    """Save permissions for a role."""
    RoleId: int
    Permissions: List[PermissionList] = Field(default_factory=list)


class PermissionTaskList(BaseModel):
    """Permission task list item."""
    Id: int
    Permissiontaskname: Optional[str] = None
    ParentPermissionTaskName: Optional[str] = None
    Path: Optional[str] = None
    Parentid: Optional[int] = None
    Isactive: Optional[bool] = None
    Displayorder: Optional[int] = None
    Icon: Optional[str] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None


class AddPermissionTask(BaseModel):
    """Add permission task DTO."""
    Permissiontaskname: Optional[str] = None
    Path: Optional[str] = None
    Parentid: Optional[int] = None
    Displayorder: Optional[int] = None
    Icon: Optional[str] = None
    Createdby: Optional[str] = None
    Isactive: bool


class UpdatePermissionTask(BaseModel):
    """Update permission task DTO."""
    Id: int
    Permissiontaskname: Optional[str] = None
    Path: Optional[str] = None
    Parentid: Optional[int] = None
    Isactive: bool
    Displayorder: Optional[int] = None
    Icon: Optional[str] = None
    Updatedby: Optional[str] = None


