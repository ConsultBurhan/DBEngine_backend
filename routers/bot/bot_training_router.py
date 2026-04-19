"""Bot trainings router - Python implementation of BotTrainingsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Path
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.bot.bot_training_service_models import (
    CreateBotDatabaseTraining,
    CreateBotGenralTraining,
    UpdateBotTraining,
)
from services.bot.bot_training_service import BotTrainingService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/BotTrainings",
    tags=["BotTrainings"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_bot_trainings(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get all active bot trainings.

    Returns:
        ApiResult: List of bot trainings
    """
    try:
        bot_training_service = BotTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_training_service.get_all_bot_trainings_async()

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
        logger.error(f"Error occurred while getting all bot trainings: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBotTrainingById", response_model=ApiResult)
async def get_bot_training_by_id(
    request: Request,
    id: int = Query(..., description="Bot training ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get a specific bot training by ID.

    Args:
        id: Bot training ID

    Returns:
        ApiResult: Bot training details
    """
    try:
        bot_training_service = BotTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_training_service.get_bot_training_by_id_async(id)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting bot training with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateBotDataBaseTraining", response_model=ApiResult)
async def create_bot_database_training(
    request: Request,
    create_bot_training: CreateBotDatabaseTraining,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new bot database training.

    Args:
        create_bot_training: Bot database training details

    Returns:
        ApiResult: Created bot training status
    """
    try:
        bot_training_service = BotTrainingService(client_id=client_id, user_id=user_id)
        result = await bot_training_service.create_bot_database_training_async(create_bot_training)

        if result.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
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
        logger.error(f"Error occurred while creating bot database training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateGenralBotTraining", response_model=ApiResult)
async def create_general_bot_training(
    request: Request,
    create_bot_training: CreateBotGenralTraining,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new bot general training.

    Args:
        create_bot_training: Bot general training details

    Returns:
        ApiResult: Created bot training status
    """
    try:
        bot_training_service = BotTrainingService(client_id=client_id, user_id=user_id)
        result = await bot_training_service.create_general_bot_training(create_bot_training)

        if result.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
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
        logger.error(f"Error occurred while creating bot general training: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("/{id}", response_model=ApiResult)
async def update_bot_training(
    request: Request,
    id: int,
    update_bot_training: UpdateBotTraining,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update an existing bot training.

    Args:
        id: Bot training ID
        update_bot_training: Updated bot training details

    Returns:
        ApiResult: Updated bot training
    """
    try:
        bot_training_service = BotTrainingService(client_id=client_id, user_id=user_id)
        response = await bot_training_service.update_bottraining_async(id, update_bot_training)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while updating bot training with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("/{id}", response_model=ApiResult)
async def delete_bot_training(
    request: Request,
    id: int,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete a bot training (soft delete).

    Args:
        id: Bot training ID

    Returns:
        ApiResult: Success status
    """
    try:
        bot_training_service = BotTrainingService(client_id=client_id, user_id=user_id)
        result = await bot_training_service.delete_bottraining_async(id)

        if result.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while deleting bot training with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
