"""Bots router - Python implementation of BotsController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id, get_client_id
from models.common import ApiResult
from models.service_models.bot.bot_service_models import CreateBot, UpdateBot, CreateBotRole
from services.bot.bot_service import BotService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Bots",
    tags=["Bots"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllBots", response_model=ApiResult)
async def get_all_bots(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get all active bots.

    Returns:
        ApiResult: List of bots
    """
    try:
        bot_service = BotService(client_id=client_id, user_id=user_id)
        response = await bot_service.get_all_bots_async()

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
    except Exception as ex:
        logger.error(f"Error occurred while getting all bots: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBotById", response_model=ApiResult)
async def get_bot_by_id(
    request: Request,
    id: int = Query(..., description="Bot ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get a specific bot by ID.

    Args:
        id: Bot ID

    Returns:
        ApiResult: Bot details
    """
    try:
        bot_service = BotService(client_id=client_id, user_id=user_id)
        response = await bot_service.get_bot_by_id_async(id)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting bot with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("", response_model=ApiResult)
async def create_bot(
    request: Request,
    botname: str = Form(..., description="Bot name"),
    logo: UploadFile = File(None, description="Logo file"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create a new bot with optional logo upload.

    Args:
        botname: Bot name
        logo: Logo file

    Returns:
        ApiResult: Created bot status
    """
    try:
        # Validate input
        if not botname or not botname.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Bot name is required",
                Result=None,
            )

        # Build CreateBot DTO from form fields
        create_bot_dto = CreateBot(
            Botname=botname,
            Logo=logo,
        )

        bot_service = BotService(client_id=client_id, user_id=user_id)
        result = await bot_service.create_bot_async(create_bot_dto)

        if result.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=result.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while creating bot: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("", response_model=ApiResult)
async def update_bot(
    request: Request,
    bot_id: int = Form(..., description="Bot ID"),
    botname: str = Form(..., description="Bot name"),
    logo: UploadFile = File(None, description="Logo file"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Update an existing bot with optional logo upload.

    Args:
        bot_id: Bot ID
        botname: Bot name
        logo: Logo file (optional)

    Returns:
        ApiResult: Updated bot status
    """
    try:
        # Validate input
        if not botname or not botname.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Bot name is required",
                Result=None,
            )

        # Build UpdateBot DTO from form fields
        update_bot_dto = UpdateBot(
            BotId=bot_id,
            Botname=botname,
            Logo=logo,
        )

        bot_service = BotService(client_id=client_id, user_id=user_id)
        result = await bot_service.update_bot_async(update_bot_dto)

        if result.Status != 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=result.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=result.Message,
            Result=None,
        )
    except Exception as ex:
        logger.error(f"Error occurred while updating bot: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("", response_model=ApiResult)
async def delete_bot(
    request: Request,
    id: int = Query(..., description="Bot ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Delete a bot (soft delete).

    Args:
        id: Bot ID

    Returns:
        ApiResult: Success status
    """
    try:
        bot_service = BotService(client_id=client_id, user_id=user_id)
        result = await bot_service.delete_bot_async(id)

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
        logger.error(f"Error occurred while deleting bot with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBots", response_model=ApiResult)
async def get_bots(
    request: Request,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get bots for dropdown with type based on database connection status.

    Returns:
        ApiResult: List of bots with type indicator
    """
    try:
        bot_service = BotService(client_id=client_id, user_id=user_id)
        response = await bot_service.get_bots_async()

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            Message=response.Message,
            Result=response.Data,
            StatusCode=0,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting bots: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBotsByRoleId", response_model=ApiResult)
async def get_bots_by_role_id(
    request: Request,
    role_ids: str = Query(..., description="Comma-separated role IDs"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get bots mapped to specific role IDs.

    Args:
        role_ids: Comma-separated role IDs

    Returns:
        ApiResult: List of bots
    """
    try:
        bot_service = BotService(client_id=client_id, user_id=user_id)
        response = await bot_service.get_bots_by_role_id_async(role_ids)

        if not response.Success:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            Message=response.Message,
            Result=response.Data,
            StatusCode=0,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting bots by role IDs: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBotRoleMap", response_model=ApiResult)
async def get_bot_role_map(
    request: Request,
    bot_id: int = Query(..., description="Bot ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Get role mappings for a specific bot.

    Args:
        bot_id: Bot ID

    Returns:
        ApiResult: Bot role mappings
    """
    try:
        bot_service = BotService(client_id=client_id, user_id=user_id)
        response = await bot_service.get_bot_role_map_list_async(bot_id)

        if not response.Success:
            return ApiResult(
                Success=False,
                StatusCode=1,
                Message=response.Message,
                Result=None,
            )

        return ApiResult(
            Success=True,
            StatusCode=0,
            Message=response.Message,
            Result=response.Data,
        )
    except Exception as ex:
        logger.error(f"Error occurred while getting bot role map: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateBotRoleMap", response_model=ApiResult)
async def create_bot_role_map(
    request: Request,
    bot_id: int = Form(..., description="Bot ID"),
    roles_id: str = Form(None, description="Comma-separated role IDs"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    client_id: int = Depends(get_client_id),
) -> ApiResult:
    """
    Create or update bot role mappings.

    Args:
        bot_id: Bot ID
        roles_id: Comma-separated role IDs

    Returns:
        ApiResult: Creation status
    """
    try:
        # Build CreateBotRole DTO from form fields
        create_bot_role_dto = CreateBotRole(
            BotId=bot_id,
            RolesId=roles_id,
        )

        bot_service = BotService(client_id=client_id, user_id=user_id)
        result = await bot_service.create_bot_role_map(create_bot_role_dto)

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
        logger.error(f"Error occurred while creating bot role map: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(ex)}"
        ) from ex
