"""Database tables router - Python implementation of DatabasetablesController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.database_table.database_table_service_model import (
    CreateDatabaseTableRole,
)
from services.database_table.database_table_service import DatabasetableService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Databasetables",
    tags=["Databasetables"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_databasetables(
    request: Request,
    connection_id: int = Query(..., description="Connection ID", alias="connectionId"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active database tables.
    
    Args:
        connection_id: Connection ID to filter database tables
        
    Returns:
        ApiResult: List of database tables
    """
    try:
        databasetable_service = DatabasetableService(client_id=client_id, user_id=user_id)
        databasetables = await databasetable_service.get_all_databasetables_async(connection_id)

        if not databasetables.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=databasetables.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=databasetables.Message,
            Result=databasetables.Data,
        )
    except Exception as e:
        logger.error(f"Error occurred while getting all database tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("/GetDatabaseTableById", response_model=ApiResult)
async def get_databasetable_by_id(
    request: Request,
    id: int = Query(..., description="Database table ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific database table by ID.
    
    Args:
        id: Database table ID
        
    Returns:
        ApiResult: Database table details
    """
    try:
        databasetable_service = DatabasetableService(client_id=client_id, user_id=user_id)
        databasetable = await databasetable_service.get_databasetable_by_id_async(id)

        if not databasetable.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=databasetable.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=databasetable.Message,
            Result=databasetable.Data,
        )
    except Exception as e:
        logger.error(f"Error occurred while getting database table with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("/GetDatabaseTables", response_model=ApiResult)
async def get_database_tables(
    request: Request,
    connection_id: int = Query(..., description="Connection ID", alias="connectionId"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get database tables as simple entities.
    
    Args:
        connection_id: Connection ID to filter database tables
        
    Returns:
        ApiResult: List of database table entities
    """
    try:
        databasetable_service = DatabasetableService(client_id=client_id, user_id=user_id)
        response = await databasetable_service.get_database_tables_async(connection_id)

        if not response.Success:
            return ApiResult(
                Success=False,
                Message=response.Message,
                StatusCode=1,
            )

        return ApiResult(
            Success=True,
            Message=response.Message,
            Result=response.Data,
            StatusCode=0,
        )
    except Exception as e:
        logger.error(f"Error occurred while getting all tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("/GetDatabaseTableRoleMap", response_model=ApiResult)
async def get_database_table_role_map(
    request: Request,
    databasetableid: int = Query(..., description="Database table ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get role mappings for a database table.
    
    Args:
        databasetableid: Database table ID
        
    Returns:
        ApiResult: List of role mappings
    """
    try:
        databasetable_service = DatabasetableService(client_id=client_id, user_id=user_id)
        response = await databasetable_service.get_database_table_map_list_async(databasetableid)

        if not response.Success:
            return ApiResult(
                Success=False,
                StatusCode=1,
                Message=response.Message,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as e:
        logger.error(f"Error occurred while getting database table role map: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("/CreateDatabaseTableRoleMap", response_model=ApiResult)
async def create_database_table_role_map(
    request: Request,
    create_table_role_map: CreateDatabaseTableRole,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create or update database table role mappings.
    
    Args:
        create_table_role_map: Role mapping details
        
    Returns:
        ApiResult: Success status
    """
    try:
        databasetable_service = DatabasetableService(client_id=client_id, user_id=user_id)
        created_database_role = await databasetable_service.create_database_table_role_map_async(create_table_role_map)

        if created_database_role.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=created_database_role.Message,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=created_database_role.Message,
        )
    except Exception as e:
        logger.error(f"Error occurred while creating database table role map: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        ) from e
