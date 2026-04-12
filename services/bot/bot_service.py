"""Bot service for managing bot operations."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.service_models.bot.bot_service_models import BotsList, CreateBot, UpdateBot, BotDropDto, BotRoleMapList, CreateBotRole
from models.common import ResponseData, UResponse, UEntity
from models.service_models.document.document_group_service_model import DocumentGroupCreate
from services.fileupload.file_upload_service import upload_file
from config.logger_config import get_logger

logger = get_logger(__name__)


class BotService:
    """Service for bot operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_bots_async(self) -> ResponseData[List[BotsList]]:
        """Get all bots for the current client, filtered by status and ordered by bot name."""
        response = ResponseData[List[BotsList]](
            Success=True,
            Message="",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            id,
                            botname,
                            logo,
                            clientid,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby,
                            status
                        FROM bots
                        WHERE status = 1
                          AND clientid = :client_id
                        ORDER BY botname
                    """),
                    {"client_id": self.client_id}
                )
                rows = result.mappings().all()

                bots = [
                    BotsList(
                        Id=row["id"],
                        Botname=row["botname"],
                        Logo=row["logo"],
                        Clientid=row["clientid"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                        Status=row["status"]
                    )
                    for row in rows
                ]

                response.Data = bots
                response.Success = True
                response.Message = "Bots fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching bots: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bots: {str(ex)}"
            response.Data = []

        return response

    async def get_bot_by_id_async(self, bot_id: int) -> ResponseData[BotsList]:
        """Get a single bot by ID, filtered by status."""
        response = ResponseData[BotsList](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            id,
                            botname,
                            logo,
                            clientid,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby,
                            status
                        FROM bots
                        WHERE id = :bot_id
                          AND status = 1
                    """),
                    {"bot_id": bot_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"No active bot found with ID {bot_id}"
                    return response

                bot = BotsList(
                    Id=row["id"],
                    Botname=row["botname"],
                    Logo=row["logo"],
                    Clientid=row["clientid"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                    Status=row["status"]
                )

                response.Data = bot
                response.Success = True
                response.Message = "Bot fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching bot by ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bot: {str(ex)}"

        return response

    async def create_bot_async(self, create_bot: CreateBot) -> UResponse:
        """Create a new bot with optional logo upload and associated document group."""
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if bot with same name already exists for this client
                result = await session.execute(
                    text("""
                        SELECT id FROM bots
                        WHERE clientid = :client_id
                          AND LOWER(TRIM(botname)) = LOWER(TRIM(:botname))
                          AND status = 1
                    """),
                    {"client_id": self.client_id, "botname": create_bot.Botname}
                )
                existing_bot = result.mappings().first()

                if existing_bot:
                    response.Status = 1
                    response.Message = "A bot with the given name already exists for this client."
                    return response

                # Upload logo if provided
                logo_filename = None
                if create_bot.Logo:
                    logo_filename = await upload_file(create_bot.Logo)

                # Create new bot
                now = datetime.now()
                insert_result = await session.execute(
                    text("""
                        INSERT INTO bots (
                            botname, logo, clientid, createddate, createdby, status
                        ) VALUES (
                            :botname, :logo, :client_id, :created_date, :created_by, :status
                        ) RETURNING id
                    """),
                    {
                        "botname": create_bot.Botname.strip(),
                        "logo": logo_filename,
                        "client_id": self.client_id,
                        "created_date": now,
                        "created_by": str(self.user_id),
                        "status": 1,
                    }
                )
                await session.commit()
                bot_row = insert_result.mappings().first()
                bot_id = bot_row["id"]

                # Create associated document group
                from services.document.document_group_service import DocumentgroupService
                document_group_service = DocumentgroupService(
                    client_id=self.client_id,
                    user_id=self.user_id,
                    db_manager=self._db_manager
                )

                document_group_create = DocumentGroupCreate(
                    Botid=bot_id,
                    Documentgroupname=create_bot.Botname.strip(),
                    Status=1
                )
                document_group_response = await document_group_service.create_document_group_async(
                    document_group_create
                )

                if document_group_response.Status != 0:
                    response.Status = 1
                    response.Message = "Error while creating a bot"
                    return response

                response.Status = 0
                response.Message = "Bot created successfully"

        except Exception as ex:
            logger.error(f"Error creating bot: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating the bot: {str(ex)}"

        return response

    async def update_bot_async(self, update_bot: UpdateBot) -> UResponse:
        """Update an existing bot with optional logo upload."""
        response = UResponse(Status=0, Message="Bot updated successfully")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if bot exists
                result = await session.execute(
                    text("""
                        SELECT id, logo FROM bots
                        WHERE id = :bot_id
                    """),
                    {"bot_id": update_bot.BotId}
                )
                existing_bot = result.mappings().first()

                if existing_bot is None:
                    response.Status = 1
                    response.Message = f"Bot with ID {update_bot.BotId} not found"
                    return response

                # Check if another bot with same name exists for this client
                result = await session.execute(
                    text("""
                        SELECT id FROM bots
                        WHERE clientid = :client_id
                          AND id != :bot_id
                          AND LOWER(TRIM(botname)) = LOWER(TRIM(:botname))
                          AND status = 1
                    """),
                    {"client_id": self.client_id, "bot_id": update_bot.BotId, "botname": update_bot.Botname}
                )
                botname_exists = result.mappings().first()

                if botname_exists:
                    response.Status = 1
                    response.Message = "A bot with the given name already exists for this client."
                    return response

                # Upload new logo if provided
                logo_filename = existing_bot["logo"]
                if update_bot.Logo:
                    logo_filename = await upload_file(update_bot.Logo)

                # Update bot
                now = datetime.now()
                await session.execute(
                    text("""
                        UPDATE bots
                        SET botname = :botname,
                            logo = :logo,
                            clientid = :client_id,
                            updateddate = :updated_date,
                            updatedby = :updated_by
                        WHERE id = :bot_id
                    """),
                    {
                        "botname": update_bot.Botname,
                        "logo": logo_filename,
                        "client_id": self.client_id,
                        "updated_date": now,
                        "updated_by": str(self.user_id),
                        "bot_id": update_bot.BotId,
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error updating bot: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating the bot: {str(ex)}"

        return response

    async def delete_bot_async(self, bot_id: int) -> UResponse:
        """Soft delete a bot by setting status to 0."""
        response = UResponse(Status=0, Message="Bot deleted successfully")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if bot exists
                result = await session.execute(
                    text("""
                        SELECT id FROM bots
                        WHERE id = :bot_id
                    """),
                    {"bot_id": bot_id}
                )
                bot = result.mappings().first()

                if bot is None:
                    response.Status = 1
                    response.Message = f"Bot with ID {bot_id} not found"
                    return response

                # Soft delete by setting status to 0
                await session.execute(
                    text("""
                        UPDATE bots
                        SET status = 0
                        WHERE id = :bot_id
                    """),
                    {"bot_id": bot_id}
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error deleting bot: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting bot: {str(ex)}"

        return response

    async def get_bots_async(self) -> ResponseData[List[BotDropDto]]:
        """Get bots for dropdown with type based on database connection status."""
        response = ResponseData[List[BotDropDto]](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Get all active bots for the client
                result = await session.execute(
                    text("""
                        SELECT id, botname
                        FROM bots
                        WHERE status = 1
                          AND clientid = :client_id
                        ORDER BY botname
                    """),
                    {"client_id": self.client_id}
                )
                bots = result.mappings().all()

                if not bots:
                    response.Success = False
                    response.Message = "No active bots found"
                    response.Data = None
                    return response

                # Get bot IDs that have database connections
                bot_ids = [bot["id"] for bot in bots]
                db_result = await session.execute(
                    text("""
                        SELECT DISTINCT botid
                        FROM databaseconnections
                        WHERE botid = ANY(:bot_ids)
                    """),
                    {"bot_ids": bot_ids}
                )
                db_connected_bot_ids = {row["botid"] for row in db_result.mappings().all() if row["botid"]}

                # Create bot dropdown list
                bot_list = [
                    BotDropDto(
                        Id=bot["id"],
                        Name=bot["botname"],
                        Type=2 if bot["id"] in db_connected_bot_ids else 1
                    )
                    for bot in bots
                ]

                response.Data = bot_list
                response.Success = True
                response.Message = "Bots fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching bots: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bots: {str(ex)}"
            response.Data = None

        return response

    async def get_bot_role_map_list_async(self, bot_id: int) -> ResponseData[BotRoleMapList]:
        """Get role mappings for a specific bot."""
        response = ResponseData[BotRoleMapList](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT roleid
                        FROM botrolemap
                        WHERE botid = :bot_id
                          AND clientid = :client_id
                          AND status = 1
                    """),
                    {"bot_id": bot_id, "client_id": self.client_id}
                )
                rows = result.mappings().all()

                role_ids = [row["roleid"] for row in rows if row["roleid"] is not None]

                bot_role_map = BotRoleMapList(
                    BotId=bot_id,
                    Clientid=self.client_id,
                    Roleid=role_ids
                )

                response.Data = bot_role_map
                response.Success = True
                response.Message = "Bot roles fetched successfully."

        except Exception as ex:
            logger.error(f"Error fetching bot roles: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching document group roles: {str(ex)}"

        return response

    async def _update_bot_role_mappings(self, bot_id: int, roles_id: Optional[str]) -> UResponse:
        """Update bot role mappings by adding new roles, deactivating removed roles, and reactivating existing roles."""
        response = UResponse(Status=0, Message="")

        try:
            # Parse new role IDs safely
            new_role_ids = []
            if roles_id and roles_id.strip():
                for r in roles_id.split(","):
                    r = r.strip()
                    if r:
                        try:
                            new_role_ids.append(int(r))
                        except ValueError:
                            continue

            async with await self._db_manager.get_session() as session:
                # Get all existing mappings for this bot
                result = await session.execute(
                    text("""
                        SELECT id, roleid, status
                        FROM botrolemap
                        WHERE botid = :bot_id
                          AND clientid = :client_id
                    """),
                    {"bot_id": bot_id, "client_id": self.client_id}
                )
                existing_mappings = result.mappings().all()

                existing_role_ids = {m["roleid"] for m in existing_mappings if m["roleid"]}

                now = datetime.now()

                # 1. Deactivate roles not in the new list
                for mapping in existing_mappings:
                    role_id = mapping["roleid"]
                    current_status = mapping["status"]

                    if role_id not in new_role_ids and current_status == 1:
                        await session.execute(
                            text("""
                                UPDATE botrolemap
                                SET status = 0,
                                    updateddate = :updated_date,
                                    updatedby = :updated_by
                                WHERE id = :mapping_id
                            """),
                            {
                                "updated_date": now,
                                "updated_by": str(self.user_id),
                                "mapping_id": mapping["id"],
                            }
                        )
                    elif role_id in new_role_ids and current_status == 0:
                        # Reactivate existing mapping
                        await session.execute(
                            text("""
                                UPDATE botrolemap
                                SET status = 1,
                                    updateddate = :updated_date,
                                    updatedby = :updated_by
                                WHERE id = :mapping_id
                            """),
                            {
                                "updated_date": now,
                                "updated_by": str(self.user_id),
                                "mapping_id": mapping["id"],
                            }
                        )

                # 2. Add new roles
                new_roles_to_add = [rid for rid in new_role_ids if rid not in existing_role_ids]

                if new_roles_to_add:
                    for role_id in new_roles_to_add:
                        await session.execute(
                            text("""
                                INSERT INTO botrolemap (
                                    botid, roleid, clientid, status,
                                    createddate, createdby
                                ) VALUES (
                                    :bot_id, :role_id, :client_id, 1,
                                    :created_date, :created_by
                                )
                            """),
                            {
                                "bot_id": bot_id,
                                "role_id": role_id,
                                "client_id": self.client_id,
                                "created_date": now,
                                "created_by": str(self.user_id),
                            }
                        )

                await session.commit()

                response.Status = 0
                response.Message = "Bot role mappings updated successfully."

        except Exception as ex:
            logger.error(f"Error updating bot role mappings: {ex}")
            response.Status = -1
            response.Message = f"An error occurred while updating Bot role mappings: {str(ex)}"

        return response

    async def create_bot_role_map(self, create_bot_role: CreateBotRole) -> UResponse:
        """Create or update bot role mappings after validating input."""
        response = UResponse(Status=0, Message="")

        try:
            if create_bot_role is None or create_bot_role.BotId <= 0:
                response.Status = -1
                response.Message = "Invalid request. Bot ID is required."
                return response

            return await self._update_bot_role_mappings(create_bot_role.BotId, create_bot_role.RolesId)

        except Exception as ex:
            logger.error(f"Error creating bot role map: {ex}")
            response.Status = -1
            response.Message = f"An error occurred while creating document group role map: {str(ex)}"

        return response

    async def get_bots_by_role_id_async(self, role_ids: str) -> ResponseData[List[UEntity]]:
        """Get bots mapped to specific role IDs."""
        response = ResponseData[List[UEntity]](
            Success=True,
            Message="",
            Data=None
        )

        try:
            # Convert comma-separated role IDs into a list of integers
            role_id_list = []
            if role_ids and role_ids.strip():
                for r in role_ids.split(","):
                    r = r.strip()
                    if r:
                        try:
                            role_id_list.append(int(r))
                        except ValueError:
                            continue

            if not role_id_list:
                response.Success = False
                response.Message = "Invalid or empty role IDs provided."
                return response

            async with await self._db_manager.get_session() as session:
                # Get all bot IDs mapped to these roles
                result = await session.execute(
                    text("""
                        SELECT DISTINCT botid
                        FROM botrolemap
                        WHERE roleid = ANY(:role_ids)
                    """),
                    {"role_ids": role_id_list}
                )
                bot_ids_rows = result.mappings().all()
                bot_ids = [row["botid"] for row in bot_ids_rows if row["botid"]]

                if not bot_ids:
                    response.Success = False
                    response.Message = "No bots mapped for the given roles."
                    return response

                # Fetch bots that are active and in the allowed bot list
                result = await session.execute(
                    text("""
                        SELECT id, botname
                        FROM bots
                        WHERE id = ANY(:bot_ids)
                          AND status = 1
                        ORDER BY botname
                    """),
                    {"bot_ids": bot_ids}
                )
                bots = result.mappings().all()

                if not bots:
                    response.Success = False
                    response.Message = "No active bots found for the given roles."
                    return response

                bot_list = [
                    UEntity(
                        Id=bot["id"],
                        Name=bot["botname"]
                    )
                    for bot in bots
                ]

                response.Data = bot_list
                response.Success = True
                response.Message = "Bots fetched successfully."

        except Exception as ex:
            logger.error(f"Error fetching bots by role IDs: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bots: {str(ex)}"
            response.Data = None

        return response
