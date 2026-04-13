"""Database table columns router - Python implementation of DatabasetablescolumnsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from services.database_table.database_tables_columns_service import DatabasetablescolumnService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Databasetablescolumns",
    tags=["DatabaseTableColumns"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_databasetablescolumns(
    request: Request,
    table_id: int = Query(..., description="Table ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get all active database table columns for a specific table.

    Args:
        table_id: Table ID

    Returns:
        ApiResult: List of database table columns
    """
    try:
        databasetablescolumn_service = DatabasetablescolumnService(
            client_id=client_id, user_id=user_id
        )
        response = await databasetablescolumn_service.get_all_database_tables_column_async(
            table_id
        )

        if not response.Success:
            return ApiResult(
                Success=False,
                Message=response.Message,
                StatusCode=1,
                Result=None,
            )

        return ApiResult(
            Success=True,
            Message=response.Message,
            StatusCode=0,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting all columns for table ID {table_id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        ) from ex


@router.get("/GetDatabaseTableColumnById", response_model=ApiResult)
async def get_database_table_column_by_id(
    request: Request,
    id: int = Query(..., description="Database table column ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get a specific database table column by ID.

    Args:
        id: Database table column ID

    Returns:
        ApiResult: Database table column details
    """
    try:
        databasetablescolumn_service = DatabasetablescolumnService(
            client_id=client_id, user_id=user_id
        )
        response = await databasetablescolumn_service.get_databasetables_column_by_id_async(
            id
        )

        if not response.Success:
            return ApiResult(
                Success=False,
                Message=response.Message,
                StatusCode=1,
                Result=None,
            )

        return ApiResult(
            Success=True,
            Message=response.Message,
            StatusCode=0,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting database table column with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        ) from ex
