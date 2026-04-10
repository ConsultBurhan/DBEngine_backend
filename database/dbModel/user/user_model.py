"""
User authentication and authorization model.
"""
from datetime import datetime
from typing import Optional
from config.DBbasemodel import _BaseDBModel
from pydantic import BaseModel, ConfigDict, Field



class User(_BaseDBModel):
    """User authentication and authorization table."""
    id: int
    username: Optional[str] = None
    clientid: Optional[int] = Field(default=None, description="Associated client ID for client-based access control")
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None
    passwordhash: Optional[str] = None
    salt: Optional[str] = None
    accesstoken: Optional[str] = None
    refreshtoken: Optional[str] = None
    refreshtokenexpiry: Optional[datetime] = None
    fullname: Optional[str] = None
    email: Optional[str] = Field(default=None, description="Unique user email address")
    phone: Optional[str] = None
    language_code: Optional[str] = None
    issubscriberuser: Optional[bool] = None
    subscriberid: Optional[int] = None
    hashed_password: Optional[str] = Field(default=None, description="BCrypt hashed password")
    botid: Optional[str] = Field(default=None, description="Associated bot ID for multi-tenant access control")
    roleid: Optional[str] = Field(default=None, description="Associated role ID for role-based access control")
    is_active: Optional[bool] = Field(default=None, description="Whether the user account is active")


"""
User-Role mapping model for many-to-many relationship.
"""
class UserRole(_BaseDBModel):
    """User-to-role mapping table."""
    id: int
    userid: int
    roleid: int
    createdat: Optional[datetime] = None
    createdby: Optional[str] = None


class Userrolemap(_BaseDBModel):
    """User role mapping table."""
    id: int
    userid: Optional[int] = None
    roleid: Optional[int] = None
    clientid: Optional[int] = None
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None


"""
Role model for user roles.
"""
class Role(_BaseDBModel):
    """Role table for user role management."""
    id: int
    rolename: Optional[str] = None
    clientid: Optional[int] = None
    status: Optional[int] = None
    createddate: Optional[datetime] = None
    createdby: Optional[str] = None
    updateddate: Optional[datetime] = None
    updatedby: Optional[str] = None




