"""
Models for PDF upload endpoints.
"""
from pydantic import BaseModel
from typing import Optional, List


class UploadResponse(BaseModel):
    """Response model for PDF upload."""
    status: str
    message: str
    document_id: Optional[str] = None
    chunks_ingested: Optional[int] = None
    source_file: Optional[str] = None
    document_type: Optional[str] = None
    error: Optional[str] = None


class CollectionInfoResponse(BaseModel):
    """Response model for collection information."""
    collection_name: str
    document_count: int
    persist_directory: str

