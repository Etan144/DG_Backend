from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DG Backend API"
    mongodb_url: str
    mongodb_db: str
    env: str = "development"
    secret_key: str
    sendgrid_api_key: str
    sendgrid_from_email: str = "noreply@deepfakeguard.com"

    class Config:
        env_file = ".env"

settings = Settings()