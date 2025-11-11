"""
Ingest mock PDF documents into ChromaDB.

This script processes the generated mock PDFs and adds them to the vector database.
"""
import os
import sys
from utils.data_ingestion import ingestion_pipeline


def ingest_all_mock_data():
    """Ingest all mock PDF files into ChromaDB."""
    mock_dir = os.path.join(os.path.dirname(__file__), "mock_data")
    
    if not os.path.exists(mock_dir):
        print(f"Error: Mock data directory not found: {mock_dir}")
        print("Run generate_mock_pdfs.py first to create the documents.")
        return False
    
    # Define documents with their types
    documents = [
        ("billing_pricing_guide.pdf", "billing"),
        ("technical_documentation.pdf", "technical"),
        ("terms_and_privacy.pdf", "policy"),
    ]
    
    print("Ingesting mock PDF documents into ChromaDB...")
    print()
    
    success_count = 0
    total_chunks = 0
    
    for filename, doc_type in documents:
        filepath = os.path.join(mock_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filename}")
            continue
        
        print(f"Processing: {filename} ({doc_type})...")
        
        try:
            result = ingestion_pipeline.ingest_pdf(
                pdf_path=filepath,
                document_type=doc_type
            )
            
            if result["status"] == "success":
                print(f"✓ Success: {result['chunks_ingested']} chunks ingested")
                print(f"  Document ID: {result['document_id']}")
                success_count += 1
                total_chunks += result['chunks_ingested']
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
        
        print()
    
    # Print summary
    print("=" * 60)
    print(f"Ingestion complete: {success_count}/{len(documents)} documents processed")
    print(f"Total chunks ingested: {total_chunks}")
    print()
    
    # Get collection info
    try:
        stats = ingestion_pipeline.get_collection_stats()
        print("ChromaDB Collection Info:")
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Total documents: {stats['document_count']}")
        print(f"  Storage location: {stats['persist_directory']}")
    except Exception as e:
        print(f"Could not retrieve collection stats: {e}")
    
    return success_count == len(documents)


if __name__ == "__main__":
    try:
        success = ingest_all_mock_data()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nIngestion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)

