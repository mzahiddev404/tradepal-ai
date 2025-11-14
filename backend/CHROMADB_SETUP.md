# ChromaDB Setup Guide

Complete guide for setting up and managing ChromaDB in the TradePal AI backend.

## Overview

ChromaDB is used as the vector database for storing document embeddings. This enables RAG (Retrieval-Augmented Generation) functionality by allowing agents to retrieve relevant context from uploaded documents.

## Initial Setup

### Automatic Initialization

ChromaDB is automatically initialized on first run. The database is created in `backend/chroma_db/` directory.

### Manual Setup

If you need to manually initialize:

```python
from utils.chromadb_client import get_chroma_client

client = get_chroma_client()
collection = client.get_or_create_collection("tradepal_documents")
```

## Configuration

### Storage Location

Default: `backend/chroma_db/`

To change location, modify `CHROMA_PERSIST_DIR` in `core/config.py`:

```python
chroma_persist_dir = "path/to/your/database"
```

### Collection Management

Collections are automatically created when documents are uploaded. The default collection name is `tradepal_documents`.

## Document Ingestion

### Uploading Documents

Documents are uploaded via the `/api/upload` endpoint:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf" \
  -F "document_type=billing"
```

### Processing Pipeline

1. PDF text extraction using pdfplumber
2. Text chunking (configurable chunk size)
3. Embedding generation using OpenAI
4. Storage in ChromaDB with metadata

### Document Types

Supported document types:
- `billing` - Billing and pricing documents
- `technical` - Technical documentation
- `policy` - Policy and compliance documents
- `general` - General documents (default)

## Querying Documents

### Retrieval Process

1. User query is converted to embedding
2. Similarity search performed in ChromaDB
3. Top K most relevant chunks retrieved
4. Context passed to agent for response generation

### Retrieval Parameters

- `top_k`: Number of documents to retrieve (default: 5)
- `similarity_threshold`: Minimum similarity score (default: 0.7)

## Maintenance

### Viewing Collection Info

```bash
curl http://localhost:8000/api/collection/info
```

### Clearing Database

To reset the database:

```bash
rm -rf backend/chroma_db/
```

Database will be recreated on next run.

### Backup

To backup ChromaDB:

```bash
cp -r backend/chroma_db/ backend/chroma_db_backup/
```

### Restore

To restore from backup:

```bash
rm -rf backend/chroma_db/
cp -r backend/chroma_db_backup/ backend/chroma_db/
```

## Mock Data

### Generating Mock Data

Pre-populate database with sample documents:

```bash
cd backend
python generate_mock_pdfs.py
python ingest_mock_data.py
```

### Mock Document Types

- Billing pricing guide
- Technical documentation
- Terms and privacy policy
- Brokerage trading guide

## Performance Considerations

### Indexing

ChromaDB automatically creates indexes for efficient similarity search. No manual indexing required.

### Query Optimization

- Use appropriate `top_k` values
- Filter by document type when possible
- Cache frequently accessed documents

### Storage

- Monitor database size
- Clean up old documents if needed
- Consider archiving inactive documents

## Troubleshooting

### Database Lock Errors

If you see lock errors:

```bash
# Stop backend server
# Remove lock files
rm -f backend/chroma_db/*.lock
# Restart server
```

### Import Errors

If ChromaDB import fails:

```bash
pip install --upgrade chromadb
```

### Permission Errors

Ensure write permissions on `chroma_db/` directory:

```bash
chmod -R 755 backend/chroma_db/
```

## Production Considerations

### Scaling

For production scale:
- Consider ChromaDB cloud hosting
- Implement connection pooling
- Monitor query performance
- Set up replication if needed

### Security

- Secure database directory
- Implement access controls
- Encrypt sensitive documents
- Regular backups

### Monitoring

- Track database size
- Monitor query performance
- Log retrieval operations
- Set up alerts for errors

## Notes for Future Development

### Potential Enhancements
- Multi-collection support for different document types
- Document versioning
- Automatic document expiration
- Enhanced metadata filtering
- Query result caching
- Document update mechanisms

### Migration Considerations
- Plan for schema changes
- Document migration procedures
- Test backup/restore processes
- Consider data export formats
