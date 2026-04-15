"""Retraining service for managing bot training map operations."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    PostgresConnectionManager,
    get_postgres_manager,
)
from models.common import ResponseData, UResponse
from models.service_models.retraining.retraining_service_models import (
    BottrainingmapDto,
    CreateBottrainingmap,
    UpdateBottrainingmap,
)
from config.logger_config import get_logger

logger = get_logger(__name__)


class RetrainingService:
    """Service for bot training map operations."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def create_async(self, entity: CreateBottrainingmap) -> ResponseData[BottrainingmapDto]:
        """Create a new bot training map."""
        response = ResponseData[BottrainingmapDto](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                insert_result = await session.execute(
                    text("""
                        INSERT INTO bottrainingmap (
                            botid, clientid, content, trainingtype, title, keywords,
                            summary, metadata, source, documentid, createddate,recordstatus
                        ) VALUES (
                            :botid, :clientid, :content, :trainingtype, :title, :keywords,
                            :summary, :metadata, :source, :documentid, :created_date, 1
                        ) RETURNING id
                    """),
                    {
                        "botid": entity.Botid,
                        "clientid": entity.Clientid,
                        "content": entity.Content,
                        "trainingtype": entity.Trainingtype,
                        "title": entity.Title,
                        "keywords": entity.Keywords,
                        "summary": entity.Summary,
                        "metadata": entity.Metadata,
                        "source": entity.Source,
                        "documentid": entity.Documentid,
                        "created_date": datetime.now(),
                    }
                )
                await session.commit()
                row = insert_result.mappings().first()
                entity_id = row["id"]

                # Fetch the created entity
                result = await session.execute(
                    text("""
                        SELECT
                            id, botid, clientid, content, trainingtype, title, keywords,
                            summary, metadata, createddate, updateddate, source, documentid, recordstatus
                        FROM bottrainingmap
                        WHERE id = :id
                    """),
                    {"id": entity_id}
                )
                created_row = result.mappings().first()

                bottrainingmap = BottrainingmapDto(
                    Id=created_row["id"],
                    Botid=created_row["botid"],
                    Clientid=created_row["clientid"],
                    Content=created_row["content"],
                    Trainingtype=created_row["trainingtype"],
                    Title=created_row["title"],
                    Keywords=created_row["keywords"],
                    Summary=created_row["summary"],
                    Metadata=created_row["metadata"],
                    Createddate=created_row["createddate"],
                    Updateddate=created_row["updateddate"],
                    Source=created_row["source"],
                    Documentid=created_row["documentid"],
                    Recordstatus=created_row["recordstatus"]
                )

                response.Data = bottrainingmap
                response.Success = True
                response.Message = "Bot training map created successfully"

        except Exception as ex:
            logger.error(f"Error creating bot training map: {ex}")
            response.Success = False
            response.Message = f"An error occurred while creating bot training map: {str(ex)}"
            response.Data = None

        return response

    async def get_by_id_async(self, id: int) -> ResponseData[BottrainingmapDto]:
        """Get a bot training map by ID with recordstatus = 1."""
        response = ResponseData[BottrainingmapDto](
            Success=True,
            Message="",
            Data=None
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            id, botid, clientid, content, trainingtype, title, keywords,
                            summary, metadata, createddate, updateddate, source, documentid, recordstatus
                        FROM bottrainingmap
                        WHERE id = :id
                          AND recordstatus = 1
                    """),
                    {"id": id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"No active bot training map found with ID {id}"
                    return response

                bottrainingmap = BottrainingmapDto(
                    Id=row["id"],
                    Botid=row["botid"],
                    Clientid=row["clientid"],
                    Content=row["content"],
                    Trainingtype=row["trainingtype"],
                    Title=row["title"],
                    Keywords=row["keywords"],
                    Summary=row["summary"],
                    Metadata=row["metadata"],
                    Createddate=row["createddate"],
                    Updateddate=row["updateddate"],
                    Source=row["source"],
                    Documentid=row["documentid"],
                    Recordstatus=row["recordstatus"]
                )

                response.Data = bottrainingmap
                response.Success = True
                response.Message = "Bot training map fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching bot training map by ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bot training map: {str(ex)}"
            response.Data = None

        return response

    async def get_by_bot_async(self, bot_id: int, client_id: str) -> ResponseData[List[BottrainingmapDto]]:
        """Get bot training maps by bot ID and client ID with recordstatus = 1, ordered by createddate descending."""
        response = ResponseData[List[BottrainingmapDto]](
            Success=True,
            Message="",
            Data=[]
        )

        try:
            async with await self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""
                        SELECT
                            id, botid, clientid, content, trainingtype, title, keywords,
                            summary, metadata, createddate, updateddate, source, documentid, recordstatus
                        FROM bottrainingmap
                        WHERE botid = :bot_id
                          AND clientid = :client_id
                          AND recordstatus = 1
                        ORDER BY createddate DESC
                    """),
                    {"bot_id": bot_id, "client_id": client_id}
                )
                rows = result.mappings().all()

                bottrainingmaps = [
                    BottrainingmapDto(
                        Id=row["id"],
                        Botid=row["botid"],
                        Clientid=row["clientid"],
                        Content=row["content"],
                        Trainingtype=row["trainingtype"],
                        Title=row["title"],
                        Keywords=row["keywords"],
                        Summary=row["summary"],
                        Metadata=row["metadata"],
                        Createddate=row["createddate"],
                        Updateddate=row["updateddate"],
                        Source=row["source"],
                        Documentid=row["documentid"],
                        Recordstatus=row["recordstatus"]
                    )
                    for row in rows
                ]

                response.Data = bottrainingmaps
                response.Success = True
                response.Message = "Bot training maps fetched successfully"

        except Exception as ex:
            logger.error(f"Error fetching bot training maps by bot ID: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching bot training maps: {str(ex)}"
            response.Data = []

        return response

    async def update_async(self, entity: UpdateBottrainingmap) -> UResponse:
        """Update an existing bot training map."""
        response = UResponse(Status=0, Message="Bot training map updated successfully")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if entity exists
                result = await session.execute(
                    text("""
                        SELECT id FROM bottrainingmap
                        WHERE id = :id
                    """),
                    {"id": entity.Id}
                )
                existing = result.mappings().first()

                if existing is None:
                    response.Status = 1
                    response.Message = f"Bot training map with ID {entity.Id} not found"
                    return response

                # Update entity
                await session.execute(
                    text("""
                        UPDATE bottrainingmap
                        SET botid = :botid,
                            clientid = :clientid,
                            content = :content,
                            trainingtype = :trainingtype,
                            title = :title,
                            keywords = :keywords,
                            summary = :summary,
                            metadata = :metadata,
                            source = :source,
                            documentid = :documentid,
                            updateddate = :updated_date
                        WHERE id = :id
                    """),
                    {
                        "botid": entity.Botid,
                        "clientid": entity.Clientid,
                        "content": entity.Content,
                        "trainingtype": entity.Trainingtype,
                        "title": entity.Title,
                        "keywords": entity.Keywords,
                        "summary": entity.Summary,
                        "metadata": entity.Metadata,
                        "source": entity.Source,
                        "documentid": entity.Documentid,
                        "updated_date": datetime.now(),
                        "id": entity.Id,
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error updating bot training map: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while updating bot training map: {str(ex)}"

        return response

    async def delete_async(self, id: int) -> UResponse:
        """Soft delete a bot training map by setting recordstatus to 0."""
        response = UResponse(Status=0, Message="Bot training map deleted successfully")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if entity exists
                result = await session.execute(
                    text("""
                        SELECT id FROM bottrainingmap
                        WHERE id = :id
                    """),
                    {"id": id}
                )
                entity = result.mappings().first()

                if entity is None:
                    response.Status = 1
                    response.Message = f"Bot training map with ID {id} not found"
                    return response

                # Soft delete by setting recordstatus to 0
                await session.execute(
                    text("""
                        UPDATE bottrainingmap
                        SET recordstatus = -1,
                            updateddate = :updated_date
                        WHERE id = :id
                    """),
                    {
                        "updated_date": datetime.now(),
                        "id": id,
                    }
                )
                await session.commit()

        except Exception as ex:
            logger.error(f"Error deleting bot training map: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting bot training map: {str(ex)}"

        return response
