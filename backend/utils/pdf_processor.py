"""
PDF processing utilities for extracting and chunking text.
"""
import os
from typing import List, Dict, Optional
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFProcessor:
    """Process PDF files and extract text chunks."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            text_content = []
            metadata = {
                "source": os.path.basename(pdf_path),
                "file_path": pdf_path,
                "total_pages": 0
            }
            
            with pdfplumber.open(pdf_path) as pdf:
                metadata["total_pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append({
                            "page": page_num,
                            "text": page_text.strip()
                        })
            
            full_text = "\n\n".join([item["text"] for item in text_content])
            
            return {
                "text": full_text,
                "metadata": metadata,
                "pages": text_content
            }
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Split text into chunks for vector storage.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk metadata
            chunk_list = []
            for idx, chunk in enumerate(chunks):
                chunk_metadata = {
                    "chunk_index": idx,
                    "total_chunks": len(chunks)
                }
                
                if metadata:
                    chunk_metadata.update(metadata)
                
                chunk_list.append({
                    "text": chunk,
                    "metadata": chunk_metadata
                })
            
            return chunk_list
            
        except Exception as e:
            raise Exception(f"Error chunking text: {str(e)}")
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a PDF file: extract text and chunk it.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of chunk dictionaries ready for vector storage
        """
        try:
            # Extract text from PDF
            extraction_result = self.extract_text_from_pdf(pdf_path)
            
            # Chunk the text
            chunks = self.chunk_text(
                text=extraction_result["text"],
                metadata=extraction_result["metadata"]
            )
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")


# Global PDF processor instance
pdf_processor = PDFProcessor()

