"""Roles router - Python implementation of C# RolesController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.roles.role_service_models import (
    CreateRoleWithBots,
    UpdateRoleWithBots,
)
from services.roles.role_service import RoleService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/roles",
    tags=["Roles"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_roles(
    request: Request,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active roles with associated bot IDs.
    
    Returns:
        ApiResult: List of roles with comma-separated bot IDs
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        roles = await role_service.get_all_roles()

        if not roles.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=roles.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=roles.Message,
            Result=roles.Data
        )
    except Exception as e:
        logger.error(f"Error occurred while getting all roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("/GetRoleById", response_model=ApiResult)
async def get_role_by_id(
    request: Request,
    id: int = Query(..., description="Role ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific role by ID with associated bot IDs.
    
    Args:
        id: Role ID
        
    Returns:
        ApiResult: Role details with comma-separated bot IDs
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        role = await role_service.get_role_by_id(id)

        if not role.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=role.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=role.Message,
            Result=role.Data
        )
    except Exception as e:
        logger.error(f"Error occurred while getting role with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("", response_model=ApiResult)
async def create_role(
    request: Request,
    create_dto: CreateRoleWithBots,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new role with associated bot IDs.
    
    Args:
        create_dto: Role details with comma-separated bot IDs in bots_id field
        
    Returns:
        ApiResult: Created role status
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        created_role = await role_service.create_role(create_dto)

        if created_role.Status != 0:
            return ApiResult(
                StatusCode=created_role.Status,
                Success=False,
                Message=created_role.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=created_role.Message,
            Result=None
        )
    except Exception as e:
        logger.error(f"Error occurred while creating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.put("", response_model=ApiResult)
async def update_role(
    request: Request,
    update_dto: UpdateRoleWithBots,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing role with associated bot IDs.
    
    Args:
        update_dto: Updated role details with comma-separated bot IDs in bots_id field
        
    Returns:
        ApiResult: Updated role status
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        updated_role = await role_service.update_role(update_dto)

        if updated_role.Status != 0:
            return ApiResult(
                StatusCode=updated_role.Status,
                Success=False,
                Message=updated_role.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=updated_role.Message,
            Result=None
        )
    except Exception as e:
        logger.error(f"Error occurred while updating role with ID {update_dto.Id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.delete("", response_model=ApiResult)
async def delete_role(
    request: Request,
    id: int = Query(..., description="Role ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a role (soft delete) and remove all bot associations.
    
    Args:
        id: Role ID
        
    Returns:
        ApiResult: Success status
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        result = await role_service.delete_role(id)

        if result.Status != 0:
            return ApiResult(
                StatusCode=result.Status,
                Success=False,
                Message=result.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.Message,
            Result=None
        )
    except Exception as e:
        logger.error(f"Error occurred while deleting role with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("/GetRoles", response_model=ApiResult)
async def get_roles(
    request: Request,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get simplified list of active roles.
    
    Returns:
        ApiResult: List of simplified roles (id, name only)
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        roles = await role_service.get_roles()

        if not roles.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=roles.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=roles.Message,
            Result=roles.Data
        )
    except Exception as e:
        logger.error(f"Error occurred while getting all roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("/GetRolesByBotId", response_model=ApiResult)
async def get_roles_by_bot_id(
    request: Request,
    bot_id: int = Query(..., description="Bot ID", alias="botId"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get roles associated with a specific bot ID.
    
    Args:
        bot_id: Bot ID
        
    Returns:
        ApiResult: List of roles associated with the bot
    """
    try:
        role_service = RoleService(client_id=client_id, user_id=user_id)
        roles = await role_service.get_roles_by_bot_id(bot_id)

        if not roles.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=roles.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=roles.Message,
            Result=roles.Data
        )
    except Exception as e:
        logger.error(f"Error occurred while getting roles by bot ID {bot_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e
