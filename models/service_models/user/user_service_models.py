"""User service DTOs for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    """DTO for creating a new user via API."""
    Username: str
    Password: str
    Email: Optional[str] = None
    CountryCode: Optional[str] = None
    Phone: Optional[str] = None
    Fullname: Optional[str] = None
    SubscriberId: Optional[int] = None
    RolesId: Optional[str] = Field(default=None, description="Comma-separated list of Role IDs to associate with this user")


class UpdateUser(BaseModel):
    """DTO for updating an existing user via API."""
    UserId: int
    Username: Optional[str] = None
    Email: Optional[str] = None
    CountryCode: Optional[str] = None
    Phone: Optional[str] = None
    Fullname: Optional[str] = None
    Clientid: Optional[int] = None
    RolesId: Optional[str] = Field(default=None, description="Comma-separated list of Role IDs to associate with this user")
    Updatedby: Optional[str] = None


class UserWithRoles(BaseModel):
    """DTO for user with roles information."""
    Id: int
    Username: str
    Email: Optional[str] = None
    CountryCode: Optional[str] = None
    Phone: Optional[str] = None
    Fullname: Optional[str] = None
    Clientid: Optional[int] = None
    Status: Optional[int] = None
    Createddate: Optional[datetime] = None
    Createdby: Optional[str] = None
    Updateddate: Optional[datetime] = None
    Updatedby: Optional[str] = None
    RolesId: Optional[str] = Field(default=None, description="Comma-separated list of Role IDs associated with this user")


class ChangePassword(BaseModel):
    """DTO for user changing their own password."""
    UserId: int
    OldPassword: str
    NewPassword: str


class AdminChangePassword(BaseModel):
    """DTO for admin changing a user's password."""
    NewPassword: str
    Updatedby: Optional[str] = None


class LoginRequest(BaseModel):
    """DTO for user login request."""
    Username: str
    Password: str


class UserPermission(BaseModel):
    """DTO for user permission information."""
    PermissionId: int
    CanView: bool
    CanCreate: bool
    CanUpdate: bool
    CanDelete: bool
    PermissionTaskId: int
    PermissionTaskName: Optional[str] = None
    Path: Optional[str] = None
    ParentId: int
    DisplayOrder: int
    Icon: Optional[str] = None
    Children: Optional[List[UserPermission]] = None


class LoginResponse(BaseModel):
    """DTO for user login response."""
    AccessToken: Optional[str] = None
    RefreshToken: Optional[str] = None
    RefreshTokenExpiry: Optional[datetime] = None
    UserId: int
    SubscriberId: Optional[int] = None
    Username: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Fullname: Optional[str] = None
    ClientId: Optional[int] = None
    ClientName: Optional[str] = None
    ClientDefaultLanguage: Optional[str] = None
    RolesId: Optional[str] = None
    Permissions: Optional[List[UserPermission]] = None


class RefreshTokenRequest(BaseModel):
    """DTO for refresh token request."""
    RefreshToken: str


class UpdateUserLanguage(BaseModel):
    """DTO for updating a user's preferred language via API."""
    UserId: int
    LanguageCode: str
