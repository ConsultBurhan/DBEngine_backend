"""Conversation service for managing conversation operations."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import httpx
from fastapi import Request
from sqlalchemy import text
from dotenv import load_dotenv
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

load_dotenv()

logger = get_logger(__name__)
# DB Bot configuration from environment variables
DB_BOT_BASE_URL = os.getenv("DB_BOT_BASE_URL")
DB_BOT_API_KEY = os.getenv("DB_BOT_API_KEY")
DB_BOT_TIMEOUT_SECONDS = int(os.getenv("DB_BOT_TIMEOUT_SECONDS", "300"))

# Validate DB bot configuration
if not DB_BOT_BASE_URL:
    raise ValueError("DB_BOT_BASE_URL environment variable is not set")
if not DB_BOT_API_KEY:
    raise ValueError("DB_BOT_API_KEY environment variable is not set")



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

    async def stream_response_async(
        self,
        request_dto: GetResponse,
    ) -> AsyncGenerator[bytes, None]:
        """Stream response from external API with SSE format.
        
        Creates conversation if needed, saves user message, streams tokens from
        external API, saves bot response, and yields SSE events.
        """
        full_response_builder: List[str] = []
        conversation_id = request_dto.ConversationId or 0

        try:
            async with await self._db_manager.get_session() as session:
                # Create new conversation if needed
                if conversation_id == 0:
                    title = request_dto.MessageText
                    if title and len(title) > 50:
                        title = title[:50]
                    
                    # Insert conversation using raw SQL
                    result = await session.execute(
                        text("""
                            INSERT INTO conversations
                                (clientid, botid, userid, status, title, createddate, createdby)
                            VALUES
                                (:clientid, :botid, :userid, :status, :title, :createddate, :createdby)
                            RETURNING id
                        """),
                        {
                            "clientid": self.client_id,
                            "botid": request_dto.BotId,
                            "userid": self.user_id,
                            "status": "Active",
                            "title": title,
                            "createddate": datetime.now(),
                            "createdby": str(self.user_id),
                        }
                    )
                    conversation_id = result.scalar()
                    request_dto.ConversationId = conversation_id

                # Save USER message (type "1" = user)
                sent_msg_result = await session.execute(
                    text("""
                        INSERT INTO conversationmessages
                            (conversationid, messagetype, messagetext, orignaltext, createddate, createdby)
                        VALUES
                            (:conversationid, :messagetype, :messagetext, :orignaltext, :createddate, :createdby)
                        RETURNING id
                    """),
                    {
                        "conversationid": conversation_id,
                        "messagetype": "1",
                        "messagetext": request_dto.MessageText,
                        "orignaltext": request_dto.MessageText,
                        "createddate": datetime.now(),
                        "createdby": str(self.user_id),
                    }
                )
                sent_msg_id = sent_msg_result.scalar()

                final_event: Optional[StreamingEvent] = None

                # Stream from external API
                async for event in self._call_external_api_async(request_dto):
                    # Serialize and yield SSE event
                    json_data = json.dumps(event.model_dump(exclude_none=True))
                    sse_bytes = f"data: {json_data}\n\n".encode("utf-8")
                    yield sse_bytes

                    # Collect tokens for full response
                    if event.event == "token" and event.Data and event.Data.Message:
                        full_response_builder.append(event.Data.Message)

                    # Capture final event
                    if event.event == "final":
                        final_event = event

                # Determine final response text
                final_response = ""
                if final_event and final_event.Data:
                    final_response = json.dumps(
                        final_event.Data.model_dump(exclude_none=True),
                        indent=2
                    )

                # Save BOT message (type "2" = bot)
                recv_msg_result = await session.execute(
                    text("""
                        INSERT INTO conversationmessages
                            (conversationid, messagetype, messagetext, orignaltext, createddate, createdby)
                        VALUES
                            (:conversationid, :messagetype, :messagetext, :orignaltext, :createddate, :createdby)
                        RETURNING id
                    """),
                    {
                        "conversationid": conversation_id,
                        "messagetype": "2",
                        "messagetext": final_response,
                        "orignaltext": final_response,
                        "createddate": datetime.now(),
                        "createdby": str(self.user_id),
                    }
                )
                recv_msg_id = recv_msg_result.scalar()

                # Update conversation with raw SQL
                await session.execute(
                    text("""
                        UPDATE conversations
                        SET
                            lastmessage = :lastmessage,
                            updateddate = :updateddate,
                            messagecount = (
                                SELECT COUNT(*) FROM conversationmessages
                                WHERE conversationid = :conversation_id
                            )
                        WHERE id = :conversation_id
                    """),
                    {
                        "lastmessage": final_response,
                        "updateddate": datetime.now(),
                        "conversation_id": conversation_id,
                    }
                )

                await session.commit()

                # Send DONE event
                done_event = {
                    "eventType": "done",
                    "conversationId": conversation_id,
                    "sentMessageId": sent_msg_id,
                    "receivedMessageId": recv_msg_id,
                }
                done_bytes = f"data: {json.dumps(done_event)}\n\n".encode("utf-8")
                yield done_bytes

        except Exception as ex:
            logger.error(f"Error in stream_response_async: {ex}")
            error_event = {
                "event": "error",
                "Content": str(ex),
            }
            error_bytes = f"data: {json.dumps(error_event)}\n\n".encode("utf-8")
            yield error_bytes

    async def _call_external_api_async(
        self,
        request_dto: GetResponse,
    ) -> AsyncGenerator[StreamingEvent, None]:
        """Call external streaming API and yield events.
        
        Parses SSE format from external API and yields StreamingEvent objects.
        """
        try:
            external_api_url = f"{DB_BOT_BASE_URL}/workflow/execute/stream"

            request_body = {
                "user_query": request_dto.MessageText,
                "bot_id": request_dto.BotId,
                "role_id": 1,
                "user_id": self.user_id,
                "client_id": self.client_id,
                "thread_id": str(request_dto.ConversationId or "0"),
            }

            async with httpx.AsyncClient(timeout=DB_BOT_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    external_api_url,
                    json=request_body,
                    headers={"X-API-Key": DB_BOT_API_KEY, "Content-Type": "application/json"},
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield StreamingEvent(
                            event="error",
                            Content=error_text.decode("utf-8"),
                        )
                        return

                    current_event: Optional[str] = None

                    async for line in response.aiter_lines():
                        if not line or not line.strip():
                            continue

                        if line.startswith("event:"):
                            current_event = line[6:].strip()
                            continue

                        if not line.startswith("data:"):
                            continue

                        data_payload = line[5:].strip()
                        if not data_payload:
                            continue

                        try:
                            external_data = StreamingEventData.model_validate_json(data_payload)
                        except Exception as ex:
                            logger.warning(f"Failed to deserialize SSE payload: {data_payload}, error: {ex}")
                            continue

                        internal_event = StreamingEvent(
                            event=current_event or "message",
                            Data=external_data,
                        )

                        yield internal_event

                        if current_event in ("final", "done"):
                            break

        except Exception as ex:
            logger.error(f"External streaming API failed: {ex}")
            yield StreamingEvent(
                event="error",
                Content=str(ex),
            )