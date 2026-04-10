"""Permission tasks router - Python implementation of C# PermissiontasksController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.permission.permission_service_models import (
    AddPermissionTask,
    UpdatePermissionTask,
)
from services.permissions.permission_tasks_service import PermissiontaskService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/permissiontasks",
    tags=["permissiontasks"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ApiResult)
async def get_all_permission_tasks(
    request: Request,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active permission tasks.
    
    Returns:
        ApiResult: List of permission tasks
    """
    try:
        permission_service = PermissiontaskService()
        permission_tasks = await permission_service.get_all_permission_tasks_async()

        if not permission_tasks.Success:
            return ApiResult(
                StatusCode=0,
                Success=True,
                Message=permission_tasks.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Result=permission_tasks.Data,
            Message=permission_tasks.Message
        )
    except Exception as e:
        logger.error(f"Error occurred while getting all permission tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("/GetPermissionTaskById", response_model=ApiResult)
async def get_permission_task_by_id(
    request: Request,
    id: int = Query(..., description="Permission task ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific permission task by ID.
    
    Args:
        id: Permission task ID
        
    Returns:
        ApiResult: Permission task details
    """
    try:
        permission_service = PermissiontaskService()
        permission_task_response = await permission_service.get_permission_task_by_id_async(id)

        if not permission_task_response.Success or permission_task_response.Data is None:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=permission_task_response.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=1,
            Success=True,
            Result=permission_task_response.Data,
            Message=permission_task_response.Message
        )
    except Exception as e:
        logger.error(f"Error occurred while getting permission task with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("", response_model=ApiResult)
async def create_permission_task(
    request: Request,
    permission_task: AddPermissionTask,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new permission task.
    
    Args:
        permission_task: Permission task details
        
    Returns:
        ApiResult: Created permission task status
    """
    try:
        # Set createdby from current user
        permission_task.Createdby = str(user_id)
        
        permission_service = PermissiontaskService()
        response = await permission_service.create_permission_task_async(permission_task)

        if response is None or response.Status > 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message if response else "Unknown error",
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Result=response,
            Message="Data added successfully"
        )
    except Exception as e:
        logger.error(f"Error occurred while creating permission task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.put("/UpdatePermissiontask", response_model=ApiResult)
async def update_permission_task(
    request: Request,
    permission_task: UpdatePermissionTask,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing permission task.
    
    Args:
        permission_task: Updated permission task details
        
    Returns:
        ApiResult: Updated permission task status
    """
    try:
        # Set updatedby from current user
        permission_task.Updatedby = str(user_id)
        
        permission_service = PermissiontaskService()
        result = await permission_service.update_permission_task_async(permission_task)

        if result.Status == 1:
            return ApiResult(
                StatusCode=0,
                Success=False,
                Message=result.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Result=None,
            Message=result.Message
        )
    except Exception as e:
        logger.error(f"Error occurred while updating permission task with ID {permission_task.Id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.delete("", response_model=ApiResult)
async def delete_permission_task(
    request: Request,
    id: int = Query(..., description="Permission task ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a permission task (soft delete) and related permissions.
    
    Args:
        id: Permission task ID
        
    Returns:
        ApiResult: Success status
    """
    try:
        permission_service = PermissiontaskService()
        result = await permission_service.delete_permission_task_async(id)

        if result.Status == 1:
            return ApiResult(
                Statuscode=0,
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
        logger.error(f"Error occurred while deleting permission task with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        ) from e


@router.get("/GetPermissionTask", response_model=ApiResult)
async def get_permission_task_dropdown(
    request: Request,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get simplified list of active permission tasks for dropdown.
    
    Returns:
        ApiResult: List of simplified permission tasks (id, name only)
    """
    try:
        permission_service = PermissiontaskService()
        permission_tasks = await permission_service.get_permission_tasks_dropdown_async()

        if not permission_tasks.Success:
            return ApiResult(
                StatusCode=0,
                Success=True,
                Message=permission_tasks.Message,
                Result=None
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Result=permission_tasks.Data,
            Message=permission_tasks.Message
        )
    except Exception as e:
        logger.error(f"Error occurred while getting permission tasks dropdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e
