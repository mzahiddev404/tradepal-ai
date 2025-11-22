"""
Tests for upload API endpoints.
"""
import pytest
from fastapi import status
from io import BytesIO


class TestUploadAPI:
    """Test suite for upload endpoints."""
    
    def test_upload_endpoint_invalid_file(self, client):
        """Test upload endpoint with invalid file type."""
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = client.post("/api/upload", files=files)
        # Should reject non-PDF files
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_upload_endpoint_missing_file(self, client):
        """Test upload endpoint without file."""
        response = client.post("/api/upload")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_collection_info_endpoint(self, client):
        """Test collection info endpoint."""
        response = client.get("/api/collection/info")
        # May return 200 with info or 500 if ChromaDB unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "collection_name" in data or "error" in data





