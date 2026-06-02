"""
Configuration settings
"""
import os


class Settings:
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/deal_analysis"
    )

    # PostGIS
    POSTGIS_ENABLED = True

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

    # AI Integration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
    AI_MAX_TOKENS = 2000

    # Pipeline
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
    PIPELINE_TIMEOUT = int(os.getenv("PIPELINE_TIMEOUT", "3600"))

    # MinIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "proposals")


settings = Settings()