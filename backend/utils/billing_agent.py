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
        
        # Default knowledge base for common billing questions
        self.default_knowledge = """[EDUCATIONAL INFORMATION - Trading Platform Fees & Billing]

NOTE: TradePal is an educational tool, not a trading platform. This is general information about how brokerages handle fees.

TYPICAL TRADING PLATFORM FEES (Educational):
- Most modern brokerages: $0 commission for stock/ETF trades
- Options contracts: Typically $0 base fee + $0.50-$0.65 per contract
- Cryptocurrency: Usually 1-2% spread fee
- Account maintenance: Most brokerages have no fees
- Inactivity fees: Rare, but some brokerages charge after 12+ months inactive

TYPICAL PAYMENT METHODS AT BROKERAGES:
- Bank transfer (ACH): Free, 1-3 business days
- Wire transfer: $20-$30 fee, same day
- Debit card: Instant, 1.5-2% fee
- Credit card: Usually not accepted for deposits

UNDERSTANDING TRADING COSTS:
- Commission-free doesn't mean free: Brokerages make money on spreads, payment for order flow
- Options fees add up: $0.65 per contract × 10 contracts = $6.50 per trade
- Margin interest: Typically 2-8% annually on borrowed funds
- Always read brokerage fee schedules before opening account"""

        self.base_system_prompt = """You are a Billing Support Agent for TradePal AI, an educational trading information center.

IMPORTANT: TradePal is NOT a trading platform. It is an educational tool. If users ask about TradePal billing/pricing, explain we're educational only.
If they ask about trading platform fees/billing, provide general educational information about how brokerages handle billing.

Your expertise includes:
- General information about trading platform fees and billing (educational)
- Payment methods at brokerages (educational)
- Pricing structures at trading platforms (educational)
- Understanding trading costs and fees (educational)

RESPONSE STYLE: Be concise and direct. Answer in 1-2 sentences. No fluff, no pleasantries.
Clarify that TradePal is educational, not a trading platform. Provide educational information about how brokerages handle billing.
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
        
        # Add default knowledge if no documents found
        if not document_context:
            system_content += f"\n\n{self.default_knowledge}\n\n"
            system_content += "Use the default knowledge above to answer billing questions when documents are not available."
        else:
            system_content += f"\n\n[BILLING DOCUMENT CONTEXT - UPLOADED FILES]\n{document_context}\n\n"
            system_content += "CRITICAL: Parse data from documents, identify trends, and ALWAYS cite sources.\n"
            system_content += "Format: 'According to [filename], Page [X]...' or 'Source: [filename]'\n"
            system_content += "If document doesn't have the answer, you may reference default knowledge as fallback.\n"
            system_content += f"\n{self.default_knowledge}\n"
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


