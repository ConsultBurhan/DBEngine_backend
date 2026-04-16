"""Dbtypes router - Python implementation of C# DbtypesController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.dbtypes.dbtypes_service_models import (
    DbtypesCreate,
    DbtypesList,
    DbtypesUpdate,
)
from services.dbtypes.dbtypes_service import DbtypeService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/dbtypes",
    tags=["Dbtypes"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_dbtypes(
    request: Request,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active database types.

    Returns:
        ApiResult: List of database types
    """
    try:
        dbtype_service = DbtypeService(client_id=client_id, user_id=user_id)
        response = await dbtype_service.get_all_dbtypes_async()

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
        logger.error(f"Error occurred while getting all database types: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetDbtypeById", response_model=ApiResult)
async def get_dbtype_by_id(
    request: Request,
    id: int = Query(..., description="Database type ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific database type by ID.

    Args:
        id: Database type ID

    Returns:
        ApiResult: Database type details
    """
    try:
        dbtype_service = DbtypeService(client_id=client_id, user_id=user_id)
        response = await dbtype_service.get_dbtype_by_id_async(id)

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
        logger.error(f"Error occurred while getting database type with ID {id}: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("", response_model=ApiResult)
async def create_dbtype(
    request: Request,
    create_dto: DbtypesCreate,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new database type.

    Args:
        create_dto: Database type details

    Returns:
        ApiResult: Created database type status
    """
    try:
        dbtype_service = DbtypeService(client_id=client_id, user_id=user_id)
        result = await dbtype_service.create_dbtype_async(create_dto)

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
        logger.error(f"Error occurred while creating database type: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("", response_model=ApiResult)
async def update_dbtype(
    request: Request,
    update_dto: DbtypesUpdate,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing database type.

    Args:
        update_dto: Updated database type details

    Returns:
        ApiResult: Updated database type status
    """
    try:
        dbtype_service = DbtypeService(client_id=client_id, user_id=user_id)
        result = await dbtype_service.update_dbtype_async(update_dto)

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
        logger.error(f"Error occurred while updating database type with ID {update_dto.Id}: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("", response_model=ApiResult)
async def delete_dbtype(
    request: Request,
    id: int = Query(..., description="Database type ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a database type (soft delete).

    Args:
        id: Database type ID

    Returns:
        ApiResult: Success status
    """
    try:
        dbtype_service = DbtypeService(client_id=client_id, user_id=user_id)
        result = await dbtype_service.delete_dbtype_async(id)

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
        logger.error(f"Error occurred while deleting database type with ID {id}: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
