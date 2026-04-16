"""BrandStore router - Python implementation of BrandStore endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.brand.brand_service_models import BrandStoreCreateDto, BrandStoreUpdateDto
from services.brand.brand_store_service import BrandStoreService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Brand",
    tags=["BrandStore"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllBrandStore", response_model=ApiResult)
async def get_all_brand_store(
    request: Request,
    brand_id: int = Query(..., description="Brand ID"),
    search: str = Query(None, description="Search filter for store name"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all brand stores, optionally filtered by brand ID and store name search.

    Args:
        brand_id: Brand ID
        search: Optional search filter for store name

    Returns:
        ApiResult: List of brand stores
    """
    try:
        brand_store_service = BrandStoreService(user_id=user_id)
        result = await brand_store_service.get_all_brand_store_async(brand_id, search)

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
    except Exception as ex:
        logger.error(f"Error occurred while getting all brand stores: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBrandStoreById", response_model=ApiResult)
async def get_brand_store_by_id(
    request: Request,
    id: int = Query(..., description="Brand Store ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific brand store by ID.

    Args:
        id: Brand Store ID

    Returns:
        ApiResult: Brand store details
    """
    try:
        brand_store_service = BrandStoreService(user_id=user_id)
        result = await brand_store_service.get_brand_store_by_id_async(id)

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
    except Exception as ex:
        logger.error(f"Error occurred while getting brand store with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateBrandStore", response_model=ApiResult)
async def create_brand_store(
    request: Request,
    create_dto: BrandStoreCreateDto,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new brand store.

    Args:
        create_dto: Brand store creation data

    Returns:
        ApiResult: Created brand store status
    """
    try:
        if not create_dto.StoreName or not create_dto.StoreName.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Store name is required",
                Result=None,
            )

        if create_dto.BrandId <= 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Valid Brand ID is required",
                Result=None,
            )

        brand_store_service = BrandStoreService(user_id=user_id)
        result = await brand_store_service.create_brand_store_async(create_dto)

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
        logger.error(f"Error occurred while creating brand store: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("/UpdateBrandStore", response_model=ApiResult)
async def update_brand_store(
    request: Request,
    update_dto: BrandStoreUpdateDto,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing brand store.

    Args:
        update_dto: Brand store update data

    Returns:
        ApiResult: Updated brand store status
    """
    try:
        if not update_dto.StoreName or not update_dto.StoreName.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Store name is required",
                Result=None,
            )

        if update_dto.BrandId <= 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Valid Brand ID is required",
                Result=None,
            )

        brand_store_service = BrandStoreService(user_id=user_id)
        result = await brand_store_service.update_brand_store_async(update_dto)

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
        logger.error(f"Error occurred while updating brand store with ID {update_dto.Id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("/DeleteBrandStore", response_model=ApiResult)
async def delete_brand_store(
    request: Request,
    id: int = Query(..., description="Brand Store ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a brand store (soft delete).

    Args:
        id: Brand Store ID

    Returns:
        ApiResult: Success status
    """
    try:
        brand_store_service = BrandStoreService(user_id=user_id)
        result = await brand_store_service.delete_brand_store_async(id)

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
        logger.error(f"Error occurred while deleting brand store with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex

