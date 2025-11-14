"""
Multi-Agent System using LangGraph.

Orchestrates routing between specialized agents:
- Billing Agent (Hybrid RAG/CAG)
- Technical Agent (Pure RAG)
- Policy Agent (Pure CAG)
- General Agent (existing LangChain agent)
"""
import logging
from typing import Dict, List, Optional, TypedDict

# Try to import LangGraph, fallback to simple routing if not available
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

from utils.orchestrator import orchestrator
from utils.billing_agent import billing_agent
from utils.technical_agent import technical_agent
from utils.policy_agent import policy_agent
from utils.langchain_agent import chat_agent

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State schema for LangGraph workflow."""
    message: str
    history: List[Dict[str, str]]
    session_id: Optional[str]
    agent_name: str
    response: str


class MultiAgentSystem:
    """Multi-agent system using LangGraph for orchestration."""
    
    def __init__(self):
        """Initialize the multi-agent system."""
        if LANGGRAPH_AVAILABLE:
            self.graph = self._build_graph()
            self.app = self.graph.compile()
            self.use_langgraph = True
            logger.info("Multi-Agent System initialized with LangGraph")
        else:
            self.use_langgraph = False
            logger.warning("LangGraph not available, using simple routing")
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("billing_agent", self._billing_node)
        workflow.add_node("technical_agent", self._technical_node)
        workflow.add_node("policy_agent", self._policy_node)
        workflow.add_node("general_agent", self._general_node)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Add conditional routing edges
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_to_agent,
            {
                "BILLING_AGENT": "billing_agent",
                "TECHNICAL_AGENT": "technical_agent",
                "POLICY_AGENT": "policy_agent",
                "GENERAL_AGENT": "general_agent",
            }
        )
        
        # All agents end
        workflow.add_edge("billing_agent", END)
        workflow.add_edge("technical_agent", END)
        workflow.add_edge("policy_agent", END)
        workflow.add_edge("general_agent", END)
        
        return workflow
    
    async def _orchestrator_node(self, state: AgentState) -> AgentState:
        """Orchestrator node - routes query to appropriate agent."""
        try:
            agent_name = await orchestrator.route_query(
                message=state["message"],
                history=state.get("history", [])
            )
            state["agent_name"] = agent_name
            logger.info(f"Orchestrator routed to: {agent_name}")
        except Exception as e:
            logger.error(f"Error in orchestrator node: {e}")
            state["agent_name"] = "GENERAL_AGENT"  # Safe fallback
        
        return state
    
    def _route_to_agent(self, state: AgentState) -> str:
        """Route to the appropriate agent based on orchestrator decision."""
        return state.get("agent_name", "GENERAL_AGENT")
    
    async def _billing_node(self, state: AgentState) -> AgentState:
        """Billing agent node."""
        try:
            response = await billing_agent.get_response(
                message=state["message"],
                history=state.get("history", []),
                session_id=state.get("session_id")
            )
            state["response"] = response
            logger.info("Billing agent response generated")
        except Exception as e:
            logger.error(f"Error in billing agent: {e}")
            state["response"] = f"I apologize, but I encountered an error processing your billing question. Please try again."
        
        return state
    
    async def _technical_node(self, state: AgentState) -> AgentState:
        """Technical agent node."""
        try:
            response = await technical_agent.get_response(
                message=state["message"],
                history=state.get("history", [])
            )
            state["response"] = response
            logger.info("Technical agent response generated")
        except Exception as e:
            logger.error(f"Error in technical agent: {e}")
            state["response"] = f"I apologize, but I encountered an error processing your technical question. Please try again."
        
        return state
    
    async def _policy_node(self, state: AgentState) -> AgentState:
        """Policy agent node."""
        try:
            response = await policy_agent.get_response(
                message=state["message"],
                history=state.get("history", [])
            )
            state["response"] = response
            logger.info("Policy agent response generated")
        except Exception as e:
            logger.error(f"Error in policy agent: {e}")
            state["response"] = f"I apologize, but I encountered an error processing your policy question. Please try again."
        
        return state
    
    async def _general_node(self, state: AgentState) -> AgentState:
        """General agent node (uses existing LangChain agent)."""
        try:
            response = await chat_agent.get_response(
                message=state["message"],
                history=state.get("history", [])
            )
            state["response"] = response
            logger.info("General agent response generated")
        except Exception as e:
            logger.error(f"Error in general agent: {e}", exc_info=True)
            # Provide more helpful error message with details
            error_msg = str(e)
            if "stock_data_service" in error_msg:
                state["response"] = f"I encountered a technical issue while fetching stock data. The error has been logged. Please try again in a moment."
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                state["response"] = f"The market data service is temporarily rate-limited. Please wait a moment and try again."
            else:
                state["response"] = f"I apologize, but I encountered an error processing your question: {error_msg}. Please try again."
        
        return state
    
    async def process_message(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        session_id: Optional[str] = None,
        use_multi_agent: bool = True
    ) -> Dict[str, str]:
        """
        Process a message through the multi-agent system.
        
        Args:
            message: User's message
            history: Conversation history
            session_id: Optional session ID for caching
            use_multi_agent: Whether to use multi-agent system (default: True)
            
        Returns:
            Dictionary with response and agent_name
        """
        if history is None:
            history = []
        
        # If multi-agent is disabled, use general agent directly
        if not use_multi_agent:
            try:
                response = await chat_agent.get_response(message, history)
                return {
                    "response": response,
                    "agent_name": "GENERAL_AGENT"
                }
            except Exception as e:
                logger.error(f"Error in general agent fallback: {e}")
                return {
                    "response": "I apologize, but I encountered an error. Please try again.",
                    "agent_name": "GENERAL_AGENT"
                }
        
        # Use multi-agent system
        try:
            if self.use_langgraph and self.app:
                # Use LangGraph workflow
                initial_state: AgentState = {
                    "message": message,
                    "history": history,
                    "session_id": session_id,
                    "agent_name": "",
                    "response": ""
                }
                
                # Run the graph
                final_state = await self.app.ainvoke(initial_state)
                
                return {
                    "response": final_state.get("response", ""),
                    "agent_name": final_state.get("agent_name", "GENERAL_AGENT")
                }
            else:
                # Fallback to simple routing without LangGraph
                agent_name = await orchestrator.route_query(message, history)
                
                # Route to appropriate agent
                if agent_name == "BILLING_AGENT":
                    response = await billing_agent.get_response(message, history, session_id)
                elif agent_name == "TECHNICAL_AGENT":
                    response = await technical_agent.get_response(message, history)
                elif agent_name == "POLICY_AGENT":
                    response = await policy_agent.get_response(message, history)
                else:
                    response = await chat_agent.get_response(message, history)
                
                return {
                    "response": response,
                    "agent_name": agent_name
                }
        except Exception as e:
            logger.error(f"Error in multi-agent system: {e}")
            # Fallback to general agent
            try:
                response = await chat_agent.get_response(message, history)
                return {
                    "response": response,
                    "agent_name": "GENERAL_AGENT"
                }
            except Exception as e2:
                logger.error(f"Error in fallback: {e2}")
                return {
                    "response": "I apologize, but I encountered an error. Please try again.",
                    "agent_name": "GENERAL_AGENT"
                }


# Global multi-agent system instance
multi_agent_system = MultiAgentSystem()

