"""
Data ingestion pipeline for processing PDFs and storing in ChromaDB.
"""
import os
import uuid
from typing import List, Dict, Optional
from utils.chromadb_client import chromadb_client
from utils.pdf_processor import pdf_processor
from utils.csv_processor import csv_processor


class DataIngestionPipeline:
    """Pipeline for ingesting documents into ChromaDB."""
    
    def __init__(self):
        """Initialize the ingestion pipeline."""
        self.chromadb = chromadb_client
        self.pdf_processor = pdf_processor
        self.csv_processor = csv_processor
    
    def ingest_file(
        self,
        file_path: str,
        document_type: Optional[str] = None,
        additional_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest a file (PDF or CSV) into ChromaDB.
        
        Args:
            file_path: Path to the file
            document_type: Type of document
            additional_metadata: Additional metadata
            
        Returns:
            Dictionary with ingestion results
        """
        if file_path.lower().endswith('.pdf'):
            return self.ingest_pdf(file_path, document_type, additional_metadata)
        elif file_path.lower().endswith('.csv'):
            return self.ingest_csv(file_path, document_type, additional_metadata)
        else:
            return {
                "status": "error",
                "error": "Unsupported file type. Only PDF and CSV are supported.",
                "source_file": os.path.basename(file_path)
            }

    def ingest_csv(
        self,
        csv_path: str,
        document_type: Optional[str] = None,
        additional_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest a CSV file into ChromaDB.
        """
        try:
            # Process CSV
            chunks = self.csv_processor.process_csv(csv_path)
            
            if not chunks:
                raise Exception("No text extracted from CSV")
            
            # Prepare texts and metadatas for ChromaDB
            texts = [chunk["text"] for chunk in chunks]
            metadatas = []
            ids = []
            
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            for idx, chunk in enumerate(chunks):
                # Prepare metadata
                metadata = chunk["metadata"].copy()
                
                if document_type:
                    metadata["document_type"] = document_type
                
                if additional_metadata:
                    metadata.update(additional_metadata)
                
                metadata["document_id"] = doc_id
                metadata["source_file"] = os.path.basename(csv_path)
                
                metadatas.append(metadata)
                
                # Generate unique chunk ID
                chunk_id = f"{doc_id}_chunk_{idx}"
                ids.append(chunk_id)
            
            # Add to ChromaDB
            self.chromadb.add_documents(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_ingested": len(chunks),
                "source_file": os.path.basename(csv_path),
                "document_type": document_type or "unknown"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "source_file": os.path.basename(csv_path) if csv_path else "unknown"
            }

    def ingest_pdf(
        self,
        pdf_path: str,
        document_type: Optional[str] = None,
        additional_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest a PDF file into ChromaDB.
        
        Args:
            pdf_path: Path to the PDF file
            document_type: Type of document (billing, technical, policy)
            additional_metadata: Additional metadata to attach
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            # Process PDF
            chunks = self.pdf_processor.process_pdf(pdf_path)
            
            if not chunks:
                raise Exception("No text extracted from PDF")
            
            # Prepare texts and metadatas for ChromaDB
            texts = [chunk["text"] for chunk in chunks]
            metadatas = []
            ids = []
            
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            for idx, chunk in enumerate(chunks):
                # Prepare metadata
                metadata = chunk["metadata"].copy()
                
                if document_type:
                    metadata["document_type"] = document_type
                
                if additional_metadata:
                    metadata.update(additional_metadata)
                
                metadata["document_id"] = doc_id
                metadata["source_file"] = os.path.basename(pdf_path)
                
                metadatas.append(metadata)
                
                # Generate unique chunk ID
                chunk_id = f"{doc_id}_chunk_{idx}"
                ids.append(chunk_id)
            
            # Add to ChromaDB
            self.chromadb.add_documents(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_ingested": len(chunks),
                "source_file": os.path.basename(pdf_path),
                "document_type": document_type or "unknown"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "source_file": os.path.basename(pdf_path) if pdf_path else "unknown"
            }
    
    def ingest_multiple_pdfs(
        self,
        pdf_paths: List[str],
        document_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Ingest multiple PDF files.
        
        Args:
            pdf_paths: List of PDF file paths
            document_type: Type of documents
            
        Returns:
            List of ingestion results
        """
        results = []
        for pdf_path in pdf_paths:
            result = self.ingest_pdf(pdf_path, document_type)
            results.append(result)
        return results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the ChromaDB collection."""
        return self.chromadb.get_collection_info()

    def clear_knowledge_base(self) -> Dict:
        """Clear all documents from the Knowledge Base."""
        try:
            self.chromadb.delete_collection()
            return {"status": "success", "message": "Knowledge Base cleared successfully"}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global ingestion pipeline instance
ingestion_pipeline = DataIngestionPipeline()



