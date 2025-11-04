"""
Database configuration and initialization.

Sets up ChromaDB and DuckDB connections for the application.
"""

import os
import duckdb
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional
import logging

from .settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections for ChromaDB and DuckDB.
    """

    def __init__(self):
        """Initialize database manager."""
        self._duckdb_conn: Optional[duckdb.DuckDBPyConnection] = None
        self._chroma_client: Optional[chromadb.Client] = None

    def get_duckdb_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Get or create DuckDB connection.

        Returns:
            duckdb.DuckDBPyConnection: DuckDB connection instance
        """
        if self._duckdb_conn is None:
            # Ensure database directory exists
            db_dir = os.path.dirname(settings.duckdb_database_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            # Create connection
            self._duckdb_conn = duckdb.connect(settings.duckdb_database_path)
            logger.info(f"DuckDB connection established: {settings.duckdb_database_path}")

            # Initialize schema if needed
            self._initialize_duckdb_schema()

        return self._duckdb_conn

    def get_chroma_client(self) -> chromadb.Client:
        """
        Get or create ChromaDB client.

        Returns:
            chromadb.Client: ChromaDB client instance
        """
        if self._chroma_client is None:
            # Ensure persist directory exists
            if not os.path.exists(settings.chroma_persist_directory):
                os.makedirs(settings.chroma_persist_directory, exist_ok=True)

            # Create persistent client
            self._chroma_client = chromadb.Client(
                ChromaSettings(
                    persist_directory=settings.chroma_persist_directory,
                    anonymized_telemetry=False,
                )
            )
            logger.info(f"ChromaDB client created: {settings.chroma_persist_directory}")

            # Initialize collections if needed
            self._initialize_chroma_collections()

        return self._chroma_client

    def _initialize_duckdb_schema(self):
        """
        Initialize DuckDB schema with required tables.

        Creates tables if they don't exist based on DATABASE-SCHEMA.md.
        """
        conn = self._duckdb_conn

        # Check if tables exist
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]

        if "media" not in table_names:
            logger.info("Initializing DuckDB schema...")
            # Schema initialization will be handled by migration scripts
            # For now, just log that initialization is needed
            logger.warning(
                "Database schema not initialized. Run migrations to create tables."
            )

    def _initialize_chroma_collections(self):
        """
        Initialize ChromaDB collections.

        Creates collections if they don't exist.
        """
        client = self._chroma_client

        # Get or create media embeddings collection
        try:
            client.get_collection(settings.chroma_collection_media)
            logger.info(f"Collection '{settings.chroma_collection_media}' already exists")
        except Exception:
            client.create_collection(
                name=settings.chroma_collection_media,
                metadata={"description": "Media content embeddings for semantic search"},
            )
            logger.info(f"Created collection '{settings.chroma_collection_media}'")

        # Get or create mashup concepts collection
        try:
            client.get_collection(settings.chroma_collection_mashups)
            logger.info(f"Collection '{settings.chroma_collection_mashups}' already exists")
        except Exception:
            client.create_collection(
                name=settings.chroma_collection_mashups,
                metadata={"description": "AI-generated mashup concepts and summaries"},
            )
            logger.info(f"Created collection '{settings.chroma_collection_mashups}'")

    def close_connections(self):
        """
        Close all database connections.

        Should be called on application shutdown.
        """
        if self._duckdb_conn:
            self._duckdb_conn.close()
            logger.info("DuckDB connection closed")
            self._duckdb_conn = None

        # ChromaDB client doesn't need explicit closing
        self._chroma_client = None


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions
def get_duckdb() -> duckdb.DuckDBPyConnection:
    """
    Get DuckDB connection.

    Returns:
        duckdb.DuckDBPyConnection: DuckDB connection
    """
    return db_manager.get_duckdb_connection()


def get_chroma() -> chromadb.Client:
    """
    Get ChromaDB client.

    Returns:
        chromadb.Client: ChromaDB client
    """
    return db_manager.get_chroma_client()
