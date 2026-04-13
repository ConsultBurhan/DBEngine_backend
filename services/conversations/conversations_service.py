"""Conversation service for managing conversation operations."""
from __future__ import annotations

from typing import List, Optional

from fastapi import Request
from sqlalchemy import text

from config.logger_config import get_logger
from database.dbConnection.postgres_connection import PostgresConnectionManager, get_postgres_manager
from models.service_models.conversation.conversation_service_models import (
    ChatApiResponse,
    ConversationDto,
    GetResponse,
    GetResponseResult,
    GraphData,
    SqlResult,
    StreamingEvent,
    StreamingEventData,
    Summary,
)
from models.common import ResponseData
from models.service_models.conversations.conversations_service_models import (
    ConversationMessages,
    ConversationsList,
)
from services.fileupload.file_upload_service import upload_file

logger = get_logger(__name__)


class ConversationService:
    """Service for conversation operations."""

    def __init__(
        self,
        client_id: int, 
        user_id: int, 
        db_manager: Optional[PostgresConnectionManager] = None,
    ) -> None: 
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_user_conversation_async(
        self, 
        user_id: int, 
        bot_id: int
    ) -> ResponseData[List[ConversationsList]]:
        """Get conversations for a specific user and bot."""
        response = ResponseData[List[ConversationsList]](
            Success=True,
            Message="",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT * FROM conversations
                        WHERE userid = :user_id AND botid = :bot_id AND status = 'Active'
                        ORDER BY createddate DESC
                    """),
                    {
                        "user_id": user_id,
                        "bot_id": bot_id,
                    },
                )
                rows = result.mappings().all()

                conversations_list: List[ConversationsList] = []
                for row in rows:
                    conversation_dto = ConversationsList(
                        Id=row["id"],
                        Clientid=row.get("clientid"),
                        Botid=row.get("botid"),
                        Userid=row.get("userid"),
                        Threadid=row.get("threadid"),
                        BotType=row.get("bottype"),
                        Chatmetadata=row.get("chatmetadata"),
                        Status=row.get("status"),
                        Createddate=row.get("createddate"),
                        Createdby=row.get("createdby"),
                        Updateddate=row.get("updateddate"),
                        Updatedby=row.get("updatedby"),
                        Title=row.get("title"),
                        Lastmessage=row.get("lastmessage"),
                        Messagecount=row.get("messagecount"),
                    )
                    conversations_list.append(conversation_dto)

                response.Success = True
                response.Message = "Conversations fetched successfully."
                response.Data = conversations_list

        except Exception as ex:
            logger.error(f"Error fetching conversations: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching conversations: {str(ex)}"
            response.Data = None

        return response

    async def get_conversation_message_by_id_async(
        self,
        conversation_id: int,
        page_number: int = 1,
        page_size: int = 10
    ) -> ResponseData[List[ConversationMessages]]:
        """Get messages for a specific conversation with pagination."""
        response = ResponseData[List[ConversationMessages]](
            Success=True,
            Message="",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Get total count
                count_result = await session.execute(
                    text("""
                        SELECT COUNT(*) FROM conversationmessages
                        WHERE conversationid = :conversation_id
                    """),
                    {"conversation_id": conversation_id},
                )
                total_count = count_result.scalar()

                # Get paginated messages
                offset = (page_number - 1) * page_size
                result = await session.execute(
                    text("""
                        SELECT * FROM conversationmessages
                        WHERE conversationid = :conversation_id
                        ORDER BY createddate DESC
                        LIMIT :page_size OFFSET :offset
                    """),
                    {
                        "conversation_id": conversation_id,
                        "page_size": page_size,
                        "offset": offset,
                    },
                )
                rows = result.mappings().all()

                messages_list: List[ConversationMessages] = []
                for row in rows:
                    message_dto = ConversationMessages(
                        Id=row["id"],
                        Conversationid=row.get("conversationid"),
                        Messagetype=row.get("messagetype"),
                        Messagetext=row.get("messagetext"),
                        Mediatype=row.get("mediatype"),
                        Mediaurl=row.get("mediaurl"),
                        Responsesource=row.get("responsesource"),
                        Voicetypeid=row.get("voicetypeid"),
                        Checkpointers=row.get("checkpointers"),
                        State=row.get("state"),
                        Status=row.get("status"),
                        Createddate=row.get("createddate"),
                        Createdby=row.get("createdby"),
                    )
                    messages_list.append(message_dto)

                response.Success = True
                response.Message = "Conversation messages fetched successfully."
                response.Data = messages_list

                # Pagination metadata
                response.totalCount = total_count
                response.PageNo = page_number
                response.pageSize = page_size

        except Exception as ex:
            logger.error(f"Error fetching conversation messages: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching messages: {str(ex)}"
            response.Data = None

        return response


    # Get Response