"""Document service for managing document operations."""
from __future__ import annotations
from typing import List, Optional
import json
from datetime import datetime

from models.service_models.document.document_service_model import (
    DocumentList,
    CreateDocument,
    UploadTranslatedDocument,
    DocumentDeleteResponse
)
from models.common import ResponseData, UResponse
from database.dbConnection.postgres_connection import PostgresConnectionManager, get_postgres_manager
from services.fileupload.file_upload_service import upload_file
from sqlalchemy import text
from config.logger_config import get_logger
from dotenv import load_dotenv
import os
import httpx

logger = get_logger(__name__)
load_dotenv()

# Chatbot configuration from environment variables
CHATBOT_BASE_URL = os.getenv("CHATBOT_BASE_URL")
CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")
CHATBOT_TIMEOUT_SECONDS = int(os.getenv("CHATBOT_TIMEOUT_SECONDS", "3000"))

# Validate chatbot configuration
if not CHATBOT_BASE_URL:
    raise ValueError("CHATBOT_BASE_URL environment variable is not set")
if not CHATBOT_API_KEY:
    raise ValueError("CHATBOT_API_KEY environment variable is not set")



class DocumentService:
    def __init__(
        self,
        client_id: int = 0,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self.client_id = client_id
        self.user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_documents_async(
        self, document_group_id: int
    ) -> ResponseData[List[DocumentList]]:
        """Get all documents by document group ID with their group names."""
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
                        d.documentgroupid,
                        g.documentgroupname as documentgroupname,
                        d.clientid,
                        d.botid,
                        d.status,
                        d.createddate,
                        d.createdby,
                        d.updateddate,
                        d.updatedby,
                        d.document_status,
                        d.fileextension
                    FROM documents d
                    INNER JOIN documentgroups g ON d.documentgroupid = g.id
                    WHERE d.documentgroupid = :document_group_id AND d.status = 1
                    ORDER BY d.documentname ASC
                """)
                result = await session.execute(
                    query, {"document_group_id": document_group_id}
                )
                rows = result.mappings().all()

                documents = [
                    DocumentList(
                        Id=row["id"],
                        Documentname=row["documentname"],
                        Documentgroupid=row["documentgroupid"],
                        DocumentGroupName=row["documentgroupname"],
                        Clientid=row["clientid"],
                        Botid=row["botid"],
                        Status=row["status"],
                        Createddate=row["createddate"],
                        Createdby=row["createdby"],
                        Updateddate=row["updateddate"],
                        Updatedby=row["updatedby"],
                        DocumentStatus=row["document_status"],
                        Fileextension=row["fileextension"],
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
        """Get a single document by ID with its group name."""
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
                        d.documentgroupid,
                        g.documentgroupname as documentgroupname,
                        d.clientid,
                        d.botid,
                        d.status,
                        d.createddate,
                        d.createdby,
                        d.updateddate,
                        d.updatedby,
                        d.document_status,
                        d.fileextension
                    FROM documents d
                    INNER JOIN documentgroups g ON d.documentgroupid = g.id
                    WHERE d.id = :document_id AND d.status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    query, {"document_id": document_id}
                )
                row = result.mappings().first()

                if row is None:
                    response.Success = False
                    response.Message = f"Document with ID {document_id} not found"
                    response.Data = None
                    return response

                response.Data = DocumentList(
                    Id=row["id"],
                    Documentname=row["documentname"],
                    Documentgroupid=row["documentgroupid"],
                    DocumentGroupName=row["documentgroupname"],
                    Clientid=row["clientid"],
                    Botid=row["botid"],
                    Status=row["status"],
                    Createddate=row["createddate"],
                    Createdby=row["createdby"],
                    Updateddate=row["updateddate"],
                    Updatedby=row["updatedby"],
                    DocumentStatus=row["document_status"],
                    Fileextension=row["fileextension"],
                )

        except Exception as ex:
            logger.error(f"Error fetching document {document_id}: {ex}")
            response.Success = False
            response.Message = f"An error occurred while fetching the document: {str(ex)}"
            response.Data = None

        return response

    async def upload_document_async(
        self, create_document: CreateDocument
    ) -> UResponse:
        """Upload a document to storage and create a database record."""
        response = UResponse(Status=0, Message="")

        try:
            if create_document.Document is None:
                response.Status = 1
                response.Message = "Document cannot be empty"
                return response

            document_url = await upload_file(create_document.Document)
            if not document_url:
                response.Status = 1
                response.Message = "Error while uploading document"
                return response

            file_extension = (
                create_document.Document.filename.split(".")[-1]
                if "." in create_document.Document.filename
                else ""
            )

            now = datetime.now()
            async with await self._db_manager.get_session() as session:
                insert_query = text("""
                    INSERT INTO documents (
                        documentname, url, fileextension, documentgroupid,
                        clientid, botid, createddate, createdby, status, document_status
                    ) VALUES (
                        :documentname, :url, :fileextension, :documentgroupid,
                        :clientid, :botid, :createddate, :createdby, :status, :document_status
                    ) RETURNING id
                """)
                await session.execute(
                    insert_query,
                    {
                        "documentname": create_document.Documentname,
                        "url": document_url,
                        "fileextension": file_extension,
                        "documentgroupid": create_document.Documentgroupid,
                        "clientid": self.client_id,
                        "botid": create_document.Botid,
                        "createddate": now,
                        "createdby": str(self.user_id),
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

    async def create_document_training_to_chatbot_async(
        self, translate_url: str, bot_id: int, client_id: int, document_id: int
    ) -> UResponse:
        """Send document to chatbot for training."""
        response = UResponse(Status=0, Message="")

        try:
            request_body = {
                "Database_Url_groups": [],
                "Document_url_groups": [translate_url],
                "Schema_Url_groups": [],
                "bot_id": str(bot_id),
                "client_id": str(client_id),
                "document_id": document_id,
            }

            url = "/BotTraining/train-Bot"
            async with httpx.AsyncClient(
                base_url=CHATBOT_BASE_URL,
                timeout=CHATBOT_TIMEOUT_SECONDS,
                headers={"X-API-Key": CHATBOT_API_KEY}
            ) as client:
                process_response = await client.post(url, json=request_body)

            if process_response.status_code != 200:
                response.Status = 1
                response.Message = f"Bot training failed: {process_response.text}"
                return response

            response.Status = 0
            response.Message = "Training uploaded and Bot training started successfully."

        except Exception as ex:
            logger.error(f"Error generating and uploading training file: {ex}")
            response.Status = 1
            response.Message = f"Error generating and uploading training file: {str(ex)}"

        return response

    async def delete_document_async(
        self, document_id: int, bot_id: int, client_id: int, content_type: str = ""
    ) -> UResponse:
        """Delete a document and its associated chunks."""
        response = UResponse(Status=0, Message="")

        try:
            # Check document existence
            async with await self._db_manager.get_session() as session:
                select_query = text("""
                    SELECT id FROM documents
                    WHERE id = :document_id AND status = 1
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

            # Delete document chunks from BotTraining service
            request_payload = {
                "document_id": document_id,
                "bot_id": str(bot_id),
                "client_id": str(client_id),
                "content_type": content_type
            }

            url = "/BotTraining/delete-document-chunks"
            async with httpx.AsyncClient(
                base_url=CHATBOT_BASE_URL,
                timeout=CHATBOT_TIMEOUT_SECONDS,
                headers={
                    "X-API-Key": CHATBOT_API_KEY,
                }
            ) as client:
                process_response = await client.request("DELETE", url, json=request_payload)
            if process_response.status_code != 200:
                response.Status = 1
                response.Message = "Failed to delete document chunks from BotTraining service."
                return response

            # Validate deletion success from JSON response
            response_content = process_response.json()
            if (
                not response_content.get("SupabaseDeleted")
                or not response_content.get("RedisDocumentDeleted")
            ):
                response.Status = 1
                response.Message = "Document chunks deletion incomplete (Supabase/Redis)."
                return response

            # Soft delete document locally
            async with await self._db_manager.get_session() as session:
                update_query = text("""
                    UPDATE documents
                    SET status = 0
                    WHERE id = :document_id
                """)
                await session.execute(
                    update_query, {"document_id": document_id}
                )
                await session.commit()

            response.Status = 0
            response.Message = "Document and associated chunks deleted successfully."

        except Exception as ex:
            logger.error(f"Error deleting document {document_id}: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while deleting the document: {str(ex)}"

        return response

    async def upload_translated_document_async(
        self, translated_document: UploadTranslatedDocument
    ) -> UResponse:
        """Upload a translated document and process it for training."""
        response = UResponse(Status=0, Message="")
        doc_info = None

        try:
            # Validate document is not empty
            if translated_document.Document is None:
                response.Status = 1
                response.Message = "Document can not be empty"
                return response

            # Find document by ID
            async with await self._db_manager.get_session() as session:
                select_query = text("""
                    SELECT id, botid, clientid, document_status, translatedtext_url
                    FROM documents
                    WHERE id = :document_id AND status = 1
                    LIMIT 1
                """)
                result = await session.execute(
                    select_query, {"document_id": translated_document.Documentid}
                )
                doc_info = result.mappings().first()

                if doc_info is None:
                    response.Status = 1
                    response.Message = "Document with provided Id can not be found"
                    return response

            # Upload translated document
            document_url = await upload_file(translated_document.Document)
            if not document_url:
                # Update document status to Failed
                async with await self._db_manager.get_session() as session:
                    update_query = text("""
                        UPDATE documents
                        SET document_status = 0
                        WHERE id = :document_id
                    """)
                    await session.execute(
                        update_query, {"document_id": translated_document.Documentid}
                    )
                    await session.commit()

                response.Status = 1
                response.Message = "Error while uploading document"
                return response

            # Create training for chatbot
            training_response = await self.create_document_training_to_chatbot_async(
                document_url,
                doc_info["botid"] or 0,
                doc_info["clientid"] or 0,
                translated_document.Documentid
            )

            if training_response.Status != 0:
                # Update document status to Failed
                async with await self._db_manager.get_session() as session:
                    update_query = text("""
                        UPDATE documents
                        SET document_status = 0
                        WHERE id = :document_id
                    """)
                    await session.execute(
                        update_query, {"document_id": translated_document.Documentid}
                    )
                    await session.commit()

                response.Status = 1
                response.Message = "Error while creating document embeddings"
                return response

            # Update document with translated URL and completed status
            async with await self._db_manager.get_session() as session:
                update_query = text("""
                    UPDATE documents
                    SET translatedtext_url = :translated_url, document_status = 2
                    WHERE id = :document_id
                """)
                await session.execute(
                    update_query,
                    {
                        "translated_url": document_url,
                        "document_id": translated_document.Documentid
                    }
                )
                await session.commit()

            response.Status = 0
            response.Message = "Document uploaded successfully"

        except Exception as ex:
            logger.error(f"Error uploading translated document: {ex}")
            # Update document status to Failed if doc_info exists
            if doc_info is not None:
                async with await self._db_manager.get_session() as session:
                    update_query = text("""
                        UPDATE documents
                        SET document_status = 0
                        WHERE id = :document_id
                    """)
                    await session.execute(
                        update_query, {"document_id": translated_document.Documentid}
                    )
                    await session.commit()

            response.Status = 1
            response.Message = f"An error occurred while creating the document: {str(ex)}"

        return response

