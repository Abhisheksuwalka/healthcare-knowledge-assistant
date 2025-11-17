"""
FastAPI application for Healthcare Knowledge Assistant
Main entry point with all API endpoints
"""

import time
from datetime import datetime
from typing import Dict, Any

import asyncio
import json
from backend.tools.registry import tool_registry

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.models import (
    HealthCheckResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    ErrorResponse
)
from backend.document_processor import document_processor

from backend.rag_engine import RAGEngine
# from backend.rag_engine import rag_engine
rag_engine = RAGEngine()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-based Healthcare Knowledge Assistant API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for all unhandled exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.DEBUG_MODE else "An error occurred",
            timestamp=datetime.now().isoformat()
        ).model_dump()
    )


# ===== Endpoints =====

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - returns API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    Returns application status and vector database statistics
    """
    try:
        doc_count = document_processor.get_document_count()
        vector_db_status = "healthy" if doc_count > 0 else "empty"
        
        return HealthCheckResponse(
            status="healthy",
            version=settings.APP_VERSION,
            vector_db_status=vector_db_status,
            document_count=doc_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents into vector database
    
    Loads documents from configured directory, chunks them,
    creates embeddings, and stores in ChromaDB.
    
    Args:
        request: Ingestion request with options
    
    Returns:
        Ingestion statistics
    """
    try:
        docs_count, chunks_count, time_taken = document_processor.ingest_documents(
            force_reindex=request.force_reindex
        )
        
        return IngestResponse(
            success=True,
            message="Documents ingested successfully" if docs_count > 0 else "No new documents to ingest",
            documents_processed=docs_count,
            chunks_created=chunks_count,
            time_taken_seconds=round(time_taken, 2)
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the healthcare knowledge base
    
    Uses RAG to answer questions based on ingested documents
    with role-specific prompting and safety controls.
    
    Args:
        request: Query request with question and options
    
    Returns:
        Answer with sources and metadata
    """
    try:
        # Check if documents are ingested
        doc_count = document_processor.get_document_count()
        if doc_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents ingested. Please call /ingest endpoint first."
            )
        
        # Process query
        result = rag_engine.query(
            question=request.question,
            user_role=request.user_role,
            include_sources=request.include_sources
        )
        
        return QueryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@app.get("/stats", response_model=Dict[str, Any])
async def get_statistics():
    """
    Get application statistics
    Returns information about current state
    """
    try:
        doc_count = document_processor.get_document_count()
        
        if hasattr(settings, 'is_gemini_configured') and settings.is_gemini_configured():
            provider_str = "Gemini (Google AI)"
        elif settings.is_azure_configured():
            provider_str = "Azure OpenAI"
        else:
            provider_str = "OpenAI"

        return {
            "total_chunks": doc_count,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "embedding_model": settings.EMBEDDING_MODEL,
            "chat_model": settings.CHAT_MODEL,
            "retrieval_top_k": settings.RETRIEVAL_TOP_K,
            "collection_name": settings.CHROMA_COLLECTION_NAME,
            "provider": provider_str
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@app.get("/tools", response_model=Dict[str, Any])
async def list_available_tools():
    """
    List all available MCP tools and their schemas
    
    Returns:
        - tool names
        - tool schemas (for LLM function calling)
        - total count
    """
    try:
        return {
            "status": "success",
            "total_tools": len(tool_registry.get_tool_names()),
            "tools": tool_registry.get_tool_names(),
            "schemas": tool_registry.get_all_schemas()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )

@app.post("/execute-tool", response_model=Dict[str, Any])
async def execute_tool_manual(tool_name: str, params: Dict[str, Any] = None):
    """
    Manually execute a specific tool
    
    Args:
        tool_name: Name of the tool to execute
        params: Dictionary of parameters
    
    Returns:
        Tool execution result
    """
    try:
        if not params:
            params = {}
        
        result = await tool_registry.execute_tool(tool_name, **params)
        return {
            "status": "success",
            "tool": tool_name,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )

# Server startup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG_MODE
    )