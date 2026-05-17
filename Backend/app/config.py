"""
Application configuration management using Pydantic Settings.
"""
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://supbuddy:password@localhost:5432/supbuddy",
        description="PostgreSQL database URL with asyncpg driver"
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")
    
    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 route prefix")
    api_title: str = Field(default="SupBuddy Logistics API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_description: str = Field(
        default="Logistics shipment tracking system with SLA monitoring and AI-powered exception analysis",
        description="API description"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Scheduler
    scheduler_enabled: bool = Field(default=True, description="Enable APScheduler")
    tracking_pull_interval_minutes: int = Field(
        default=5,
        description="Interval for pulling tracking data (minutes)"
    )
    sla_eval_interval_minutes: int = Field(
        default=10,
        description="Interval for SLA evaluation (minutes)"
    )
    
    # Agent
    watsonx_api_url: str = Field(
        default="https://api.watsonx.ai/v1",
        description="Watsonx API base URL"
    )
    watsonx_api_key: str = Field(default="mock", description="Watsonx API key")
    agent_timeout_seconds: int = Field(default=30, description="Agent API timeout")
    
    # Context Collection
    context_collection_timeout: int = Field(
        default=20,
        description="Overall timeout for context collection (seconds)"
    )
    context_tool_timeout: int = Field(
        default=10,
        description="Timeout per individual context tool (seconds)"
    )
    context_retry_enabled: bool = Field(
        default=True,
        description="Enable retry logic for failed context tools"
    )
    context_max_retries: int = Field(
        default=1,
        description="Maximum number of retries per context tool"
    )
    context_parallel_execution: bool = Field(
        default=True,
        description="Execute context tools in parallel"
    )
    
    # External APIs
    weather_api_key: str = Field(default="mock", description="Weather API key")
    traffic_api_key: str = Field(default="mock", description="Traffic API key")
    port_api_key: str = Field(default="mock", description="Port status API key")
    news_api_key: str = Field(default="mock", description="News API key")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.database_url.replace("+asyncpg", "")


# Global settings instance
settings = Settings()

# Made with Bob
