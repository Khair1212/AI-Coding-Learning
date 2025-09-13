from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: Optional[str] = None
    
    # SSLCommerz Payment Gateway
    sslcommerz_store_id: str = "testbox"
    sslcommerz_store_pass: str = "qwerty"  
    sslcommerz_sandbox: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()

def get_settings():
    return settings