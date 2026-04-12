"""Bot training service for bot training operations."""

import json
import os
from typing import List, Optional

from dotenv import load_dotenv
from httpx import AsyncClient, TimeoutException
from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.common import ResponseData, UResponse
from models.service_models.bot.bot_training_service_models import (
    BotsTrainingListing,
    UpdateBotTraining,
    CreateBotGenralTraining,
    CreateBotDatabaseTraining,
)
from config.logger_config import get_logger

logger = get_logger(__name__)
load_dotenv()

# Chatbot configuration from environment variables
CHATBOT_BASE_URL = os.getenv("CHATBOT_BASE_URL")
CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")
CHATBOT_TIMEOUT_SECONDS = int(os.getenv("CHATBOT_TIMEOUT_SECONDS", "300"))

# Validate chatbot configuration
if not CHATBOT_BASE_URL:
    raise ValueError("CHATBOT_BASE_URL environment variable is not set")
if not CHATBOT_API_KEY:
    raise ValueError("CHATBOT_API_KEY environment variable is not set")

# DB Bot configuration from environment variables
DB_BOT_BASE_URL = os.getenv("DB_BOT_BASE_URL")
DB_BOT_API_KEY = os.getenv("DB_BOT_API_KEY")
DB_BOT_TIMEOUT_SECONDS = int(os.getenv("DB_BOT_TIMEOUT_SECONDS", "300"))

# Validate DB bot configuration
if not DB_BOT_BASE_URL:
    raise ValueError("DB_BOT_BASE_URL environment variable is not set")
if not DB_BOT_API_KEY:
    raise ValueError("DB_BOT_API_KEY environment variable is not set")


class BotTrainingService:
    """Service for bot training operations."""

    def __init__(self, client_id: int, user_id: int):
        """Initialize BotTrainingService with client_id and user_id."""
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = get_postgres_manager()

    async def get_all_bot_trainings_async(self) -> ResponseData[List[BotsTrainingListing]]:
        """Get all active bot trainings."""
        response = ResponseData[List[BotsTrainingListing]](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, type, subid, trainingtext, embeddingdb, embeddingdetails,
                               botid, status, issqlquery, createddate, createdby, updateddate, updatedby
                        FROM bottraining
                        WHERE status = '1'
                        ORDER BY trainingtext
                    """)
                )
                rows = result.mappings().all()

                bot_trainings = [
                    BotsTrainingListing(
                        Id=row["id"],
                        Type=row["type"],
                        Subid=row["subid"],
                        Trainingtext=row["trainingtext"],
                        Embeddingdb=row["embeddingdb"],
                        Embeddingdetails=row["embeddingdetails"],
                        Botid=row["botid"],
                        Status=row["status"],
                        Issqlquery=row["issqlquery"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )
                    for row in rows
                ]

                response.Data = bot_trainings
                response.Success = True
                response.Message = "Bot trainings fetched successfully."

        except Exception as ex:
            logger.error(f"Error fetching bot trainings: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bot trainings: {str(ex)}"
            response.Data = []

        return response

    async def get_bot_training_by_id_async(self, bot_training_id: int) -> ResponseData[BotsTrainingListing]:
        """Get a specific bot training by ID."""
        response = ResponseData[BotsTrainingListing](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, type, subid, trainingtext, embeddingdb, embeddingdetails,
                               botid, status, issqlquery, createddate, createdby, updateddate, updatedby
                        FROM bottraining
                        WHERE id = :id AND status = '1'
                    """),
                    {"id": bot_training_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Bot training with ID {bot_training_id} not found."
                else:
                    bot_training = BotsTrainingListing(
                        Id=row["id"],
                        Type=row["type"],
                        Subid=row["subid"],
                        Trainingtext=row["trainingtext"],
                        Embeddingdb=row["embeddingdb"],
                        Embeddingdetails=row["embeddingdetails"],
                        Botid=row["botid"],
                        Status=row["status"],
                        Issqlquery=row["issqlquery"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                    )

                    response.Data = bot_training
                    response.Success = True
                    response.Message = "Bot training fetched successfully."

        except Exception as ex:
            logger.error(f"Error fetching bot training: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bot training: {str(ex)}"

        return response

    async def delete_bottraining_async(self, bot_training_id: int) -> UResponse:
        """Soft delete a bot training by setting status to '0'."""
        response = UResponse(Status=0, Message="Bot training deleted successfully")

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id FROM bottraining
                        WHERE id = :id
                    """),
                    {"id": bot_training_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Status = 1
                    response.Message = f"Bot training with ID {bot_training_id} not found"
                    return response

                await session.execute(
                    text("""
                        UPDATE bottraining
                        SET status = '0',
                            updateddate = NOW()
                        WHERE id = :id
                    """),
                    {"id": bot_training_id}
                )
                await session.commit()

                return response

        except Exception as ex:
            logger.error(f"Error deleting bot training: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting bot training: {str(ex)}"
            return response

    async def update_bottraining_async(self, bot_training_id: int, update_bot_training: UpdateBotTraining) -> ResponseData[BotsTrainingListing]:
        """Update an existing bot training."""
        response = ResponseData[BotsTrainingListing](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if bot training exists
                result = await session.execute(
                    text("""
                        SELECT id FROM bottraining
                        WHERE id = :id
                    """),
                    {"id": bot_training_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Bot training with ID {bot_training_id} not found"
                    return response

                # Update bot training
                await session.execute(
                    text("""
                        UPDATE bottraining
                        SET trainingtext = :trainingtext,
                            botid = :botid,
                            status = :status,
                            updateddate = NOW(),
                            updatedby = :updatedby
                        WHERE id = :id
                    """),
                    {
                        "trainingtext": update_bot_training.Trainingtext,
                        "botid": update_bot_training.Botid,
                        "status": update_bot_training.Status,
                        "updatedby": str(self.user_id),
                        "id": bot_training_id,
                    }
                )
                await session.commit()

                # Fetch updated record
                result = await session.execute(
                    text("""
                        SELECT id, type, subid, trainingtext, embeddingdb, embeddingdetails,
                               botid, status, issqlquery, createddate, createdby, updateddate, updatedby
                        FROM bottraining
                        WHERE id = :id
                    """),
                    {"id": bot_training_id}
                )
                updated_row = result.mappings().first()

                updated_bot_training = BotsTrainingListing(
                    Id=updated_row["id"],
                    Type=updated_row["type"],
                    Subid=updated_row["subid"],
                    Trainingtext=updated_row["trainingtext"],
                    Embeddingdb=updated_row["embeddingdb"],
                    Embeddingdetails=updated_row["embeddingdetails"],
                    Botid=updated_row["botid"],
                    Status=updated_row["status"],
                    Issqlquery=updated_row["issqlquery"],
                    Createddate=updated_row["createddate"],
                    Createdby=updated_row["createdby"],
                    Updateddate=updated_row["updateddate"],
                    Updatedby=updated_row["updatedby"],
                )

                response.Data = updated_bot_training
                response.Success = True
                response.Message = "Bot training updated successfully."

        except Exception as ex:
            logger.error(f"Error updating bot training: {ex}")
            response.Success = False
            response.Message = f"An error occurred while updating bot training: {str(ex)}"

        return response

    async def _upload_general_training_to_chatbot(self, create_bot_training: CreateBotGenralTraining) -> UResponse:
        """Upload general training to chatbot service."""
        response = UResponse(Status=0, Message="")

        try:
            # Create request body
            request_body = {
                "text": create_bot_training.TraingingText,
                "question": create_bot_training.QuestionText,
                "bot_id": str(create_bot_training.BotId),
                "training_type": create_bot_training.TrainingType,
                "client_id": str(self.client_id),
                "source": create_bot_training.Source
            }

            # Make HTTP POST request to chatbot service
            url = f"{CHATBOT_BASE_URL}/BotTraining/re-train"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": CHATBOT_API_KEY
            }

            async with AsyncClient(timeout=CHATBOT_TIMEOUT_SECONDS) as client:
                process_response = await client.post(url, json=request_body, headers=headers)

                if not process_response.is_success:
                    response_content = process_response.text
                    response.Status = 1
                    response.Message = f"Bot training failed: {response_content}"
                    return response

            # Update BotResponseRating status to 2 (Trained) if BotResponseRatingId is provided
            if create_bot_training.BotResponseRatingId:
                async with await self._db_manager.get_session() as session:
                    result = await session.execute(
                        text("""
                            SELECT id FROM bot_response_rating
                            WHERE id = :id
                        """),
                        {"id": create_bot_training.BotResponseRatingId}
                    )
                    bot_response_rating = result.mappings().first()

                    if bot_response_rating:
                        await session.execute(
                            text("""
                                UPDATE bot_response_rating
                                SET status = 2
                                WHERE id = :id
                            """),
                            {"id": create_bot_training.BotResponseRatingId}
                        )
                        await session.commit()

            response.Status = 0
            response.Message = "Training uploaded and Bot training started successfully."

        except TimeoutException as ex:
            logger.error(f"Timeout while uploading training to chatbot: {ex}")
            response.Status = 1
            response.Message = f"Timeout while uploading training to chatbot: {str(ex)}"
        except Exception as ex:
            logger.error(f"Error generating and uploading training file: {ex}")
            response.Status = 1
            response.Message = f"Error generating and uploading training file: {str(ex)}"

        return response

    async def create_general_bot_training(self, create_bot_training: CreateBotGenralTraining) -> UResponse:
        """Create general bot training."""
        response = UResponse(Status=0, Message="")

        try:
            if create_bot_training is None:
                response.Status = 1
                response.Message = "Missing required parameters"
                return response

            return await self._upload_general_training_to_chatbot(create_bot_training)

        except Exception as ex:
            logger.error(f"Error generating and uploading training file: {ex}")
            response.Status = 1
            response.Message = f"Error generating and uploading training file: {str(ex)}"

        return response

    async def create_bot_database_training_async(self, create_bot_training: CreateBotDatabaseTraining) -> UResponse:
        """Create bot database training."""
        result = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Validate database connection
                connection_result = await session.execute(
                    text("""
                        SELECT id, dbname FROM databaseconnection
                        WHERE id = :id AND status != '-1'
                    """),
                    {"id": create_bot_training.ConnectionId}
                )
                connection_detail = connection_result.mappings().first()

                if connection_detail is None:
                    result.Status = 1
                    result.Message = "Database connection not found."
                    return result

                # Validate View_Metadata
                if create_bot_training.View_Metadata is None:
                    result.Status = 1
                    result.Message = "View data is required."
                    return result

                # Build view data
                view_data = {
                    "schema_name": connection_detail["dbname"] or "",
                    "view_name": create_bot_training.View_Metadata.View_Name or "",
                    "business_logic": create_bot_training.View_Metadata.Description or "",
                    "RelationShip": create_bot_training.View_Metadata.RelationShip or "",
                    "synonyms": create_bot_training.View_Metadata.Synonyms or []
                }

                # Validate Columns_Metadata
                if create_bot_training.Columns_Metadata is None or not create_bot_training.Columns_Metadata:
                    result.Status = 1
                    result.Message = "Columns_Metadata is required."
                    return result

                # Get column information from database
                column_ids = [col.ColumnId for col in create_bot_training.Columns_Metadata]
                columns_result = await session.execute(
                    text("""
                        SELECT id, columnname, dbtype FROM databasetablescolumns
                        WHERE id = ANY(:column_ids)
                    """),
                    {"column_ids": column_ids}
                )
                columns = columns_result.mappings().all()

                if len(columns) != len(column_ids):
                    result.Status = 1
                    result.Message = "One or more column IDs not found in database."
                    return result

                # Build columns_metadata array
                columns_metadata = []
                columns_dict = {col["id"]: col for col in columns}

                for column_metadata in create_bot_training.Columns_Metadata:
                    column = columns_dict.get(column_metadata.ColumnId)
                    if column is None:
                        continue

                    column_data = {
                        "column_name": column["columnname"] or "",
                        "column_datatype": column["dbtype"] or "",
                        "synonyms": column_metadata.Synonyms or [],
                        "column_description": column_metadata.Description or "",
                        "RelationShip": column_metadata.RelationShip or "",
                        "sample_data": []
                    }
                    columns_metadata.append(column_data)

                # Build request body
                request_body = {
                    "view_metadata": {
                        "additionalProp1": view_data
                    },
                    "columns_metadata": columns_metadata,
                    "clientId": str(self.client_id),
                    "botId": create_bot_training.BotId,
                    "roleId": create_bot_training.RoleId
                }

                # Send request to DB bot service
                url = f"{DB_BOT_BASE_URL}/EmbeddViewMetaData/"
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": DB_BOT_API_KEY
                }

                async with AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                    process_response = await client.post(url, json=request_body, headers=headers)

                    if not process_response.is_success:
                        response_content = process_response.text
                        result.Status = 1
                        result.Message = f"Failed to embed view metadata: {response_content}"
                        return result

                result.Status = 0
                result.Message = "View metadata embedded successfully."

        except TimeoutException as ex:
            logger.error(f"Timeout while creating bot database training: {ex}")
            result.Status = 1
            result.Message = f"Timeout while creating bot database training: {str(ex)}"
        except Exception as ex:
            logger.error(f"Error occurred while creating bot training: {ex}")
            result.Status = 1
            result.Message = f"Error occurred while creating bot training: {str(ex)}"

        return result
