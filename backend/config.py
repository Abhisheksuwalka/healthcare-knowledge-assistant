"""
Configuration management for Healthcare Knowledge Assistant
Handles environment variables and application settings
Adapted for Gemini API (Google AI) as primary provider
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    All values are validated using Pydantic v2
    """
    
    # ===== Gemini API Settings (Primary) =====
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Gemini API key (required; get from https://aistudio.google.com/app/apikey)"
    )
    
    # ===== OpenAI Settings (Fallback) =====
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key (fallback if Gemini not configured)"
    )
    
    # ===== Application Settings =====
    APP_NAME: str = "Healthcare Knowledge Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG_MODE: bool = Field(
        default=False,
        description="Enable debug logging and auto-reload"
    )
    
    # ===== Vector Database Settings =====
    CHROMA_PERSIST_DIRECTORY: str = Field(
        default="./vectordb/chroma_db",
        description="ChromaDB persistent storage directory"
    )
    CHROMA_COLLECTION_NAME: str = Field(
        default="healthcare_docs",
        description="ChromaDB collection name"
    )
    
    # ===== Document Processing Settings =====
    DOCUMENTS_PATH: str = Field(
        default="./data/sample_docs",
        description="Path to healthcare documents"
    )
    CHUNK_SIZE: int = Field(
        default=1000,
        description="Text chunk size for splitting documents (tokens)"
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Overlap between chunks (tokens)"
    )
    
    # ===== RAG Settings =====
    RETRIEVAL_TOP_K: int = Field(
        default=5,
        description="Number of document chunks to retrieve per query"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.0,
        description="LLM temperature (0.0 = deterministic, 1.0 = creative)"
    )
    LLM_MAX_OUTPUT_TOKENS: int = Field(
        default=1000,
        description="Maximum tokens for LLM response"
    )
    
    # ===== Model Settings =====
    EMBEDDING_MODEL: str = Field(
        default="models/gemini-embedding-001",
        description="Embedding model name (Gemini: models/gemini-embedding-001)"
    )
    CHAT_MODEL: str = Field(
        default="models/gemini-2.5-flash",  # Or models/gemini-2.5-flash for faster/cheaper
        description="Chat model name (Gemini Pro 2.5)"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def is_gemini_configured(self) -> bool:
        """
        Check if Gemini API is properly configured
        
        Returns:
            True if API key is set
        """
        return self.GEMINI_API_KEY is not None
    
    def is_openai_configured(self) -> bool:
        """
        Check if OpenAI is properly configured
        
        Returns:
            True if OpenAI API key is set
        """
        return self.OPENAI_API_KEY is not None
    
    def get_llm_config(self) -> dict:
        """
        Get configuration for LLM client
        
        Returns:
            Dictionary with LLM configuration
            
        Raises:
            ValueError: If neither Gemini nor OpenAI is configured
        """
        if self.is_gemini_configured():
            return {
                "provider": "gemini",
                "api_key": self.GEMINI_API_KEY,
                "model": self.CHAT_MODEL
            }
        elif self.is_openai_configured():
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.CHAT_MODEL
            }
        else:
            raise ValueError(
                "❌ Neither Gemini nor OpenAI is properly configured. "
                "Please set GEMINI_API_KEY in .env file for primary support."
            )
    
    def get_embedding_config(self) -> dict:
        """
        Get configuration for embedding client
        
        Returns:
            Dictionary with embedding configuration
            
        Raises:
            ValueError: If neither Gemini nor OpenAI is configured
        """
        if self.is_gemini_configured():
            return {
                "provider": "gemini",
                "api_key": self.GEMINI_API_KEY,
                "model": self.EMBEDDING_MODEL
            }
        elif self.is_openai_configured():
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.EMBEDDING_MODEL
            }
        else:
            raise ValueError(
                "❌ Neither Gemini nor OpenAI is properly configured for embeddings. "
                "Please set GEMINI_API_KEY in .env file."
            )


# Create global settings instance
settings = Settings()

# Validate configuration on startup
if not settings.is_gemini_configured() and not settings.is_openai_configured():
    raise ValueError(
        "❌ Application is not properly configured.\n"
        "Please set GEMINI_API_KEY in your .env file for Gemini support."
    )