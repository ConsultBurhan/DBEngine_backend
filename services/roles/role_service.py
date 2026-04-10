"""Role service for managing roles and bot mappings."""
from __future__ import annotations

from datetime import datetime
from sre_parse import SUCCESS
from typing import Any, List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from models.common import ResponseData, UEntity, UResponse
from models.service_models.roles.role_service_models import (
    CreateRoleWithBots,
    RoleWithBots,
    UpdateRoleWithBots,
)


class RoleService:
    """Service for role management operations."""

    def __init__(
        self,
        client_id: int,
        user_id: int,
        db_manager: Optional[PostgresConnectionManager] = None,
    ) -> None:
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_roles(self) -> ResponseData[List[RoleWithBots]]:
        """Get all active roles for the current client."""
        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT * FROM roles
                        WHERE clientid = :client_id AND status = 1
                        ORDER BY rolename
                    """),
                    {"client_id": self.client_id},
                )
                role_rows = result.mappings().all()

                result: List[RoleWithBots] = []
                for row in role_rows:
                    bot_ids = await self._get_bot_ids_for_role(session, row["id"])
                    role_dto = RoleWithBots(
                        Id=row["id"],
                        Rolename=row["rolename"],
                        Clientid=row["clientid"],
                        Status=row["status"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                        BotsId=",".join(bot_ids) if bot_ids else None,
                    )
                    result.append(role_dto)

                return ResponseData(
                    Success=True,
                    Message="Roles fetched successfully",
                    Data=result,
                )
        except Exception as exc:
            return ResponseData(
                Success=False,
                Message=f"An error occurred while fetching roles: {exc}",
                Data=None,
            )

    async def get_role_by_id(self, role_id: int) -> ResponseData[RoleWithBots]:
        """Get a single role by ID."""
        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("SELECT * FROM roles WHERE id = :role_id AND status = 1"),
                    {"role_id": role_id},
                )
                row = result.mappings().first()

                if row is None:
                    return ResponseData(
                        Success=False,
                        Message=f"No active role found with ID {role_id}",
                        Data=None,
                    )

                bot_ids = await self._get_bot_ids_for_role(session, row["id"])
                role_dto = RoleWithBots(
                    Id=row["id"],
                    Rolename=row["rolename"],
                    Clientid=row["clientid"],
                    Status=row["status"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                    BotsId=",".join(bot_ids) if bot_ids else None,
                )

                return ResponseData(
                    Success=True,
                    Message="Role fetched successfully",
                    Data=role_dto,
                )
        except Exception as exc:
            return ResponseData(
                Success=False,
                Message=f"An error occurred while fetching the role: {exc}",
                Data=None,
            )

    async def create_role(self, create_dto: CreateRoleWithBots) -> UResponse:
        """Create a new role with bot mappings."""
        try:
            async with await self._db_manager.get_session() as session:
                existing_result = await session.execute(
                    text("""
                        SELECT id FROM roles
                        WHERE clientid = :client_id
                          AND LOWER(rolename) = LOWER(:rolename)
                          AND status = 1
                    """),
                    {"client_id": self.client_id, "rolename": create_dto.Rolename},
                )
                if existing_result.mappings().first() is not None:
                    return UResponse(
                        Status=-1,
                        Message="A role with the same name already exists",
                    )

                now = datetime.now()
                insert_result = await session.execute(
                    text("""
                        INSERT INTO roles (
                            rolename, clientid, status, createddate, createdby
                        ) VALUES (
                            :rolename, :client_id, :status, :created_date, :created_by
                        ) RETURNING id
                    """),
                    {
                        "rolename": create_dto.Rolename,
                        "client_id": self.client_id,
                        "status": create_dto.Status,
                        "created_date": now,
                        "created_by": str(self.user_id),
                    },
                )
                row = insert_result.mappings().first()
                role_id = row["id"] if row else None

                await session.commit()

                if role_id:
                    bot_result = await self._update_bot_role_mappings(
                        session, role_id, create_dto.BotsId
                    )
                    if bot_result.Status != 0:
                        return UResponse(
                            Status=bot_result.Status,
                            Message=f"Role created successfully, but there was an error creating Bot role map: {bot_result.Message}",
                        )

                return UResponse(Status=0, Message="Role created successfully")
        except Exception as exc:
            return UResponse(
                Status=-1,
                Message=f"An error occurred while creating the role: {exc}",
            )

    async def update_role(self, update_dto: UpdateRoleWithBots) -> UResponse:
        """Update an existing role and its bot mappings."""
        try:
            async with await self._db_manager.get_session() as session:
                existing_result = await session.execute(
                    text("SELECT id FROM roles WHERE id = :role_id"),
                    {"role_id": update_dto.Id},
                )
                if existing_result.mappings().first() is None:
                    return UResponse(
                        Status=1,
                        Message=f"No role found with ID {update_dto.Id}",
                    )

                now = datetime.now()
                await session.execute(
                    text("""
                        UPDATE roles
                        SET rolename = :rolename,
                            clientid = :client_id,
                            status = :status,
                            updateddate = :updated_date,
                            updatedby = :updated_by
                        WHERE id = :role_id
                    """),
                    {
                        "rolename": update_dto.Rolename,
                        "client_id": self.client_id,
                        "status": update_dto.Status,
                        "updated_date": now,
                        "updated_by": str(self.user_id),
                        "role_id": update_dto.Id,
                    },
                )
                await session.commit()

                bot_result = await self._update_bot_role_mappings(
                    session, update_dto.Id, update_dto.BotsId
                )
                if bot_result.Status != 0:
                    return UResponse(
                        Status=bot_result.Status,
                        Message=f"Role updated successfully, but there was an error updating Bot role mappings: {bot_result.Message}",
                    )

                return UResponse(Status=0, Message="Role updated successfully")
        except Exception as exc:
            return UResponse(
                Status=-1,
                Message=f"An error occurred while updating the role: {exc}",
            )

    async def delete_role(self, role_id: int) -> UResponse:
        """Soft delete a role and its associated mappings."""
        try:
            async with await self._db_manager.get_session() as session:
                existing_result = await session.execute(
                    text("SELECT id FROM roles WHERE id = :role_id"),
                    {"role_id": role_id},
                )
                if existing_result.mappings().first() is None:
                    return UResponse(
                        Status=1,
                        Message=f"No role found with ID {role_id}",
                    )

                now = datetime.now()
                # Soft delete role
                await session.execute(
                    text("""
                        UPDATE roles
                        SET status = 0, updateddate = :now
                        WHERE id = :role_id
                    """),
                    {"now": now, "role_id": role_id},
                )

                # Soft delete bot role mappings
                await session.execute(
                    text("""
                        UPDATE botrolemap
                        SET status = 0, updateddate = :now, updatedby = :updated_by
                        WHERE roleid = :role_id
                    """),
                    {"now": now, "updated_by": str(self.user_id), "role_id": role_id},
                )

                # Soft delete user role mappings
                await session.execute(
                    text("""
                        UPDATE userrolemap
                        SET status = 0, updateddate = :now, updatedby = :updated_by
                        WHERE roleid = :role_id
                    """),
                    {"now": now, "updated_by": str(self.user_id), "role_id": role_id},
                )
                await session.commit()

                return UResponse(
                    Status=0,
                    Message="Role and associated bot mappings deleted successfully",
                )
        except Exception as exc:
            return UResponse(
                Status=-1,
                Message=f"An error occurred while deleting the role: {exc}",
            )

    async def get_roles(self) -> ResponseData[List[UEntity]]:
        """Get simplified list of active roles."""
        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, rolename FROM roles
                        WHERE status = 1 AND clientid = :client_id
                        ORDER BY rolename
                    """),
                    {"client_id": self.client_id},
                )
                role_rows = result.mappings().all()

                if not role_rows:
                    return ResponseData(
                        Success=False,
                        Message="No active roles found",
                        Data=[],
                    )

                result = [
                    UEntity(Id=row["id"], Name=row["rolename"]) for row in role_rows
                ]

                return ResponseData(
                    Success=True,
                    Message="Roles fetched successfully",
                    Data=result,
                )
        except Exception as exc:
            return ResponseData(
                Success=False,
                Message=f"An error occurred while fetching roles: {exc}",
                Data=None,
            )

    async def get_roles_by_bot_id(self, bot_id: int) -> ResponseData[List[UEntity]]:
        """Get roles associated with a specific bot ID."""
        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT DISTINCT roleid FROM botrolemap
                        WHERE botid = :bot_id AND status = 1
                    """),
                    {"bot_id": bot_id},
                )
                role_ids = result.mappings().all()

                if not role_ids:
                    return ResponseData(
                        Success=True,
                        Message="Roles fetched successfully.",
                        Data=[],
                    )

                role_id_list = [r["roleid"] for r in role_ids if r["roleid"] is not None]

                result = await session.execute(
                    text("""
                        SELECT id, rolename FROM roles
                        WHERE status = 1 AND id = ANY(:role_ids)
                        ORDER BY rolename
                    """),
                    {"role_ids": role_id_list},
                )
                role_rows = result.mappings().all()

                result = [
                    UEntity(Id=row["id"], Name=row["rolename"]) for row in role_rows
                ]

                return ResponseData(
                    Success=True,
                    Message="Roles fetched successfully.",
                    Data=result,
                )
        except Exception as exc:
            return ResponseData(
                Success=False,
                Message=f"An error occurred while fetching roles: {exc}",
                Data=None,
            )

    async def _get_bot_ids_for_role(self, session, role_id: int) -> List[str]:
        """Get bot IDs associated with a role."""
        result = await session.execute(
            text("SELECT botid FROM botrolemap WHERE roleid = :role_id AND status = 1"),
            {"role_id": role_id},
        )
        rows = result.mappings().all()
        return [str(row["botid"]) for row in rows if row["botid"] is not None]

    async def _update_bot_role_mappings(
        self, session, role_id: int, bots_id: Optional[str]
    ) -> UResponse:
        """Update bot-role mappings for a role."""
        try:
            now = datetime.now()

            # Soft delete existing mappings
            await session.execute(
                text("""
                    UPDATE botrolemap
                    SET status = 0, updateddate = :now, updatedby = :updated_by
                    WHERE roleid = :role_id
                """),
                {"now": now, "updated_by": str(self.user_id), "role_id": role_id},
            )

            # Add new mappings if provided
            if bots_id:
                bot_id_strings = [b.strip() for b in bots_id.split(",") if b.strip()]
                for bot_id_str in bot_id_strings:
                    if bot_id_str.isdigit():
                        bot_id = int(bot_id_str)
                        existing_result = await session.execute(
                            text("""
                                SELECT id FROM botrolemap
                                WHERE roleid = :role_id AND botid = :bot_id
                            """),
                            {"role_id": role_id, "bot_id": bot_id},
                        )
                        existing_row = existing_result.mappings().first()

                        if existing_row:
                            # Reactivate existing mapping
                            await session.execute(
                                text("""
                                    UPDATE botrolemap
                                    SET status = 1, updateddate = :now, updatedby = :updated_by
                                    WHERE id = :mapping_id
                                """),
                                {
                                    "now": now,
                                    "updated_by": str(self.user_id),
                                    "mapping_id": existing_row["id"],
                                },
                            )
                        else:
                            # Create new mapping
                            client_result = await session.execute(
                                text("SELECT clientid FROM roles WHERE id = :role_id"),
                                {"role_id": role_id},
                            )
                            client_row = client_result.mappings().first()
                            client_id = client_row["clientid"] if client_row else None

                            await session.execute(
                                text("""
                                    INSERT INTO botrolemap (
                                        roleid, botid, clientid, status, createddate, createdby
                                    ) VALUES (
                                        :role_id, :bot_id, :client_id, 1, :now, :created_by
                                    )
                                """),
                                {
                                    "role_id": role_id,
                                    "bot_id": bot_id,
                                    "client_id": client_id,
                                    "now": now,
                                    "created_by": str(self.user_id),
                                },
                            )

            await session.commit()
            return UResponse(
                Status=0, Message="Bot-role mappings updated successfully"
            )
        except Exception as exc:
            return UResponse(
                Status=-1,
                Message=f"An error occurred while updating bot-role mappings: {exc}",
            )
