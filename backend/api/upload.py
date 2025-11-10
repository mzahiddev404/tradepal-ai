"""
PDF upload API endpoints.
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from models.upload import UploadResponse, CollectionInfoResponse
from utils.data_ingestion import ingestion_pipeline

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None)
):
    """
    Upload and process a PDF file.
    
    Args:
        file: PDF file to upload
        document_type: Optional document type (billing, technical, policy)
        
    Returns:
        UploadResponse with processing results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Create temporary file to save uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            # Read uploaded file content
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Ingest PDF into ChromaDB
            result = ingestion_pipeline.ingest_pdf(
                pdf_path=tmp_file_path,
                document_type=document_type
            )
            
            if result["status"] == "error":
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Unknown error processing PDF")
                )
            
            return UploadResponse(
                status="success",
                message=f"PDF processed and ingested successfully",
                document_id=result.get("document_id"),
                chunks_ingested=result.get("chunks_ingested"),
                source_file=result.get("source_file"),
                document_type=result.get("document_type")
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF upload: {str(e)}"
        )


@router.get("/collection/info", response_model=CollectionInfoResponse)
async def get_collection_info():
    """
    Get information about the ChromaDB collection.
    
    Returns:
        CollectionInfoResponse with collection statistics
    """
    try:
        info = ingestion_pipeline.get_collection_stats()
        
        if "error" in info:
            raise HTTPException(
                status_code=500,
                detail=info["error"]
            )
        
        return CollectionInfoResponse(
            collection_name=info["collection_name"],
            document_count=info["document_count"],
            persist_directory=info["persist_directory"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting collection info: {str(e)}"
        )

