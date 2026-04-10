"""User service for managing user CRUD operations and role mappings."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Request
from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from database.dbModel.user.user_model import User
from models.service_models.user.user_service_models import (
    CreateUser,
    UpdateUser,
    UpdateUserLanguage,
    UserWithRoles,
)
from models.common import ResponseData, UResponse
from services.crypto.crypto_service import CryptoService
from services.JWT.JWT_service import JWTService
from config.logger_config import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for managing user operations."""

    def __init__(
        self,
        request: Request,
        db_manager: Optional[PostgresConnectionManager] = None,
        crypto_service: Optional[CryptoService] = None,
        jwt_service: Optional[JWTService] = None,
    ):
        self._request = request
        self._db_manager = db_manager or get_postgres_manager()
        self._crypto_service = crypto_service or CryptoService()
        self._jwt_service = jwt_service or JWTService()

        # Extract claims from JWT token via request state
        self._client_id = self._jwt_service.get_client_id_from_access_token(request)
        self._user_id = self._jwt_service.get_user_id_from_access_token(request)
        self._subscriber_id = self._jwt_service.get_sub_id_from_access_token(request)

    async def get_all_users_async(self) -> ResponseData[List[UserWithRoles]]:
        """Get all active users for the current client and subscriber."""
        response = ResponseData[List[UserWithRoles]](
            success=True,
            message="",
            data=[],
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT * FROM users
                        WHERE status = 1 AND clientid = :client_id AND subscriberid = :subscriber_id
                        ORDER BY username
                    """),
                    {
                        "client_id": self._client_id,
                        "subscriber_id": self._subscriber_id,
                    },
                )
                rows = result.mappings().all()

                if not rows:
                    response.success = False
                    response.message = "No active users found"
                    response.data = []
                    return response

                result_list: List[UserWithRoles] = []
                for row in rows:
                    user = self._row_to_user(row)
                    role_ids = await self._get_user_role_ids(session, user.id)

                    user_dto = UserWithRoles(
                        Id=user.id,
                        Username=user.username or "",
                        Email=user.email,
                        Phone=user.phone,
                        Fullname=user.fullname,
                        Clientid=user.clientid,
                        Status=user.status,
                        Createddate=user.createddate,
                        Createdby=user.createdby,
                        Updateddate=user.updateddate,
                        Updatedby=user.updatedby,
                        RolesId=",".join(role_ids),
                    )
                    result_list.append(user_dto)

                response.success = True
                response.message = "Users fetched successfully"
                response.data = result_list

        except Exception as ex:
            logger.error(f"Error fetching users: {ex}")
            response.success = False
            response.message = f"An error occurred while fetching users: {str(ex)}"
            response.data = []

        return response

    async def get_user_by_id_async(self, user_id: int) -> ResponseData[UserWithRoles]:
        """Get a specific user by ID."""
        response = ResponseData[UserWithRoles](
            success=True,
            message="",
            data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("SELECT * FROM users WHERE id = :user_id AND status = 1"),
                    {"user_id": user_id},
                )
                row = result.mappings().first()

                if row is None:
                    response.success = False
                    response.message = f"No active user found with ID {user_id}"
                    response.data = None
                    return response

                user = self._row_to_user(row)
                role_ids = await self._get_user_role_ids(session, user.id)
                country_code, phone_number = self._split_phone(user.phone)

                user_dto = UserWithRoles(
                    Id=user.id,
                    Username=user.username or "",
                    Email=user.email,
                    CountryCode=country_code,
                    Phone=phone_number,
                    Fullname=user.fullname,
                    Clientid=user.clientid,
                    Status=user.status,
                    CreatedDate=user.createddate,
                    CreatedBy=user.createdby,
                    UpdatedDate=user.updateddate,
                    UpdatedBy=user.updatedby,
                    RolesId=",".join(role_ids),
                )

                response.success = True
                response.message = "User fetched successfully"
                response.data = user_dto

        except Exception as ex:
            logger.error(f"Error fetching user: {ex}")
            response.success = False
            response.message = f"An error occurred while fetching the user: {str(ex)}"
            response.data = None

        return response

    async def create_user_async(self, user_dto: CreateUser) -> UResponse:
        """Create a new user."""
        response = UResponse(status=0, message="")

        try:
            # Generate salt and hash password
            salt = await self._crypto_service.generate_salt()
            password_hash = await self._crypto_service.hash_password(user_dto.password, salt)

            async with await self._db_manager.get_session() as session:
                # Get client info
                client_result = await session.execute(
                    text("""SELECT client_prefix, "DefaultLanguageCode" FROM clients WHERE id = :client_id"""),
                    {"client_id": self._client_id},
                )
                client_row = client_result.mappings().first()

                if client_row is None:
                    response.status = -1
                    response.message = "Client not found"
                    return response

                username = f"{client_row['client_prefix']}-{user_dto.username}"

                # Check for existing user
                existing_result = await session.execute(
                    text("""
                        SELECT id FROM users
                        WHERE LOWER(username) = LOWER(:username)
                        AND clientid = :client_id AND status = 1
                    """),
                    {"username": username, "client_id": self._client_id},
                )
                if existing_result.mappings().first() is not None:
                    response.status = -1
                    response.message = f"A user with the username '{user_dto.Username}' already exists for this client."
                    return response

                # Create user
                phone = self._join_phone(user_dto.CountryCode, user_dto.Phone)
                now = datetime.now()

                insert_result = await session.execute(
                    text("""
                        INSERT INTO users (
                            username, subscriberid, email, phone, fullname,
                            clientid, status, passwordhash, salt, createddate,
                            createdby, "LanguageCode"
                        ) VALUES (
                            :username, :subscriber_id, :email, :phone, :fullname,
                            :client_id, 1, :password_hash, :salt, :created_date,
                            :created_by, :language_code
                        ) RETURNING id
                    """),
                    {
                        "username": username,
                        "subscriber_id": user_dto.SubscriberId or 0,
                        "email": user_dto.Email,
                        "phone": phone,
                        "fullname": user_dto.Fullname,
                        "client_id": self._client_id,
                        "password_hash": password_hash,
                        "salt": salt,
                        "created_date": now,
                        "created_by": str(self._user_id),
                        "language_code": client_row["DefaultLanguageCode"],
                    },
                )
                row = insert_result.mappings().first()
                created_user_id = row["id"] if row else None

                await session.commit()

                # Update role mappings
                if created_user_id:
                    await self._update_user_role_mappings(
                        session, created_user_id, user_dto.roles_id, str(self._user_id)
                    )

                response.status = 0
                response.message = "User created successfully"

        except Exception as ex:
            logger.error(f"Error creating user: {ex}")
            response.status = -1
            response.message = f"An error occurred while creating the user: {str(ex)}"

        return response

    async def update_user_async(self, user_dto: UpdateUser) -> UResponse:
        """Update an existing user."""
        response = UResponse(status=0, message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if user exists
                existing_result = await session.execute(
                    text("SELECT id FROM users WHERE id = :user_id"),
                    {"user_id": user_dto.user_id},
                )
                if existing_result.mappings().first() is None:
                    response.status = 1
                    response.message = f"No user found with ID {user_dto.user_id}"
                    return response

                # Check for duplicate username
                if user_dto.username:
                    duplicate_result = await session.execute(
                        text("""
                            SELECT id FROM users
                            WHERE LOWER(username) = LOWER(:username)
                            AND id != :user_id AND clientid = :client_id AND status = 1
                        """),
                        {
                            "username": user_dto.Username,
                            "user_id": user_dto.UserId,
                            "client_id": self._client_id,
                        },
                    )
                    if duplicate_result.mappings().first() is not None:
                        response.status = -1
                        response.message = f"A user with the username '{user_dto.Username}' already exists for this client."
                        return response

                # Update user
                phone = self._join_phone(user_dto.CountryCode, user_dto.Phone)
                now = datetime.now()

                await session.execute(
                    text("""
                        UPDATE users
                        SET username = :username, email = :email, phone = :phone,
                            fullname = :fullname, updateddate = :updated_date, updatedby = :updated_by
                        WHERE id = :user_id
                    """),
                    {
                        "username": user_dto.Username,
                        "email": user_dto.Email,
                        "phone": phone,
                        "fullname": user_dto.Fullname,
                        "updated_date": now,
                        "updated_by": user_dto.Updatedby,
                        "user_id": user_dto.UserId,
                    },
                )
                await session.commit()

                # Update role mappings
                await self._update_user_role_mappings(
                    session, user_dto.UserId, user_dto.RolesId, user_dto.Updatedby
                )

                response.status = 0
                response.message = "User updated successfully"

        except Exception as ex:
            logger.error(f"Error updating user: {ex}")
            response.status = -1
            response.message = f"An error occurred while updating the user: {str(ex)}"

        return response

    async def delete_user_async(self, user_id: int) -> UResponse:
        """Soft delete a user."""
        response = UResponse(status=0, message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if user exists
                existing_result = await session.execute(
                    text("SELECT id FROM users WHERE id = :user_id"),
                    {"user_id": user_id},
                )
                if existing_result.mappings().first() is None:
                    response.status = 1
                    response.message = f"No user found with ID {user_id}"
                    return response

                now = datetime.now()

                # Soft delete user
                await session.execute(
                    text("UPDATE users SET status = 0, updateddate = :now WHERE id = :user_id"),
                    {"now": now, "user_id": user_id},
                )

                # Soft delete user role mappings
                await session.execute(
                    text("""
                        UPDATE userrolemap
                        SET status = 0, updateddate = :now
                        WHERE userid = :user_id AND status = 1
                    """),
                    {"now": now, "user_id": user_id},
                )
                await session.commit()

                response.status = 0
                response.message = "User deleted successfully"

        except Exception as ex:
            logger.error(f"Error deleting user: {ex}")
            response.status = -1
            response.message = f"An error occurred while deleting the user: {str(ex)}"

        return response

    async def update_user_prefered_language(self, user_lang_dto: UpdateUserLanguage) -> UResponse:
        """Update user's preferred language."""
        response = UResponse(status=0, message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if user exists
                existing_result = await session.execute(
                    text("SELECT id FROM users WHERE id = :user_id"),
                    {"user_id": user_lang_dto.user_id},
                )
                if existing_result.mappings().first() is None:
                    response.status = 1
                    response.message = f"No user found with ID {user_lang_dto.user_id}"
                    return response

                await session.execute(
                    text("UPDATE users SET languagecode = :language_code WHERE id = :user_id"),
                    {
                        "language_code": user_lang_dto.LanguageCode,
                        "user_id": user_lang_dto.UserId,
                    },
                )
                await session.commit()

                response.status = 0
                response.message = "User language updated successfully"

        except Exception as ex:
            logger.error(f"Error updating user language: {ex}")
            response.status = -1
            response.message = f"An error occurred while updating the user language: {str(ex)}"

        return response

    async def _update_user_role_mappings(
        self,
        session,
        user_id: int,
        roles_id: Optional[str],
        updated_by: Optional[str],
    ) -> None:
        """Update user role mappings."""
        now = datetime.now()

        # Soft delete all existing mappings for this user
        await session.execute(
            text("""
                UPDATE userrolemap
                SET status = 0, updateddate = :now, updatedby = :updated_by
                WHERE userid = :user_id
            """),
            {"now": now, "updated_by": updated_by, "user_id": user_id},
        )

        if not roles_id:
            await session.commit()
            return

        # Get client_id for the user
        client_result = await session.execute(
            text("SELECT clientid FROM users WHERE id = :user_id"),
            {"user_id": user_id},
        )
        client_row = client_result.mappings().first()
        client_id = client_row["clientid"] if client_row else None

        # Process each role ID
        for role_id_str in roles_id.split(","):
            role_id_str = role_id_str.strip()
            if not role_id_str.isdigit():
                continue
            role_id = int(role_id_str)

            # Check if mapping already exists
            existing_result = await session.execute(
                text("SELECT id FROM userrolemap WHERE userid = :user_id AND roleid = :role_id"),
                {"user_id": user_id, "role_id": role_id},
            )
            existing_row = existing_result.mappings().first()

            if existing_row:
                # Reactivate existing mapping
                await session.execute(
                    text("""
                        UPDATE userrolemap
                        SET status = 1, updateddate = :now, updatedby = :updated_by
                        WHERE id = :mapping_id
                    """),
                    {
                        "now": now,
                        "updated_by": updated_by,
                        "mapping_id": existing_row["id"],
                    },
                )
            else:
                # Create new mapping
                await session.execute(
                    text("""
                        INSERT INTO userrolemap (
                            userid, roleid, clientid, status, createddate, createdby
                        ) VALUES (
                            :user_id, :role_id, :client_id, 1, :now, :created_by
                        )
                    """),
                    {
                        "user_id": user_id,
                        "role_id": role_id,
                        "client_id": client_id,
                        "now": now,
                        "created_by": updated_by,
                    },
                )

        await session.commit()

    async def _get_user_role_ids(self, session, user_id: int) -> List[str]:
        """Get list of active role IDs for a user as strings."""
        result = await session.execute(
            text("SELECT roleid FROM userrolemap WHERE userid = :user_id AND status = 1"),
            {"user_id": user_id},
        )
        rows = result.mappings().all()
        return [str(row["roleid"]) for row in rows if row["roleid"] is not None]

    @staticmethod
    def _join_phone(country_code: Optional[str], phone: Optional[str]) -> Optional[str]:
        """Join country code and phone number."""
        if not country_code and not phone:
            return None
        if country_code and phone:
            return f"{country_code}-{phone}"
        return phone or country_code

    @staticmethod
    def _split_phone(phone: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """Split phone into country code and number."""
        if not phone:
            return None, None
        parts = phone.split("-", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return None, phone

    @staticmethod
    def _row_to_user(row) -> User:
        """Convert database row to User model."""
        data = dict(row)
        # Map database columns to model fields
        if "languagecode" in data and "language_code" not in data:
            data["language_code"] = data.pop("languagecode")
        if "isactive" in data and "is_active" not in data:
            data["is_active"] = data.pop("isactive")
        if "hashedpassword" in data and "hashed_password" not in data:
            data["hashed_password"] = data.pop("hashedpassword")
        return User.model_validate(data)
