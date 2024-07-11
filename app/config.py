# Path: app/config.py
# Description: This file contains code to load `.env` file and make a pydantic `BaseSettings` class which can be used to access environment variables in the application.

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Any
from app.logging import logger


class Settings(BaseSettings):
    # Environment Configuration
    ENV: str
    
    MODEL_PATH: str
    CUDA_VISIBLE_DEVICES: str
    
    #TODO: set cuda visible devices to environment variable
    # import os
    # os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # GPU-0
    
    HOST: str
    PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
