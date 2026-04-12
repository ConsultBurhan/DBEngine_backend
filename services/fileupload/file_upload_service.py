import httpx
from fastapi import UploadFile
from config.logger_config import get_logger
from config.settings import (
    FILE_UPLOAD_API_URL,
    FILE_UPLOAD_BUCKET_NAME, 
    FILE_UPLOAD_PUBLIC_URL, 
    FILE_UPLOAD_KEY
)

logger = get_logger(__name__)
async def upload_file(file: UploadFile) -> str:
    """
    Uploads a file to the configured storage bucket and returns the public URL.
    
    Args:
        file: The uploaded file from a FastAPI endpoint.
        
    Returns:
        The public URL of the uploaded file.
        
    Raises:
        ValueError: If the file is empty or None.
        httpx.HTTPStatusError: If the upload request fails.
    """
    if file is None or file.size == 0:
        raise ValueError("File is empty or null")

    url = (
        f"{FILE_UPLOAD_API_URL}"
        f"?key={FILE_UPLOAD_KEY}"
        f"&bucketName={FILE_UPLOAD_BUCKET_NAME}"
    )

    file_content = await file.read()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                files={
                    "file": (
                        file.filename,
                        file_content,
                        file.content_type or "application/octet-stream",
                    )
                },
            )

            if response.status_code != 200:
                logger.error(
                    "Failed to upload file. Status: %s, Error: %s",
                    response.status_code,
                    response.text,
                )
                response.raise_for_status()

            uploaded_file_name = response.text.strip().strip('"').strip("'")
            uploaded_file_url = f"{FILE_UPLOAD_PUBLIC_URL}{uploaded_file_name}"

            logger.info("File uploaded successfully: %s", uploaded_file_name)

            return uploaded_file_url

    except httpx.HTTPStatusError as e:
        logger.error("HTTP error during file upload: %s", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error uploading file: %s", str(e))
        raise