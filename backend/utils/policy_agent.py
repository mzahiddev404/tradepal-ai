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

TRADEPAL TERMS OF SERVICE - Key Points:
- TradePal is an EDUCATIONAL tool, NOT a trading platform
- Users must be 18+ years old to use educational content
- No account required - this is informational/educational only
- TradePal does NOT execute trades or hold funds
- Users responsible for their own trading decisions at actual brokerages
- TradePal not liable for trading losses or decisions

PRIVACY POLICY - Key Points:
- We collect: usage data, queries, uploaded documents (for analysis)
- Data used for: improving educational content, pattern analysis
- Data shared with: AI services for processing (OpenAI, etc.)
- Data retention: As needed for service improvement
- User rights: access, correction, deletion
- Security: encrypted storage, secure connections

SEC/FINRA REGULATIONS (Educational Information):
- SEC/FINRA regulations apply to ALL U.S. brokerages, not TradePal
- Pattern Day Trader (PDT) rule: SEC/FINRA regulation for accounts under $25,000
- Margin requirements: SEC/FINRA regulation ($2,000 minimum)
- Settlement rules: SEC regulation (T+2 for stocks, T+1 for options)
- SIPC insurance: SEC-mandated protection up to $500,000 per account
- KYC/AML: SEC/FINRA requirement for all brokerages
- Tax reporting: IRS requirement (1099 forms)

EDUCATIONAL DISCLAIMER:
- TradePal provides educational information only
- Not financial advice
- Users should consult licensed professionals for actual trading
- Market data may be delayed or inaccurate
- Past performance doesn't guarantee future results
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
        system_content = f"""You are a Policy & Compliance Agent for TradePal AI, an educational trading information center.

IMPORTANT: TradePal is NOT a trading platform. It is an educational tool. When discussing SEC/FINRA regulations, clarify these apply to all U.S. brokerages, not TradePal.

Your expertise includes:
- TradePal's Terms of Service (educational tool)
- Privacy Policy
- SEC/FINRA regulations (educational information)
- Trading platform policies (general educational info)

RESPONSE STYLE: Be concise and direct. Answer in 1-2 sentences. Cite specific policies when relevant. No fluff.
Clarify that TradePal is educational, not a trading platform.

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


