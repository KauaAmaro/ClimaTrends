from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ClimaTrends"
    OPENWEATHER_API_KEY: str = "test_key"
    DATABASE_URL: str = "postgresql://climatrends:climatrends@localhost/climatrends_db"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()