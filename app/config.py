from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str = "postgresql+asyncpg://tutorbot:tutorbot@postgres:5432/tutorbot"
    timezone: str = "Europe/Moscow"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
