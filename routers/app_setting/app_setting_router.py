"""App settings router - Python implementation of AppsettingsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.app_settings.app_settings_service_models import AppSetting, AppsettingCreate
from services.app_settings.app_settings_service import AppSettingsService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Appsettings",
    tags=["Appsettings"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_appsettings(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get all active app settings.

    Returns:
        ApiResult: List of app settings
    """
    try:
        appsettings_service = AppSettingsService(client_id=client_id, user_id=user_id)
        response = await appsettings_service.get_all_appsettings_async()

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
        logger.error(f"Error occurred while getting all app settings: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetAppsettingById", response_model=ApiResult)
async def get_appsetting_by_id(
    request: Request,
    id: int = Query(..., description="App setting ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get a specific app setting by ID.

    Args:
        id: App setting ID

    Returns:
        ApiResult: App setting details
    """
    try:
        appsettings_service = AppSettingsService(client_id=client_id, user_id=user_id)
        response = await appsettings_service.get_appsetting_by_id_async(id)

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
        logger.error(f"Error occurred while getting app setting with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("", response_model=ApiResult)
async def create_appsetting(
    request: Request,
    appsetting: AppsettingCreate,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new app setting.

    Args:
        appsetting: App setting details

    Returns:
        ApiResult: Created app setting status
    """
    try:
        appsettings_service = AppSettingsService(client_id=client_id, user_id=user_id)
        result = await appsettings_service.create_appsetting_async(appsetting)

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
        logger.error(f"Error occurred while creating app setting: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("", response_model=ApiResult)
async def update_appsetting(
    request: Request,
    appsetting: AppSetting,
    id: int = Query(..., description="App setting ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update an existing app setting.

    Args:
        id: App setting ID
        appsetting: Updated app setting details

    Returns:
        ApiResult: Updated app setting
    """
    try:
        appsettings_service = AppSettingsService(client_id=client_id, user_id=user_id)
        response = await appsettings_service.update_appsetting_async(id, appsetting)

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
        logger.error(f"Error occurred while updating app setting with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("", response_model=ApiResult)
async def delete_appsetting(
    request: Request,
    id: int = Query(..., description="App setting ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete an app setting (soft delete).

    Args:
        id: App setting ID

    Returns:
        ApiResult: Success status
    """
    try:
        appsettings_service = AppSettingsService(client_id=client_id, user_id=user_id)
        result = await appsettings_service.delete_appsetting_async(id)

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
        logger.error(f"Error occurred while deleting app setting with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
