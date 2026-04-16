"""Database table service for managing database table operations."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from models.service_models.database_table.database_table_service_model import (
    CreateDatabaseTableRole,
    DatabasetableList,
    DatabaseTableRoleMapList,
)
from models.common import ResponseData, UEntity, UResponse
from config.logger_config import get_logger

logger = get_logger(__name__)


class DatabasetableService:
    """Service for database table operations including CRUD and role mappings."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self._client_id = client_id
        self._user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_databasetables_async(
        self, connection_id: int
    ) -> ResponseData[List[DatabasetableList]]:
        """Get all database tables for a connection."""
        response = ResponseData[List[DatabasetableList]](
            Success=True,
            Message="Tables retrieved successfully.",
            Data=[],
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT 
                        id,
                        dbid,
                        tablename,
                        status,
                        embeddingdb,
                        embeddingdetails,
                        botid,
                        tablecount,
                        createddate,
                        createdby,
                        updateddate,
                        updatedby
                    FROM databasetables
                    WHERE dbid = :connection_id AND status = '1'
                    ORDER BY tablename ASC
                """)
                result = await session.execute(query, {"connection_id": connection_id})
                rows = result.mappings().all()

                tables = [
                    DatabasetableList(
                        Id=row["id"],
                        Dbid=row["dbid"],
                        Tablename=row["tablename"],
                        Status=row["status"],
                        Embeddingdb=row["embeddingdb"],
                        Embeddingdetails=row["embeddingdetails"],
                        Botid=row["botid"],
                        Tablecount=row["tablecount"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )
                    for row in rows
                ]

                response.Data = tables

        except Exception as ex:
            logger.error(f"Error retrieving tables for connection {connection_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while retrieving tables: {str(ex)}"

        return response

    async def get_databasetable_by_id_async(
        self, table_id: int
    ) -> ResponseData[DatabasetableList]:
        """Get a database table by ID."""
        response = ResponseData[DatabasetableList](
            Success=True,
            Message="Database table retrieved successfully.",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT 
                        id,
                        dbid,
                        tablename,
                        status,
                        embeddingdb,
                        embeddingdetails,
                        botid,
                        tablecount,
                        createddate,
                        createdby,
                        updateddate,
                        updatedby
                    FROM databasetables
                    WHERE id = :table_id AND status = '1'
                    LIMIT 1
                """)
                result = await session.execute(query, {"table_id": table_id})
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Database table with ID {table_id} not found."
                    response.Data = None
                else:
                    response.Data = DatabasetableList(
                        Id=row["id"],
                        Dbid=row["dbid"],
                        Tablename=row["tablename"],
                        Status=row["status"],
                        Embeddingdb=row["embeddingdb"],
                        Embeddingdetails=row["embeddingdetails"],
                        Botid=row["botid"],
                        Tablecount=row["tablecount"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )

        except Exception as ex:
            logger.error(f"Error retrieving database table {table_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while retrieving the database table: {str(ex)}"
            response.Data = None

        return response

    async def get_database_tables_async(
        self, connection_id: int
    ) -> ResponseData[List[UEntity]]:
        """Get database tables as simple entities for a connection."""
        response = ResponseData[List[UEntity]](
            Success=True,
            Message="Tables fetched successfully",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT id, tablename
                    FROM databasetables
                    WHERE dbid = :connection_id AND status = '1'
                    ORDER BY tablename ASC
                """)
                result = await session.execute(query, {"connection_id": connection_id})
                rows = result.mappings().all()

                if not rows:
                    response.Success = False
                    response.Message = "No Table found"
                    response.Data = None
                    return response

                table_list = [
                    UEntity(Id=row["id"], Name=row["tablename"]) for row in rows
                ]

                response.Data = table_list

        except Exception as ex:
            logger.error(f"Error fetching tables for connection {connection_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching Tables: {str(ex)}"
            response.Data = None

        return response

    async def get_database_table_map_list_async(
        self, database_table_id: int
    ) -> ResponseData[DatabaseTableRoleMapList]:
        """Get role mappings for a database table."""
        response = ResponseData[DatabaseTableRoleMapList](
            Success=True,
            Message="Database table roles fetched successfully.",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT id, roleid, databasetableid, clientid, status
                    FROM databasetablerolemap
                    WHERE databasetableid = :database_table_id
                        AND clientid = :client_id
                        AND status = 1
                """)
                result = await session.execute(
                    query,
                    {
                        "database_table_id": database_table_id,
                        "client_id": self._client_id,
                    },
                )
                rows = result.mappings().all()

                role_ids = [row["roleid"] for row in rows if row["roleid"] is not None]

                response.Data = DatabaseTableRoleMapList(
                    DatabaseTableid=database_table_id,
                    Clientid=self._client_id,
                    Roleid=role_ids,
                )

        except Exception as ex:
            logger.error(f"Error fetching database table roles for {database_table_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching database table roles: {str(ex)}"

        return response

    async def create_database_table_role_map_async(
        self, create_database_table_role: CreateDatabaseTableRole
    ) -> UResponse:
        """Create or update database table role mappings."""
        response = UResponse(Status=0, Message="")

        try:
            if (
                create_database_table_role is None
                or create_database_table_role.DatabaseTableId <= 0
            ):
                response.Status = 1
                response.Message = "Invalid request. Database Table ID is required."
                return response

            return await self._update_database_table_role_mappings(
                create_database_table_role.DatabaseTableId,
                create_database_table_role.RolesId,
            )

        except Exception as ex:
            logger.error(f"Error creating database table role map: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating document group role map: {str(ex)}"

        return response

    async def _update_database_table_role_mappings(
        self, databasetable_id: int, roles_id: Optional[str]
    ) -> UResponse:
        """Update database table role mappings."""
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
                # Get all existing mappings for this database table
                select_query = text("""
                    SELECT id, roleid, status
                    FROM databasetablerolemap
                    WHERE databasetableid = :databasetable_id
                        AND clientid = :client_id
                """)
                result = await session.execute(
                    select_query,
                    {
                        "databasetable_id": databasetable_id,
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
                            UPDATE databasetablerolemap
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
                            UPDATE databasetablerolemap
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
                            INSERT INTO databasetablerolemap (
                                databasetableid, roleid, clientid, status,
                                createddate, createdby
                            ) VALUES (
                                :databasetable_id, :role_id, :client_id, 1,
                                :created_date, :created_by
                            )
                        """)
                        await session.execute(
                            insert_query,
                            {
                                "databasetable_id": databasetable_id,
                                "role_id": role_id,
                                "client_id": self._client_id,
                                "created_date": now,
                                "created_by": str(self._user_id),
                            },
                        )

                await session.commit()

                response.Status = 0
                response.Message = "Database Table role mappings updated successfully."

        except Exception as ex:
            logger.error(f"Error updating database table role mappings: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating document group role mappings: {str(ex)}"

        return response
