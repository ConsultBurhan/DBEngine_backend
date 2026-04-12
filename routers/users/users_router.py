"""Users router - Python implementation of C# UsersController."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id
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
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Get all active users with associated role IDs.
    
    Returns:
        ApiResult: List of users with comma-separated role IDs
    """
    try:
        user_service = UserService(request)
        result = await user_service.get_all_users_async()

        if not result.success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.message,
            Result=result.data
        )
        
    except Exception as e:
        logger.error(f"Error occurred while getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("", response_model=ApiResult)
async def get_user(
    request: Request,
    id: int = Query(..., description="User ID"),
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Get a specific user by ID with associated role IDs.
    
    Args:
        id: User ID
        
    Returns:
        ApiResult: User details with comma-separated role IDs
    """
    try:
        user_service = UserService(request)
        result = await user_service.get_user_by_id_async(id)

        if not result.success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.message,
            Result=result.data
        )
        
    except Exception as e:
        logger.error(f"Error occurred while getting user with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.post("", response_model=ApiResult)
async def create_user(
    request: Request,
    user_dto: CreateUser,
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Create a new user with associated role IDs.
    
    Args:
        user_dto: User details with password and comma-separated role IDs in roles_id field
        
    Returns:
        ApiResult: Created user status
    """
    try:
        user_service = UserService(request)
        created_user = await user_service.create_user_async(user_dto)

        if created_user.status != 0:
            return ApiResult(
                StatusCode=created_user.status,
                Success=False,
                Message=created_user.message,
                Result=None
            )

        return ApiResult(
            StatusCode=created_user.status,
            Success=True,
            Message=created_user.message,
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
    request: Request,
    user_dto: UpdateUser,
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Update an existing user with associated role IDs (password not updated).
    
    Args:
        user_dto: Updated user details with comma-separated role IDs in roles_id field
        
    Returns:
        ApiResult: Updated user status
    """
    try:
        user_service = UserService(request)
        updated_user = await user_service.update_user_async(user_dto)

        if updated_user.status == 1:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=updated_user.message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=updated_user.message,
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
    request: Request,
    user_dto: UpdateUserLanguage,
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Update user's preferred language.
    
    Args:
        user_dto: User language update details
        
    Returns:
        ApiResult: Update status
    """
    try:
        user_service = UserService(request)
        updated_user_lang = await user_service.update_user_prefered_language(user_dto)

        if updated_user_lang.status == 1:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=updated_user_lang.message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=updated_user_lang.message,
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
    request: Request,
    id: int = Query(..., description="User ID"),
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Delete a user (soft delete) and remove all role associations.
    
    Args:
        id: User ID
        
    Returns:
        ApiResult: Success status
    """
    try:
        user_service = UserService(request)
        result = await user_service.delete_user_async(id)

        if result.status == 1:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.message,
                Result=None
            )
        
        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=result.message,
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
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
) -> UserWithRoles:
    """
    Get current user profile (requires authentication).
    
    Returns:
        UserWithRoles: Current user information
    """
    try:
        user_service = UserService(request)
        result = await user_service.get_user_by_id_async(current_user_id)
        
        if not result.success or result.data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred while getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e