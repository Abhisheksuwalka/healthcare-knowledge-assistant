"""
Pydantic models for request/response validation
All models include detailed descriptions and examples
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    """User roles for query context and role-specific responses"""
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"
    BILLING = "billing"
    GENERAL = "general"


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint"""
    status: str = Field(description="Application status (healthy)")
    version: str = Field(description="Application version")
    vector_db_status: str = Field(description="Vector database status (healthy/empty)")
    document_count: int = Field(description="Number of documents indexed")


class IngestRequest(BaseModel):
    """Request body for document ingestion"""
    force_reindex: bool = Field(
        default=False,
        description="Force re-indexing even if documents already exist"
    )


class IngestResponse(BaseModel):
    """Response for document ingestion"""
    success: bool = Field(description="Whether ingestion was successful")
    message: str = Field(description="Status message")
    documents_processed: int = Field(description="Number of documents processed")
    chunks_created: int = Field(description="Number of text chunks created")
    time_taken_seconds: float = Field(description="Total time taken for ingestion")


class DocumentSource(BaseModel):
    """Information about a source document chunk"""
    filename: str = Field(description="Source document filename")
    chunk_index: int = Field(description="Index of chunk within document")
    relevance_score: float = Field(description="Relevance score (0-1)")
    content_preview: str = Field(description="Preview of chunk content (first 200 chars)")

class QueryRequest(BaseModel):
    """Request body for knowledge base query"""
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="User question about hospital policies",
        examples=["What are the visiting hours for ICU patients?"]
    )
    user_role: UserRole = Field(
        default=UserRole.GENERAL,
        description="User role for role-specific response tailoring"
    )
    include_sources: bool = Field(
        default=True,
        description="Whether to include source documents in response"
    )

# class QueryResponse(BaseModel):
#     """Response for knowledge base query"""
#     question: str = Field(description="Original question asked")
#     answer: str = Field(description="Generated answer from RAG pipeline")
#     sources: List[DocumentSource] = Field(
#         default=[],
#         description="Source documents used to generate answer"
#     )
#     user_role: str = Field(description="User role context")
#     disclaimer: str = Field(description="Safety disclaimer for medical information")
#     processing_time_seconds: float = Field(description="Query processing time")


class QueryResponse(BaseModel):
    """Response for knowledge base query"""
    question: str = Field(description="Original question asked")
    answer: str = Field(description="Generated answer from RAG pipeline")
    sources: List[DocumentSource] = Field(
        default=[],
        description="Source documents used to generate answer"
    )
    user_role: str = Field(description="User role context")
    disclaimer: str = Field(description="Safety disclaimer for medical information")
    processing_time_seconds: float = Field(description="Query processing time")
    tools_used: List[str] = Field(
        default=[],
        description="List of MCP tools used in generating response"  # NEW
    )


class ErrorResponse(BaseModel):
    """Response for error cases"""
    error: str = Field(description="Error type/title")
    detail: Optional[str] = Field(default=None, description="Detailed error message")
    timestamp: str = Field(description="ISO format timestamp of error")