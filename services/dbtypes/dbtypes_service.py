"""Dbtype service for managing database type operations."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.common import ResponseData, UResponse
from models.service_models.dbtypes.dbtypes_service_models import (
    DbtypesCreate,
    DbtypesList,
    DbtypesUpdate,
)
from config.logger_config import get_logger

logger = get_logger(__name__)


class DbtypeService:
    """Service for dbtype operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_dbtypes_async(self) -> ResponseData[List[DbtypesList]]:
        """Get all active dbtypes ordered by dbprovider."""
        response = ResponseData[List[DbtypesList]](
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
                            dbprovider,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby
                        FROM dbtypes
                        WHERE status = 1
                        ORDER BY dbprovider
                    """)
                )
                rows = result.mappings().all()

                dbtypes = [
                    DbtypesList(
                        Id=row["id"],
                        Dbprovider=row["dbprovider"],
                        Status=row["status"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )
                    for row in rows
                ]

                response.Data = dbtypes
                response.Success = True
                response.Message = "Dbtypes fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching dbtypes: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching dbtypes: {str(ex)}"
            response.Data = []

        return response

    async def get_dbtype_by_id_async(self, dbtype_id: int) -> ResponseData[DbtypesList]:
        """Get a single dbtype by ID, filtered by status."""
        response = ResponseData[DbtypesList](
            Success=True,
            Message="",
            Data=None
        )

        try:

            if dbtype_id is None or dbtype_id <= 0:
                response.Message = "Valid dbtype ID is required"
                response.Success = False
                return response


            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            id,
                            dbprovider,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby
                        FROM dbtypes
                        WHERE id = :dbtype_id
                          AND status = 1
                    """),
                    {"dbtype_id": dbtype_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"No active dbtype found with ID {dbtype_id}"
                    return response

                dbtype = DbtypesList(
                    Id=row["id"],
                    Dbprovider=row["dbprovider"],
                    Status=row["status"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                )

                response.Data = dbtype
                response.Success = True
                response.Message = "Dbtype fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching dbtype by ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching dbtype: {str(ex)}"

        return response

    async def create_dbtype_async(self, create_dbtype: DbtypesCreate) -> UResponse:
        """Create a new dbtype."""
        response = UResponse(Status=0, Message="")

        try:
            if create_dbtype is None:
                response.Message = "Dbtype information is required"
                response.Status = 1
                return response

            if not create_dbtype.Dbprovider or not create_dbtype.Dbprovider.strip():
                response.Message = "Dbprovider is required"
                response.Status = 1
                return response

            async with await self._db_manager.get_session() as session:
                insert_result = await session.execute(
                    text("""
                        INSERT INTO dbtypes (
                            dbprovider, status, createddate, createdby
                        ) VALUES (
                            :dbprovider, :status, :created_date, :created_by
                        ) RETURNING id
                    """),
                    {
                        "dbprovider": create_dbtype.Dbprovider,
                        "status": create_dbtype.Status if create_dbtype.Status is not None else 1,
                        "created_date": datetime.now(),
                        "created_by": str(self.user_id),
                    }
                )
                await session.commit()

                response.Status = 0
                response.Message = "Dbtype created successfully"

        except Exception as ex:
            logger.error(f"Error creating dbtype: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating the dbtype: {str(ex)}"

        return response

    async def update_dbtype_async(self, update_dbtype: DbtypesUpdate) -> UResponse:
        """Update an existing dbtype."""
        response = UResponse(Status=0, Message="Dbtype updated successfully")

        try:
            if update_dbtype is None:
                response.Message = "Dbtype information is required"
                response.Status = 1
                return response

            if update_dbtype.Id is None or update_dbtype.Id <= 0:
                response.Message = "Valid dbtype ID is required"
                response.Status = 1
                return response

            async with await self._db_manager.get_session() as session:
                # Check if dbtype exists
                result = await session.execute(
                    text("""
                        SELECT id FROM dbtypes
                        WHERE id = :dbtype_id
                    """),
                    {"dbtype_id": update_dbtype.Id}
                )
                existing_dbtype = result.mappings().first()

                if existing_dbtype is None:
                    response.Status = 1
                    response.Message = f"Dbtype with ID {update_dbtype.Id} not found"
                    return response

                # Update dbtype
                now = datetime.now()
                await session.execute(
                    text("""
                        UPDATE dbtypes
                        SET dbprovider = :dbprovider,
                            status = :status,
                            updateddate = :updated_date,
                            updatedby = :updated_by
                        WHERE id = :dbtype_id
                    """),
                    {
                        "dbprovider": update_dbtype.Dbprovider,
                        "status": update_dbtype.Status,
                        "updated_date": now,
                        "updated_by": str(self.user_id),
                        "dbtype_id": update_dbtype.Id,
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error updating dbtype: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating the dbtype: {str(ex)}"

        return response

    async def delete_dbtype_async(self, dbtype_id: int) -> UResponse:
        """Soft delete a dbtype by setting status to 0."""
        response = UResponse(Status=0, Message="Dbtype deleted successfully")

        try:
            if dbtype_id is None or dbtype_id <= 0:
                response.Message = "Valid dbtype ID is required"
                response.Status = 1
                return response

            async with await self._db_manager.get_session() as session:
                # Check if dbtype exists
                result = await session.execute(
                    text("""
                        SELECT id FROM dbtypes
                        WHERE id = :dbtype_id
                    """),
                    {"dbtype_id": dbtype_id}
                )
                dbtype = result.mappings().first()

                if dbtype is None:
                    response.Status = 1
                    response.Message = f"Dbtype with ID {dbtype_id} not found"
                    return response

                # Soft delete by setting status to 0
                now = datetime.now()
                await session.execute(
                    text("""
                        UPDATE dbtypes
                        SET status = 0,
                            updateddate = :updated_date
                        WHERE id = :dbtype_id
                    """),
                    {
                        "updated_date": now,
                        "dbtype_id": dbtype_id,
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error deleting dbtype: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting dbtype: {str(ex)}"

        return response
