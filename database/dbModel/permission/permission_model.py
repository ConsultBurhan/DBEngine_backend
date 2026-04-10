"""Permission models for role-based access control."""
from datetime import datetime
from typing import Optional

from config.DBbasemodel import _BaseDBModel


class Permission(_BaseDBModel):
    """Permission table defining what actions a role can perform."""
    id: int
    roleid: Optional[int] = None
    canview: Optional[bool] = None
    cancreate: Optional[bool] = None
    canupdate: Optional[bool] = None
    candelete: Optional[bool] = None
    createdby: Optional[str] = None
    createddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    updateddate: Optional[datetime] = None
    permissiontaskid: Optional[int] = None
    isactive: Optional[bool] = None


class Permissiontask(_BaseDBModel):
    """Permission task/privilege definition."""
    id: int
    permissiontaskname: Optional[str] = None
    path: Optional[str] = None
    parentid: Optional[int] = None
    isactive: Optional[bool] = None
    displayorder: Optional[int] = None
    icon: Optional[str] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    isadmintask: Optional[bool] = None
    issubscribertask: Optional[bool] = None
