"""Clients router - Python implementation of ClientsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.clients.clients_service_model import ClientCreate, ClientUpdate
from services.clients.clients_service import ClientService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Clients",
    tags=["Clients"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllClients", response_model=ApiResult)
async def get_all_clients(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all active clients.

    Returns:
        ApiResult: List of clients
    """
    try:
        client_service = ClientService(user_id=user_id)
        clients = await client_service.get_all_clients_async()

        if not clients.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=clients.Message,
                Result=None,
            )

        return ApiResult(
            StatusCode=0,
            Success=True,
            Message=clients.Message,
            Result=clients.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting all clients: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetClientById", response_model=ApiResult)
async def get_client_by_id(
    request: Request,
    id: int = Query(..., description="Client ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific client by ID.

    Args:
        id: Client ID

    Returns:
        ApiResult: Client details
    """
    try:
        client_service = ClientService(user_id=user_id)
        client_response = await client_service.get_client_by_id_async(id)

        if not client_response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=client_response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=client_response.Message,
            Result=client_response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting client with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("", response_model=ApiResult)
async def create_client(
    request: Request,
    clientname: str = Form(..., description="Client name"),
    status: int = Form(1, description="Status"),
    logo: UploadFile = File(..., description="Logo file"),
    createdby: str = Form(None, description="Created by"),
    DefaultLanguageCode: str = Form(None, description="Default language code"),
    ClientPrefix: str = Form(..., description="Client prefix"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new client with logo upload.

    Args:
        clientname: Client name
        status: Status
        logo: Logo file
        createdby: Created by
        DefaultLanguageCode: Default language code
        ClientPrefix: Client prefix

    Returns:
        ApiResult: Created client status
    """
    try:
        if not clientname or not clientname.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Client name is required",
                Result=None,
            )

        if logo is None:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Client logo file is required",
                Result=None,
            )

        # Build ClientCreate DTO from form fields
        create_client_dto = ClientCreate(
            Clientname=clientname,
            Status=status,
            Logo=logo,
            DefaultLanguageCode=DefaultLanguageCode,
            ClientPrefix=ClientPrefix,
        )

        client_service = ClientService(user_id=user_id)
        created_client = await client_service.create_client_async(create_client_dto)

        if created_client.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=created_client.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=created_client.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while creating client: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("", response_model=ApiResult)
async def update_client(
    request: Request,
    clientid: int = Form(..., description="Client ID"),
    clientname: str = Form(..., description="Client name"),
    status: int = Form(1, description="Status"),
    logo: UploadFile = File(None, description="Logo file"),
    updatedby: str = Form(None, description="Updated by"),
    DefaultLanguageCode: str = Form(None, description="Default language code"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing client with optional logo upload.

    Args:
        clientid: Client ID
        clientname: Client name
        status: Status
        logo: Logo file (optional)
        updatedby: Updated by
        DefaultLanguageCode: Default language code

    Returns:
        ApiResult: Updated client status
    """
    try:
        if not clientname or not clientname.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Client name is required",
                Result=None,
            )

        # Build ClientUpdate DTO from form fields
        update_client_dto = ClientUpdate(
            ClientId=clientid,
            Clientname=clientname,
            Status=status,
            Logo=logo,
            DefaultLanguageCode=DefaultLanguageCode,
        )

        client_service = ClientService(user_id=user_id)
        updated_client = await client_service.update_client_async(update_client_dto)

        if updated_client.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=updated_client.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=updated_client.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while updating client with ID {clientid}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("", response_model=ApiResult)
async def delete_client(
    request: Request,
    id: int = Query(..., description="Client ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a client (soft delete).

    Args:
        id: Client ID

    Returns:
        ApiResult: Success status
    """
    try:
        client_service = ClientService(user_id=user_id)
        result = await client_service.delete_client_async(id)

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
        logger.error(f"Error occurred while deleting client with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetClients", response_model=ApiResult)
async def get_clients(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get simplified list of clients (ID and name only).

    Returns:
        ApiResult: List of clients with ID and name
    """
    try:
        client_service = ClientService(user_id=user_id)
        response = await client_service.get_client_async()

        if not response.Success:
            return ApiResult(
                Success=False,
                Message=response.Message,
                Result=None,
                StatusCode=1,
            )

        return ApiResult(
            Success=True,
            Message=response.Message,
            Result=response.Data,
            StatusCode=0,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting all clients: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
