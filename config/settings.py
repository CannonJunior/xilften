"""
Application configuration settings.

Loads configuration from environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="xilften", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    app_port: int = Field(default=7575, description="Application port - MUST be 7575")
    app_host: str = Field(default="0.0.0.0", description="Application host")
    debug: bool = Field(default=False, description="Debug mode")

    # TMDB API Configuration
    tmdb_api_key: str = Field(
        default="", description="TMDB API key - get from themoviedb.org"
    )
    tmdb_base_url: str = Field(
        default="https://api.themoviedb.org/3", description="TMDB API base URL"
    )
    tmdb_image_base_url: str = Field(
        default="https://image.tmdb.org/t/p", description="TMDB image base URL"
    )
    tmdb_rate_limit: int = Field(default=40, description="TMDB rate limit (requests/10s)")

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama API base URL"
    )
    ollama_default_model: str = Field(
        default="qwen2.5:3b", description="Default Ollama model"
    )
    ollama_fallback_model: str = Field(
        default="llama3.1", description="Fallback Ollama model"
    )
    ollama_timeout: int = Field(default=60, description="Ollama request timeout (seconds)")

    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./database/chroma_data", description="ChromaDB persistence directory"
    )
    chroma_collection_media: str = Field(
        default="media_embeddings", description="Media embeddings collection name"
    )
    chroma_collection_mashups: str = Field(
        default="mashup_concepts", description="Mashup concepts collection name"
    )

    # DuckDB Configuration
    duckdb_database_path: str = Field(
        default="./database/xilften.duckdb", description="DuckDB database file path"
    )

    # CORS Settings
    cors_origins: str = Field(
        default="http://localhost:7575,http://localhost:3000,http://127.0.0.1:7575",
        description="Allowed CORS origins (comma-separated)",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )
    log_file: str = Field(default="./logs/xilften.log", description="Log file path")

    # Pagination Defaults
    default_page_size: int = Field(default=20, description="Default pagination page size")
    max_page_size: int = Field(default=100, description="Maximum pagination page size")

    # Cache Settings
    enable_cache: bool = Field(default=False, description="Enable response caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

    # Feature Flags
    enable_ai_features: bool = Field(default=True, description="Enable AI/Ollama features")
    enable_tmdb_sync: bool = Field(default=True, description="Enable TMDB synchronization")
    enable_telemetry: bool = Field(default=False, description="Enable telemetry")

    @validator("app_port")
    def validate_port(cls, v):
        """
        Validate that the port is 7575 as required by CLAUDE.md.

        Args:
            v (int): Port number

        Returns:
            int: Validated port number

        Raises:
            ValueError: If port is not 7575
        """
        if v != 7575:
            raise ValueError(
                "Port must be 7575. See CLAUDE.md for port requirements. "
                "Never change the port without explicit user permission."
            )
        return v

    def get_cors_origins_list(self) -> List[str]:
        """
        Get CORS origins as a list.

        Returns:
            List[str]: List of allowed CORS origins
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_tmdb_headers(self) -> dict:
        """
        Get headers for TMDB API requests.

        Returns:
            dict: Headers dictionary with authorization
        """
        return {
            "Authorization": f"Bearer {self.tmdb_api_key}",
            "Content-Type": "application/json",
        }


# Global settings instance
settings = Settings()
