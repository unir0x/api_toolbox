import os
import json
import sys
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, SecretStr, ValidationError

# --- Pydantic Settings Model ---
# Defines the structure and validation for all configuration parameters.

class ApiToken(BaseModel):
    description: str
    last_used: Optional[str] = None

class Settings(BaseModel):
    # From settings.json
    ADMIN_CREDENTIALS: Dict[str, str] = Field(..., description="Admin credentials for the web UI. Passwords should be hashed.")
    API_TOKENS: Dict[str, ApiToken] = Field(..., description="A dictionary of hashed API tokens and their metadata.")
    ALLOWED_EXTENSIONS: List[str] = Field(..., description="List of allowed file extensions for uploads.")
    LOG_FILE: str = Field("logs/app.log", description="Path to the application log file.")
    MAX_BYTES: int = Field(10 * 1024 * 1024, description="Maximum log file size in bytes.")
    BACKUP_COUNT: int = Field(5, description="Number of log file backups to keep.")
    LOG_LEVEL: str = Field("WARNING", description="Logging level (e.g., DEBUG, INFO, WARNING).")
    SESSION_TYPE: str = Field("redis", description="Session storage type. Should be 'redis'.")
    SESSION_PERMANENT: bool = Field(False, description="Whether sessions should be permanent.")
    MAX_UPLOAD_FILE_SIZE: int = Field(10 * 1024 * 1024, description="Maximum file upload size in bytes.")
    GUNICORN_ACCESS_LOG: str = Field("logs/access.log", description="Path for Gunicorn access logs.")
    GUNICORN_ERROR_LOG: str = Field("logs/error.log", description="Path for Gunicorn error logs.")

    # From environment variables
    SECRET_KEY: SecretStr = Field(..., description="A secret key for signing session data. Loaded from env.")
    REDIS_HOST: str = Field("localhost", description="Redis server hostname. Loaded from env.")
    REDIS_PORT: int = Field(6379, description="Redis server port. Loaded from env.")
    REDIS_DB: int = Field(0, description="Redis database number. Loaded from env.")

# --- Configuration Loading Logic ---

# Define SETTINGS_PATH at the module level so it can be imported elsewhere
SETTINGS_PATH = os.getenv("SETTINGS_PATH", "config/settings.json")

def load_configuration() -> Settings:
    """
    Loads configuration from a JSON file and environment variables,
    validates it using the Pydantic model, and returns a Settings object.
    """
    # 1. Load from JSON file
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings_from_file = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"CRITICAL: Could not read or parse settings file at '{SETTINGS_PATH}'. Error: {e}")
        sys.exit(1)

    # 2. Load from environment variables
    settings_from_env = {
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": os.getenv("REDIS_PORT"),
        "REDIS_DB": os.getenv("REDIS_DB"),
    }
    # Filter out None values so Pydantic defaults can apply if needed
    settings_from_env = {k: v for k, v in settings_from_env.items() if v is not None}

    # 3. Merge and Validate
    try:
        combined_settings = {**settings_from_file, **settings_from_env}
        return Settings(**combined_settings)
    except ValidationError as e:
        logging.error(f"CRITICAL: Configuration validation failed!\n{e}")
        sys.exit(1)

# --- Global Config Object ---
# This object is imported by other parts of the application.
Config = load_configuration()

