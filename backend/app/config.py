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

    # OpenAI
    openai_api_key: str = ""
    openrouter_api_key: str = ""

    # Resend
    resend_api_key: str = ""
    email_from: str = "meetings@example.com"

    # Storage
    upload_dir: str = "./uploads"

    # Zoom
    zoom_client_id: str = ""
    zoom_client_secret: str = ""
    zoom_secret_token: str = ""
    zoom_bot_jid: str = ""
    zoom_account_id: str = ""
    zoom_webhook_secret_token: str = ""
    zoom_access_token: str = ""
    zoom_refresh_token: str = ""
    zoom_redirect_uri: str = ""
    zoom_skip_signature_verification: bool = True  # Set to True for local testing only
    zoom_sdk_key: str = ""
    zoom_sdk_secret: str = ""

    zoomrec_image: str = "kastldratza/zoomrec:latest"
    zoomrec_timezone: str = "UTC"
    zoom_display_name: str = "Spoon Bot"

    recall_api_key: str = ""
    recall_region: str = "us-east-1"
    recall_base_url: str = "https://api.recall.ai/v1"
    recall_webhook_secret: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
