"""
LangChain agent setup and configuration.

This module provides the ChatAgent class that handles AI-powered chat interactions
with integrated stock market data fetching capabilities.
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional, Tuple
from core.config import settings
from utils.stock_data import stock_data_service
import logging

logger = logging.getLogger(__name__)


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
        
        # Get current date for context
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # System prompt for the customer service agent
        self.system_prompt = f"""You are TradePal AI, a helpful customer service assistant with access to real-time stock market data.

CURRENT DATE: {current_date}

IMPORTANT CONTEXT:
- While your training data may be from the past, you have access to LIVE, REAL-TIME stock market data
- When users ask about stock prices, I will provide you with CURRENT data from today
- You are operating in the present day: {current_date}
- Always refer to today's date as {current_date}, not any date from your training data

You help customers with:
- Real-time stock prices and market information (you have LIVE access to current stock data)
- Billing questions and pricing information
- Technical support and troubleshooting
- Policy inquiries and compliance questions

STOCK DATA INSTRUCTIONS:
When users ask about stock prices, I will provide [Real-time Stock Data] sections in messages.
This contains ACTUAL CURRENT prices fetched live from the market.
ALWAYS use this real-time data when provided. NEVER say you cannot access current stock prices.
Present the data as if you're looking at it right now, because you are!

Popular symbols: AAPL (Apple), TSLA (Tesla), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), SPY (S&P 500 ETF), NVDA (Nvidia), META (Meta/Facebook).

Be professional, friendly, and concise in your responses. Always acknowledge the current date context when relevant."""
    
    def _format_history(self, history: List[Dict[str, str]]) -> List:
        """Convert history dict to LangChain message format."""
        messages = [SystemMessage(content=self.system_prompt)]
        
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages
    
    def _check_for_stock_query(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message is asking for stock information.
        
        Args:
            message: User's message text
            
        Returns:
            Tuple of (is_stock_query, symbol)
        """
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
                from datetime import datetime
                current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
                stock_data = stock_data_service.get_stock_quote(symbol)
                if "error" not in stock_data:
                    stock_context = f"\n\n[Real-time Stock Data for {symbol} - LIVE DATA as of {current_time}]\n"
                    stock_context += f"THIS IS CURRENT, LIVE DATA - NOT FROM YOUR TRAINING DATA\n"
                    stock_context += f"Data Retrieved: {current_time}\n"
                    stock_context += f"Symbol: {symbol}\n"
                    if stock_data.get('name'):
                        stock_context += f"Company Name: {stock_data['name']}\n"
                    stock_context += f"Current Price: ${stock_data.get('current_price', 'N/A')}\n"
                    stock_context += f"Price Change: ${stock_data.get('change', 'N/A')} ({stock_data.get('change_percent', 'N/A')}%)\n"
                    stock_context += f"Previous Close: ${stock_data.get('previous_close', 'N/A')}\n"
                    stock_context += f"Volume: {stock_data.get('volume', 'N/A'):,}\n"
                    if stock_data.get('market_cap'):
                        stock_context += f"Market Cap: ${stock_data.get('market_cap', 0):,}\n"
                    stock_context += f"52 Week High: ${stock_data.get('high_52w', 'N/A')}\n"
                    stock_context += f"52 Week Low: ${stock_data.get('low_52w', 'N/A')}\n"
                    stock_context += f"\nIMPORTANT: Use this CURRENT data in your response. This is live market data from {current_time}. Do NOT refer to dates from your training data.\n"
            except Exception as e:
                logger.error(f"Error fetching stock data: {e}")
                stock_context = f"\n\n[System Note: Unable to fetch stock data: {str(e)}. Apologize and ask them to try a different symbol.]\n"
        
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

