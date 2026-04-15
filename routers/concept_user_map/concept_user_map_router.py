"""ConceptUserMap router - Python implementation of SaveUserConceptMap endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as fastapiStatus

from config.logger_config import get_logger
from dependencies.jwt_dependencies import get_current_user, get_current_user_id
from models.common import ApiResult
from models.service_models.concept_user_map.concept_user_map_service_models import UserConceptMapDto
from services.concept_user_map.concept_user_map_service import ConceptUserMapService

logger = get_logger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/Brand",
    tags=["ConceptUserMap"],
    responses={404: {"description": "Not found"}},
)


@router.post("/SaveUserConceptMap", response_model=ApiResult)
async def save_user_concept_map(
    request: Request,
    create_dto: UserConceptMapDto,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
) -> ApiResult:
    """
    Save user concept and store mappings.

    Args:
        create_dto: User concept mapping data

    Returns:
        ApiResult: Save operation status
    """
    try:
        if create_dto.UserId <= 0:
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="Valid User ID is required",
                Result=None,
            )

        if (not create_dto.ConceptIds or not create_dto.ConceptIds) and \
           (not create_dto.StoreIds or not create_dto.StoreIds):
            return ApiResult(
                StatusCode=1,
                Success=False,
                Message="At least one concept or store is required",
                Result=None,
            )

        concept_user_map_service = ConceptUserMapService(user_id=user_id)
        result = await concept_user_map_service.save_user_concept_map_async(create_dto)

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
        logger.error(f"Error occurred while saving user concept map for UserID {create_dto.UserId}: {ex}")
        raise HTTPException(
            status_code=fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        ) from ex
