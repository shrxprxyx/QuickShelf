from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    clerk_jwks_url: str
    frontend_url: str = "http://localhost:3000"
    fine_per_day: int = 10
    supabase_url: str | None = None
    supabase_key: str | None = None


settings = Settings()