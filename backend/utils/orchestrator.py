"""
Orchestrator agent for routing queries to specialized agents.

Uses AWS Bedrock (Claude 3 Haiku) for fast, cost-effective routing decisions.
Falls back to OpenAI if AWS Bedrock is not configured.
"""
import logging
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from core.config import settings

# Try to import AWS Bedrock, fallback to OpenAI if not available
try:
    from langchain_aws import ChatBedrock
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    ChatBedrock = None

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Orchestrator agent that routes queries to appropriate specialized agents."""
    
    def __init__(self):
        """Initialize the orchestrator with routing LLM."""
        # Use AWS Bedrock if available, otherwise fallback to OpenAI
        if BEDROCK_AVAILABLE and settings.aws_access_key_id and settings.aws_secret_access_key:
            try:
                self.llm = ChatBedrock(
                    model_id=settings.bedrock_model_id,
                    region_name=settings.aws_region,
                    credentials_profile_name=None,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    temperature=0.1  # Low temperature for consistent routing
                )
                self.use_bedrock = True
                logger.info("Orchestrator using AWS Bedrock (Claude 3 Haiku)")
            except Exception as e:
                logger.warning(f"Failed to initialize AWS Bedrock: {e}. Falling back to OpenAI.")
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    openai_api_key=settings.openai_api_key
                )
                self.use_bedrock = False
        else:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                openai_api_key=settings.openai_api_key
            )
            self.use_bedrock = False
            logger.info("Orchestrator using OpenAI (AWS Bedrock not configured)")
        
        self.system_prompt = """You are an orchestrator agent for TradePal AI, an educational trading information center.

IMPORTANT: TradePal is NOT a trading platform. It is an educational tool for learning trading patterns (especially SPY and Tesla) and understanding SEC/FINRA regulations.

Your job is to analyze user queries and route them to the most appropriate specialized agent:

1. **BILLING_AGENT**: Questions about:
   - Trading platform fees and billing (educational information)
   - Understanding trading costs
   - Payment methods at brokerages (educational)

2. **TECHNICAL_AGENT**: Questions about:
   - How to use TradePal's educational features
   - Trading pattern analysis tools
   - Technical questions about TradePal

3. **POLICY_AGENT**: Questions about:
   - SEC/FINRA regulations (educational information)
   - Trading rules and compliance (educational)
   - TradePal's terms/privacy (educational tool)

4. **GENERAL_AGENT**: For:
   - Trading patterns (SPY, Tesla analysis)
   - Getting started with trading (educational)
   - Market sentiment and analysis
   - Stock market queries
   - General trading education questions

Respond with ONLY the agent name: BILLING_AGENT, TECHNICAL_AGENT, POLICY_AGENT, or GENERAL_AGENT.
Do not include any explanation or additional text."""

    async def route_query(self, message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Route a query to the appropriate agent.
        
        Args:
            message: User's message
            history: Optional conversation history
            
        Returns:
            Agent name: BILLING_AGENT, TECHNICAL_AGENT, POLICY_AGENT, or GENERAL_AGENT
        """
        try:
            # Build messages
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add history context if available
            if history:
                for msg in history[-3:]:  # Last 3 messages for context
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=f"User: {msg['content']}"))
                    elif msg["role"] == "assistant":
                        messages.append(HumanMessage(content=f"Assistant: {msg['content']}"))
            
            # Add current query
            messages.append(HumanMessage(content=f"Route this query: {message}"))
            
            # Get routing decision
            response = await self.llm.ainvoke(messages)
            agent_name = response.content.strip().upper()
            
            # Validate and normalize agent name
            valid_agents = ["BILLING_AGENT", "TECHNICAL_AGENT", "POLICY_AGENT", "GENERAL_AGENT"]
            if agent_name not in valid_agents:
                # Try to extract agent name from response
                for agent in valid_agents:
                    if agent in agent_name:
                        agent_name = agent
                        break
                else:
                    # Default to GENERAL_AGENT if unclear
                    agent_name = "GENERAL_AGENT"
                    logger.warning(f"Unclear routing decision: {response.content}. Defaulting to GENERAL_AGENT.")
            
            logger.info(f"Orchestrator routed query to: {agent_name}")
            return agent_name
            
        except Exception as e:
            logger.error(f"Error in orchestrator routing: {e}")
            return "GENERAL_AGENT"  # Safe fallback


# Global orchestrator instance
orchestrator = OrchestratorAgent()


