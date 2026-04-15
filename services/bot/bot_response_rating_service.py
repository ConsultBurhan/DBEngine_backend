"""Bot response rating service for managing bot response rating operations."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.service_models.bot.bot_response_rating_service_models import BotResponseRatingList, CreateBotResponseRating
from models.common import ResponseData, UResponse
from config.logger_config import get_logger

logger = get_logger(__name__)


class BotResponseRatingService:
    """Service for bot response rating operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_bot_response_rating_list_async(self, bot_id: int) -> ResponseData[List[BotResponseRatingList]]:
        """Get bot response ratings for a specific bot with question and answer text."""
        response = ResponseData[List[BotResponseRatingList]](
            Success=True,
            Message="",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT 
                            brr."Id", 
                            brr."ConversationId", 
                            brr."ConversationMessageId",
                            brr."BotId", 
                            brr."Ratings",
                            brr."ReviewMessage", 
                            brr."CreatedDate", 
                            brr."CreatedBy", 
                            brr."Status", 
                            answer_msg.messagetext AS AnswerText, 
                            question_msg.messagetext AS QuestionText
                        FROM bot_response_rating brr
                        LEFT JOIN conversationmessages answer_msg 
                            ON answer_msg.id = brr."ConversationMessageId"
                            AND answer_msg.conversationid = brr."ConversationId"
                        LEFT JOIN LATERAL (
                            SELECT cm.messagetext
                            FROM conversationmessages cm
                            WHERE cm.conversationid = brr."ConversationId"
                            AND cm.id < brr."ConversationMessageId"
                            ORDER BY cm.id DESC 
                            LIMIT 1
                        ) question_msg ON true
                        WHERE brr."BotId" = :bot_id
                    """),
                    {"bot_id": bot_id}
                )
                rows = result.mappings().all()

                ratings = [
                    BotResponseRatingList(
                        Id=row["Id"],
                        ConversationId=row["ConversationId"],
                        ConversationMessageId=row["ConversationMessageId"],
                        BotId=row["BotId"],
                        Ratings=row["Ratings"],
                        ReviewMessage=row["ReviewMessage"],
                        AnswerText=row.get("answertext", ""),
                        QuestionText=row.get("questiontext", ""),
                        CreatedDate=row["CreatedDate"],
                        CreatedBy=row["CreatedBy"] if row["CreatedBy"] else 0,
                        Status=row["Status"]
                    )
                    for row in rows
                ]

                response.Data = ratings
                response.Success = True
                response.Message = "Bot response ratings retrieved successfully."

        except Exception as ex:
            logger.error(f"Error retrieving bot response ratings: {ex}")
            response.Success = False
            response.Message = f"Error retrieving bot response ratings: {str(ex)}"
            response.Data = []

        return response

    async def create_bot_response_rating_async(self, bot_rating: CreateBotResponseRating) -> UResponse:
        """Create a new bot response rating."""
        response = UResponse(Status=0, Message="")

        try:
            if bot_rating is None:
                response.Status = 1
                response.Message = "Invalid request data."
                return response

            async with await self._db_manager.get_session() as session:
                now = datetime.now()
                await session.execute(
                    text("""
                        INSERT INTO bot_response_rating (
                            "ConversationId",
                            "ConversationMessageId",
                            "BotId",
                            "Ratings",
                            "ReviewMessage",
                            "CreatedDate",
                            "CreatedBy",
                            "ClientId",
                            "Status"
                        ) VALUES (
                            :conversation_id,
                            :conversation_message_id,
                            :bot_id,
                            :ratings,
                            :review_message,
                            :created_date,
                            :created_by,
                            :client_id,
                            :status
                        )
                    """),
                    {
                        "conversation_id": bot_rating.ConversationId,
                        "conversation_message_id": bot_rating.ConversationMessageId,
                        "bot_id": bot_rating.BotId,
                        "ratings": bot_rating.Ratings,
                        "review_message": bot_rating.ReviewMessage,
                        "created_date": now,
                        "created_by": self.user_id,
                        "client_id": self.client_id,
                        "status": 1,  # Not Trained
                    }
                )
                await session.commit()

                response.Status = 0
                response.Message = "Bot's response rating created successfully."

        except Exception as ex:
            logger.error(f"Error creating bot response rating: {ex}")
            response.Status = 1
            response.Message = f"Error creating bot response rating: {str(ex)}"

        return response
