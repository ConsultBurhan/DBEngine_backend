"""
PostgreSQL async database connection using SQLAlchemy + asyncpg.
"""

import ssl
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import asyncio
from config.settings import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SSL_MODE,
    POSTGRES_USERNAME,
)
from config.logger_config import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class PostgresConnectionManager:
    """Manages PostgreSQL async connection pool using SQLAlchemy + asyncpg."""

    def __init__(
        self,
        host: str = POSTGRES_HOST,
        port: int = POSTGRES_PORT,
        database: str = POSTGRES_DATABASE,
        username: str = POSTGRES_USERNAME,
        password: str = POSTGRES_PASSWORD,
        ssl_mode: str = POSTGRES_SSL_MODE,
    ):
        self._host = host
        self._port = port
        self._database = database
        self._username = username
        self._password = password
        self._ssl_mode = ssl_mode
        self._async_engine: Optional[AsyncEngine] = None
        self._async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    def _build_ssl_arg(self) -> ssl.SSLContext | None:
        """Map POSTGRES_SSL_MODE to SSL configuration for asyncpg."""
        mode = (self._ssl_mode or "").lower()

        if mode in ("require", "verify-ca", "verify-full"):
            ssl_context = ssl.create_default_context()
            if mode == "require":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context

        return None

    def _build_database_url(self) -> str:
        """Build async PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self._username}:{self._password}@{self._host}:{self._port}/{self._database}"

    async def initialize_pool(
        self,
        min_size: int = 1,
        max_size: int = 10,
        timeout: float = 60.0,
    ) -> AsyncEngine:
        """Initialize SQLAlchemy async engine once at startup."""
        if self._async_engine is not None:
            return self._async_engine

        ssl_context = self._build_ssl_arg()
        connect_args = {}
        if ssl_context:
            connect_args["ssl"] = ssl_context

        self._async_engine = create_async_engine(
            self._build_database_url(),
            pool_size=min_size,
            max_overflow=max_size - min_size,
            pool_timeout=timeout,
            pool_recycle=3600,
            echo=False,
            connect_args=connect_args,
        )

        self._async_session_maker = async_sessionmaker(
            bind=self._async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        logger.info("PostgreSQL SQLAlchemy async engine initialized")
        return self._async_engine

    def get_engine(self) -> AsyncEngine:
        """Return initialized SQLAlchemy async engine."""
        if self._async_engine is None:
            raise RuntimeError(
                "PostgreSQL engine not initialized. Call initialize_pool() at startup."
            )
        return self._async_engine

    def get_session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Return async session maker for creating sessions."""
        if self._async_session_maker is None:
            raise RuntimeError(
                "PostgreSQL session maker not initialized. Call initialize_pool() at startup."
            )
        return self._async_session_maker

    async def get_session(self) -> AsyncSession:
        """Get a new async session."""
        session_maker = self.get_session_maker()
        return session_maker()

    async def close_pool(self) -> None:
        if self._async_engine is None:
            return

        # Nullify session maker first to prevent new sessions
        self._async_session_maker = None

        try:
            await asyncio.wait_for(
                self._async_engine.dispose(close=True),
                timeout=5.0
            )
            logger.info("PostgreSQL SQLAlchemy async engine closed")
        except asyncio.TimeoutError:
            logger.warning("Engine dispose timed out — forcing shutdown")
        finally:
            self._async_engine = None

    async def test_connection(self) -> None:
        """Run a lightweight DB connectivity check."""
        from sqlalchemy import text
        engine = self.get_engine()

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("PostgreSQL SQLAlchemy async connection verified")


# ---------- Singleton instance for convenience ----------
_postgres_manager: Optional[PostgresConnectionManager] = None


def get_postgres_manager() -> PostgresConnectionManager:
    """Get or create the singleton Postgres connection manager instance."""
    global _postgres_manager
    if _postgres_manager is None:
        _postgres_manager = PostgresConnectionManager()
    return _postgres_manager


# ---------- Legacy compatibility functions ----------
async def initialize_postgres_pool(
    min_size: int = 1,
    max_size: int = 10,
    timeout: float = 60.0,
) -> AsyncEngine:
    """Initialize async engine using singleton manager."""
    return await get_postgres_manager().initialize_pool(min_size, max_size, timeout)


def get_postgres_engine() -> AsyncEngine:
    """Return initialized SQLAlchemy async engine from singleton."""
    return get_postgres_manager().get_engine()


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Return async session maker from singleton."""
    return get_postgres_manager().get_session_maker()


async def get_async_session() -> AsyncSession:
    """Get a new async session from singleton."""
    return await get_postgres_manager().get_session()


async def close_postgres_pool() -> None:
    """Close SQLAlchemy async engine from singleton."""
    await get_postgres_manager().close_pool()


async def test_postgres_connection() -> None:
    """Run a lightweight DB connectivity check using singleton."""
    await get_postgres_manager().test_connection()

