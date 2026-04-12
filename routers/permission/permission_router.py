"""Permissions router - Python implementation of C# PermissionsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.permission.permission_service_models import SavePermissions
from services.permissions.permission_service import PermissionService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/permissions",
    tags=["Permissions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/SavePermissions", response_model=ApiResult)
async def save_permission_by_role(
    request: Request,
    permission_dto: SavePermissions,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Save permissions for a role.
    Removes existing permissions and creates new ones.
    
    Args:
        permission_dto: Permission details with role ID and permission list
        
    Returns:
        ApiResult: Success status
    """
    try:
        permission_service = PermissionService(user_id=user_id)
        result = await permission_service.save_permission_by_role_async(permission_dto)

        if result.status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.Message,
            Result=None
        )
    except Exception as e:
        logger.error(f"Error occurred while saving permissions for role {permission_dto.RoleId}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("", response_model=ApiResult)
async def get_permissions_list(
    request: Request,
    role_id: int = Query(..., description="Role ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all permissions for a specific role.
    
    Args:
        role_id: Role ID
        
    Returns:
        ApiResult: List of permissions for the role
    """
    try:
        permission_service = PermissionService(user_id=user_id)
        result = await permission_service.get_permissions_list_async(role_id)

        if not result.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.Message,
            Result=result.Data
        )
    except Exception as e:
        logger.error(f"Error occurred while getting permissions for role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e
