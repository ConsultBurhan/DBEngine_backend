"""Bot response rating router - Python implementation of BotResponseRatingController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus
from pydantic import BaseModel

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.bot.bot_response_rating_service_models import CreateBotResponseRating
from services.bot.bot_response_rating_service import BotResponseRatingService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/BotResponseRating",
    tags=["BotResponseRating"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_bot_response_rating_list(
    request: Request,
    bot_id: int = Query(..., description="Bot ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get bot response ratings for a specific bot.

    Args:
        bot_id: Bot ID

    Returns:
        ApiResult: List of bot response ratings
    """
    try:
        bot_response_rating_service = BotResponseRatingService(client_id=client_id, user_id=user_id)
        result = await bot_response_rating_service.get_bot_response_rating_list_async(bot_id)

        if not result.Success:
            return ApiResult(
                Success=False,
                StatusCode=1,
                Message=result.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=result.Message,
            Result=result.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while fetching ratings: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("", response_model=ApiResult)
async def create_bot_response_rating(
    request: Request,
    create_response: CreateBotResponseRating,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new bot response rating.

    Args:
        create_response: Bot response rating data

    Returns:
        ApiResult: Creation status
    """
    try:
        bot_response_rating_service = BotResponseRatingService(client_id=client_id, user_id=user_id)
        result = await bot_response_rating_service.create_bot_response_rating_async(create_response)

        if result.Status != 0:
            return ApiResult(
                Success=False,
                StatusCode=1,
                Message=result.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=result.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while creating ratings: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
