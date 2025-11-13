"""
Policy & Compliance Agent - Pure CAG approach.

Uses Context-Augmented Generation (CAG) with pre-loaded policy documents.
No vector search needed - fast, consistent answers from static documents.
"""
import logging
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from core.config import settings

logger = logging.getLogger(__name__)


class PolicyAgent:
    """Policy & Compliance Agent with Pure CAG strategy."""
    
    def __init__(self):
        """Initialize the policy agent with pre-loaded context."""
        self.llm = ChatOpenAI(
            model=settings.llm_model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )
        
        # Pre-loaded policy context (CAG - no retrieval needed)
        self.policy_context = self._load_policy_context()
        
        logger.info("Policy Agent: Initialized with pre-loaded policy context (CAG)")

    def _load_policy_context(self) -> str:
        """
        Load policy documents context (static, pre-loaded).
        In a real system, this would load from actual policy documents.
        
        Returns:
            Pre-loaded policy context string
        """
        return """[POLICY DOCUMENTS CONTEXT]

TERMS OF SERVICE - Key Points:
- Users must be 18+ years old
- Account verification required for trading
- Platform fees: 0.1% per trade (minimum $1)
- Margin trading requires $25,000 minimum account balance
- Day trading restrictions apply (PDT rule)
- Users responsible for all trading decisions
- Platform not liable for trading losses
- Account termination possible for violations

PRIVACY POLICY - Key Points:
- We collect: name, email, trading data, IP address
- Data used for: account management, compliance, analytics
- Data shared with: payment processors, regulatory bodies (when required)
- Data retention: 7 years for compliance
- User rights: access, correction, deletion (subject to legal requirements)
- Security: encrypted storage, secure connections
- Cookies: used for authentication and analytics

COMPLIANCE & REGULATIONS:
- SEC registered broker-dealer
- FINRA member
- SIPC insured up to $500,000
- KYC/AML compliance required
- Suspicious activity reporting
- Tax reporting (1099 forms)
- International users subject to local regulations

ACCOUNT POLICIES:
- Minimum deposit: $100
- Withdrawal processing: 1-3 business days
- Account inactivity: fees after 12 months
- Account closure: 30 days notice required
- Dispute resolution: arbitration required
"""

    async def get_response(
        self,
        message: str,
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Get response from policy agent using Pure CAG.
        
        Args:
            message: User's message
            history: Conversation history
            
        Returns:
            Agent response
        """
        if history is None:
            history = []
        
        # Build system prompt with pre-loaded policy context (CAG)
        system_content = f"""You are a Policy & Compliance Agent for TradePal AI, a trading platform.

Your expertise includes:
- Terms of Service
- Privacy Policy
- Compliance and regulatory information
- Account policies and rules

Provide accurate, clear information from the policy documents.
Always cite specific policies when relevant.

{self.policy_context}

Use the policy information above to answer questions accurately.
If a question is not covered in the policies, say so."""

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


# Global policy agent instance
policy_agent = PolicyAgent()

