"""Documents router - Python implementation of DocumentsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form, status
from typing import Optional

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_client_id, get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.document_group.document_service_model import (
    CreateDocument,
    UplopadTranslatedDocument,
)
from services.document.document_service import DocumentService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllDocuments", response_model=ApiResult)
async def get_all_documents(
    request: Request,
    DocumentGroupId: int = Query(..., description="Document Group ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active documents.

    Args:
        DocumentGroupId: Document Group ID to filter documents

    Returns:
        ApiResult: List of documents
    """
    try:
        document_service = DocumentService(client_id=client_id, user_id=user_id)
        documents = await document_service.get_all_documents_async(DocumentGroupId)

        if not documents.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=documents.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=documents.Message,
            Result=documents.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting all documents: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(ex)}"
        ) from ex


@router.get("/GetDocumentById", response_model=ApiResult)
async def get_document_by_id(
    request: Request,
    id: int = Query(..., description="Document ID"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific document by ID.

    Args:
        id: Document ID

    Returns:
        ApiResult: Document details
    """
    try:
        document_service = DocumentService(client_id=client_id, user_id=user_id)
        document = await document_service.get_document_by_id_async(id)

        if not document.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=document.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=document.Message,
            Result=document.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting document with ID {id}: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/UploadDocument", response_model=ApiResult)
async def upload_document(
    request: Request,
    Documentname: str = Form(..., description="Document name"),
    Documentgroupid: int = Form(..., description="Document group ID"),
    Botid: int = Form(..., description="Bot ID"),
    file: UploadFile = File(..., description="Document file to upload"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new document.

    Args:
        Documentname: Document name
        Documentgroupid: Document group ID
        Botid: Bot ID
        file: Document file to upload

    Returns:
        ApiResult: Created document status
    """
    try:
        # Build CreateDocument DTO from form fields
        create_document = CreateDocument(
            Documentname=Documentname,
            Documentgroupid=Documentgroupid,
            Botid=Botid,
        )

        # Extract file extension from uploaded file
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = file.filename.rsplit(".", 1)[-1]

        # Read file content and get document URL (this would typically upload to storage)
        # For now, using a placeholder URL - in production this would upload to blob storage
        document_url = f"uploads/{file.filename}"

        document_service = DocumentService(client_id=client_id, user_id=user_id)
        result = await document_service.upload_document_async(
            create_document, document_url, file_extension
        )

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
        logger.error(f"Error occurred while creating document: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(ex)}"
        ) from ex


@router.post("/UploadTranslatedDocument", response_model=ApiResult)
async def upload_translated_document(
    request: Request,
    Documentid: int = Form(..., description="Document ID"),
    file: Optional[UploadFile] = File(None, description="Translated document file"),
) -> ApiResult:
    """
    Upload a translated document.
    Note: This endpoint allows anonymous access.

    Args:
        Documentid: Document ID
        file: Translated document file to upload

    Returns:
        ApiResult: Created document status
    """
    try:
        # Build UplopadTranslatedDocument DTO from form fields
        translated_document = UplopadTranslatedDocument(
            Documentid=Documentid,
        )

        # Get document URL from uploaded file or empty if no file
        document_url = ""
        if file and file.filename:
            document_url = f"uploads/translated/{file.filename}"

        # Create service without client_id/user_id for anonymous access
        document_service = DocumentService()
        result = await document_service.upload_translated_document_async(
            translated_document, document_url
        )

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
        logger.error(f"Error occurred while uploading translated document: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(ex)}"
        ) from ex


@router.delete("", response_model=ApiResult)
async def delete_document(
    request: Request,
    id: int = Query(..., description="Document ID"),
    botId: int = Query(..., description="Bot ID"),
    contentType: str = Query("", description="Content type"),
    current_user: dict = Depends(get_current_user),
    client_id: int = Depends(get_client_id),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a document (soft delete).

    Args:
        id: Document ID
        botId: Bot ID
        contentType: Content type

    Returns:
        ApiResult: Success status
    """
    try:
        document_service = DocumentService(client_id=client_id, user_id=user_id)
        result = await document_service.delete_document_async(id, botId, client_id, contentType)

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
        logger.error(f"Error occurred while deleting document with ID {id}: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
