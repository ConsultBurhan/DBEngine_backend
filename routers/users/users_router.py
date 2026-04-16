"""Users router - Python implementation of C# UsersController."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id, get_subscriber_id
from models.common import ApiResult
from models.service_models.user.user_service_models import (
    CreateUser,
    UpdateUser,
    UpdateUserLanguage,
    UserWithRoles,
)
from services.user.user_service import UserService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllUsers", response_model=ApiResult)
async def get_all_users(
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> ApiResult:
    """
    Get all active users with associated role IDs.
    
    Returns:
        ApiResult: List of users with comma-separated role IDs
    """
    try:
        user_service = UserService(client_id, user_id, subscriber_id)
        result = await user_service.get_all_users_async()

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
        logger.error(f"Error occurred while getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("", response_model=ApiResult)
async def get_user(
    id: int = Query(..., description="User ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> ApiResult:
    """
    Get a specific user by ID with associated role IDs.
    
    Args:
        id: User ID
        
    Returns:
        ApiResult: User details with comma-separated role IDs
    """
    try:
        user_service = UserService(client_id, user_id, subscriber_id)
        result = await user_service.get_user_by_id_async(id)

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
        logger.error(f"Error occurred while getting user with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.post("", response_model=ApiResult)
async def create_user(
    user_dto: CreateUser,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> ApiResult:
    """
    Create a new user with associated role IDs.
    
    Args:
        user_dto: User details with password and comma-separated role IDs in roles_id field
        
    Returns:
        ApiResult: Created user status
    """
    try:
        user_service = UserService(client_id, user_id, subscriber_id)
        created_user = await user_service.create_user_async(user_dto)

        if created_user.Status != 0:
            return ApiResult(
                StatusCode=created_user.Status,
                Success=False,
                Message=created_user.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=created_user.Status,
            Success=True,
            Message=created_user.Message,
            Result=None
        )
        
    except Exception as e:
        logger.error(f"Error occurred while creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.put("", response_model=ApiResult)
async def update_user(
    user_dto: UpdateUser,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> ApiResult:
    """
    Update an existing user with associated role IDs (password not updated).
    
    Args:
        user_dto: Updated user details with comma-separated role IDs in roles_id field
        
    Returns:
        ApiResult: Updated user status
    """
    try:
        user_service = UserService(client_id, user_id, subscriber_id)
        updated_user = await user_service.update_user_async(user_dto)

        if updated_user.Status == 1:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=updated_user.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=updated_user.Message,
            Result=None
        )
        
    except Exception as e:
        logger.error(f"Error occurred while updating user with ID {user_dto.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.put("/UpdateUserLanguage", response_model=ApiResult)
async def update_user_language(
    user_dto: UpdateUserLanguage,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> ApiResult:
    """
    Update user's preferred language.
    
    Args:
        user_dto: User language update details
        
    Returns:
        ApiResult: Update status
    """
    try:
        user_service = UserService(client_id, user_id, subscriber_id)
        updated_user_lang = await user_service.update_user_prefered_language(user_dto)

        if updated_user_lang.Status == 1:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=updated_user_lang.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=updated_user_lang.Message,
            Result=None
        )
        
    except Exception as e:
        logger.error(f"Error occurred while updating user language with ID {user_dto.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.delete("", response_model=ApiResult)
async def delete_user(
    id: int = Query(..., description="User ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> ApiResult:
    """
    Delete a user (soft delete) and remove all role associations.
    
    Args:
        id: User ID
        
    Returns:
        ApiResult: Success status
    """
    try:
        user_service = UserService(client_id, user_id, subscriber_id)
        result = await user_service.delete_user_async(id)

        if result.Status == 1:
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
            Result=None
        )
        
    except Exception as e:
        logger.error(f"Error occurred while deleting user with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("/profile", response_model=UserWithRoles)
async def get_profile(
    current_user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
    subscriber_id: int = Depends(get_subscriber_id)
) -> UserWithRoles:
    """
    Get current user profile (requires authentication).
    
    Returns:
        UserWithRoles: Current user information
    """
    try:
        user_service = UserService(client_id, current_user_id, subscriber_id)
        result = await user_service.get_user_by_id_async(current_user_id)
        
        if not result.Success or result.Data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return result.Data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred while getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e