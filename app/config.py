from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    test_database_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()