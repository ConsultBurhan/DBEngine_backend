"""Database connection service for managing database connection operations."""
from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import List, Optional

from sqlalchemy import text
import asyncio
import hdbcli.dbapi as hana
import asyncpg

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.common import ResponseData, UResponse, UEntity
from models.service_models.database_connections.database_connections_service_models import (
    DatabaseConnectionList,
    TableInfo,
    ColumnInfo,
    CreateDatabaseConnection,
    DatabaseCheckResult,
    UpdateDatabaseConnection
)
from database.dbModel.database_connections.database_connections import Databaseconnections
from database.dbModel.database_table.databasetable import Databasetable, Databasetablescolumn
from config.logger_config import get_logger

logger = get_logger(__name__)

class DatabaseType(IntEnum):
    """Database type enumeration."""
    POSTGRESQL = 1
    SAP_HANA = 2
    SQL_SERVER = 3


class DatabaseconnectionService:
    """Service for database connection operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_databaseconnections_async(self) -> ResponseData[List[DatabaseConnectionList]]:
        """Get all active database connections for the current client with bot name."""
        response = ResponseData[List[DatabaseConnectionList]](
            Success=True,
            Message="",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            dc.id,
                            dc.connectiontype,
                            dc.server,
                            dc.username,
                            dc.password,
                            dc.dbname,
                            dc.connectionstring,
                            dc.clientid,
                            dc.botid,
                            b.botname as botname,
                            dc.tablecount,
                            dc.status,
                            dc.createddate,
                            dc.createdby,
                            dc.updateddate,
                            dc.updatedby
                        FROM databaseconnections dc
                        LEFT JOIN bots b ON dc.botid = b.id
                        WHERE dc.status = '1'
                          AND dc.clientid = :client_id
                        ORDER BY dc.createddate
                    """),
                    {"client_id": self.client_id}
                )
                rows = result.mappings().all()
                connections = [
                    DatabaseConnectionList(
                        Id=row["id"],
                        Connectiontype=row["connectiontype"],
                        Server=row["server"],
                        Username=row["username"],
                        Password=row["password"],
                        Dbname=row["dbname"],
                        Connectionstring=row["connectionstring"],
                        Clientid=row["clientid"],
                        Botid=row["botid"],
                        BotName=row["botname"],
                        Tablecount=row["tablecount"],
                        Status=row["status"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )
                    for row in rows
                ]

                response.Data = connections
                response.Success = True
                response.Message = "Database connections fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching database connections: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching database connections: {str(ex)}"
            response.Data = []

        return response

    async def get_database_connection_by_id_async(self, connection_id: int) -> ResponseData[DatabaseConnectionList]:
        """Get a single database connection by ID, filtered by status."""
        response = ResponseData[DatabaseConnectionList](
            Success=True,
            Message="",
            Data=None
        )

        try:
            if connection_id is None or connection_id <= 0:
                response.Message = "Valid database connection ID is required"
                response.Success = False
                return response

            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            dc.id,
                            dc.connectiontype,
                            dc.server,
                            dc.username,
                            dc.password,
                            dc.dbname,
                            dc.connectionstring,
                            dc.clientid,
                            dc.botid,
                            b.botname as botname,
                            dc.tablecount,
                            dc.status,
                            dc.createddate,
                            dc.createdby,
                            dc.updateddate,
                            dc.updatedby
                        FROM databaseconnections dc
                        LEFT JOIN bots b ON dc.botid = b.id
                        WHERE dc.id = :connection_id
                          AND dc.status = '1'
                    """),
                    {"connection_id": connection_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"No active database connection found with ID {connection_id}"
                    return response

                connection = DatabaseConnectionList(
                    Id=row["id"],
                    Connectiontype=row["connectiontype"],
                    Server=row["server"],
                    Username=row["username"],
                    Password=row["password"],
                    Dbname=row["dbname"],
                    Connectionstring=row["connectionstring"],
                    Clientid=row["clientid"],
                    Botid=row["botid"],
                    BotName=row["botname"],
                    Tablecount=row["tablecount"],
                    Status=row["status"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                )

                response.Data = connection
                response.Success = True
                response.Message = "Database connection fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching database connection by ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching database connection: {str(ex)}"

        return response

        
    async def _connect_to_sap_hana_and_get_views(
        self,
        server: str,
        db_name: str,
        username: str,
        password: str,
        result: DatabaseCheckResult
    ) -> None:
        try:
            connection = await asyncio.to_thread(
                hana.connect,
                address=server,
                databaseName=db_name,
                user=username,
                password=password
            )
            result.IsConnected = True
            logger.info(["DEBUGGING"])
            view_query = """
                SELECT SCHEMA_NAME, VIEW_NAME
                FROM SYS.VIEWS
                WHERE IS_VALID = 'TRUE'
                ORDER BY SCHEMA_NAME, VIEW_NAME
            """

            view_cursor = connection.cursor()
            await asyncio.to_thread(view_cursor.execute, view_query)
            views = await asyncio.to_thread(view_cursor.fetchall)

            for schema_name, view_name in views:
                view = TableInfo(schema_name=schema_name, table_name=view_name)

                column_query = """
                    SELECT COLUMN_NAME, DATA_TYPE_NAME, IS_NULLABLE
                    FROM SYS.VIEW_COLUMNS
                    WHERE SCHEMA_NAME = ?
                    AND VIEW_NAME = ?
                    ORDER BY POSITION
                """

                column_cursor = connection.cursor()
                await asyncio.to_thread(column_cursor.execute, column_query, (schema_name, view_name))
                columns = await asyncio.to_thread(column_cursor.fetchall)

                for col_name, data_type, is_nullable in columns:
                    view.columns.append(ColumnInfo(
                        column_name=col_name,
                        data_type=data_type,
                        is_nullable=is_nullable.upper() == "TRUE",
                        is_primary=False
                    ))
                
                column_cursor.close()
                result.tables.append(view)

            view_cursor.close()
            connection.close()

        except Exception as ex:
            result.IsConnected = False

    async def _connect_to_postgresql_and_get_tables(
        self,
        server: str,
        db_name: str,
        username: str,
        password: str,
        result: DatabaseCheckResult,
        port: int = 5432
    ) -> None:
        try:
            # Build connection string: postgresql://user:password@host:port/database
            connection_string = f"postgresql://{username}:{password}@{server}/{db_name}"
            
            connection = await asyncpg.connect(connection_string)
            try:
                result.IsConnected = True

                table_query = """
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """
                tables = await connection.fetch(table_query)

                column_query = """
                    SELECT
                        c.column_name,
                        c.data_type,
                        CASE WHEN c.is_nullable = 'YES' THEN TRUE ELSE FALSE END AS is_nullable,
                        EXISTS (
                            SELECT 1 FROM information_schema.key_column_usage kcu
                            JOIN information_schema.table_constraints tc
                                ON kcu.constraint_name = tc.constraint_name
                                AND kcu.table_schema = tc.table_schema
                                AND kcu.table_name = tc.table_name
                            WHERE tc.constraint_type = 'PRIMARY KEY'
                            AND kcu.table_schema = c.table_schema
                            AND kcu.table_name = c.table_name
                            AND kcu.column_name = c.column_name
                        ) AS is_primary_key
                    FROM information_schema.columns c
                    WHERE c.table_schema = 'public'
                    AND c.table_name = $1
                    ORDER BY c.ordinal_position
                """

                for row in tables:
                    table = TableInfo(
                        SchemaName=row["table_schema"],
                        TableName=row["table_name"],
                        Columns=[]
                    )

                    columns = await connection.fetch(column_query, table.TableName)

                    for col_row in columns:
                        table.Columns.append(ColumnInfo(
                            ColumnName=col_row["column_name"],
                            DataType=col_row["data_type"],
                            IsNullable=col_row["is_nullable"],
                            IsPrimary=col_row["is_primary_key"]
                        ))

                    result.Tables.append(table)
            finally:
                await connection.close()

        except Exception as ex:
            logger.error(f"Error connecting to PostgreSQL: {ex}")
            result.IsConnected = False
            
    async def check_database_and_get_tables_async(
        self,
        db_type: int,
        server: str,
        db_name: str,
        username: str,
        password: str
    ) -> DatabaseCheckResult:
        """
        Check database connection and get tables/views based on database type.

        Args:
            db_type: Database type enum value (1=SQL Server, 2=PostgreSQL, 3=SAP HANA)
            server: Database server address
            db_name: Database name
            username: Database username
            password: Database password

        Returns:
            DatabaseCheckResult with connection status and tables/views list
        """
        result = DatabaseCheckResult(IsConnected=False, Tables=[])

        try:
            # PostgreSQL
            if db_type == DatabaseType.POSTGRESQL:
                await self._connect_to_postgresql_and_get_tables(
                    server, db_name, username, password, result
                )
            # SAP HANA
            elif db_type == DatabaseType.SAP_HANA:
                await self._connect_to_sap_hana_and_get_views(
                    server, db_name, username, password, result
                )
            # SQL Server - not implemented yet
            elif db_type == DatabaseType.SQL_SERVER:
                result.IsConnected = False
                logger.warning("SQL Server connection not implemented yet")
            else:
                result.IsConnected = False
                logger.warning(f"Unknown database type: {db_type}")

        except Exception as ex:
            logger.error(f"Error checking database connection: {ex}")
            result.IsConnected = False

        return result

    async def create_database_connection_async(
        self,
        create_dto: CreateDatabaseConnection
    ) -> UResponse:
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                async with session.begin():
                    # Step 1: Save the database connection
                    result = await session.execute(
                        text("""
                            INSERT INTO databaseconnections
                                (connectiontype, server, username, password, dbname, connectionstring,
                                 clientid, botid, tablecount, status, createddate, createdby)
                            VALUES
                                (:connectiontype, :server, :username, :password, :dbname, :connectionstring,
                                 :clientid, :botid, :tablecount, :status, :createddate, :createdby)
                            RETURNING id
                        """),
                        {
                            "connectiontype": create_dto.Connectiontype,
                            "server": create_dto.Server,
                            "username": create_dto.Username,
                            "password": create_dto.Password,
                            "dbname": create_dto.Dbname,
                            "connectionstring": create_dto.Connectionstring,
                            "clientid": self.client_id,
                            "botid": create_dto.Botid,
                            "tablecount": create_dto.Tablecount,
                            "status": "1",
                            "createddate": datetime.now(),
                            "createdby": str(self.user_id)
                        }
                    )
                    database_connection_id = result.scalar()  

                    # Step 2: Check database connection
                    db_check_result = await self.check_database_and_get_tables_async(
                        int(create_dto.Connectiontype),
                        create_dto.Server,
                        create_dto.Dbname,
                        create_dto.Username,
                        create_dto.Password
                    )

                    if not db_check_result.IsConnected:
                        response.Status = 1
                        response.Message = "Database connection failed. Please verify the details."
                        return response  

                    # Step 3: Insert tables and columns
                    for table in db_check_result.Tables:
                        table_result = await session.execute(
                            text("""
                                INSERT INTO databasetables
                                    (dbid, tablename, status, botid, createddate, createdby)
                                VALUES
                                    (:dbid, :tablename, :status, :botid, :createddate, :createdby)
                                RETURNING id
                            """),
                            {
                                "dbid": database_connection_id,
                                "tablename": table.TableName,
                                "status": "1",
                                "botid": create_dto.Botid,
                                "createddate": datetime.now(),
                                "createdby": str(self.user_id)
                            }
                        )
                        db_table_id = table_result.scalar()
                        for column in table.Columns:
                            await session.execute(
                                text("""
                                    INSERT INTO databasetablescolumns
                                        (tableid, columnname, dbtype, botid, "IsPrimary", "IsNullable", createddate, createdby)
                                    VALUES
                                        (:tableid, :columnname, :dbtype, :botid, :isprimary, :isnullable, :createddate, :createdby)
                                """),
                                {
                                    "tableid": db_table_id,
                                    "columnname": column.ColumnName,
                                    "dbtype": column.DataType,
                                    "botid": create_dto.Botid,
                                    "isprimary": column.IsPrimary,
                                    "isnullable": column.IsNullable,
                                    "createddate": datetime.now(),
                                    "createdby": str(self.user_id)
                                }
                            )

                    response.Status = True
                    response.Message = "Database connection and table metadata saved successfully."

        except Exception as ex:
            logger.error(f"Error creating database connection: {ex}")
            response.Status = False
            response.Message = f"An error occurred: {str(ex)}"

        return response

    async def update_database_connection_async(
        self,
        update_dto: UpdateDatabaseConnection
    ) -> UResponse:
        """
        Update a database connection and refresh table/column metadata.

        Args:
            update_dto: DTO containing updated database connection details

        Returns:
            ResponseData with success status and message
        """
        response = UResponse(Status=0, Message="")
        try:
            async with await self._db_manager.get_session() as session:
                async with session.begin():
                    # Step 1: Fetch existing record
                    result = await session.execute(
                        text("""
                            SELECT id, connectiontype, server, username, password, dbname,
                                   connectionstring, clientid, botid, tablecount, status
                            FROM database_connections
                            WHERE id = :connection_id AND status = '1'
                        """),
                        {"connection_id": update_dto.Id}
                    )
                    row = result.mappings().first()

                    if row is None:
                        response.Status = 1
                        response.Message = "No active database connection found with the provided ID."
                        return response

                    # Step 2: Update database connection details
                    await session.execute(
                        text("""
                            UPDATE databaseconnections
                            SET connectiontype = :connectiontype,
                                server = :server,
                                username = :username,
                                password = :password,
                                dbname = :dbname,
                                connectionstring = :connectionstring,
                                tablecount = :tablecount,
                                updateddate = :updateddate,
                                updatedby = :updatedby
                            WHERE id = :connection_id
                        """),
                        {
                            "connectiontype": update_dto.Connectiontype,
                            "server": update_dto.Server,
                            "username": update_dto.Username,
                            "password": update_dto.Password,
                            "dbname": update_dto.Dbname,
                            "connectionstring": update_dto.Connectionstring,
                            "tablecount": update_dto.Tablecount,
                            "updateddate": datetime.now(),
                            "updatedby": str(self.user_id),
                            "connection_id": update_dto.Id
                        }
                    )

                    # Step 3: Check connection validity
                    db_check_result = await self.check_database_and_get_tables_async(
                        int(update_dto.Connectiontype),
                        update_dto.Server,
                        update_dto.Dbname,
                        update_dto.Username,
                        update_dto.Password
                    )

                    if not db_check_result.IsConnected:
                        await session.rollback()
                        response.Status = 1
                        response.Message = "Failed to connect to the database with updated details. Please verify the information."
                        return response

                    # Step 4: Remove existing tables and columns
                    await session.execute(
                        text("""
                            DELETE FROM databasetablescolumns
                            WHERE tableid IN (
                                SELECT id FROM database_tables WHERE dbid = :db_id
                            )
                        """),
                        {"db_id": update_dto.Id}
                    )

                    await session.execute(
                        text("""
                            DELETE FROM databasetables
                            WHERE dbid = :db_id
                        """),
                        {"db_id": update_dto.Id}
                    )

                    # Step 5: Insert new tables and columns
                    for table in db_check_result.Tables:
                        table_result = await session.execute(
                            text("""
                                INSERT INTO databasetables
                                    (dbid, tablename, status, botid, createddate, createdby)
                                VALUES
                                    (:dbid, :tablename, :status, :botid, :createddate, :createdby)
                                RETURNING id
                            """),
                            {
                                "dbid": update_dto.Id,
                                "tablename": table.TableName,
                                "status": "1",
                                "botid": update_dto.Botid,
                                "createddate": datetime.now(),
                                "createdby": str(self.user_id)
                            }
                        )
                        db_table_id = table_result.scalar()

                        for column in table.Columns:
                            await session.execute(
                                text("""
                                    INSERT INTO databasetablescolumns
                                        (tableid, columnname, dbtype, botid, "IsPrimary", "IsNullable", createddate, createdby)
                                    VALUES
                                        (:tableid, :columnname, :dbtype, :botid, :isprimary, :isnullable, :createddate, :createdby)
                                """),
                                {
                                    "tableid": db_table_id,
                                    "columnname": column.ColumnName,
                                    "dbtype": column.DataType,
                                    "botid": update_dto.Botid,
                                    "isprimary": column.IsPrimary,
                                    "isnullable": column.IsNullable,
                                    "createddate": datetime.now(),
                                    "createdby": str(self.user_id)
                                }
                            )

                    response.Status = 0
                    response.Message = "Database connection and related tables/columns updated successfully."

        except Exception as ex:
            logger.error(f"Error updating database connection: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating the database connection: {str(ex)}"

        return response

    async def refresh_database_schema_async(
        self,
        connection_id: int
    ) -> UResponse:
        """
        Refresh database schema (tables and columns) without updating connection details.

        Args:
            connection_id: ID of the database connection to refresh

        Returns:
            ResponseData with success status and message
        """
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                async with session.begin():
                    # Step 1: Fetch existing record
                    result = await session.execute(
                        text("""
                            SELECT id, connectiontype, server, username, password, dbname,
                                   connectionstring, clientid, botid, tablecount, status
                            FROM databaseconnections
                            WHERE id = :connection_id AND status = '1'
                        """),
                        {"connection_id": connection_id}
                    )
                    row = result.mappings().first()

                    if row is None:
                        response.Status = 1
                        response.Message = "No active database connection found with the provided ID."
                        return response

                    # Step 2: Check connection validity
                    db_check_result = await self.check_database_and_get_tables_async(
                        int(row["connectiontype"]),
                        row["server"],
                        row["dbname"],
                        row["username"],
                        row["password"]
                    )

                    if not db_check_result.IsConnected:
                        await session.rollback()
                        response.Status = 1
                        response.Message = "Failed to connect to the database with provided details. Please verify the information."
                        return response

                    # Step 3: Remove existing tables and columns
                    await session.execute(
                        text("""
                            DELETE FROM databasetablescolumns
                            WHERE tableid IN (
                                SELECT id FROM databasetables WHERE dbid = :db_id
                            )
                        """),
                        {"db_id": connection_id}
                    )

                    await session.execute(
                        text("""
                            DELETE FROM databasetables
                            WHERE dbid = :db_id
                        """),
                        {"db_id": connection_id}
                    )
                    # Step 4: Insert new tables and columns
                    for table in db_check_result.Tables:
                        table_result = await session.execute(
                            text("""
                                INSERT INTO databasetables
                                    (dbid, tablename, status, botid, createddate, createdby)
                                VALUES
                                    (:dbid, :tablename, :status, :botid, :createddate, :createdby)
                                RETURNING id
                            """),
                            {
                                "dbid": connection_id,
                                "tablename": table.TableName,
                                "status": "1",
                                "botid": row["botid"],
                                "createddate": datetime.now(),
                                "createdby": str(self.user_id)
                            }
                        )
                        db_table_id = table_result.scalar()


                        for column in table.Columns:
                            await session.execute(
                                text("""
                                    INSERT INTO databasetablescolumns
                                        (tableid, columnname, dbtype, botid, "IsPrimary", "IsNullable", createddate, createdby)
                                    VALUES
                                        (:tableid, :columnname, :dbtype, :botid, :isprimary, :isnullable, :createddate, :createdby)
                                """),
                                {
                                    "tableid": db_table_id,
                                    "columnname": column.ColumnName,
                                    "dbtype": column.DataType,
                                    "botid": row["botid"],
                                    "isprimary": column.IsPrimary,
                                    "isnullable": column.IsNullable,
                                    "createddate": datetime.now(),
                                    "createdby": str(self.user_id)
                                }
                            )

                    response.Status = 0
                    response.Message = "Database schema refreshed successfully."

        except Exception as ex:
            logger.error(f"Error refreshing database schema: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while refreshing the database schema: {str(ex)}"

        return response

    async def delete_database_connection_async(
        self,
        connection_id: int
    ) -> UResponse:
        """
        Soft delete a database connection by setting status to "0".

        Args:
            connection_id: ID of the database connection to delete

        Returns:
            ResponseData with success status and message
        """
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Fetch existing record
                result = await session.execute(
                    text("""
                        SELECT id, status
                        FROM databaseconnections
                        WHERE id = :connection_id AND status = '1'
                    """),
                    {"connection_id": connection_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Status = 1
                    response.Message = "No active database connection found with the provided ID."
                    return response

                # Soft delete by setting status to "0"
                await session.execute(
                    text("""
                        UPDATE databaseconnections
                        SET status = '0'
                        WHERE id = :connection_id
                    """),
                    {"connection_id": connection_id}
                )

                response.Status = 0
                response.Message = "Database connection deleted successfully."

        except Exception as ex:
            logger.error(f"Error deleting database connection: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting the database connection: {str(ex)}"

        return response

    async def get_database_connections_async(self) -> ResponseData:
        """
        Get simplified list of database connections (id and name only) for the current client.

        Returns:
            ResponseData with list of connection entities containing id and name
        """
        response = ResponseData(Success=True, Message="", Data=[])

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, dbname
                        FROM databaseconnections
                        WHERE status = '1' AND clientid = :client_id
                    """),
                    {"client_id": self.client_id}
                )
                rows = result.mappings().all()

                connection_list = [
                    UEntity(Id=row["id"], Name=row["dbname"])
                    for row in rows
                ]

                response.Data = connection_list
                response.Success = True
                response.Message = "Connections fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching database connections: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching connections: {str(ex)}"
            response.Data = []

        return response