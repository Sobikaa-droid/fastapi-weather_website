import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

load_dotenv()

class AuthJWT(BaseModel):
    PRIVATE_KEY_PATH: Path = Path(os.getenv("PRIVATE_KEY_PATH"))
    PUBLIC_KEY_PATH: Path = Path(os.getenv("PUBLIC_KEY_PATH"))
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class Settings(BaseSettings):
    app_name: str = "Weather API"
    api_v1_prefix: str = "/api/v1"
    auth_jwt: AuthJWT = AuthJWT()
    debug: bool = True


settings = Settings()