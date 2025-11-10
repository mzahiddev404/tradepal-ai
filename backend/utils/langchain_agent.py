"""
LangChain agent setup and configuration.
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from core.config import settings


class ChatAgent:
    """Simple LangChain chat agent."""
    
    def __init__(self):
        """Initialize the chat agent with OpenAI LLM."""
        self.llm = ChatOpenAI(
            model=settings.llm_model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )
        
        # System prompt for the customer service agent
        self.system_prompt = """You are TradePal AI, a helpful customer service assistant.
You help customers with billing questions, technical support, and policy inquiries.
Be professional, friendly, and concise in your responses."""
    
    def _format_history(self, history: List[Dict[str, str]]) -> List:
        """Convert history dict to LangChain message format."""
        messages = [SystemMessage(content=self.system_prompt)]
        
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages
    
    async def get_response(
        self, 
        message: str, 
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Get response from the agent.
        
        Args:
            message: User's message
            history: Conversation history
            
        Returns:
            AI response string
        """
        if history is None:
            history = []
        
        # Format conversation history
        messages = self._format_history(history)
        
        # Add current user message
        messages.append(HumanMessage(content=message))
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        
        return response.content


# Global agent instance
chat_agent = ChatAgent()

