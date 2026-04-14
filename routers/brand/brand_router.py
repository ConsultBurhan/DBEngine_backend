"""Brand router - Python implementation of BrandController."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.brand.brand_service_models import BrandCreateDto, BrandUpdateDto
from services.brand.brand_service import BrandService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Brand",
    tags=["Brand"],
    responses={404: {"description": "Not found"}},
)


@router.get("/GetAllBrand", response_model=ApiResult)
async def get_all_brand(
    request: Request,
    brand_name: str = Query(None, description="Brand name filter"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get all brands, optionally filtered by brand name.

    Args:
        brand_name: Optional brand name filter

    Returns:
        ApiResult: List of brands
    """
    try:
        brand_service = BrandService(user_id=user_id)
        result = await brand_service.get_all_brand_async(brand_name)

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
        logger.error(f"Error occurred while getting all brands: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.get("/GetBrandById", response_model=ApiResult)
async def get_brand_by_id(
    request: Request,
    id: int = Query(..., description="Brand ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Get a specific brand by ID.

    Args:
        id: Brand ID

    Returns:
        ApiResult: Brand details
    """
    try:
        brand_service = BrandService(user_id=user_id)
        result = await brand_service.get_brand_by_id_async(id)

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
        logger.error(f"Error occurred while getting brand with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.post("/CreateBrand", response_model=ApiResult)
async def create_brand(
    request: Request,
    create_dto: BrandCreateDto,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Create a new brand.

    Args:
        create_dto: Brand creation data

    Returns:
        ApiResult: Created brand status
    """
    try:
        if not create_dto.BrandName or not create_dto.BrandName.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Brand name is required",
                Result=None,
            )

        brand_service = BrandService(user_id=user_id)
        result = await brand_service.create_brand_async(create_dto)

        if result.Status != 200:
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
        logger.error(f"Error occurred while creating brand: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.put("/UpdateBrand", response_model=ApiResult)
async def update_brand(
    request: Request,
    update_dto: BrandUpdateDto,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Update an existing brand.

    Args:
        update_dto: Brand update data

    Returns:
        ApiResult: Updated brand status
    """
    try:
        if not update_dto.BrandName or not update_dto.BrandName.strip():
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Brand name is required",
                Result=None,
            )

        brand_service = BrandService(user_id=user_id)
        result = await brand_service.update_brand_async(update_dto)

        if result.Status != 200:
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
        logger.error(f"Error occurred while updating brand with ID {update_dto.Id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex


@router.delete("/DeleteBrand", response_model=ApiResult)
async def delete_brand(
    request: Request,
    id: int = Query(..., description="Brand ID"),
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Delete a brand (soft delete).

    Args:
        id: Brand ID

    Returns:
        ApiResult: Success status
    """
    try:
        brand_service = BrandService(user_id=user_id)
        result = await brand_service.delete_brand_async(id)

        if result.Status != 200:
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
        logger.error(f"Error occurred while deleting brand with ID {id}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
