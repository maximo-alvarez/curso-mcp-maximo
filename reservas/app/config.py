from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str = "sqlite:///./reservas.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    LOG_LEVEL: str = "INFO"
    MCP_DEMO_USER_EMAIL: str = "demo@reservas.local"
    MCP_DEMO_PASSWORD: str = "demo1234"
    MCP_ISSUER_URL: str = "http://127.0.0.1:8000"
    MCP_RESOURCE_URL: str = "http://127.0.0.1:8000/mcp"

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
