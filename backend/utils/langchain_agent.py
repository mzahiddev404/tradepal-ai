"""
LangChain agent setup and configuration.
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from core.config import settings
from utils.stock_data import get_stock_quote


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
        self.system_prompt = """You are TradePal AI, a helpful customer service assistant with access to real-time stock market data.

You help customers with:
- Real-time stock prices and market information
- Billing questions and pricing information
- Technical support and troubleshooting
- Policy inquiries and compliance questions

When users ask about stock prices, use your knowledge to provide current market information.
Popular symbols include: AAPL (Apple), TSLA (Tesla), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), SPY (S&P 500 ETF).

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
    
    def _check_for_stock_query(self, message: str) -> tuple[bool, str]:
        """Check if message is asking for stock information."""
        message_lower = message.lower()
        stock_keywords = ['stock', 'price', 'ticker', 'share', 'market', 'trading', 'quote']
        
        # Common stock symbols
        common_symbols = ['aapl', 'tsla', 'msft', 'googl', 'amzn', 'spy', 'nvda', 'meta', 'nflx']
        
        is_stock_query = any(keyword in message_lower for keyword in stock_keywords)
        
        # Extract symbol if mentioned
        symbol = None
        for sym in common_symbols:
            if sym in message_lower:
                symbol = sym.upper()
                break
        
        # Check for explicit stock symbols (all caps)
        words = message.split()
        for word in words:
            clean_word = word.strip('.,!?()[]{}')
            if clean_word.isupper() and 2 <= len(clean_word) <= 5:
                symbol = clean_word
                is_stock_query = True
                break
        
        return is_stock_query, symbol
    
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
        
        # Check if this is a stock-related query
        is_stock_query, symbol = self._check_for_stock_query(message)
        
        # If stock query with symbol, fetch data
        stock_context = ""
        if is_stock_query and symbol:
            try:
                stock_data = get_stock_quote(symbol)
                if "error" not in stock_data:
                    stock_context = f"\n\n[Real-time Stock Data for {symbol}]\n"
                    stock_context += f"Current Price: ${stock_data.get('price', 'N/A')}\n"
                    stock_context += f"Change: {stock_data.get('change', 'N/A')} ({stock_data.get('change_percent', 'N/A')}%)\n"
                    stock_context += f"Open: ${stock_data.get('open', 'N/A')} | High: ${stock_data.get('high', 'N/A')} | Low: ${stock_data.get('low', 'N/A')}\n"
                    stock_context += f"Volume: {stock_data.get('volume', 'N/A')}\n"
                    if stock_data.get('name'):
                        stock_context += f"Company: {stock_data['name']}\n"
            except Exception as e:
                stock_context = f"\n\n[Note: Unable to fetch stock data: {str(e)}]\n"
        
        # Format conversation history
        messages = self._format_history(history)
        
        # Add current user message with stock context if available
        user_message = message + stock_context if stock_context else message
        messages.append(HumanMessage(content=user_message))
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        
        return response.content


# Global agent instance
chat_agent = ChatAgent()

