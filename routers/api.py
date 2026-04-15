"""
FastAPI application setup with PostgreSQL lifespan management.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.logger_config import get_logger
from database.dbConnection.postgres_connection import (
    initialize_postgres_pool,
    close_postgres_pool,
    test_postgres_connection,
)
from routers.users.users_router import router as users_router
from routers.authentication.authentication_routers import router as auth_router
from routers.roles.roles_router import router as role_router
from routers.permission.permission_task_router import router as permission_task_router
from routers.permission.permission_router import router as permission_router
from routers.document.document_group_router import router as document_group_router
from routers.document.document_router import router as document_router
from routers.clients.clients_router import router as client_router
from routers.bot.bot_router import router as bot_router
from routers.bot.bot_training_router import router as bot_training_router
from routers.bot.bot_response_rating_router import router as bot_response_rating_router
from routers.conversations.conversations_router import router as conversations_router
from routers.database_table.database_tables_columns_router import router as database_table_column_router
from routers.database_table.database_table_router import router as database_table_router
from routers.brand.brand_router import router as brand_router
from routers.brand.brand_store_router import router as brand_store_router
from routers.concept_user_map.concept_user_map_router import router as concept_user_map_router
from routers.bot.bot_column_training_router import router as bot_column_training_router
from routers.bot.bot_special_training_router import router as bot_special_training_router
from routers.retraining.retraining_router import router as retraining_router
from routers.app_setting.app_setting_router import router as app_setting_router
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Initializes PostgreSQL pool on startup and closes it on shutdown.
    """
    logger.info("Application startup: Initializing database pool...")
    try:
        await initialize_postgres_pool()
        logger.info("Application startup: PostgreSQL pool initialized successfully")

        await test_postgres_connection()
        logger.info("Application startup: PostgreSQL connection verified")
    except Exception as e:
        logger.error(f"Application startup: Failed to initialize PostgreSQL: {str(e)}")
        raise

    logger.info("Application startup: FastAPI application ready")
    yield

    # Shutdown: close pool
    logger.info("Application shutdown: Closing database pool...")
    try:
        await close_postgres_pool()
        logger.info("Application shutdown: PostgreSQL pool closed")
    except Exception as e:
        logger.warning(f"Application shutdown: PostgreSQL pool close failed: {e}")

    logger.info("Application shutdown: Complete")


# Create FastAPI app with lifespan events
logger.info("Creating FastAPI application instance")
app = FastAPI(
    title="DBEngine Backend",
    description="FastAPI backend for user management with PostgreSQL and AI Bot along with the services for dbengine",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """
    Basic root endpoint.
    """
    return {"message": "This is DBEngine Backend"}

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
logger.info("CORS middleware configured to allow all origins (development mode)")

# Include routers
logger.info("Registering API routers")
app.include_router(users_router)
logger.info("Registered users router")
app.include_router(auth_router)
logger.info("Registered authentication router")
app.include_router(role_router)
logger.info("Registered roles router")
app.include_router(permission_task_router)
logger.info("Registered permission task router")
app.include_router(permission_router)
logger.info("Registered permission router")
app.include_router(document_group_router)
logger.info("Registered document group router")
app.include_router(document_router)
logger.info("Registered document router")
app.include_router(client_router)
logger.info("Registered clients router")
app.include_router(bot_router)
logger.info("Registered bots router")
# Testing of create general training for chatbot and the create training of the database chatbot are pending 
app.include_router(bot_training_router)  
logger.info("Registered bot trainings router")
app.include_router(bot_response_rating_router)
logger.info("Registered bot response rating router")
app.include_router(conversations_router) # Get response yet to be implemented 
logger.info("Registered conversations router")
app.include_router(database_table_column_router)
logger.info("Registered database table column router")
app.include_router(database_table_router)
logger.info("Registered database table router")
app.include_router(brand_router)
logger.info("Registered brand router")
app.include_router(brand_store_router)
logger.info("Registered brand store router")
app.include_router(concept_user_map_router)
logger.info("Registered concept user map router")
app.include_router(bot_column_training_router)
logger.info("Registered bot column training router")
app.include_router(bot_special_training_router)
logger.info("Registered bot special training router")
app.include_router(retraining_router)
logger.info("Registered retraining router")
app.include_router(app_setting_router)
logger.info("Registered app settings router")