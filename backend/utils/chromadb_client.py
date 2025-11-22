"""
ChromaDB client utilities for vector database operations.
"""
import os
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None
from typing import Optional, List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from core.config import settings


class ChromaDBClient:
    """Client for managing ChromaDB collections and vector operations."""
    
    def __init__(self, collection_name: str = "tradepal_documents"):
        """
        Initialize ChromaDB client.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is not installed. Please install it with: pip install chromadb")
        
        # Set up persistent storage directory
        self.persist_directory = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "chroma_db"
        )
        os.makedirs(self.persist_directory, exist_ok=True)
        print(f"ChromaDB Persistence Path: {self.persist_directory}")
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection_name = collection_name
        self.collection = None
        self._initialize_collection()
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model="text-embedding-3-small"
        )
        
        # Initialize LangChain Chroma vector store
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def _initialize_collection(self):
        """Initialize or get existing collection."""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "TradePal AI document collection"}
            )
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks to add
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        try:
            return self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of document dictionaries with text and metadata
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            return [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        except Exception as e:
            print(f"Error searching: {e}")
            raise
    
    def query_documents(
        self,
        query_text: str,
        n_results: int = 10,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Query documents using raw ChromaDB query (for getting raw text/metadata).
        
        Args:
            query_text: Text to query
            n_results: Number of results
            where: Metadata filter
            where_document: Document content filter
            
        Returns:
            Dictionary with 'documents', 'metadatas', 'distances'
        """
        try:
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
        except Exception as e:
            print(f"Error querying documents: {e}")
            raise

    def get_retriever(self, k: int = 4):
        """
        Get a LangChain retriever for RAG.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            LangChain retriever
        """
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    
    def delete_collection(self):
        """Delete the collection (use with caution)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._initialize_collection()
            
            # Re-initialize vectorstore as it might hold reference to old collection
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            print(f"Error deleting collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {"error": str(e)}


# Global ChromaDB client instance
chromadb_client = ChromaDBClient()


