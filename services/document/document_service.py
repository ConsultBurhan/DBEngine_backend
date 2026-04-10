"""Document service for managing document operations."""
from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from database.dbModel.document.document import Document
from models.service_models.document_group.document_service_model import (
    CreateDocument,
    DocumentDeleteResponse,
    DocumentList,
    UplopadTranslatedDocument,
)
from models.common import ResponseData, UResponse
from config.logger_config import get_logger

logger = get_logger(__name__)


class DocumentService:
    """Service for document operations including CRUD and external service integration."""

    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
        translator_client: Optional[httpx.AsyncClient] = None,
        chatbot_client: Optional[httpx.AsyncClient] = None,
    ):
        self._client_id = client_id
        self._user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()
        self._translator_client = translator_client
        self._chatbot_client = chatbot_client

    async def get_all_documents_async(
        self, document_group_id: int
    ) -> ResponseData[List[DocumentList]]:
        """Get all documents for a document group."""
        response = ResponseData[List[DocumentList]](
            Success=True,
            Message="Documents fetched successfully",
            Data=[],
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT 
                        d.id,
                        d.documentname,
                        d.url,
                        d.documentgroupid,
                        dg.documentgroupname,
                        d.clientid,
                        d.botid,
                        d.noofchunks,
                        d.createddate,
                        d.createdby,
                        d.updateddate,
                        d.updatedby,
                        d.status,
                        d.embeddingdb,
                        d.embeddingdetails,
                        d.fileextension,
                        d.documentstatus
                    FROM documents d
                    INNER JOIN documentgroups dg ON d.documentgroupid = dg.id
                    WHERE d.documentgroupid = :document_group_id 
                        AND d.status = 1
                    ORDER BY d.documentname
                """)
                result = await session.execute(
                    query, {"document_group_id": document_group_id}
                )
                rows = result.mappings().all()

                documents = [
                    DocumentList(
                        Id=row["id"],
                        Documentname=row["documentname"],
                        Url=row["url"],
                        Documentgroupid=row["documentgroupid"],
                        DocumentGroupName=row["documentgroupname"],
                        Clientid=row["clientid"],
                        Botid=row["botid"],
                        Noofchunks=row["noofchunks"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                        Status=row["status"],
                        Embeddingdb=row["embeddingdb"],
                        Embeddingdetails=row["embeddingdetails"],
                        Fileextension=row["fileextension"],
                        DocumentStatus=row["documentstatus"],
                    )
                    for row in rows
                ]

                response.Data = documents

        except Exception as ex:
            logger.error(f"Error fetching documents for group {document_group_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching documents: {str(ex)}"
            response.Data = []

        return response

    async def get_document_by_id_async(
        self, document_id: int
    ) -> ResponseData[DocumentList]:
        """Get a document by ID."""
        response = ResponseData[DocumentList](
            Success=True,
            Message="Document fetched successfully",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT 
                        d.id,
                        d.documentname,
                        d.url,
                        d.documentgroupid,
                        dg.documentgroupname,
                        d.clientid,
                        d.botid,
                        d.noofchunks,
                        d.createddate,
                        d.createdby,
                        d.updateddate,
                        d.updatedby,
                        d.status,
                        d.embeddingdb,
                        d.embeddingdetails,
                        d.fileextension,
                        d.documentstatus
                    FROM documents d
                    INNER JOIN documentgroups dg ON d.documentgroupid = dg.id
                    WHERE d.id = :document_id AND d.status = 1
                    LIMIT 1
                """)
                result = await session.execute(query, {"document_id": document_id})
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Document with ID {document_id} not found"
                    return response

                response.Data = DocumentList(
                    Id=row["id"],
                    Documentname=row["documentname"],
                    Url=row["url"],
                    Documentgroupid=row["documentgroupid"],
                    DocumentGroupName=row["documentgroupname"],
                    Clientid=row["clientid"],
                    Botid=row["botid"],
                    Noofchunks=row["noofchunks`"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                    Status=row["status"],
                    Embeddingdb=row["embeddingdb"],
                    Embeddingdetails=row["embeddingdetails"],
                    Fileextension=row["fileextension"],
                    DocumentStatus=row["documentstatus"],
                )

        except Exception as ex:
            logger.error(f"Error fetching document {document_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching the document: {str(ex)}"
            response.Data = None

        return response

    async def upload_document_async(
        self, create_document: CreateDocument, document_url: str, file_extension: str
    ) -> UResponse:
        """Upload a new document."""
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                now = datetime.now()
                insert_query = text("""
                    INSERT INTO documents (
                        documentname, url, fileextension, documentgroupid,
                        clientid, botid, createddate, createdby, status, documentstatus
                    ) VALUES (
                        :document_name, :url, :file_extension, :document_group_id,
                        :client_id, :bot_id, :created_date, :created_by, :status, :document_status
                    ) RETURNING id
                """)
                result = await session.execute(
                    insert_query,
                    {
                        "document_name": create_document.Documentname,
                        "url": document_url,
                        "file_extension": file_extension,
                        "document_group_id": create_document.Documentgroupid,
                        "client_id": self._client_id,
                        "bot_id": create_document.Botid,
                        "created_date": now,
                        "created_by": str(self._user_id),
                        "status": 1,
                        "document_status": 1,  # Pending status
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Document uploaded and under process"

        except Exception as ex:
            logger.error(f"Error uploading document: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while uploading the document: {str(ex)}"

        return response

    async def upload_translated_document_async(
        self,
        translated_document: UplopadTranslatedDocument,
        document_url: str,
    ) -> UResponse:
        """Upload translated document and trigger training."""
        response = UResponse(Status=0, Message="")
        doc_info: Optional[Document] = None

        try:
            async with await self._db_manager.get_session() as session:
                # Get document info
                select_query = text("""
                    SELECT 
                        id, documentname, url, documentgroupid, clientid, botid,
                        noofchunks, createddate, createdby, updateddate, updatedby,
                        status, embeddingdb, embeddingdetails, fileextension,
                        translatedtexturl, documentstatus
                    FROM documents 
                    WHERE id = :document_id AND status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    select_query, {"document_id": translated_document.Documentid}
                )
                row = result.mappings().first()

                if row is None:
                    response.Status = 1
                    response.Message = "Document with provided Id can not be found"
                    return response

                doc_info = Document(
                    Id=row["id"],
                    Documentname=row["documentname"],
                    Url=row["url"],
                    Documentgroupid=row["documentgroupid"],
                    Clientid=row["clientid"],
                    Botid=row["botid"],
                    Noofchunks=row["noofchunks"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                    Status=row["status"],
                    Embeddingdb=row["embeddingdb"],
                    Embeddingdetails=row["embeddingdetails"],
                    Fileextension=row["fileextension"],
                    TranslatedtextUrl=row["translatedtexturl"],
                    DocumentStatus=row["documentstatus"],
                )

                if not document_url:
                    # Update status to failed
                    update_query = text("""
                        UPDATE documents 
                        SET documentstatus = :status
                        WHERE id = :document_id
                    """)
                    await session.execute(
                        update_query,
                        {
                            "status": 2,  # Failed
                            "document_id": translated_document.Documentid,
                        },
                    )
                    await session.commit()

                    response.Status = 1
                    response.Message = "Error while uploading document"
                    return response

                # Create training
                training_response = await self._create_document_training_to_chatbot(
                    document_url, doc_info.Botid or 0, doc_info.Clientid or 0, translated_document.Documentid
                )

                if training_response.Status != 0:
                    # Update status to failed
                    update_query = text("""
                        UPDATE documents 
                        SET documentstatus = :status
                        WHERE id = :document_id
                    """)
                    await session.execute(
                        update_query,
                        {
                            "status": 2,  # Failed
                            "document_id": translated_document.Documentid,
                        },
                    )
                    await session.commit()

                    response.Status = 1
                    response.Message = "Error while creating document embeddings"
                    return response

                # Update document with translated URL and success status
                update_query = text("""
                    UPDATE documents 
                    SET translatedtexturl = :url, documentstatus = :status
                    WHERE id = :document_id
                """)
                await session.execute(
                    update_query,
                    {
                        "url": document_url,
                        "status": 0,  # Completed
                        "document_id": translated_document.Documentid,
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Document uploaded successfully"

        except Exception as ex:
            logger.error(f"Error uploading translated document: {ex}")
            if doc_info:
                try:
                    async with await self._db_manager.get_session() as session:
                        update_query = text("""
                            UPDATE documents 
                            SET documentstatus = :status
                            WHERE id = :document_id
                        """)
                        await session.execute(
                            update_query,
                            {
                                "status": 2,  # Failed
                                "document_id": translated_document.Documentid,
                            },
                        )
                        await session.commit()
                except Exception as inner_ex:
                    logger.error(f"Error updating document status: {inner_ex}")

            response.Status = 1
            response.Message = f"An error occurred while creating the document: {str(ex)}"

        return response

    async def delete_document_async(
        self, document_id: int, bot_id: int, client_id: int, content_type: str = ""
    ) -> UResponse:
        """Delete a document and its chunks from external services."""
        response = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check document existence
                select_query = text("""
                    SELECT id FROM documents WHERE id = :document_id AND status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    select_query, {"document_id": document_id}
                )
                document = result.mappings().first()

                if document is None:
                    response.Status = 1
                    response.Message = f"Document with ID {document_id} not found."
                    return response

                # Call chatbot service to delete document chunks
                if self._chatbot_client:
                    request_payload = {
                        "document_id": document_id,
                        "bot_id": str(bot_id),
                        "client_id": str(client_id),
                        "content_type": content_type,
                    }

                    try:
                        chatbot_response = await self._chatbot_client.request(
                            method="DELETE",
                            url="/BotTraining/delete-document-chunks",
                            content=json.dumps(request_payload),
                            headers={"Content-Type": "application/json"},
                        )

                        if chatbot_response.status_code != 200:
                            response.Status = 1
                            response.Message = "Failed to delete document chunks from BotTraining service."
                            return response

                        response_content = chatbot_response.text
                        delete_response = DocumentDeleteResponse.parse_raw(response_content)

                        # Validate deletion success
                        if not delete_response.SupabaseDeleted or not delete_response.RedisDocumentDeleted:
                            response.Status = 1
                            response.Message = "Document chunks deletion incomplete (Supabase/Redis)."
                            return response

                    except Exception as ex:
                        logger.error(f"Error calling chatbot service: {ex}")
                        response.Status = 1
                        response.Message = f"Error calling chatbot service: {str(ex)}"
                        return response

                # Soft delete document locally
                update_query = text("""
                    UPDATE documents SET status = 0 WHERE id = :document_id
                """)
                await session.execute(update_query, {"document_id": document_id})
                await session.commit()

                response.Status = 0
                response.Message = "Document and associated chunks deleted successfully."

        except Exception as ex:
            logger.error(f"Error deleting document {document_id}: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting the document: {str(ex)}"

        return response

    async def _create_document_training_to_chatbot(
        self, translate_url: str, bot_id: int, client_id: int, document_id: int
    ) -> UResponse:
        """Create document training in chatbot service."""
        response = UResponse(Status=0, Message="")

        try:
            if self._chatbot_client:
                request_body = {
                    "Database_Url_groups": [],
                    "Document_url_groups": [translate_url],
                    "Schema_Url_groups": [],
                    "bot_id": str(bot_id),
                    "client_id": str(client_id),
                    "document_id": document_id,
                }

                chatbot_response = await self._chatbot_client.post(
                    "/BotTraining/train-Bot",
                    json=request_body,
                )

                response_content = chatbot_response.text

                if chatbot_response.status_code != 200:
                    response.Status = 1
                    response.Message = f"Bot training failed: {response_content}"
                    return response

            response.Status = 0
            response.Message = "Training uploaded and Bot training started successfully."

        except Exception as ex:
            logger.error(f"Error creating document training: {ex}")
            response.Status = 1
            response.Message = f"Error generating and uploading training file: {str(ex)}"

        return response
