"""Database table service for managing database table column operations."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.common import ResponseData
from models.service_models.database_table.database_table_service_model import (
    DatabaseTablesColumnList,
)
from config.logger_config import get_logger

logger = get_logger(__name__)


class DatabasetablescolumnService:
    """Service for database table column operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_database_tables_column_async(
        self, table_id: int
    ) -> ResponseData[List[DatabaseTablesColumnList]]:
        """Get all database table columns for a specific table ID."""
        response = ResponseData[List[DatabaseTablesColumnList]](
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
                            tableid,
                            columnname,
                            dbtype,
                            embeddingdb,
                            embeddingdetails,
                            botid,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby
                        FROM databasetablescolumns
                        WHERE tableid = :table_id
                        ORDER BY columnname
                    """),
                    {"table_id": table_id}
                )
                rows = result.mappings().all()

                columns = [
                    DatabaseTablesColumnList(
                        Id=row["id"],
                        Tableid=row["tableid"],
                        Columnname=row["columnname"],
                        Dbtype=row["dbtype"],
                        Embeddingdb=row["embeddingdb"],
                        Embeddingdetails=row["embeddingdetails"],
                        Botid=row["botid"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )
                    for row in rows
                ]

                response.Data = columns
                response.Success = True
                response.Message = "Columns retrieved successfully."

        except Exception as ex:
            logger.error(f"Error retrieving columns: {ex}")
            response.Success = False
            response.Message = f"An error occurred while retrieving columns: {str(ex)}"
            response.Data = []

        return response

    async def get_databasetables_column_by_id_async(
        self, id: int
    ) -> ResponseData[DatabaseTablesColumnList]:
        """Get a database table column by ID."""
        response = ResponseData[DatabaseTablesColumnList](
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
                            tableid,
                            columnname,
                            dbtype,
                            embeddingdb,
                            embeddingdetails,
                            botid,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby
                        FROM databasetablescolumns
                        WHERE id = :id
                    """),
                    {"id": id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Column with ID {id} not found."
                    return response

                column = DatabaseTablesColumnList(
                    Id=row["id"],
                    Tableid=row["tableid"],
                    Columnname=row["columnname"],
                    Dbtype=row["dbtype"],
                    Embeddingdb=row["embeddingdb"],
                    Embeddingdetails=row["embeddingdetails"],
                    Botid=row["botid"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                )

                response.Data = column
                response.Success = True
                response.Message = "Column retrieved successfully."

        except Exception as ex:
            logger.error(f"Error retrieving column: {ex}")
            response.Success = False
            response.Message = f"An error occurred while retrieving the column: {str(ex)}"
            response.Data = None

        return response
