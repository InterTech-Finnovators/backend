from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str
    port: int
    json_file: str

    class Config:
        env_file = ".env"

settings = Settings()