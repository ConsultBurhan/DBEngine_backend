"""Concept user map service for managing user concept and store mappings."""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from models.concept_user_map.concept_user_map_service_models import UserConceptMapDto
from models.common import UResponse
from database.dbConnection.postgres_connection import PostgresConnectionManager, get_postgres_manager
from sqlalchemy import text
from config.logger_config import get_logger

logger = get_logger(__name__)


class ConceptUserMapService:
    def __init__(
        self,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None
    ):
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def save_user_concept_map_async(self, create_dto: UserConceptMapDto) -> UResponse:
        """Save user concept and store mappings."""
        response = UResponse(
            Status=500,
            Message="Error"
        )

        try:
            # Validate UserId
            if create_dto.UserId <= 0:
                response.Status = 400
                response.Message = "Valid User ID is required"
                return response

            # Validate that at least one concept or store is provided
            if (not create_dto.ConceptIds or not create_dto.ConceptIds) and \
               (not create_dto.StoreIds or not create_dto.StoreIds):
                response.Status = 400
                response.Message = "At least one concept or store is required"
                return response

            async with await self._db_manager.get_session() as session:
                # Fetch brand names from Brand table using ConceptIds
                if create_dto.ConceptIds and create_dto.ConceptIds:
                    # Build IN clause for ConceptIds
                    concept_ids_list = create_dto.ConceptIds
                    placeholders = ', '.join([f':concept_id_{i}' for i in range(len(concept_ids_list))])
                    params = {f'concept_id_{i}': cid for i, cid in enumerate(concept_ids_list)}

                    result = await session.execute(
                        text(f"""
                            SELECT "Id", "BrandName"
                            FROM "Brand"
                            WHERE "Id" IN ({placeholders})
                            AND "RecordStatus" != '-1'
                        """),
                        params
                    )
                    brands = result.mappings().all()

                    # Create concept maps
                    for brand in brands:
                        await session.execute(
                            text("""
                                INSERT INTO conceptusermap (
                                    user_id,
                                    concept_id,
                                    concept_name,
                                    created_date
                                ) VALUES (
                                    :user_id,
                                    :concept_id,
                                    :concept_name,
                                    :created_date
                                )
                            """),
                            {
                                "user_id": create_dto.UserId,
                                "concept_id": brand["Id"],
                                "concept_name": brand["BrandName"],
                                "created_date": datetime.now()
                            }
                        )

                # Fetch store names from BrandStore table using StoreIds
                if create_dto.StoreIds and create_dto.StoreIds:
                    # Build IN clause for StoreIds
                    store_ids_list = create_dto.StoreIds
                    placeholders = ', '.join([f':store_id_{i}' for i in range(len(store_ids_list))])
                    params = {f'store_id_{i}': sid for i, sid in enumerate(store_ids_list)}

                    result = await session.execute(
                        text(f"""
                            SELECT "Id", "StoreName"
                            FROM "BrandStore"
                            WHERE "Id" IN ({placeholders})
                            AND "RecordStatus" != '-1'
                        """),
                        params
                    )
                    stores = result.mappings().all()

                    # Create store maps
                    for store in stores:
                        await session.execute(
                            text("""
                                INSERT INTO storeusermap (
                                    user_id,
                                    store_id, 
                                    store_name, 
                                    created_date
                                ) VALUES (
                                    :user_id,
                                    :store_id,
                                    :store_name,
                                    :created_date
                                )
                            """),
                            {
                                "user_id": create_dto.UserId,
                                "store_id": store["Id"],
                                "store_name": store["StoreName"],
                                "created_date": datetime.now()
                            }
                        )

                await session.commit()

                response.Status = 200
                response.Message = "User concept map saved successfully"

        except Exception as ex:
            logger.error(f"Error saving user concept map: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response
