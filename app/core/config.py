from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DG Backend API"
    mongodb_url: str
    mongodb_db: str
    smtp_email: str
    smtp_password: str
    env: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()