"""JWT dependencies for FastAPI routes."""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.logger_config import get_logger
from services.JWT.JWT_service import get_jwt_service, JWTService

security = HTTPBearer()
logger = get_logger(__name__)



async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> dict:
    """
    Dependency to get current user from JWT token.
    
    Args:
        request: FastAPI request object
        credentials: HTTP authorization credentials
        jwt_service: JWT service instance
        
    Returns:
        dict: User claims from JWT token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and validate the token
        payload = jwt_service.decode_token(credentials.credentials)
        
        # Store user info in request state for later use
        request.state.user = payload
        return payload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user_id(
    current_user: dict = Depends(get_current_user),
) -> int:
    """
    Dependency to get current user ID from JWT token.
    
    Args:
        current_user: User claims from JWT token
        
    Returns:
        int: User ID
        
    Raises:
        HTTPException: If user ID is not found or invalid
    """
    user_id_str = current_user.get("UserId")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )
    try:
        user_id = int(user_id_str)
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID must be a positive integer"
            )
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be a positive integer"
        )


async def get_client_id(
    current_user: dict = Depends(get_current_user),
) -> int:
    """
    Dependency to get client ID from JWT token.
    
    Args:
        current_user: User claims from JWT token
        
    Returns:
        int: Client ID
    """
    client_id_str = current_user.get("ClientId")
    if client_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID not found in token"
        )
    try:
        client_id = int(client_id_str)
        if client_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client ID must be a positive integer"
            )
        return client_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID must be a positive integer"
        )


async def get_subscriber_id(
    current_user: dict = Depends(get_current_user),
) -> int:
    """
    Dependency to get subscriber ID from JWT token.
    
    Args:
        current_user: User claims from JWT token
        
    Returns:
        int: Subscriber ID
    """
    subscriber_id_str = current_user.get("SubscriberId")
    if subscriber_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscriber ID not found in token"
        )
    try:
        subscriber_id = int(subscriber_id_str)
        if subscriber_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscriber ID must be a positive integer"
            )
        return subscriber_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscriber ID must be a positive integer"
        )
