"""Bot Column Training router - Python implementation of BotColumnTrainingController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.bot.bot_column_training_service_models import (
    BotColumnTrainingCreate,
    BotColumnTrainingUpdate,
)
from services.bot.bot_column_training_service import BotColumnTrainingService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/BotColumnTraining",
    tags=["BotColumnTraining"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetColumnTrainingList", response_model=ApiResult)
async def get_column_training_list(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get column training list.

    Returns:
        ApiResult: List of column training data
    """
    try:
        bot_column_training_service = BotColumnTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_column_training_service.get_column_training_list()

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while fetching column training list: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetColumnTrainingById", response_model=ApiResult)
async def get_column_training_by_id(
    request: Request,
    training_id: str = Query(..., description="Training ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get column training detail by training ID.

    Args:
        training_id: Training ID

    Returns:
        ApiResult: Column training detail
    """
    try:
        bot_column_training_service = BotColumnTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_column_training_service.get_column_training_by_training_id(training_id)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while fetching column training by ID: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateColumnTraining", response_model=ApiResult)
async def create_column_training(
    request: Request,
    training: BotColumnTrainingCreate,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create column training.

    Args:
        training: Column training data

    Returns:
        ApiResult: Creation status
    """
    try:
        bot_column_training_service = BotColumnTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_column_training_service.create_column_training(training)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=response.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while creating column training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/UpdateColumnTraining", response_model=ApiResult)
async def update_column_training(
    request: Request,
    training: BotColumnTrainingUpdate,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update column training.

    Args:
        training: Column training data

    Returns:
        ApiResult: Update status
    """
    try:
        bot_column_training_service = BotColumnTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_column_training_service.update_column_training(training)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=response.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while updating column training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("/DeleteColumnTraining", response_model=ApiResult)
async def delete_column_training(
    request: Request,
    training_id: str = Query(..., description="Training ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete column training.

    Args:
        training_id: Training ID

    Returns:
        ApiResult: Deletion status
    """
    try:
        bot_column_training_service = BotColumnTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_column_training_service.delete_training(training_id)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=response.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while deleting column training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
