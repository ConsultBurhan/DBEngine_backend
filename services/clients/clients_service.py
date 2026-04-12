"""Client service for managing client operations."""
from __future__ import annotations 
from typing import List, Optional
import json
from datetime import datetime 
from models.service_models.clients.clients_service_model import (
    ClientCreate,
    ClientList,
    ClientUpdate,
)
from models.common import ResponseData, UResponse, UEntity
from database.dbConnection.postgres_connection import PostgresConnectionManager, get_postgres_manager
from services.fileupload.file_upload_service import upload_file 
from sqlalchemy import text 
from config.logger_config import get_logger
from dotenv import load_dotenv
import os, httpx


logger = get_logger(__name__)
load_dotenv()



class ClientService:
    def __init__(
        self,
        client_id: int = 0, 
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()


    async def get_all_clients_async(self) -> ResponseData[List[ClientList]]:
        response = ResponseData[List[ClientList]](
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
                            clientname,
                            logo,
                            "DefaultLanguageCode",
                            client_prefix,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby
                        FROM clients
                        WHERE status = 1
                        ORDER BY clientname
                    """)
                )
                rows = result.mappings().all()

                clients = [
                    ClientList(
                        Id=row["id"],
                        Clientname=row["clientname"],
                        Logo=row["logo"],
                        DefaultLanguageCode=row["DefaultLanguageCode"],
                        ClientPrefix=row["client_prefix"],
                        Status=row["status"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"]
                    )
                    for row in rows
                ]

                response.Data = clients
                response.Success = True
                response.Message = "Clients fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching clients: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching clients: {str(ex)}"
            response.Data = []

        return response

    async def get_client_by_id_async(self, id: int) -> ResponseData[ClientList]:
        response = ResponseData[ClientList](
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
                            clientname,
                            logo,
                            "DefaultLanguageCode",
                            client_prefix,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby
                        FROM clients
                        WHERE id = :id
                    """),
                    {"id": id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Client with ID {id} not found"
                    return response

                client = ClientList(
                    Id=row["id"],
                    Clientname=row["clientname"],
                    Logo=row["logo"],
                    DefaultLanguageCode=row["DefaultLanguageCode"],
                    ClientPrefix=row["client_prefix"],
                    Status=row["status"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"]
                )

                response.Data = client
                response.Success = True
                response.Message = "Data fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching client by ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching the client: {str(ex)}"
            response.Data = None

        return response

    async def delete_client_async(self, id: int) -> UResponse:
        response = UResponse(
            Status=0,
            Message="Client deleted successfully"
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id FROM clients WHERE id = :id
                    """),
                    {"id": id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Status = 1
                    response.Message = f"Client with ID {id} not found"
                    return response

                await session.execute(
                    text("""
                        UPDATE clients
                        SET status = 0
                        WHERE id = :id
                    """),
                    {"id": id}
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error deleting client: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting client: {str(ex)}"

        return response

    async def get_client_async(self) -> ResponseData[List[UEntity]]:
        response = ResponseData[List[UEntity]](
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
                            clientname
                        FROM clients
                        WHERE status = 1
                        ORDER BY createddate
                    """)
                )
                rows = result.mappings().all()

                if not rows:
                    response.Success = False
                    response.Message = "No active Client found"
                    response.Data = None
                    return response

                client_list = [
                    UEntity(
                        Id=row["id"],
                        Name=row["clientname"]
                    )
                    for row in rows
                ]

                response.Success = True
                response.Message = "Client fetched successfully"
                response.Data = client_list

        except Exception as ex:
            logger.error(f"Error fetching clients: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching clients: {str(ex)}"
            response.Data = None

        return response

    async def create_client_async(self, client_dto: ClientCreate) -> UResponse:
        response = UResponse(
            Status=0,
            Message=""
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if client with same name already exists
                result = await session.execute(
                    text("""
                        SELECT id FROM clients
                        WHERE LOWER(TRIM(clientname)) = LOWER(TRIM(:clientname))
                        AND status = 1
                    """),
                    {"clientname": client_dto.Clientname}
                )
                existing_client = result.mappings().first()

                if existing_client:
                    response.Status = 1
                    response.Message = "A client with the given name already exists."
                    return response

                # Upload logo if provided
                logo_filename = None
                if client_dto.Logo:
                    pass
                    # logo_filename = await upload_file(client_dto.Logo)

                # Create new client
                await session.execute(
                    text("""
                        INSERT INTO clients (
                            clientname,
                            status,
                            logo,
                            "DefaultLanguageCode",
                            client_prefix,
                            createddate,
                            createdby
                        ) VALUES (
                            :clientname,
                            :status,
                            :logo,
                            :default_language_code,
                            :client_prefix,
                            :createddate,
                            :createdby
                        )
                    """),
                    {
                        "clientname": client_dto.Clientname.strip(),
                        "status": client_dto.Status if client_dto.Status is not None else 1,
                        "logo": logo_filename,
                        "default_language_code": client_dto.DefaultLanguageCode,
                        "client_prefix": client_dto.ClientPrefix,
                        "createddate": datetime.now(),
                        "createdby": str(self.user_id)
                    }
                )
                await session.commit()

                response.Status = 0
                response.Message = "Client created successfully"

        except Exception as ex:
            logger.error(f"Error creating client: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating the client: {str(ex)}"

        return response

    async def update_client_async(self, client_dto: ClientUpdate) -> UResponse:
        response = UResponse(
            Status=0,
            Message="Client updated successfully"
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if client exists
                result = await session.execute(
                    text("""
                        SELECT id, logo FROM clients WHERE id = :client_id
                    """),
                    {"client_id": client_dto.ClientId}
                )
                existing_client = result.mappings().first()

                if existing_client is None:
                    response.Status = 1
                    response.Message = f"Client with ID {client_dto.ClientId} not found"
                    return response

                # Check if another client with same name exists
                result = await session.execute(
                    text("""
                        SELECT id FROM clients
                        WHERE LOWER(TRIM(clientname)) = LOWER(TRIM(:clientname))
                        AND id != :client_id
                        AND status = 1
                    """),
                    {"clientname": client_dto.Clientname, "client_id": client_dto.ClientId}
                )
                existing_clientname = result.mappings().first()

                if existing_clientname:
                    response.Status = 1
                    response.Message = "A client with the given name already exists."
                    return response

                # Handle logo upload if provided
                logo_filename = existing_client["logo"]
                if client_dto.Logo:
                    logo_filename = await upload_file(client_dto.Logo)

                # Update client
                await session.execute(
                    text("""
                        UPDATE clients
                        SET
                            clientname = :clientname,
                            status = :status,
                            logo = :logo,
                            updateddate = :updateddate,
                            updatedby = :updatedby
                        WHERE id = :client_id
                    """),
                    {
                        "clientname": client_dto.Clientname,
                        "status": client_dto.Status,
                        "logo": logo_filename,
                        "updateddate": datetime.now(),
                        "updatedby": str(self.user_id),
                        "client_id": client_dto.ClientId
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error updating client: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating the client: {str(ex)}"

        return response



        



