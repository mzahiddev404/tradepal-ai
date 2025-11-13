"""
Technical Support Agent - Pure RAG approach.

Always uses RAG to retrieve from technical documents.
No caching - always fresh retrieval for up-to-date information.
"""
import logging
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from core.config import settings

# Try to import ChromaDB retriever
try:
    from utils.chromadb_client import chromadb_client, CHROMADB_AVAILABLE
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb_client = None

logger = logging.getLogger(__name__)


class TechnicalAgent:
    """Technical Support Agent with Pure RAG strategy."""
    
    def __init__(self):
        """Initialize the technical agent."""
        self.llm = ChatOpenAI(
            model=settings.llm_model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )
        
        # Initialize RAG retriever if available
        self.retriever = None
        self.use_rag = False
        if CHROMADB_AVAILABLE and chromadb_client:
            try:
                self.retriever = chromadb_client.get_retriever(k=4)
                self.use_rag = True
                logger.info("Technical Agent: RAG retriever initialized")
            except Exception as e:
                logger.warning(f"Technical Agent: Could not initialize RAG: {e}")
        
        self.base_system_prompt = """You are a Technical Support Agent for TradePal AI, a trading platform.

Your expertise includes:
- Technical troubleshooting and support
- API usage and integrations
- Platform features and functionality
- How-to guides and tutorials
- Bug reports and technical issues
- Trading platform technical features

Provide clear, step-by-step technical guidance.
If you don't know something, say so rather than guessing."""

    def _retrieve_technical_documents(self, query: str) -> str:
        """
        Retrieve relevant technical documents using RAG.
        Always retrieves fresh documents (no caching).
        
        Args:
            query: User query
            
        Returns:
            Formatted document context string
        """
        if not self.use_rag or not self.retriever:
            return ""
        
        try:
            # Retrieve documents (always fresh)
            docs = self.retriever.get_relevant_documents(query)
            
            if not docs:
                return ""
            
            # Filter for technical documents
            technical_docs = [
                doc for doc in docs
                if doc.metadata.get('document_type', '').lower() in ['technical', 'api', 'documentation']
            ]
            
            if not technical_docs:
                technical_docs = docs  # Use all docs if no technical-specific ones found
            
            context_parts = []
            for i, doc in enumerate(technical_docs[:4], 1):  # Top 4 results
                source = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                
                context_parts.append(
                    f"[Technical Document {i}]\n"
                    f"Source: {source} (Page {page})\n"
                    f"Content: {doc.page_content}\n"
                )
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Technical Agent: Error retrieving documents: {e}")
            return ""

    async def get_response(
        self,
        message: str,
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Get response from technical agent using Pure RAG.
        
        Args:
            message: User's message
            history: Conversation history
            
        Returns:
            Agent response
        """
        if history is None:
            history = []
        
        # Always retrieve fresh documents (Pure RAG)
        document_context = self._retrieve_technical_documents(message)
        logger.info("Technical Agent: Using Pure RAG (fresh retrieval)")
        
        # Build system prompt with context
        system_content = self.base_system_prompt
        if document_context:
            system_content += f"\n\n[TECHNICAL DOCUMENT CONTEXT]\n{document_context}\n\n"
            system_content += "Use the information above to provide accurate technical support."
        else:
            system_content += "\n\nNote: No relevant technical documents found. Answer based on general knowledge."
        
        # Format messages
        messages = [SystemMessage(content=system_content)]
        
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=message))
        
        # Get response
        response = await self.llm.ainvoke(messages)
        return response.content


# Global technical agent instance
technical_agent = TechnicalAgent()

