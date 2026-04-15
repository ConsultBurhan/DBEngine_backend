"""App settings service for managing app settings operations."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.service_models.app_settings.app_settings_service_models import AppSetting, AppsettingCreate
from models.common import ResponseData, UResponse
from config.logger_config import get_logger

logger = get_logger(__name__)


class AppSettingsService:
    """Service for app settings operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self._client_id = client_id
        self._user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_appsettings_async(self) -> ResponseData[List[AppSetting]]:
        """Get all app settings filtered by status and ordered by keyname."""
        response = ResponseData[List[AppSetting]](
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
                            keyname,
                            value,
                            botid,
                            iseditable,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby,
                            clientid
                        FROM appsettings
                        WHERE status = '1'
                        ORDER BY keyname
                    """)
                )
                rows = result.mappings().all()

                appsettings = [
                    AppSetting(
                        id=row["id"],
                        keyname=row["keyname"],
                        value=row["value"],
                        botid=row["botid"],
                        iseditable=row["iseditable"],
                        status=row["status"],
                        createddate=row["createddate"],
                        createdby=row["createdby"],
                        updateddate=row["updateddate"],
                        updatedby=row["updatedby"],
                        clientid=row["clientid"]
                    )
                    for row in rows
                ]

                response.Data = appsettings
                response.Success = True
                response.Message = "App settings fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching app settings: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching app settings: {str(ex)}"
            response.Data = []

        return response

    async def get_appsetting_by_id_async(self, appsetting_id: int) -> ResponseData[AppSetting]:
        """Get a single app setting by ID, filtered by status."""
        response = ResponseData[AppSetting](
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
                            keyname,
                            value,
                            botid,
                            iseditable,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby,
                            clientid
                        FROM appsettings
                        WHERE id = :appsetting_id
                          AND status = '1'
                    """),
                    {"appsetting_id": appsetting_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"No active app setting found with ID {appsetting_id}"
                    return response

                appsetting = AppSetting(
                    id=row["id"],
                    keyname=row["keyname"],
                    value=row["value"],
                    botid=row["botid"],
                    iseditable=row["iseditable"],
                    status=row["status"],
                    createddate=row["createddate"],
                    createdby=row["createdby"],
                    updateddate=row["updateddate"],
                    updatedby=row["updatedby"],
                    clientid=row["clientid"]
                )

                response.Data = appsetting
                response.Success = True
                response.Message = "App setting fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching app setting by ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching app setting: {str(ex)}"

        return response

    async def create_appsetting_async(self, appsetting: AppsettingCreate) -> UResponse:
        """Create a new app setting with current timestamp and active status."""
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                insert_result = await session.execute(
                    text("""
                        INSERT INTO appsettings (
                            keyname, value, botid, iseditable, status,
                            createddate, createdby, clientid
                        ) VALUES (
                            :keyname, :value, :botid, :iseditable, :status,
                            :created_date, :created_by, :client_id
                        ) RETURNING id
                    """),
                    {
                        "keyname": appsetting.keyname,
                        "value": appsetting.value,
                        "botid": appsetting.botid,
                        "iseditable": appsetting.iseditable,
                        "status": "1",
                        "created_date": datetime.now(),
                        "created_by": str(self._user_id),
                        "client_id": self._client_id,
                    }
                )
                await session.commit()

                response.Status = 0
                response.Message = "App setting created successfully"

        except Exception as ex:
            logger.error(f"Error creating app setting: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating the app setting: {str(ex)}"

        return response

    async def update_appsetting_async(self, appsetting_id: int, appsetting: AppSetting) -> ResponseData[AppSetting]:
        """Update an existing app setting."""
        response = ResponseData[AppSetting](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if app setting exists
                result = await session.execute(
                    text("""
                        SELECT id FROM appsettings
                        WHERE id = :appsetting_id
                    """),
                    {"appsetting_id": appsetting_id}
                )
                existing_appsetting = result.mappings().first()

                if existing_appsetting is None:
                    response.Success = False
                    response.Message = f"App setting with ID {appsetting_id} not found"
                    return response

                # Update app setting
                now = datetime.now()
                await session.execute(
                    text("""
                        UPDATE appsettings
                        SET keyname = :keyname,
                            value = :value,
                            status = :status,
                            updateddate = :updated_date,
                            updatedby = :updated_by
                        WHERE id = :appsetting_id
                    """),
                    {
                        "keyname": appsetting.keyname,
                        "value": appsetting.value,
                        "status": appsetting.status,
                        "updated_date": now,
                        "updated_by": appsetting.updatedby,
                        "appsetting_id": appsetting_id,
                    }
                )
                await session.commit()

                # Fetch updated record
                result = await session.execute(
                    text("""
                        SELECT
                            id,
                            keyname,
                            value,
                            botid,
                            iseditable,
                            status,
                            createddate,
                            createdby,
                            updateddate,
                            updatedby,
                            clientid
                        FROM appsettings
                        WHERE id = :appsetting_id
                    """),
                    {"appsetting_id": appsetting_id}
                )
                row = result.mappings().first()

                updated_appsetting = AppSetting(
                    id=row["id"],
                    keyname=row["keyname"],
                    value=row["value"],
                    botid=row["botid"],
                    iseditable=row["iseditable"],
                    status=row["status"],
                    createddate=row["createddate"],
                    createdby=row["createdby"],
                    updateddate=row["updateddate"],
                    updatedby=row["updatedby"],
                    clientid=row["clientid"]
                )

                response.Data = updated_appsetting
                response.Success = True
                response.Message = "App setting updated successfully"

        except Exception as ex:
            logger.error(f"Error updating app setting: {ex}")
            response.Success = False
            response.Message = f"An error occurred while updating the app setting: {str(ex)}"

        return response

    async def delete_appsetting_async(self, appsetting_id: int) -> UResponse:
        """Soft delete an app setting by setting status to '0'."""
        response = UResponse(Status=0, Message="App setting deleted successfully")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if app setting exists
                result = await session.execute(
                    text("""
                        SELECT id FROM appsettings
                        WHERE id = :appsetting_id
                    """),
                    {"appsetting_id": appsetting_id}
                )
                appsetting = result.mappings().first()

                if appsetting is None:
                    response.Status = 1
                    response.Message = f"App setting with ID {appsetting_id} not found"
                    return response

                # Soft delete by setting status to '0'
                now = datetime.now()
                await session.execute(
                    text("""
                        UPDATE appsettings
                        SET status = '0',
                            updateddate = :updated_date
                        WHERE id = :appsetting_id
                    """),
                    {
                        "updated_date": now,
                        "appsetting_id": appsetting_id
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error deleting app setting: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting app setting: {str(ex)}"

        return response
