"""Authentication router - Python implementation of C# AuthenticationController."""

from datetime import datetime, timedelta
from tkinter.constants import S
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user
from models.common import ApiResult
from models.service_models.user.user_service_models import (
    ChangePassword,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
)
from services.authentication.authentication_service import AuthenticationService
from services.JWT.JWT_service import JWTService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/authentication",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

# JWT service instance for token generation
jwt_service = JWTService()


@router.post("/login", response_model=ApiResult)
async def login(
    login_request: LoginRequest,
) -> ApiResult:
    """
    User login with username and password.
    
    Args:
        login_request: Login credentials
        
    Returns:
        ApiResult: Access token, refresh token, and user information
    """
    try:
        if not login_request.Username or not login_request.Password:
            return ApiResult(
                StatusCode=400,
                Success=False,
                Message="Username and password are required",
                Result=None
            )

        auth_service = AuthenticationService()
        user_result = await auth_service.user_login(login_request)
        
        if not user_result.Success or user_result.Data is None:
            return ApiResult(
                StatusCode=401,
                Success=False,
                Result=None,
                Message=user_result.Message
            )

        # Generate tokens
        user_data = user_result.Data
        access_token = jwt_service.generate_access_token(
            user_id=user_data.UserId,
            username=user_data.Username or "",
            client_id=str(user_data.ClientId) if user_data.ClientId else None,
            default_language=user_data.ClientDefaultLanguage or "",
            subscriber_id=user_data.SubscriberId or 0
        )
        refresh_token = jwt_service.generate_refresh_token()
        refresh_token_expiry = datetime.now() + timedelta(days=7)

        # Update user with tokens
        token_updated = await auth_service.update_user_tokens_async(
            user_data.UserId,
            access_token,
            refresh_token,
            refresh_token_expiry
        )

        if not token_updated:
            logger.warning(f"Failed to update tokens for user {user_data.UserId}")

        # Update response data with tokens
        user_data.AccessToken = access_token
        user_data.RefreshToken = refresh_token
        user_data.RefreshTokenExpiry = refresh_token_expiry

        return ApiResult(
            StatusCode=200,
            Success=True,
            Result=user_data,
            Message=""
        )
        
    except Exception as e:
        logger.error(f"Error occurred during login for user {login_request.Username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("/refresh-token", response_model=LoginResponse)
async def refresh_token(
    refresh_token_request: RefreshTokenRequest,
) -> LoginResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token_request: Refresh token
        
    Returns:
        LoginResponse: New access token, refresh token, and user information
    """
    try:
        if not refresh_token_request.RefreshToken:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )

        auth_service = AuthenticationService()
        user_result = await auth_service.refresh_token_async(refresh_token_request)
        
        if not user_result.Success or user_result.Data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Generate new tokens
        user_data = user_result.Data
        new_access_token = jwt_service.generate_access_token(
            user_id=user_data.UserId,
            username=user_data.Username or "",
            client_id=str(user_data.ClientId) if user_data.ClientId else None,
            default_language=user_data.ClientDefaultLanguage or "",
            subscriber_id=user_data.SubscriberId or 0
        )
        new_refresh_token = jwt_service.generate_refresh_token()
        new_refresh_token_expiry = datetime.now() + timedelta(days=7)

        # Update user with new tokens
        token_updated = await auth_service.update_user_tokens_async(
            user_data.UserId,
            new_access_token,
            new_refresh_token,
            new_refresh_token_expiry
        )

        if not token_updated:
            logger.warning(f"Failed to update tokens for user {user_data.UserId}")

        # Build response
        response = LoginResponse(
            AccessToken=new_access_token,
            RefreshToken=new_refresh_token,
            RefreshTokenExpiry=new_refresh_token_expiry,
            UserId=user_data.UserId,
            SubscriberId=user_data.SubscriberId,
            Username=user_data.Username,
            Email=user_data.Email,
            Phone=user_data.Phone,
            Fullname=user_data.Fullname,
            ClientId=user_data.ClientId,
            ClientName=user_data.ClientName,
            ClientDefaultLanguage=user_data.ClientDefaultLanguage,
            RolesId=user_data.RolesId,
            Permissions=user_data.Permissions,
        )

        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("/ChangePassword", response_model=ApiResult)
async def change_password(
    change_password_dto: ChangePassword,
    current_user: dict = Depends(get_current_user)
) -> ApiResult:
    """
    Change user password (requires old password verification).
    
    Args:
        change_password_dto: Old and new password
        current_user: Current authenticated user
        
    Returns:
        ApiResult: Success status
    """
    try:
        if not change_password_dto.OldPassword or not change_password_dto.NewPassword:
            return ApiResult(
                StatusCode=400,
                Success=False,
                Message="Old password and new password are required"
            )

        auth_service = AuthenticationService()
        result = await auth_service.change_password_async(change_password_dto)

        if result.Status != 0:
            return ApiResult(
                Success=False,
                Message=result.Message,
                StatusCode=1
            )

        return ApiResult(
            Success=True,
            Message=result.Message,
            StatusCode=0
        )
        
    except Exception as e:
        logger.error(f"Error occurred while changing password for user with ID {change_password_dto.UserId}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e