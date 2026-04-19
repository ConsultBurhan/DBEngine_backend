"""Database connections router - Python implementation of DatabaseconnectionsController."""

from os import path
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Path
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.database_connections.database_connections_service_models import (
    CreateDatabaseConnection,
    UpdateDatabaseConnection,
)
from services.database_connection.database_connection_service import DatabaseconnectionService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Databaseconnections",
    tags=["Database Connections"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_databaseconnections(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get all active database connections.

    Returns:
        ApiResult: List of database connections
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        response = await db_service.get_all_databaseconnections_async()

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
        logger.error(f"Error occurred while getting all database connections: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetDatabaseConnectionById", response_model=ApiResult)
async def get_databaseconnection_by_id(
    request: Request,
    id: int = Query(..., description="Database connection ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get a specific database connection by ID.

    Args:
        id: Database connection ID

    Returns:
        ApiResult: Database connection details
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        response = await db_service.get_database_connection_by_id_async(id)

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
        logger.error(f"Error occurred while getting database connection with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("", response_model=ApiResult)
async def create_databaseconnection(
    request: Request,
    create_dto: CreateDatabaseConnection,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new database connection.

    Args:
        create_dto: Database connection details

    Returns:
        ApiResult: Created database connection status
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        result = await db_service.create_database_connection_async(create_dto)

        if not result.Status != 0:
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
        )
    except Exception as ex:
        logger.error(f"Error occurred while creating database connection: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("", response_model=ApiResult)
async def update_databaseconnection(
    request: Request,
    update_dto: UpdateDatabaseConnection,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update an existing database connection.

    Args:
        update_dto: Updated database connection details

    Returns:
        ApiResult: Updated database connection status
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        result = await db_service.update_database_connection_async(update_dto)

        if not result.Status != 0:
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
        )
    except Exception as ex:
        logger.error(f"Error occurred while updating database connection with ID {update_dto.Id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("/RefreshDatabaseSchema", response_model=ApiResult)
async def refresh_database_schema(
    request: Request,
    connection_id: int = Query(..., description="Database connection ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Refresh database schema (tables and columns) for a connection.

    Args:
        connection_id: Database connection ID

    Returns:
        ApiResult: Refresh status
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        result = await db_service.refresh_database_schema_async(connection_id)

        if not result.Status != 0:
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
        )
    except Exception as ex:
        logger.error(f"Error occurred while refreshing database schema with ID {connection_id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("", response_model=ApiResult)
async def delete_databaseconnection(
    request: Request,
    id: int = Query(..., description="Database connection ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete a database connection (soft delete).

    Args:
        id: Database connection ID

    Returns:
        ApiResult: Success status
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        result = await db_service.delete_database_connection_async(id)

        if not result.Status != 0:
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
        )
    except Exception as ex:
        logger.error(f"Error occurred while deleting database connection with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetDatabaseConnetion", response_model=ApiResult)
async def get_database_connection(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get simplified list of database connections (id and name only) for dropdown.

    Returns:
        ApiResult: List of connection entities containing id and name
    """
    try:
        db_service = DatabaseconnectionService(client_id=client_id, user_id=user_id)
        response = await db_service.get_database_connections_async()

        if not response.Success:
            return ApiResult(
                StatusCode=0,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=1,
            Success=True,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting database connections: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
