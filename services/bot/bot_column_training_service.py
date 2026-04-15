import json
import os
from datetime import datetime
from typing import Optional, List

from sqlalchemy import text

from config.logger_config import get_logger
from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from database.dbModel.column_training.column_training import ColumnTraining
from httpx import AsyncClient
from services.JWT.JWT_service import JWTService
from dotenv import load_dotenv
from models.common import ResponseData
from models.service_models.bot.bot_column_training_service_models import (
    BotColumnTrainingList,
    BotColumnTrainingCreate,
    BotColumnTrainingUpdate,
)

logger = get_logger(__name__)
load_dotenv()


# DB Bot configuration from environment variables
DB_BOT_BASE_URL = os.getenv("DB_BOT_BASE_URL")
DB_BOT_API_KEY = os.getenv("DB_BOT_API_KEY")
DB_BOT_TIMEOUT_SECONDS = int(os.getenv("DB_BOT_TIMEOUT_SECONDS", "300"))

# Validate DB bot configuration
if not DB_BOT_BASE_URL:
    raise ValueError("DB_BOT_BASE_URL environment variable is not set")
if not DB_BOT_API_KEY:
    raise ValueError("DB_BOT_API_KEY environment variable is not set")




class BotColumnTrainingService:
    def __init__(
        self,
        client_id: int,
        user_id: int,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self._client_id = client_id
        self._user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_column_training_list(
        self,
    ) -> ResponseData[List[BotColumnTrainingList]]:
        """Get column training list from DB bot API."""
        response = ResponseData[List[BotColumnTrainingList]](
            Success=True,
            Message="SUCCESS",
            Data=[],
        )

        try:
            url = f"{DB_BOT_BASE_URL}/training/list"
            headers = {"X-API-Key": DB_BOT_API_KEY}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.get(url, headers=headers)

                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to fetch list: {process_response.text}"
                    return response

                response_content = process_response.text
                parsed_data = json.loads(response_content)
                if parsed_data.get("data", None):
                    data = [
                        BotColumnTrainingList(**item) for item in parsed_data.get("data")
                    ]
                data = list()
                response.Data = data if data else []

        except Exception as ex:
            logger.error(f"Error in get_column_training_list: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

    async def get_column_training_by_training_id(
        self,
        training_id: str,
    ) -> ResponseData[BotColumnTrainingList]:
        """Get column training detail by training ID from DB bot API."""
        response = ResponseData[BotColumnTrainingList](
            Success=True,
            Message="SUCCESS",
            Data=None,
        )

        try:
            url = f"{DB_BOT_BASE_URL}/training/get/{training_id}"
            headers = {"X-API-Key": DB_BOT_API_KEY}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.get(url, headers=headers)

                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to fetch detail: {process_response.text}"
                    return response

                response_content = process_response.text
                parsed_data = json.loads(response_content)
                data = BotColumnTrainingList(**parsed_data.get("data")) if parsed_data.get("data", None) else []
                response.Data = data 

        except Exception as ex:
            logger.error(f"Error in get_column_training_by_training_id: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

    async def create_column_training(
        self,
        training: BotColumnTrainingCreate,
    ) -> ResponseData:
        """Create column training record and send to DB bot API."""
        response = ResponseData(
            Success=True,
            Message="SUCCESS",
            Data=None,
        )

        try:
            if training is None:
                response.Success = False
                response.Message = "Invalid data"
                return response

            # Insert into database
            async with await self._db_manager.get_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO column_training
                        ("ColumnName", "ColumnType", "ColumnDescription", "SchemaName", "TableName",
                         "Synonyms", "SampleValues", "CreatedDate", "CreatedBy")
                        VALUES
                        (:column_name, :column_type, :column_description, :schema_name, :table_name,
                         :synonyms, :sample_values, :created_date, :created_by)
                        RETURNING "TrainingId"
                    """),
                    {
                        "column_name": training.ColumnName,
                        "column_type": training.ColumnType,
                        "column_description": training.ColumnDescription,
                        "schema_name": training.SchemaName,
                        "table_name": training.TableName,
                        "synonyms": training.Synonyms,
                        "sample_values": training.SampleData,
                        "created_date": datetime.now(),
                        "created_by": self._user_id,
                    }
                )
                await session.commit()

            # Prepare request body for external API
            sample_values_list = []
            if training.SampleData:
                sample_values_list = [
                    x.strip() for x in training.SampleData.split(',')
                    if x.strip()
                ]

            synonyms_list = []
            if training.Synonyms:
                synonyms_list = [
                    x.strip() for x in training.Synonyms.split(',')
                    if x.strip()
                ]

            db_req_body = {
                "schema_name": training.SchemaName,
                "table_name": training.TableName,
                "column_name": training.ColumnName,
                "column_description": training.ColumnDescription,
                "column_dtype": training.ColumnType,
                "sample_values": sample_values_list,
                "sysnonyms": synonyms_list
            }

            # Make POST request to external API
            url = f"{DB_BOT_BASE_URL}/training/create"
            headers = {"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.post(url, json=[db_req_body], headers=headers)
            
                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to embed view metadata: {process_response.text}"
                    return response

            response.Message = "Bot training created successfully"

        except Exception as ex:
            logger.error(f"Error in create_column_training: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

    async def update_column_training(
        self,
        training: BotColumnTrainingUpdate,
    ) -> ResponseData:
        """Update column training record via DB bot API."""
        response = ResponseData(
            Success=True,
            Message="SUCCESS",
            Data=None,
        )

        try:
            if training is None:
                response.Success = False
                response.Message = "Invalid data"
                return response

            # Prepare request body for external API
            sample_values_list = []
            if training.SampleData:
                sample_values_list = [
                    x.strip() for x in training.SampleData.split(',')
                    if x.strip()
                ]

            synonyms_list = []
            if training.Synonyms:
                synonyms_list = [
                    x.strip() for x in training.Synonyms.split(',')
                    if x.strip()
                ]

            db_req_body = {
                "id": training.TrainingId,
                "data": {
                    "schema_name": training.SchemaName,
                    "table_name": training.TableName,
                    "column_name": training.ColumnName,
                    "column_description": training.ColumnDescription,
                    "column_dtype": training.ColumnType,
                    "sample_values": sample_values_list,
                    "sysnonyms": synonyms_list
                }
            }

            # Make PUT request to external API
            url = f"{DB_BOT_BASE_URL}/training/update"
            headers = {"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.put(url, json=db_req_body, headers=headers)
                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to embed view metadata: {process_response.text}"
                    return response

            response.Message = "Bot training updated successfully"

        except Exception as ex:
            logger.error(f"Error in update_column_training: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

    async def delete_training(
        self,
        training_id: str,
    ) -> ResponseData:
        """Delete column training record via DB bot API."""
        response = ResponseData(
            Success=True,
            Message="SUCCESS",
            Data=None,
        )

        try:
            if training_id is None:
                response.Success = False
                response.Message = "Training Id is required"
                return response

            # Make DELETE request to external API
            url = f"{DB_BOT_BASE_URL}/training/delete/{training_id}"
            headers = {"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.delete(url, headers=headers)

                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to delete training: {process_response.text}"
                    return response

            response.Message = "Training deleted successfully"

        except Exception as ex:
            logger.error(f"Error in delete_training: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

