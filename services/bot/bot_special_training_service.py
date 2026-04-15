import json
import os
from typing import Optional, List

from config.logger_config import get_logger
from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from httpx import AsyncClient
from dotenv import load_dotenv
from models.common import ResponseData, UResponse
from models.service_models.bot.bot_column_training_service_models import (
    BotSpecialTrainingUpdate,
    BotSpecialTrainingCreate,
    BotSpecialTrainingList,
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

class BotSpecialTrainingService:
    def __init__(self, client_id: int, user_id: int, db_manager: Optional[PostgresConnectionManager] = None):
        self._user_id = user_id
        self._client_id = client_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_special_training_list(self) -> ResponseData[List[BotSpecialTrainingList]]:
        """Get special training list from DB bot API."""
        response = ResponseData[List[BotSpecialTrainingList]](
            Success=True,
            Message="SUCCESS",
            Data=[],
        )

        try:
            url = f"{DB_BOT_BASE_URL}/training/rules/list"
            headers = {"X-API-Key": DB_BOT_API_KEY}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.get(url, headers=headers)

                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to fetch list: {process_response.text}"
                    return response

                response_content = json.loads(process_response.text)
                parsed_data = response_content.get("data", None)
                data = [
                    BotSpecialTrainingList(**item) for item in parsed_data
                ] if parsed_data else []

                response.Data = data

        except Exception as ex:
            logger.error(f"Error in get_special_training_list: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

    async def get_special_training_by_training_id(
        self,
        training_id: str,
    ) -> ResponseData[BotSpecialTrainingList]:
        """Get special training detail by training ID from DB bot API."""
        response = ResponseData[BotSpecialTrainingList](
            Success=True,
            Message="SUCCESS",
            Data=None,
        )

        try:
            url = f"{DB_BOT_BASE_URL}/training/rules/get/{training_id}"
            headers = {"X-API-Key": DB_BOT_API_KEY}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.get(url, headers=headers)

                if not process_response.is_success:
                    response.Success = False
                    response.Message = f"Failed to fetch detail: {process_response.text}"
                    return response

                response_content = json.loads(process_response.text)
                parsed_data = response_content.get("data", None)
                data = BotSpecialTrainingList(**parsed_data) if parsed_data else None

                response.Data = data

        except Exception as ex:
            logger.error(f"Error in get_special_training_by_training_id: {ex}")
            response.Success = False
            response.Message = str(ex)

        return response

    async def create_special_training(self, training: BotSpecialTrainingCreate) -> UResponse:
        """Create special training via DB bot API."""
        response = UResponse(Status=0, Message="SUCCESS")

        try:
            if training is None:
                response.Status = 1
                response.Message = "Invalid data"
                return response

            db_req_body = {
                "text": training.text,
                "title": training.title,
                "category": training.category
            }

            url = f"{DB_BOT_BASE_URL}/training/rules/create"
            headers = {"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.post(url, json=[db_req_body], headers=headers)

                if not process_response.is_success:
                    response.Status = 1
                    response.Message = f"Failed to create special training: {process_response.text}"
                    return response

            response.Message = "Bot special training created successfully"

        except Exception as ex:
            logger.error(f"Error in create_special_training: {ex}")
            response.Status = 1
            response.Message = str(ex)

        return response

    async def update_special_training(self, training: BotSpecialTrainingList) -> UResponse:
        """Update special training via DB bot API."""
        response = UResponse(Status=0, Message="SUCCESS")

        try:
            if training is None:
                response.Status = 1
                response.Message = "Invalid data"
                return response

            db_req_body = {
                "id": training.id,
                "text": training.text,
                "title": training.title,
                "category": training.category
            }

            url = f"{DB_BOT_BASE_URL}/training/rules/update"
            headers = {"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.put(url, json=db_req_body, headers=headers)

                if not process_response.is_success:
                    response.Status = 1
                    response.Message = f"Failed to update special training: {process_response.text}"
                    return response

            response.Message = "Bot special training updated successfully"

        except Exception as ex:
            logger.error(f"Error in update_special_training: {ex}")
            response.Status = 1
            response.Message = str(ex)

        return response

    async def delete_special_training(self, training_id: str) -> UResponse:
        """Delete special training via DB bot API."""
        response = UResponse(Status=0, Message="SUCCESS")

        try:
            if training_id is None:
                response.Status = 1
                response.Message = "Training ID is required"
                return response

            url = f"{DB_BOT_BASE_URL}/training/rules/delete/{training_id}"
            headers = {"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"}

            async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                process_response = await client.delete(url, headers=headers)

                if not process_response.is_success:
                    response.Status = 1
                    response.Message = f"Failed to delete special training: {process_response.text}"
                    return response

            response.Message = "Training deleted successfully"

        except Exception as ex:
            logger.error(f"Error in delete_special_training: {ex}")
            response.Status = 1
            response.Message = str(ex)

        return response
