import logging
import sys
import uvicorn
import asyncio

from routers.api import app
from config.logger_config import get_logger

# Configure logging - force it to be visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)


logger = get_logger(__name__)


async def startup():
    """Application startup tasks."""
    logger.info("Application starting up...")
    logger.info("Application started successfully")


if __name__ == "__main__":
    asyncio.run(startup())
    logger.info("Server starting...")
    uvicorn.run(
        "routers.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        use_colors=True
    )