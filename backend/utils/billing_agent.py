"""
Billing Support Agent - Hybrid RAG/CAG approach.

Initial query uses RAG to retrieve billing information.
Subsequent queries use CAG (cached context) for faster responses.
"""
import logging
from typing import Dict, List, Optional
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


class BillingAgent:
    """Billing Support Agent with Hybrid RAG/CAG strategy."""
    
    def __init__(self):
        """Initialize the billing agent."""
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
                self.retriever = chromadb_client.get_retriever(k=3)
                self.use_rag = True
                logger.info("Billing Agent: RAG retriever initialized")
            except Exception as e:
                logger.warning(f"Billing Agent: Could not initialize RAG: {e}")
        
        # Cache for CAG (Context-Augmented Generation)
        self.cached_context = {}
        
        self.base_system_prompt = """You are a Billing Support Agent for TradePal AI, a trading platform.

Your expertise includes:
- Billing and invoicing
- Payment methods and processing
- Pricing plans and subscriptions
- Refunds and credits
- Account billing history
- Fee structures

Provide accurate, helpful information about billing-related questions.
If you don't know something, say so rather than guessing."""

    def _retrieve_billing_documents(self, query: str) -> str:
        """
        Retrieve relevant billing documents using RAG.
        
        Args:
            query: User query
            
        Returns:
            Formatted document context string
        """
        if not self.use_rag or not self.retriever:
            return ""
        
        try:
            # Filter for billing documents
            docs = self.retriever.get_relevant_documents(query)
            
            if not docs:
                return ""
            
            # Filter for billing-related documents
            billing_docs = [
                doc for doc in docs
                if doc.metadata.get('document_type', '').lower() in ['billing', 'pricing', 'payment']
            ]
            
            if not billing_docs:
                billing_docs = docs  # Use all docs if no billing-specific ones found
            
            context_parts = []
            for i, doc in enumerate(billing_docs[:3], 1):  # Top 3 results
                source = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                
                context_parts.append(
                    f"[Billing Document {i}]\n"
                    f"Source: {source} (Page {page})\n"
                    f"Content: {doc.page_content}\n"
                )
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Billing Agent: Error retrieving documents: {e}")
            return ""

    async def get_response(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Get response from billing agent using Hybrid RAG/CAG.
        
        Args:
            message: User's message
            history: Conversation history
            session_id: Session ID for caching context
            
        Returns:
            Agent response
        """
        if history is None:
            history = []
        
        # Check if we have cached context for this session (CAG mode)
        use_cag = False
        cached_context = ""
        if session_id and session_id in self.cached_context:
            cached_context = self.cached_context[session_id]
            use_cag = True
            logger.info(f"Billing Agent: Using CAG (cached context) for session {session_id}")
        
        # If no cached context, use RAG to retrieve documents
        if not use_cag:
            document_context = self._retrieve_billing_documents(message)
            if document_context:
                # Cache the context for this session
                if session_id:
                    self.cached_context[session_id] = document_context
                cached_context = document_context
                logger.info(f"Billing Agent: Using RAG, retrieved documents for session {session_id}")
        else:
            document_context = cached_context
        
        # Build system prompt with context
        system_content = self.base_system_prompt
        if document_context:
            system_content += f"\n\n[BILLING DOCUMENT CONTEXT]\n{document_context}\n\n"
            system_content += "Use the information above to answer billing questions accurately."
        
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

    def clear_cache(self, session_id: Optional[str] = None):
        """Clear cached context for a session or all sessions."""
        if session_id:
            self.cached_context.pop(session_id, None)
        else:
            self.cached_context.clear()


# Global billing agent instance
billing_agent = BillingAgent()

