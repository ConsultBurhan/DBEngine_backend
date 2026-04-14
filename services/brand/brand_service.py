"""Brand service for managing brand operations."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from models.service_models.brand.brand_service_models import BrandCreateDto, BrandUpdateDto, BrandResponseDto
from models.common import UResponse, ResponseData, UEntity
from database.dbConnection.postgres_connection import PostgresConnectionManager, get_postgres_manager
from sqlalchemy import text
from config.logger_config import get_logger

logger = get_logger(__name__)


class BrandService:
    def __init__(
        self,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None
    ):
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def create_brand_async(self, create_dto: BrandCreateDto) -> UResponse:
        """Create a new brand."""
        response = UResponse(
            Status=500,
            Message="Error"
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Check if brand with same name already exists
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "Brand"
                        WHERE LOWER("BrandName") = LOWER(:brand_name)
                        AND "RecordStatus" != '-1'
                    """),
                    {"brand_name": create_dto.BrandName}
                )
                existing_brand = result.mappings().first()

                if existing_brand:
                    response.Status = 409
                    response.Message = "Brand name already exists"
                    return response

                # Create new brand
                await session.execute(
                    text("""
                        INSERT INTO "Brand" (
                            "BrandId",
                            "BrandName",
                            "RecordStatus",
                            "IsActive",
                            "CreatedBy",
                            "CreatedDate"
                        ) VALUES (
                            :brand_id,
                            :brand_name,
                            :record_status,
                            :is_active,
                            :created_by,
                            :created_date
                        )
                    """),
                    {
                        "brand_id": create_dto.BrandId,
                        "brand_name": create_dto.BrandName,
                        "record_status": "0",
                        "is_active": create_dto.IsActive,
                        "created_by": self.user_id,
                        "created_date": datetime.now()
                    }
                )
                await session.commit()

                response.Status = 200
                response.Message = "Brand created successfully"

        except Exception as ex:
            logger.error(f"Error creating brand: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response

    async def update_brand_async(self, update_dto: BrandUpdateDto) -> UResponse:
        """Update an existing brand."""
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
                        WHERE "Id" = :id
                        AND "RecordStatus" != '-1'
                    """),
                    {"id": update_dto.Id}
                )
                brand = result.mappings().first()

                if brand is None:
                    response.Status = 404
                    response.Message = "Brand not found"
                    return response

                # Check if another brand with same name already exists
                result = await session.execute(
                    text("""
                        SELECT "Id" FROM "Brand"
                        WHERE LOWER("BrandName") = LOWER(:brand_name)
                        AND "RecordStatus" != '-1'
                        AND "Id" != :id
                    """),
                    {"brand_name": update_dto.BrandName, "id": update_dto.Id}
                )
                existing_brand = result.mappings().first()

                if existing_brand:
                    response.Status = 409
                    response.Message = "Brand name already exists"
                    return response

                # Update brand
                await session.execute(
                    text("""
                        UPDATE "Brand"
                        SET
                            "BrandId" = :brand_id,
                            "BrandName" = :brand_name,
                            "RecordStatus" = :record_status,
                            "IsActive" = :is_active,
                            "UpdatedBy" = :updated_by,
                            "UpdatedDate" = :updated_date
                        WHERE "Id" = :id
                    """),
                    {
                        "brand_id": update_dto.BrandId,
                        "brand_name": update_dto.BrandName,
                        "record_status": "0",
                        "is_active": update_dto.IsActive,
                        "updated_by": self.user_id,
                        "updated_date": datetime.now(),
                        "id": update_dto.Id
                    }
                )
                await session.commit()

                response.Status = 200
                response.Message = "Brand updated successfully"

        except Exception as ex:
            logger.error(f"Error updating brand: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response

    async def delete_brand_async(self, brand_id: int) -> UResponse:
        """Soft delete a brand and its related stores."""
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
                        WHERE "Id" = :brand_id
                        AND "RecordStatus" != '-1'
                    """),
                    {"brand_id": brand_id}
                )
                brand = result.mappings().first()

                if brand is None:
                    response.Status = 404
                    response.Message = "Brand not found"
                    return response

                # Soft delete all related brand stores
                await session.execute(
                    text("""
                        UPDATE "BrandStore"
                        SET
                            "RecordStatus" = :record_status,
                            "IsActive" = :is_active,
                            "UpdatedDate" = :updated_date
                        WHERE "BrandId" = :brand_id
                        AND "RecordStatus" != '-1'
                    """),
                    {
                        "record_status": "-1",
                        "is_active": False,
                        "updated_date": datetime.now(),
                        "brand_id": brand_id
                    }
                )

                # Get count of affected stores
                result = await session.execute(
                    text("""
                        SELECT COUNT(*) as count FROM "BrandStore"
                        WHERE "BrandId" = :brand_id
                        AND "RecordStatus" = '-1'
                    """),
                    {"brand_id": brand_id}
                )
                store_count = result.mappings().first()["count"]

                # Soft delete the "Brand"
                await session.execute(
                    text("""
                        UPDATE "Brand"
                        SET
                            "RecordStatus" = :record_status,
                            "IsActive" = :is_active,
                            "UpdatedDate" = :updated_date
                        WHERE "Id" = :brand_id
                    """),
                    {
                        "record_status": "-1",
                        "is_active": False,
                        "updated_date": datetime.now(),
                        "brand_id": brand_id
                    }
                )
                await session.commit()

                response.Status = 200
                response.Message = f"Brand and {store_count} store(s) deleted successfully"

        except Exception as ex:
            logger.error(f"Error deleting brand: {ex}")
            response.Status = 500
            response.Message = str(ex)

        return response

    async def get_all_brand_async(self, brand_name: Optional[str] = None) -> ResponseData[List[BrandResponseDto]]:
        """Get all brands, optionally filtered by brand name."""
        response = ResponseData[List[BrandResponseDto]](
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
                        "BrandName",
                        "RecordStatus",
                        "IsActive",
                        "CreatedBy",
                        "CreatedDate"
                    FROM "Brand"
                """
                params = {}

                # Add filter if brand_name is provided
                if brand_name and brand_name.strip():
                    query += ' WHERE LOWER("BrandName") LIKE LOWER(:brand_name)'
                    params["brand_name"] = f"%{brand_name.strip()}%"

                result = await session.execute(text(query), params)
                rows = result.mappings().all()

                # Map to BrandResponseDto
                brands = [
                    BrandResponseDto(
                        Id=row["Id"],
                        BrandId=row["BrandId"],
                        BrandName=row["BrandName"],
                        RecordStatus=row["RecordStatus"] if row["RecordStatus"] else "",
                        IsActive=row["IsActive"],
                        CreatedBy=row["CreatedBy"],
                        CreatedDate=row["CreatedDate"]
                    )
                    for row in rows
                ]

                response.Data = brands
                response.Success = True
                response.Message = "Brand retrieved successfully"

        except Exception as ex:
            logger.error(f"Error fetching brands: {ex}")
            response.Success = False
            response.Message = str(ex)
            response.Data = []

        return response

    async def get_brand_by_id_async(self, brand_id: int) -> ResponseData[BrandResponseDto]:
        """Get a brand by ID."""
        response = ResponseData[BrandResponseDto](
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
                            "BrandName",
                            "RecordStatus",
                            "IsActive",
                            "CreatedBy",
                            "CreatedDate"
                        FROM "Brand"
                        WHERE "Id" = :brand_id
                        AND "RecordStatus" != '-1'
                    """),
                    {"brand_id": brand_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = "Brand not found"
                    return response

                brand = BrandResponseDto(
                    Id=row["Id"],
                    BrandId=row["BrandId"],
                    BrandName=row["BrandName"],
                    RecordStatus=row["RecordStatus"] if row["RecordStatus"] else "",
                    IsActive=row["IsActive"] if row["IsActive"] is not None else True,
                    CreatedBy=row["CreatedBy"],
                    CreatedDate=row["CreatedDate"]
                )

                response.Data = brand
                response.Success = True
                response.Message = "Brand retrieved successfully"

        except Exception as ex:
            logger.error(f"Error fetching brand by ID: {ex}")
            response.Success = False
            response.Message = str(ex)
            response.Data = None

        return response

    async def get_brand_dropdown_async(self) -> ResponseData[List[UEntity]]:
        """Get brand dropdown list (active brands only)."""
        response = ResponseData[List[UEntity]](
            Success=False,
            Message="Error",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            "Id",
                            "BrandName"
                        FROM "Brand"
                        WHERE "RecordStatus" != '-1'
                        AND "IsActive" = true
                    """)
                )
                rows = result.mappings().all()

                brands = [
                    UEntity(
                        Id=row["Id"],
                        Name=row["BrandName"]
                    )
                    for row in rows
                ]

                response.Data = brands
                response.Success = True
                response.Message = "Brand retrieved successfully"

        except Exception as ex:
            logger.error(f"Error fetching brand dropdown: {ex}")
            response.Success = False
            response.Message = str(ex)
            response.Data = []

        return response
