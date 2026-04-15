"""Bot Special Training router"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.bot.bot_column_training_service_models import (
    BotSpecialTrainingCreate,
    BotSpecialTrainingUpdate,
    BotSpecialTrainingList,
)
from services.bot.bot_special_training_service import BotSpecialTrainingService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/BotColumnTraining",
    tags=["BotSpecialTraining"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetSpecialTrainingList", response_model=ApiResult)
async def get_special_training_list(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get special training list.

    Returns:
        ApiResult: List of special training data
    """
    try:
        bot_special_training_service = BotSpecialTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_special_training_service.get_special_training_list()

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
        logger.error(f"Error occurred while fetching special training list: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetSpecialTrainingById", response_model=ApiResult)
async def get_special_training_by_id(
    request: Request,
    training_id: str = Query(..., description="Training ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get special training detail by training ID.

    Args:
        training_id: Training ID

    Returns:
        ApiResult: Special training detail
    """
    try:
        bot_special_training_service = BotSpecialTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_special_training_service.get_special_training_by_training_id(training_id)

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
        logger.error(f"Error occurred while fetching special training by ID: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateSpecialTraining", response_model=ApiResult)
async def create_special_training(
    request: Request,
    training: BotSpecialTrainingCreate,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create special training.

    Args:
        training: Special training data

    Returns:
        ApiResult: Creation status
    """
    try:
        bot_special_training_service = BotSpecialTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_special_training_service.create_special_training(training)

        if response.Status != 0:
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
        logger.error(f"Error occurred while creating special training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/UpdateSpecialTraining", response_model=ApiResult)
async def update_special_training(
    request: Request,
    training: BotSpecialTrainingUpdate,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update special training.

    Args:
        training: Special training data

    Returns:
        ApiResult: Update status
    """
    try:
        bot_special_training_service = BotSpecialTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_special_training_service.update_special_training(training)

        if response.Status != 0:
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
        logger.error(f"Error occurred while updating special training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("/DeleteSpecialTraining", response_model=ApiResult)
async def delete_special_training(
    request: Request,
    training_id: str = Query(..., description="Training ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete special training.

    Args:
        training_id: Training ID

    Returns:
        ApiResult: Deletion status
    """
    try:
        bot_special_training_service = BotSpecialTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_special_training_service.delete_special_training(training_id)

        if response.Status != 0:
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
        logger.error(f"Error occurred while deleting special training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
