"""
Configuration module for the AI Document Chat Agent.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_model_name: str = os.getenv("AZURE_OPENAI_MODEL_NAME")
    
    # Application Configuration
    upload_dir: str = "uploads"
    vector_store_dir: str = "vector_store"
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes")
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Vector Store Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Tokenizers Configuration
    tokenizers_parallelism: bool = Field(default=False, description="Enable/disable tokenizers parallelism")
    
    @validator('max_file_size', pre=True)
    def parse_max_file_size(cls, v):
        """Parse max_file_size, handling comments in the value."""
        if isinstance(v, str):
            # Remove comments and whitespace
            v = v.split('#')[0].strip()
            return int(v)
        return v
    
    @validator('debug', pre=True)
    def parse_debug(cls, v):
        """Parse debug flag, handling various string representations."""
        if isinstance(v, str):
            v = v.lower().strip()
            if v in ('true', '1', 'yes', 'on'):
                return True
            elif v in ('false', '0', 'no', 'off', 'warn', 'warning'):
                return False
        return bool(v)
    
    @validator('tokenizers_parallelism', pre=True)
    def parse_tokenizers_parallelism(cls, v):
        """Parse tokenizers_parallelism flag, handling various string representations."""
        if isinstance(v, str):
            v = v.lower().strip()
            if v in ('true', '1', 'yes', 'on'):
                return True
            elif v in ('false', '0', 'no', 'off'):
                return False
        return bool(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Set tokenizers parallelism environment variable
os.environ["TOKENIZERS_PARALLELISM"] = str(settings.tokenizers_parallelism).lower()

# Ensure required directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.vector_store_dir, exist_ok=True) 