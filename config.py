"""
Configuration Module
Handles loading environment variables and secrets from .env file or environment.
All secrets and authentication credentials are loaded from environment variables.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")


def load_environment():
    """Load environment variables from .env file if it exists"""
    if DOTENV_AVAILABLE:
        # Look for .env file in the same directory as this config file
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ Loaded environment variables from {env_path}")
        else:
            print(f"⚠ No .env file found at {env_path}")
            print("  Using environment variables from system or defaults")
    else:
        print("⚠ python-dotenv not available. Using system environment variables only")


# Load environment variables on import
load_environment()


class Config:
    """Configuration class for managing secrets and settings"""
    
    # Authentication
    AUTH_USERNAME: Optional[str] = os.getenv("AUTH_USERNAME", None)
    AUTH_PASSWORD: Optional[str] = os.getenv("AUTH_PASSWORD", None)
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() in ("true", "1", "yes")
    
    # API Keys (if needed for future AI services)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    CUSTOM_AI_API_KEY: Optional[str] = os.getenv("CUSTOM_AI_API_KEY", None)
    CUSTOM_AI_BASE_URL: Optional[str] = os.getenv("CUSTOM_AI_BASE_URL", None)
    
    # Server Configuration
    SERVER_NAME: str = os.getenv("SERVER_NAME", "127.0.0.1")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "7860"))
    SHARE: bool = os.getenv("SHARE", "false").lower() in ("true", "1", "yes")
    
    # Storage Paths
    DOCUMENTS_STORAGE_DIR: str = os.getenv("DOCUMENTS_STORAGE_DIR", "./uploaded_documents")
    KNOWLEDGE_BASE_DIR: str = os.getenv("KNOWLEDGE_BASE_DIR", "./knowledge_base")
    
    # Security Settings
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY", None)
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour default
    
    # Google Drive Integration
    GOOGLE_DRIVE_ENABLED: bool = os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() in ("true", "1", "yes")
    GOOGLE_DRIVE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_DRIVE_CLIENT_ID", None)
    GOOGLE_DRIVE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET", None)
    GOOGLE_DRIVE_CREDENTIALS_FILE: Optional[str] = os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE", None)  # Path to credentials.json
    GOOGLE_DRIVE_TOKEN_FILE: Optional[str] = os.getenv("GOOGLE_DRIVE_TOKEN_FILE", "./google_drive_token.json")
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = os.getenv("GOOGLE_DRIVE_FOLDER_ID", None)  # Optional: specific folder to sync
    
    @classmethod
    def get_auth_tuple(cls) -> Optional[Tuple[str, str]]:
        """Get authentication tuple for Gradio if auth is enabled"""
        if cls.AUTH_ENABLED and cls.AUTH_USERNAME and cls.AUTH_PASSWORD:
            return (cls.AUTH_USERNAME, cls.AUTH_PASSWORD)
        return None
    
    @classmethod
    def validate_auth_config(cls) -> bool:
        """Validate that authentication is properly configured"""
        if cls.AUTH_ENABLED:
            if not cls.AUTH_USERNAME or not cls.AUTH_PASSWORD:
                print("⚠ WARNING: AUTH_ENABLED is True but AUTH_USERNAME or AUTH_PASSWORD is missing!")
                print("  Authentication will be disabled.")
                return False
            return True
        return True
    
    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration (without sensitive data)"""
        print("\n" + "="*60)
        print("Configuration Summary")
        print("="*60)
        print(f"Authentication: {'ENABLED' if cls.AUTH_ENABLED and cls.validate_auth_config() else 'DISABLED'}")
        if cls.AUTH_ENABLED:
            print(f"  Username: {cls.AUTH_USERNAME}")
            print(f"  Password: {'*' * len(cls.AUTH_PASSWORD) if cls.AUTH_PASSWORD else 'NOT SET'}")
        print(f"Server: {cls.SERVER_NAME}:{cls.SERVER_PORT}")
        print(f"Share: {cls.SHARE}")
        print(f"Documents Storage: {cls.DOCUMENTS_STORAGE_DIR}")
        print(f"Knowledge Base: {cls.KNOWLEDGE_BASE_DIR}")
        print(f"Session Timeout: {cls.SESSION_TIMEOUT}s")
        print(f"Google Drive: {'ENABLED' if cls.GOOGLE_DRIVE_ENABLED else 'DISABLED'}")
        if cls.GOOGLE_DRIVE_ENABLED:
            print(f"  Folder ID: {cls.GOOGLE_DRIVE_FOLDER_ID or 'All accessible files'}")
        print("="*60 + "\n")


# Validate configuration on import
Config.validate_auth_config()
