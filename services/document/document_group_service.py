"""Document group service for managing document group operations."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from models.service_models.document_group.document_group_service_model import (
    CreateDocumentGroupRole,
    DocumentGroupCreate,
    DocumentGroupList,
    DocumentGroupRoleMapList,
    DocumentGroupUpdate,
)
from models.common import ResponseData, UResponse
from config.logger_config import get_logger

logger = get_logger(__name__)


class DocumentgroupService:
    """Service for document group operations including CRUD and role mappings."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self._client_id = client_id
        self._user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_document_groups_async(
        self, bot_id: Optional[int]
    ) -> ResponseData[List[DocumentGroupList]]:
        """Get all document groups for a bot."""
        response = ResponseData[List[DocumentGroupList]](
            Success=True,
            Message="Document groups fetched successfully",
            Data=[],
        )

        try:
            if bot_id is None:
                response.Success = False
                response.Message = "Bot Id is required"
                return response

            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT 
                        dg.id,
                        dg.clientid,
                        dg.botid,
                        b.botname,
                        dg.documentgroupname,
                        dg.createddate,
                        dg.createdby,
                        dg.updateddate,
                        dg.updatedby,
                        dg.status
                    FROM documentgroups dg
                    INNER JOIN bots b ON dg.botid = b.id
                    WHERE dg.status = 1 AND dg.botid = :bot_id
                    ORDER BY dg.documentgroupname ASC
                """)
                result = await session.execute(query, {"bot_id": bot_id})
                rows = result.mappings().all()
                logger.info(rows)
                document_groups = [
                    DocumentGroupList(
                        Id=row["id"],
                        Clientid=row["clientid"],
                        Botid=row["botid"],
                        BotName=row["botname"],
                        Documentgroupname=row["documentgroupname"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                        Status=row["status"],
                    )
                    for row in rows
                ]

                response.Data = document_groups

        except Exception as ex:
            logger.error(f"Error fetching document groups for bot {bot_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching document groups: {str(ex)}"

        return response

    async def get_document_group_by_id_async(
        self, document_group_id: int
    ) -> ResponseData[DocumentGroupList]:
        """Get a document group by ID."""
        response = ResponseData[DocumentGroupList](
            Success=True,
            Message="Document group fetched successfully",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT 
                        id,
                        documentgroupname,
                        status,
                        createddate,
                        createdby,
                        updateddate,
                        updatedby
                    FROM documentgroups
                    WHERE id = :document_group_id AND status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    query, {"document_group_id": document_group_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Document group with ID {document_group_id} not found"
                    response.Data = None
                    return response

                response.Data = DocumentGroupList(
                    Id=row["id"],
                    Documentgroupname=row["documentgroupname"],
                    Status=row["status"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                )

        except Exception as ex:
            logger.error(f"Error fetching document group {document_group_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching document group: {str(ex)}"
            response.Data = None

        return response

    async def create_document_group_async(
        self, create_document_group: DocumentGroupCreate
    ) -> UResponse:
        """Create a new document group."""
        response = UResponse(Status=0, Message="")

        try:
            if not create_document_group.Documentgroupname:
                response.Status = 1
                response.Message = "Document group name is required."
                return response

            async with await self._db_manager.get_session() as session:
                now = datetime.now()
                insert_query = text("""
                    INSERT INTO documentgroups (
                        clientid, botid, documentgroupname, createddate, createdby, status
                    ) VALUES (
                        :client_id, :bot_id, :document_group_name, :created_date, :created_by, :status
                    ) RETURNING id
                """)
                await session.execute(
                    insert_query,
                    {
                        "client_id": self._client_id,
                        "bot_id": create_document_group.Botid,
                        "document_group_name": create_document_group.Documentgroupname,
                        "created_date": now,
                        "created_by": str(self._user_id),
                        "status": 1,
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Document group created successfully."

        except Exception as ex:
            logger.error(f"Error creating document group: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating the document group: {str(ex)}"

        return response

    async def update_document_group_async(
        self, update_document_group: DocumentGroupUpdate
    ) -> UResponse:
        """Update an existing document group."""
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if document group exists
                select_query = text("""
                    SELECT id FROM documentgroups
                    WHERE id = :document_group_id AND status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    select_query,
                    {"document_group_id": update_document_group.DocumentGroupId},
                )
                existing = result.mappings().first()

                if existing is None:
                    response.Status = 1
                    response.Message = f"Document group with ID {update_document_group.DocumentGroupId} not found."
                    return response

                now = datetime.now()
                update_query = text("""
                    UPDATE documentgroups
                    SET documentgroupname = :document_group_name,
                        clientid = :client_id,
                        status = :status,
                        updateddate = :updated_date,
                        updatedby = :updated_by
                    WHERE id = :document_group_id
                """)
                await session.execute(
                    update_query,
                    {
                        "document_group_name": update_document_group.Documentgroupname,
                        "client_id": self._client_id,
                        "status": update_document_group.Status,
                        "updated_date": now,
                        "updated_by": str(self._user_id),
                        "document_group_id": update_document_group.DocumentGroupId,
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Document group updated successfully."

        except Exception as ex:
            logger.error(f"Error updating document group: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating the document group: {str(ex)}"

        return response

    async def delete_document_group_async(self, document_group_id: int) -> UResponse:
        """Soft delete a document group."""
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if document group exists
                select_query = text("""
                    SELECT id FROM documentgroups
                    WHERE id = :document_group_id AND status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    select_query, {"document_group_id": document_group_id}
                )
                document_group = result.mappings().first()

                if document_group is None:
                    response.Status = 1
                    response.Message = f"Document group with ID {document_group_id} not found."
                    return response

                now = datetime.now()
                update_query = text("""
                    UPDATE documentgroups
                    SET status = 0, updateddate = :updated_date
                    WHERE id = :document_group_id
                """)
                await session.execute(
                    update_query,
                    {
                        "updated_date": now,
                        "document_group_id": document_group_id,
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Document group deleted successfully."

        except Exception as ex:
            logger.error(f"Error deleting document group {document_group_id}: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting the document group: {str(ex)}"

        return response

    async def get_document_group_role_map_list_async(
        self, document_group_id: int
    ) -> ResponseData[DocumentGroupRoleMapList]:
        """Get role mappings for a document group."""
        response = ResponseData[DocumentGroupRoleMapList](
            Success=True,
            Message="Document group roles fetched successfully.",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT id, roleid, documentgroupid, clientid, status
                    FROM documentgrouprolemap
                    WHERE documentgroupid = :document_group_id
                        AND clientid = :client_id
                        AND status = 1
                """)
                result = await session.execute(
                    query,
                    {
                        "document_group_id": document_group_id,
                        "client_id": self._client_id,
                    },
                )
                rows = result.mappings().all()

                role_ids = [row["roleid"] for row in rows if row["roleid"] is not None]

                response.Data = DocumentGroupRoleMapList(
                    Documentgroupid=document_group_id,
                    Clientid=self._client_id,
                    Roleid=role_ids,
                )

        except Exception as ex:
            logger.error(f"Error fetching document group roles for {document_group_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching document group roles: {str(ex)}"

        return response

    async def create_document_group_role_map_async(
        self, create_document_group_role: CreateDocumentGroupRole
    ) -> UResponse:
        """Create or update document group role mappings."""
        response = UResponse(Status=0, Message="")

        try:
            if (
                create_document_group_role is None
                or create_document_group_role.DocumentGroupId <= 0
            ):
                response.Status = -1
                response.Message = "Invalid request. Document Group ID is required."
                return response

            return await self._update_document_group_role_mappings(
                create_document_group_role.DocumentGroupId,
                create_document_group_role.RolesId,
            )

        except Exception as ex:
            logger.error(f"Error creating document group role map: {ex}")
            response.Status = -1
            response.Message = f"An error occurred while creating document group role map: {str(ex)}"

        return response

    async def _update_document_group_role_mappings(
        self, document_group_id: int, roles_id: Optional[str]
    ) -> UResponse:
        """Update document group role mappings."""
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
                # Get all existing mappings for this document group
                select_query = text("""
                    SELECT id, roleid, status
                    FROM documentgrouprolemap
                    WHERE documentgroupid = :document_group_id
                        AND clientid = :client_id
                """)
                result = await session.execute(
                    select_query,
                    {
                        "document_group_id": document_group_id,
                        "client_id": self._client_id,
                    },
                )
                existing_mappings = result.mappings().all()

                existing_role_ids = {m["roleid"] for m in existing_mappings if m["roleid"]}

                now = datetime.now()

                # 1. Deactivate roles not in the new list
                for mapping in existing_mappings:
                    role_id = mapping["roleid"]
                    current_status = mapping["status"]
                    
                    if role_id not in new_role_ids and current_status == 1:
                        update_query = text("""
                            UPDATE documentgrouprolemap
                            SET status = 0,
                                updateddate = :updated_date,
                                updatedby = :updated_by
                            WHERE id = :mapping_id
                        """)
                        await session.execute(
                            update_query,
                            {
                                "updated_date": now,
                                "updated_by": str(self._user_id),
                                "mapping_id": mapping["id"],
                            },
                        )
                    elif role_id in new_role_ids and current_status == 0:
                        # Reactivate existing mapping
                        update_query = text("""
                            UPDATE documentgrouprolemap
                            SET status = 1,
                                updateddate = :updated_date,
                                updatedby = :updated_by
                            WHERE id = :mapping_id
                        """)
                        await session.execute(
                            update_query,
                            {
                                "updated_date": now,
                                "updated_by": str(self._user_id),
                                "mapping_id": mapping["id"],
                            },
                        )

                # 2. Add new roles
                new_roles_to_add = [rid for rid in new_role_ids if rid not in existing_role_ids]

                if new_roles_to_add:
                    for role_id in new_roles_to_add:
                        insert_query = text("""
                            INSERT INTO documentgrouprolemap (
                                documentgroupid, roleid, clientid, status,
                                createddate, createdby
                            ) VALUES (
                                :document_group_id, :role_id, :client_id, 1,
                                :created_date, :created_by
                            )
                        """)
                        await session.execute(
                            insert_query,
                            {
                                "document_group_id": document_group_id,
                                "role_id": role_id,
                                "client_id": self._client_id,
                                "created_date": now,
                                "created_by": str(self._user_id),
                            },
                        )

                await session.commit()

                response.Status = 0
                response.Message = "Document group role mappings updated successfully."

        except Exception as ex:
            logger.error(f"Error updating document group role mappings: {ex}")
            response.Status = -1
            response.Message = f"An error occurred while updating document group role mappings: {str(ex)}"

        return response
