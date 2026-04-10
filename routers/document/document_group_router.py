"""Document groups router - Python implementation of DocumentgroupsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.document_group.document_group_service_model import (
    CreateDocumentGroupRole,
    DocumentGroupCreate,
    DocumentGroupUpdate,
)
from services.document_group.document_group_service import DocumentgroupService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Documentgroups",
    tags=["Documentgroups"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllDocumentGroup", response_model=ApiResult)
async def get_all_document_groups(
    request: Request,
    bot_id: int = Query(None, description="Bot ID", alias="botId"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active document groups.
    
    Args:
        bot_id: Optional Bot ID to filter document groups
        
    Returns:
        ApiResult: List of document groups
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        response = await document_group_service.get_all_document_groups_async(bot_id)

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
    except Exception as e:
        logger.error(f"Error occurred while getting all document groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("/GetDocumentGroupById", response_model=ApiResult)
async def get_document_group_by_id(
    request: Request,
    id: int = Query(..., description="Document group ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific document group by ID.
    
    Args:
        id: Document group ID
        
    Returns:
        ApiResult: Document group details
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        result = await document_group_service.get_document_group_by_id_async(id)

        if not result.Success:
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
            Result=result.Data,
        )
    except Exception as e:
        logger.error(f"Error occurred while getting document group with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("", response_model=ApiResult)
async def create_document_group(
    request: Request,
    document_group: DocumentGroupCreate,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new document group.
    
    Args:
        document_group: Document group details
        
    Returns:
        ApiResult: Created document group status
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        created_document_group = await document_group_service.create_document_group_async(document_group)

        if created_document_group.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=created_document_group.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=created_document_group.Message,
            Result=None,
        )
    except Exception as e:
        logger.error(f"Error occurred while creating document group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.put("", response_model=ApiResult)
async def update_document_group(
    request: Request,
    update_document_group: DocumentGroupUpdate,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing document group.
    
    Args:
        update_document_group: Updated document group details
        
    Returns:
        ApiResult: Updated document group status
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        result = await document_group_service.update_document_group_async(update_document_group)

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
    except Exception as e:
        logger.error(f"Error occurred while updating document group with ID {update_document_group.DocumentGroupId}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.delete("", response_model=ApiResult)
async def delete_document_group(
    request: Request,
    id: int = Query(..., description="Document group ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a document group (soft delete).
    
    Args:
        id: Document group ID
        
    Returns:
        ApiResult: Success status
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        result = await document_group_service.delete_document_group_async(id)

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
    except Exception as e:
        logger.error(f"Error occurred while deleting document group with ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.get("/GetDocumentGroupRoleMap", response_model=ApiResult)
async def get_document_group_role_map(
    request: Request,
    document_group_id: int = Query(..., description="Document group ID", alias="documentgroupId"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get role mappings for a document group.
    
    Args:
        document_group_id: Document group ID
        
    Returns:
        ApiResult: List of role mappings
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        response = await document_group_service.get_document_group_role_map_list_async(document_group_id)

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
    except Exception as e:
        logger.error(f"Error occurred while getting document group role map for {document_group_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e


@router.post("/CreateDocumentGroupRoleMap", response_model=ApiResult)
async def create_document_group_role_map(
    request: Request,
    create_group_role_map: CreateDocumentGroupRole,
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create or update document group role mappings.
    
    Args:
        create_group_role_map: Role mapping details
        
    Returns:
        ApiResult: Success status
    """
    try:
        document_group_service = DocumentgroupService(client_id=client_id, user_id=user_id)
        created_document_group = await document_group_service.create_document_group_role_map_async(create_group_role_map)

        if created_document_group.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=created_document_group.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=created_document_group.Message,
            Result=None,
        )
    except Exception as e:
        logger.error(f"Error occurred while creating document group role map: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from e
