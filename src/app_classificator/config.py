from typing import Optional, Dict, Union, Any
from pydantic import (
    BaseSettings,
    validator,
    AnyHttpUrl,
    SecretStr,
    AnyUrl,
    parse_obj_as,
)
from pathlib import Path


class Settings(BaseSettings):
    """
    Settings for the application.
    """

    DEBUG: bool = True
    ENV: str = "dev"
    
    USE_CPU=True
    MODEL_PATH: str = "./models/model_0"

    # Sanic configuration
    # For more info take a look at https://sanicframework.org/guide/deployment/configuration.html#builtin-values
    LOGO: str = ""
    ACCESS_LOG: bool = True
    # REQUEST_MAX_SIZE: int = 2*1024*1024  # 2MB
    REQUEST_TIMEOUT: int = 60 * 2  # 5 min
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    WORKERS: int = 1

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
