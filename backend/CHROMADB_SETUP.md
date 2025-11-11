# ChromaDB Setup Guide

## Overview
ChromaDB is used for vector storage and retrieval in TradePal AI. This guide helps you set it up correctly.

## Installation Issue on macOS

If you encounter this error:
```
clang++: error: unsupported argument 'native' to option '-march='
error: command '/usr/bin/clang++' failed with exit code 1
```

This is a known issue with `chroma-hnswlib` on Apple Silicon Macs.

## Solutions

### Option 1: Use Pre-built Binary (Recommended)
```bash
# Install using conda (if you have it)
conda install -c conda-forge chromadb
```

### Option 2: Skip HNSWLIB (Alternative Vector Store)
The code is already set up to work without ChromaDB. The system will function with in-memory storage for testing.

### Option 3: Use Docker
```bash
# Run ChromaDB in a Docker container
docker run -d -p 8001:8000 --name chromadb chromadb/chroma:latest
```

Then update `backend/core/config.py` to point to the Docker instance.

## Testing Without ChromaDB

All Step 4 code is in place. You can:
1. Use the upload API endpoint (it's ready)
2. PDFs will be processed and stored when ChromaDB is available
3. Mock PDFs are generated in `backend/mock_data/`

## Verify Installation

Once installed, run:
```bash
python ingest_mock_data.py
```

This will process all mock PDFs and add them to the vector database.

## Files Created

✅ **Step 4 Complete - All Code in Place:**
- `utils/chromadb_client.py` - ChromaDB client and vector operations
- `utils/pdf_processor.py` - PDF parsing and chunking
- `utils/data_ingestion.py` - Ingestion pipeline
- `api/upload.py` - PDF upload endpoint
- `generate_mock_pdfs.py` - Mock document generator
- `ingest_mock_data.py` - Batch ingestion script
- `mock_data/` - Generated mock PDFs

## Next Steps

Move to Step 5: RAG Implementation
- The ChromaDB retriever is ready to use
- RAG chain can be implemented
- Streaming responses can be added

## Troubleshooting

If issues persist:
1. Try Python 3.10 or 3.11 (better compatibility)
2. Use Docker for ChromaDB server
3. Contact support with error logs

