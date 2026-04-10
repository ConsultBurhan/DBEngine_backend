"""Authentication service for user login, password change, and token management."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from models.service_models.user.user_service_models import (
    ChangePassword,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    UserPermission,
)
from models.common import ResponseData, UResponse
from services.crypto.crypto_service import CryptoService
from config.logger_config import get_logger

logger = get_logger(__name__)


class AuthenticationService:
    """Service for authentication operations including login, password change, and token refresh."""

    def __init__(
        self,
        db_manager: Optional[PostgresConnectionManager] = None,
        crypto_service: Optional[CryptoService] = None,
    ):
        self._db_manager = db_manager or get_postgres_manager()
        self._crypto_service = crypto_service or CryptoService()

    async def change_password_async(self, change_password_dto: ChangePassword) -> UResponse:
        """Change user's password after verifying old password."""
        response = UResponse(Status=0, Message="")
        try:
            async with await self._db_manager.get_session() as session:
                # Get user by ID
                result = await session.execute(
                    text("SELECT id, passwordhash, salt FROM users WHERE id = :user_id"),
                    {"user_id": change_password_dto.UserId},
                )
                logger.info("User Info")
                row = result.mappings().first()

                if row is None:
                    response.Status = 1
                    response.Message = "User not found."
                    return response

                # Verify old password
                is_old_password_valid = await self._verify_password(
                    change_password_dto.OldPassword,
                    row["passwordhash"],
                    row["salt"],
                )
                if not is_old_password_valid:
                    response.Status = 1
                    response.Message = "Old password is incorrect."
                    return response

                # Generate new salt and hash
                new_salt = await self._crypto_service.generate_salt()
                new_password_hash = await self._crypto_service.hash_password(
                    change_password_dto.NewPassword, new_salt
                )

                now = datetime.now()

                # Update user password
                await session.execute(
                    text("""
                        UPDATE users
                        SET passwordhash = :password_hash,
                            salt = :salt,
                            updateddate = :updated_date
                        WHERE id = :user_id
                    """),
                    {
                        "password_hash": new_password_hash,
                        "salt": new_salt,
                        "updated_date": now,
                        "user_id": change_password_dto.UserId,
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Password changed successfully."

        except Exception as ex:
            logger.error(f"Error changing password: {ex}")
            response.Status = 1
            response.Message = f"An error occurred: {str(ex)}"

        return response

    async def user_login(self, login_request: LoginRequest) -> ResponseData[LoginResponse]:
        """Authenticate user and return login response with permissions."""
        result = ResponseData[LoginResponse](
            Success=True,
            Message="SUCCESS",
            Data=LoginResponse(UserId=0),
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Get user by username
                user_result = await session.execute(
                    text("""
                        SELECT id, username, subscriberid, email, phone, fullname,
                               clientid, passwordhash, salt, "LanguageCode"
                        FROM users
                        WHERE LOWER(username) = LOWER(:username) AND status = 1
                    """),
                    {"username": login_request.Username},
                )
                user_row = user_result.mappings().first()

                if user_row is None:
                    result.Success = False
                    result.Message = "Invalid Username or Password"
                    return result

                # Verify password
                is_password_valid = await self._verify_password(
                    login_request.Password,
                    user_row["passwordhash"],
                    user_row["salt"],
                )

                if not is_password_valid:
                    result.Success = False
                    result.Message = "Invalid Username or Password"
                    return result

                user_id = user_row["id"]

                # Get user role IDs
                role_result = await session.execute(
                    text("""
                        SELECT roleid FROM userrolemap
                        WHERE userid = :user_id AND status = 1
                    """),
                    {"user_id": user_id},
                )
                role_rows = role_result.mappings().all()
                role_ids = [row["roleid"] for row in role_rows if row["roleid"] is not None]

                # Get client info
                client_result = await session.execute(
                    text("""
                        SELECT clientname FROM clients
                        WHERE id = :client_id AND status = 1
                    """),
                    {"client_id": user_row["clientid"]},
                )
                client_row = client_result.mappings().first()

                # Get permissions
                permissions = await self._get_user_permissions_async(session, user_id, role_ids)

                # Build response
                result.Data = LoginResponse(
                    UserId=user_id,
                    SubscriberId=user_row["subscriberid"],
                    Username=user_row["username"],
                    Email=user_row["email"],
                    Phone=user_row["phone"],
                    Fullname=user_row["fullname"],
                    ClientId=user_row["clientid"],
                    ClientName=client_row["clientname"] if client_row else None,
                    ClientDefaultLanguage=user_row["LanguageCode"],
                    RolesId=",".join(str(rid) for rid in role_ids),
                    Permissions=permissions,
                )

        except Exception as ex:
            logger.error(f"Error during login: {ex}")
            result.Success = False
            result.Message = "An unexpected error occurred while processing the login request."

        return result

    async def refresh_token_async(
        self, refresh_token_request: RefreshTokenRequest
    ) -> ResponseData[LoginResponse]:
        """Refresh access token using valid refresh token."""
        result = ResponseData[LoginResponse](
            Success=True,
            Message="SUCCESS",
            Data=LoginResponse(UserId=0),
        )

        try:
            async with await self._db_manager.get_session() as session:
                now = datetime.now()

                # Get user by refresh token
                user_result = await session.execute(
                    text("""
                        SELECT id, username, subscriberid, email, phone, fullname,
                               clientid, refreshtokenexpiry, "LanguageCode"
                        FROM users
                        WHERE refreshtoken = :refresh_token
                          AND refreshtokenexpiry > :now
                          AND status = 1
                    """),
                    {"refresh_token": refresh_token_request.RefreshToken, "now": now},
                )
                user_row = user_result.mappings().first()

                if user_row is None:
                    result.Success = False
                    result.Message = "User not found"
                    return result

                user_id = user_row["id"]

                # Get user role IDs
                role_result = await session.execute(
                    text("""
                        SELECT roleid FROM userrolemap
                        WHERE userid = :user_id AND status = 1
                    """),
                    {"user_id": user_id},
                )
                role_rows = role_result.mappings().all()
                role_ids = [row["roleid"] for row in role_rows if row["roleid"] is not None]

                # Get client info
                client_result = await session.execute(
                    text("""
                        SELECT clientname, "DefaultLanguageCode" FROM clients
                        WHERE id = :client_id AND status = 1
                    """),
                    {"client_id": user_row["clientid"]},
                )
                client_row = client_result.mappings().first()

                # Get permissions
                permissions = await self._get_user_permissions_async(session, user_id, role_ids)

                # Build response
                result.Data = LoginResponse(
                    UserId=user_id,
                    SubscriberId=user_row["subscriberid"],
                    Username=user_row["username"],
                    Email=user_row["email"],
                    Phone=user_row["phone"],
                    Fullname=user_row["fullname"],
                    ClientId=user_row["clientid"],
                    ClientName=client_row["clientname"] if client_row else None,
                    ClientDefaultLanguage=client_row["DefaultLanguageCode"] if client_row else None,
                    RolesId=",".join(str(rid) for rid in role_ids),
                    Permissions=permissions,
                )

        except Exception as ex:
            logger.error(f"Error during token refresh: {ex}")
            result.Success = False
            result.Message = "An error occurred during token refresh."

        return result

    async def update_user_tokens_async(
        self,
        user_id: int,
        access_token: str,
        refresh_token: str,
        refresh_token_expiry: datetime,
    ) -> bool:
        """Update user's access and refresh tokens."""
        try:
            async with await self._db_manager.get_session() as session:
                await session.execute(
                    text("""
                        UPDATE users
                        SET accesstoken = :access_token,
                            refreshtoken = :refresh_token,
                            refreshtokenexpiry = :refresh_token_expiry,
                            updateddate = :updated_date
                        WHERE id = :user_id
                    """),
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "refresh_token_expiry": refresh_token_expiry,
                        "updated_date": datetime.now(),
                        "user_id": user_id,
                    },
                )
                await session.commit()
                return True

        except Exception as ex:
            logger.error(f"Error updating user tokens: {ex}")
            return False

    async def _verify_password(
        self, password: str, stored_hash: Optional[str], stored_salt: Optional[str]
    ) -> bool:
        """Verify password against stored hash and salt."""
        if not stored_hash or not stored_salt:
            return False
        computed_hash = await self._crypto_service.hash_password(password, stored_salt)
        return computed_hash == stored_hash

    async def _get_user_permissions_async(
        self, session, user_id: int, role_ids: List[int]
    ) -> List[UserPermission]:
        """Get hierarchical permissions for user's roles."""
        if not role_ids:
            return []

        # Get permissions for user's roles
        permission_result = await session.execute(
            text("""
                SELECT p.id as permission_id,
                       p.canview as can_view,
                       p.cancreate as can_create,
                       p.canupdate as can_update,
                       p.candelete as can_delete,
                       pt.id as permission_task_id,
                       pt.permissiontaskname as permission_task_name,
                       pt.path,
                       pt.parentid as parent_id,
                       pt.displayorder as display_order,
                       pt.icon
                FROM permission p
                JOIN permissiontasks pt ON p.permissiontaskid = pt.id
                WHERE p.roleid = ANY(:role_ids) AND p.isactive = TRUE
            """),
            {"role_ids": role_ids},
        )
        permission_rows = permission_result.mappings().all()

        # Build permission DTOs
        permissions = []
        for row in permission_rows:
            permissions.append(
                UserPermission(
                    PermissionId=row["permission_id"],
                    CanView=row["can_view"] or False,
                    CanCreate=row["can_create"] or False,
                    CanUpdate=row["can_update"] or False,
                    CanDelete=row["can_delete"] or False,
                    PermissionTaskId=row["permission_task_id"],
                    PermissionTaskName=row["permission_task_name"] or "",
                    Path=row["path"] or "",
                    ParentId=row["parent_id"] or 0,
                    DisplayOrder=row["display_order"] or 0,
                    Icon=row["icon"] or "",
                    Children=[],
                )
            )

        # Build hierarchical structure
        return self._build_permission_hierarchy(permissions)

    @staticmethod
    def _build_permission_hierarchy(permissions: List[UserPermission]) -> List[UserPermission]:
        """Build hierarchical permission structure from flat list."""
        permission_dict = {p.PermissionTaskId: p for p in permissions}
        root_permissions: List[UserPermission] = []

        for permission in permissions:
            if permission.ParentId == 0:
                root_permissions.append(permission)
            elif permission.ParentId in permission_dict:
                parent = permission_dict[permission.ParentId]
                if parent.Children is None:
                    parent.Children = []
                parent.Children.append(permission)

        # Sort by display order
        return sorted(root_permissions, key=lambda p: p.DisplayOrder)
