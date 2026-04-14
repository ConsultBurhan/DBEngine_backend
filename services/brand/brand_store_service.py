"""Brand service for managing brand operations."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from models.service_models.brand.brand_service_models import BrandStoreResponseDto, BrandStoreCreateDto, BrandStoreUpdateDto
from models.common import UResponse, ResponseData, UEntity
from database.dbConnection.postgres_connection import PostgresConnectionManager, get_postgres_manager
from sqlalchemy import text
from config.logger_config import get_logger

logger = get_logger(__name__)


class BrandStoreService:
    def __init__(
        self,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None
    ):
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_brand_store_async(self, brand_id: int, search: Optional[str] = None) -> ResponseData[List[BrandStoreResponseDto]]:
        """Get all brand stores, optionally filtered by brand ID and store name search."""
        response = ResponseData[List[BrandStoreResponseDto]](
            Success=False,
            Message="Error",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Build query
                query = """
                    SELECT
                        "Id",
                        "BrandId",
                        "StoreName",
                        "RecordStatus",
                        "IsActive",
                        "CreatedBy",
                        "CreatedDate"
                    FROM "BrandStore"
                """
                conditions = []
                params = {}

                # Add brand_id filter if provided
                if brand_id > 0:
                    conditions.append('"BrandId" = :brand_id')
                    params["brand_id"] = brand_id

                # Add search filter if provided
                if search and search.strip():
                    conditions.append('LOWER("StoreName") LIKE LOWER(:search)')
                    params["search"] = f"%{search.strip()}%"

                # Add WHERE clause if there are conditions
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                result = await session.execute(text(query), params)
                rows = result.mappings().all()

                # Map to BrandStoreResponseDto
                stores = [
                    BrandStoreResponseDto(
                        Id=row["Id"],
                        BrandId=row["BrandId"],
                        StoreName=row["StoreName"],
                        RecordStatus=row["RecordStatus"] if row["RecordStatus"] else "",
                        IsActive=row["IsActive"],
                        CreatedBy=row["CreatedBy"],
                        CreatedDate=row["CreatedDate"]
                    )
                    for row in rows
                ]

                response.Data = stores
                response.Success = True
                response.Message = "Success"

        except Exception as ex:
            logger.error(f"Error fetching brand stores: {ex}")
            response.Success = False
            response.Message = str(ex)
            response.Data = []

        return response

    async def get_brand_store_by_id_async(self, id: int) -> ResponseData[BrandStoreResponseDto]:
        """Get a brand store by ID."""
        response = ResponseData[BrandStoreResponseDto](
            Success=False,
            Message="Error",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            "Id",
                            "BrandId",
                            "StoreName",
                            "RecordStatus",
                            "IsActive",
                            "CreatedBy",
                            "CreatedDate"
                        FROM "BrandStore"
                        WHERE "Id" = :id
                        AND "RecordStatus" != '-1'
                    """),
                    {"id": id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = "BrandStore not found"
                    return response

                store = BrandStoreResponseDto(
                    Id=row["Id"],
                    BrandId=row["BrandId"],
                    StoreName=row["StoreName"],
                    RecordStatus=row["RecordStatus"] if row["RecordStatus"] else "",
                    IsActive=row["IsActive"],
                    CreatedBy=row["CreatedBy"],
                    CreatedDate=row["CreatedDate"]
                )

                response.Data = store
                response.Success = True
                response.Message = "Success"

        except Exception as ex:
            logger.error(f"Error fetching brand store by ID: {ex}")
            response.Success = False
            response.Message = str(ex)
            response.Data = None

        return response

    async def create_brand_store_async(self, create_dto: BrandStoreCreateDto) -> UResponse:
        """Create a new brand store."""
        response = UResponse(
            Status=500,
            Message="Error"
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if brand exists
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "Brand"
                        WHERE "BrandId" = :brand_id
                    """),
                    {"brand_id": create_dto.BrandId}
                )
                brand = result.mappings().first()

                if brand is None:
                    response.Status = 409
                    response.Message = "Brand not found"
                    return response

                # Check if store name already exists for this brand
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "BrandStore"
                        WHERE LOWER("StoreName") = LOWER(:store_name)
                        AND "BrandId" = :brand_id
                        AND "RecordStatus" != '-1'
                    """),
                    {"store_name": create_dto.StoreName, "brand_id": create_dto.BrandId}
                )
                existing_store = result.mappings().first()

                if existing_store:
                    response.Status = 409
                    response.Message = "Store name already exists for this brand"
                    return response

                # Create new brand store
                await session.execute(
                    text("""
                        INSERT INTO "BrandStore" (
                            "BrandId",
                            "StoreName",
                            "RecordStatus",
                            "IsActive",
                            "CreatedBy",
                            "CreatedDate"
                        ) VALUES (
                            :brand_id,
                            :store_name,
                            :record_status,
                            :is_active,
                            :created_by,
                            :created_date
                        )
                    """),
                    {
                        "brand_id": create_dto.BrandId,
                        "store_name": create_dto.StoreName,
                        "record_status": "0",
                        "is_active": create_dto.IsActive,
                        "created_by": self.user_id,
                        "created_date": datetime.now()
                    }
                )
                await session.commit()

                response.Status = 200
                response.Message = "BrandStore created successfully"

        except Exception as ex:
            logger.error(f"Error creating brand store: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response

    async def update_brand_store_async(self, update_dto: BrandStoreUpdateDto) -> UResponse:
        """Update an existing brand store."""
        response = UResponse(
            Status=500,
            Message="Error"
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if brand exists
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "Brand"
                        WHERE "BrandId" = :brand_id
                    """),
                    {"brand_id": update_dto.BrandId}
                )
                brand = result.mappings().first()

                if brand is None:
                    response.Status = 409
                    response.Message = "Brand not found"
                    return response

                # Check if store exists
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "BrandStore"
                        WHERE "Id" = :id
                        AND "RecordStatus" != '-1'
                    """),
                    {"id": update_dto.Id}
                )
                store = result.mappings().first()

                if store is None:
                    response.Status = 404
                    response.Message = "BrandStore not found"
                    return response

                # Check if another store with same name already exists for this brand
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "BrandStore"
                        WHERE LOWER("StoreName") = LOWER(:store_name)
                        AND "BrandId" = :brand_id
                        AND "RecordStatus" != '-1'
                        AND "Id" != :id
                    """),
                    {"store_name": update_dto.StoreName, "brand_id": update_dto.BrandId, "id": update_dto.Id}
                )
                existing_store = result.mappings().first()

                if existing_store:
                    response.Status = 409
                    response.Message = "Store name already exists for this brand"
                    return response

                # Update brand store
                await session.execute(
                    text("""
                        UPDATE "BrandStore"
                        SET
                            "BrandId" = :brand_id,
                            "StoreName" = :store_name,
                            "RecordStatus" = :record_status,
                            "IsActive" = :is_active,
                            "UpdatedBy" = :updated_by,
                            "UpdatedDate" = :updated_date
                        WHERE "Id" = :id
                    """),
                    {
                        "brand_id": update_dto.BrandId,
                        "store_name": update_dto.StoreName,
                        "record_status": "0",
                        "is_active": update_dto.IsActive,
                        "updated_by": self.user_id,
                        "updated_date": datetime.now(),
                        "id": update_dto.Id
                    }
                )
                await session.commit()

                response.Status = 200
                response.Message = "BrandStore updated successfully"

        except Exception as ex:
            logger.error(f"Error updating brand store: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response

    async def delete_brand_store_async(self, id: int) -> UResponse:
        """Soft delete a brand store."""
        response = UResponse(
            Status=500,
            Message="Error"
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if store exists
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "BrandStore"
                        WHERE "Id" = :id
                        AND "RecordStatus" != '-1'
                    """),
                    {"id": id}
                )
                store = result.mappings().first()

                if store is None:
                    response.Status = 404
                    response.Message = "BrandStore not found"
                    return response

                # Soft delete the store
                await session.execute(
                    text("""
                        UPDATE "BrandStore"
                        SET
                            "RecordStatus" = :record_status,
                            "IsActive" = :is_active,
                            "UpdatedDate" = :updated_date
                        WHERE "Id" = :id
                    """),
                    {
                        "record_status": "-1",
                        "is_active": False,
                        "updated_date": datetime.now(),
                        "id": id
                    }
                )
                await session.commit()

                response.Status = 200
                response.Message = "BrandStore deleted successfully"

        except Exception as ex:
            logger.error(f"Error deleting brand store: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response

    async def get_brand_store_dropdown_async(self, brand_id: Optional[int] = None) -> ResponseData[List[UEntity]]:
        """Get brand store dropdown list (active stores only, optionally filtered by brand ID)."""
        response = ResponseData[List[UEntity]](
            Success=False,
            Message="Error",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Build query
                query = """
                    SELECT
                        "Id",
                        "StoreName"
                    FROM "BrandStore"
                    WHERE "RecordStatus" != '-1'
                    AND "IsActive" = true
                """
                params = {}

                # Add brand_id filter if provided
                if brand_id and brand_id > 0:
                    query += ' AND "BrandId" = :brand_id'
                    params["brand_id"] = brand_id

                result = await session.execute(text(query), params)
                rows = result.mappings().all()

                stores = [
                    UEntity(
                        Id=row["Id"],
                        Name=row["StoreName"]
                    )
                    for row in rows
                ]

                response.Data = stores
                response.Success = True
                response.Message = "Success"

        except Exception as ex:
            logger.error(f"Error fetching brand store dropdown: {ex}")
            response.Success = False
            response.Message = str(ex)
            response.Data = []

        return response