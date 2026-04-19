"""Retraining router - Python implementation of RetrainingController."""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Path
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.retraining.retraining_service_models import (
    CreateBottrainingmap,
    UpdateBottrainingmap,
)
from services.retraining.retraining_service import RetrainingService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Retraining",
    tags=["Retraining"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=ApiResult)
async def create(
    request: Request,
    entity: CreateBottrainingmap,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new bot training map.

    Args:
        entity: Bot training map data

    Returns:
        ApiResult: Created bot training map
    """
    try:
        retraining_service = RetrainingService(client_id=client_id, user_id=user_id)
        response = await retraining_service.create_async(entity)

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
        logger.error(f"Error occurred while creating bot training map: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("{id}", response_model=ApiResult)
async def get_by_id(
    request: Request,
    id: int = Path(..., description="Bot Training map Id"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get a bot training map by ID.

    Args:
        id: Bot training map ID

    Returns:
        ApiResult: Bot training map details
    """
    try:
        retraining_service = RetrainingService(client_id=client_id, user_id=user_id)
        response = await retraining_service.get_by_id_async(id)

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
        logger.error(f"Error occurred while getting bot training map with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/bot/{botId}/{clientId}", response_model=ApiResult)
async def get_by_bot(
    request: Request,
    botId: int = Path(..., description="Bot ID"),
    clientId: str = Path(..., description="Client ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get bot training maps by bot ID and client ID.

    Args:
        botId: Bot ID
        clientId: Client ID

    Returns:
        ApiResult: List of bot training maps
    """
    try:
        retraining_service = RetrainingService(client_id=client_id, user_id=user_id)
        response = await retraining_service.get_by_bot_async(botId, clientId)

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
        logger.error(f"Error occurred while getting bot training maps by bot ID {botId}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("", response_model=ApiResult)
async def update(
    request: Request,
    entity: UpdateBottrainingmap,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update an existing bot training map.

    Args:
        entity: Bot training map data to update

    Returns:
        ApiResult: Update status
    """
    try:
        retraining_service = RetrainingService(client_id=client_id, user_id=user_id)
        response = await retraining_service.update_async(entity)

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
        logger.error(f"Error occurred while updating bot training map: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("/{id}", response_model=ApiResult)
async def delete(
    request: Request,
    id: int = Path(..., description="Training Map Id"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete a bot training map (soft delete).

    Args:
        id: Bot training map ID

    Returns:
        ApiResult: Delete status
    """
    try:
        retraining_service = RetrainingService(client_id=client_id, user_id=user_id)
        response = await retraining_service.delete_async(id)

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
        logger.error(f"Error occurred while deleting bot training map with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
