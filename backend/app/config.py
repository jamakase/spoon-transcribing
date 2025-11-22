from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/meetings"

    # Redis/Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Whisper
    whisper_model: str = "base"

    # Resend
    resend_api_key: str = ""
    email_from: str = "meetings@example.com"

    # Storage
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"


settings = Settings()
