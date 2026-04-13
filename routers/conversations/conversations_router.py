"""Conversations router - Python implementation of ConversationsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from services.conversations.conversations_service import ConversationService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Conversations",
    tags=["Conversations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/GetResponse")
async def get_response(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
):
    """
    Get response from bot with message and optional file attachment.
    Placeholder implementation - to be implemented with streaming support.

    Returns:
        Streaming response with conversation events
    """
    try:
        # Placeholder - TODO: Implement streaming response
        return ApiResult(
            Success=False,
            Message="GetResponse endpoint is not yet implemented",
            Result=None,
            StatusCode=501,
        )
    except Exception as ex:
        logger.error(f"Error occurred in GetResponse: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetUserConversations", response_model=ApiResult)
async def get_user_conversations(
    request: Request,
    userId: int = Query(..., description="User ID"),
    botId: int = Query(..., description="Bot ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get all conversations for a specific user and bot.

    Args:
        userId: User ID
        botId: Bot ID

    Returns:
        ApiResult: List of conversations
    """
    try:
        conversation_service = ConversationService(client_id=client_id, user_id=user_id)
        conversations = await conversation_service.get_user_conversation_async(userId, botId)

        if not conversations.Success:
            return ApiResult(
                Success=False,
                Message=conversations.Message,
                Result=None,
                StatusCode=1,
            )

        return ApiResult(
            Success=True,
            Message=conversations.Message,
            Result=conversations.Data,
            StatusCode=0,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting conversations for user {userId}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetConversationMessage", response_model=ApiResult)
async def get_conversation_message(
    request: Request,
    id: int = Query(..., description="Conversation ID"),
    PageNo: int = Query(1, description="Page number"),
    PageSize: int = Query(10, description="Page size"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get messages for a specific conversation with pagination.

    Args:
        id: Conversation ID
        PageNo: Page number (default 1)
        PageSize: Page size (default 10)

    Returns:
        ApiResult: List of conversation messages with pagination metadata
    """
    try:
        conversation_service = ConversationService(client_id=client_id, user_id=user_id)
        messages = await conversation_service.get_conversation_message_by_id_async(id, PageNo, PageSize)

        if not messages.Success:
            return ApiResult(
                Success=False,
                Message=messages.Message,
                Result=None,
                StatusCode=1,
            )

        return ApiResult(
            Success=True,
            Message=messages.Message,
            Result=messages.Data,
            pageSize=messages.pageSize,
            PageNo=messages.PageNo,
            totalCount=messages.totalCount,
            StatusCode=0,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting messages for conversation {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
