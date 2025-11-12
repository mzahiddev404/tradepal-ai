"""
LangChain agent setup and configuration.

This module provides the ChatAgent class that handles AI-powered chat interactions
with integrated stock market data fetching capabilities.
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from core.config import settings
from utils.stock_data import stock_data_service
import logging
import re

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
        
        # Get current date and time in EST timezone for context
        est_tz = ZoneInfo("America/New_York")
        current_datetime = datetime.now(est_tz)
        current_date = current_datetime.strftime("%B %d, %Y")
        current_time = current_datetime.strftime("%I:%M %p %Z")
        
        # System prompt for the customer service agent - EXTREMELY EXPLICIT
        self.system_prompt = f"""You are TradePal AI - a DATA-DRIVEN trading assistant.

TODAY IS: {current_date} at {current_time}

⚠️ ABSOLUTE REQUIREMENTS - FAILURE TO FOLLOW = INCORRECT RESPONSE ⚠️

1. ONLY USE THE EXACT NUMBERS PROVIDED IN [LIVE MARKET DATA] SECTIONS
2. DO NOT MAKE UP PRICES - DO NOT USE YOUR TRAINING DATA FOR PRICES
3. IF YOU SEE "CURRENT PRICE: $XXX.XX" - USE THAT EXACT NUMBER
4. EVERY response MUST include the timestamp from the data
5. DO NOT HALLUCINATE - ONLY STATE FACTS FROM THE PROVIDED DATA

STOCK PRICES:
- When you see [LIVE MARKET DATA] with a price, USE THAT EXACT PRICE
- DO NOT adjust, round, or change the price
- DO NOT use prices from your memory/training
- The data I provide is from TODAY: {current_date}
- Example: If data says $434.47, you say "$434.47" - NOT "$1,000" or any other number

RESPONSE FORMAT:
"As of [DATE] at [TIME]: [SYMBOL] is $[EXACT_PRICE_FROM_DATA]"

BANNED PHRASES:
- "As of my last update"
- "According to my training data"
- "Approximately"
- "Around"
- "Roughly"

BE DIRECT. BE ACCURATE. USE ONLY THE DATA PROVIDED."""
    
    def _format_history(self, history: List[Dict[str, str]]) -> List:
        """Convert history dict to LangChain message format."""
        messages = [SystemMessage(content=self.system_prompt)]
        
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages
    
    def _check_for_stock_query(self, message: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if message is asking for stock information and detect dates.
        
        Args:
            message: User's message text
            
        Returns:
            Tuple of (is_stock_query, symbol, date)
        """
        message_lower = message.lower()
        stock_keywords = ['stock', 'price', 'ticker', 'share', 'market', 'trading', 'quote', 'historical', 'past', 'was', 'were', 'current', 'live', 'now', 'today']
        
        # Common stock symbols and company names mapping
        symbol_mapping = {
            'aapl': 'AAPL', 'apple': 'AAPL',
            'tsla': 'TSLA', 'tesla': 'TSLA',
            'msft': 'MSFT', 'microsoft': 'MSFT',
            'googl': 'GOOGL', 'google': 'GOOGL', 'alphabet': 'GOOGL',
            'amzn': 'AMZN', 'amazon': 'AMZN',
            'spy': 'SPY',
            'nvda': 'NVDA', 'nvidia': 'NVDA',
            'meta': 'META', 'facebook': 'META',
            'nflx': 'NFLX', 'netflix': 'NFLX'
        }
        
        is_stock_query = any(keyword in message_lower for keyword in stock_keywords)
        
        # Extract symbol if mentioned (check both symbols and company names)
        symbol = None
        for key, sym in symbol_mapping.items():
            if key in message_lower:
                symbol = sym
                is_stock_query = True
                break
        
        # Check for explicit stock symbols (all caps)
        words = message.split()
        for word in words:
            clean_word = word.strip('.,!?()[]{}')
            if clean_word.isupper() and 2 <= len(clean_word) <= 5:
                symbol = clean_word
                is_stock_query = True
                break
        
        # Detect date in message
        date = None
        est_tz = ZoneInfo("America/New_York")
        now_est = datetime.now(est_tz)
        
        # Check for YYYY-MM-DD format
        date_pattern = r'\b(\d{4}-\d{2}-\d{2})\b'
        match = re.search(date_pattern, message)
        if match:
            date = match.group(1)
        else:
            # Check for relative dates
            if 'yesterday' in message_lower:
                date = (now_est - timedelta(days=1)).strftime("%Y-%m-%d")
            elif 'last week' in message_lower or 'a week ago' in message_lower:
                date = (now_est - timedelta(days=7)).strftime("%Y-%m-%d")
            elif 'last month' in message_lower or 'a month ago' in message_lower:
                date = (now_est - timedelta(days=30)).strftime("%Y-%m-%d")
            elif 'last year' in message_lower or 'a year ago' in message_lower:
                date = (now_est - timedelta(days=365)).strftime("%Y-%m-%d")
            else:
                # Try to parse dates like "January 15, 2024", "Jan 15 2024", "1/15/2024"
                try:
                    from dateutil import parser
                    # Look for date-like patterns
                    date_patterns = [
                        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                        r'\b\d{1,2}-\d{1,2}-\d{4}\b',
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, message, re.IGNORECASE)
                        if match:
                            parsed_date = parser.parse(match.group(0), fuzzy=True)
                            date = parsed_date.strftime("%Y-%m-%d")
                            break
                except (ImportError, ValueError, Exception):
                    pass
        
        return is_stock_query, symbol, date
    
    def _is_unclear_query(self, message: str, symbol: Optional[str]) -> bool:
        """
        Check if the query is unclear or minimal.
        
        Args:
            message: User's message text
            symbol: Detected stock symbol (if any)
            
        Returns:
            True if query is unclear but symbol is detected
        """
        if not symbol:
            return False
        
        message_lower = message.lower().strip()
        words = message.split()
        
        # Check if message is very short (3 words or less)
        if len(words) <= 3:
            # Check if it's just the symbol/company name with minimal context
            if len(words) == 1:
                return True  # Just "TSLA" or "Tesla"
            
            # Check if message lacks clear question words
            question_words = ['what', 'show', 'price', 'tell', 'give', 'get', 'how', 'when', 'where', 'why']
            has_question_word = any(word.lower() in question_words for word in words)
            
            # If no question words and just symbol + minimal words, it's unclear
            if not has_question_word and len(words) <= 2:
                return True
        
        # Check if message is just company name variations
        company_only_patterns = [
            r'^(tesla|apple|microsoft|google|amazon|meta|nvidia|netflix)$',
            r'^(tsla|aapl|msft|googl|amzn|meta|nvda|nflx)$'
        ]
        for pattern in company_only_patterns:
            if re.match(pattern, message_lower):
                return True
        
        return False
    
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
        
        # Check if this is a stock-related query and detect date
        is_stock_query, symbol, date = self._check_for_stock_query(message)
        
        # Check if query is unclear but symbol is detected
        is_unclear = self._is_unclear_query(message, symbol)
        
        # If stock query with symbol, fetch data (current or historical)
        stock_context = ""
        is_historical = False
        stock_data = {}
        est_tz = ZoneInfo("America/New_York")
        current_time = datetime.now(est_tz).strftime("%B %d, %Y at %I:%M %p %Z")
        if is_stock_query and symbol:
            try:
                
                # Use historical data if date is detected, otherwise use current quote
                if date:
                    stock_data = stock_data_service.get_historical_price(symbol, date)
                    is_historical = True
                else:
                    stock_data = stock_data_service.get_stock_quote(symbol)
                    is_historical = False
                
                if "error" not in stock_data:
                    if is_historical:
                        # Historical price data
                        historical_date = stock_data.get('data_timestamp', stock_data.get('date', date))
                        close_price = stock_data.get('close', 0)
                        open_price = stock_data.get('open', 0)
                        high_price = stock_data.get('high', 0)
                        low_price = stock_data.get('low', 0)
                        volume = stock_data.get('volume', 0)
                        
                        stock_context = f"\n\n{'='*70}\n"
                        stock_context += f"📅 HISTORICAL MARKET DATA - {symbol} 📅\n"
                        stock_context += f"Date: {historical_date}\n"
                        stock_context += f"Retrieved: {current_time}\n"
                        stock_context += f"{'='*70}\n\n"
                        
                        if stock_data.get('name'):
                            stock_context += f"Company: {stock_data['name']} ({symbol})\n\n"
                        
                        # CRITICAL PRICE INFORMATION - ABSOLUTELY MUST USE THIS
                        stock_context += f"\n{'🚨'*25}\n"
                        stock_context += f"⚠️  DO NOT HALLUCINATE - USE THIS EXACT PRICE ⚠️\n"
                        stock_context += f"{'🚨'*25}\n\n"
                        stock_context += f"╔{'═'*50}╗\n"
                        stock_context += f"║  CLOSING PRICE FOR {symbol} ON {historical_date}: ${close_price:<28} ║\n"
                        stock_context += f"╚{'═'*50}╝\n\n"
                        stock_context += f"THIS IS THE ONLY CORRECT PRICE. DO NOT USE ANY OTHER NUMBER.\n"
                        stock_context += f"NOT $1000, NOT $500, ONLY ${close_price}\n\n"
                        
                        stock_context += f"Open: ${open_price:.2f}\n"
                        stock_context += f"High: ${high_price:.2f}\n"
                        stock_context += f"Low: ${low_price:.2f}\n"
                        stock_context += f"Close: ${close_price:.2f}\n"
                        if volume:
                            stock_context += f"Volume: {volume:,} shares\n"
                        
                        stock_context += f"\n{'='*70}\n"
                        stock_context += f"⚠️  MANDATORY RESPONSE FORMAT ⚠️\n"
                        stock_context += f"{'='*70}\n"
                        stock_context += f"YOU MUST SAY:\n"
                        stock_context += f"'On {historical_date}, {symbol} closed at ${close_price}'\n\n"
                        stock_context += f"VERIFICATION CHECKS:\n"
                        stock_context += f"✓ Price = ${close_price}? YES = Correct | NO = Wrong\n"
                        stock_context += f"✓ Date included? YES = Correct | NO = Wrong\n"
                        stock_context += f"✓ Used provided data only? YES = Correct | NO = Wrong\n"
                        stock_context += f"{'='*70}\n\n"
                        stock_context += f"FINAL REMINDER: The closing price on {historical_date} was ${close_price}, not any other number.\n"
                        stock_context += f"If you say anything other than ${close_price}, you are WRONG.\n"
                        stock_context += f"{'='*70}\n"
                        
                        logger.info(f"[HISTORICAL] Stock data for {symbol} on {date}: CLOSE=${close_price}")
                    else:
                        # Current price data
                        current_price = stock_data.get('current_price', 0)
                        change = stock_data.get('change', 0)
                        change_pct = stock_data.get('change_percent', 0)
                        direction = "UP ⬆" if change > 0 else "DOWN ⬇" if change < 0 else "FLAT →"
                        market_state = stock_data.get('market_state', 'UNKNOWN')
                        
                        stock_context = f"\n\n{'='*70}\n"
                        stock_context += f"🔴 LIVE MARKET DATA - {symbol} 🔴\n"
                        stock_context += f"Retrieved: {current_time}\n"
                        stock_context += f"Market Status: {market_state}\n"
                        stock_context += f"{'='*70}\n\n"
                        
                        if stock_data.get('name'):
                            stock_context += f"Company: {stock_data['name']} ({symbol})\n\n"
                        
                        # CRITICAL PRICE INFORMATION - ABSOLUTELY MUST USE THIS
                        stock_context += f"\n{'🚨'*25}\n"
                        stock_context += f"⚠️  DO NOT HALLUCINATE - USE THIS EXACT PRICE ⚠️\n"
                        stock_context += f"{'🚨'*25}\n\n"
                        stock_context += f"╔{'═'*50}╗\n"
                        stock_context += f"║  CURRENT PRICE FOR {symbol}: ${current_price:<36} ║\n"
                        stock_context += f"╚{'═'*50}╝\n\n"
                        stock_context += f"THIS IS THE ONLY CORRECT PRICE. DO NOT USE ANY OTHER NUMBER.\n"
                        stock_context += f"NOT $1000, NOT $500, ONLY ${current_price}\n\n"
                        
                        stock_context += f"Price Movement: {direction}\n"
                        stock_context += f"Change: ${change:.2f} ({change_pct:+.2f}%)\n"
                        stock_context += f"Previous Close: ${stock_data.get('previous_close', 'N/A')}\n\n"
                        
                        # Additional data
                        if stock_data.get('volume'):
                            stock_context += f"Volume: {stock_data['volume']:,} shares\n"
                        if stock_data.get('market_cap'):
                            market_cap_b = stock_data['market_cap'] / 1_000_000_000
                            stock_context += f"Market Cap: ${market_cap_b:.2f}B\n"
                        stock_context += f"52W Range: ${stock_data.get('low_52w', 'N/A')} - ${stock_data.get('high_52w', 'N/A')}\n"
                        
                        stock_context += f"\n{'='*70}\n"
                        stock_context += f"⚠️  MANDATORY RESPONSE FORMAT ⚠️\n"
                        stock_context += f"{'='*70}\n"
                        stock_context += f"YOU MUST SAY:\n"
                        stock_context += f"'As of {current_time}: {symbol} is ${current_price}'\n\n"
                        stock_context += f"VERIFICATION CHECKS:\n"
                        stock_context += f"✓ Price = ${current_price}? YES = Correct | NO = Wrong\n"
                        stock_context += f"✓ Timestamp included? YES = Correct | NO = Wrong\n"
                        stock_context += f"✓ Used provided data only? YES = Correct | NO = Wrong\n"
                        stock_context += f"{'='*70}\n\n"
                        stock_context += f"FINAL REMINDER: The price is ${current_price}, not any other number.\n"
                        stock_context += f"If you say anything other than ${current_price}, you are WRONG.\n"
                        stock_context += f"{'='*70}\n"
                        
                        logger.info(f"[EXPLICIT] Stock data for {symbol}: PRICE=${current_price} at {current_time}")
            except Exception as e:
                logger.error(f"Error fetching stock data: {e}")
                stock_context = f"\n\n[Error: Cannot retrieve {symbol} data. Ask user to verify symbol or try again.]\n"
                stock_data = {"error": f"Failed to fetch stock data: {str(e)}"}
        
        # If query is unclear but we have stock data, return simple format
        if is_unclear and symbol and stock_data and "error" not in stock_data:
            if not is_historical:
                # Return simple format: symbol, current price, current time
                current_price = stock_data.get('current_price', 0)
                name = stock_data.get('name', symbol)
                return f"{{\n  \"symbol\": \"{symbol}\",\n  \"name\": \"{name}\",\n  \"current_price\": {current_price},\n  \"previous_close\": {stock_data.get('previous_close', 0)},\n  \"change\": {stock_data.get('change', 0)},\n  \"change_percent\": {stock_data.get('change_percent', 0)},\n  \"timestamp\": \"{current_time}\"\n}}"
            else:
                # For historical data, return date and closing price
                close_price = stock_data.get('close', 0)
                historical_date = stock_data.get('data_timestamp', stock_data.get('date', date))
                name = stock_data.get('name', symbol)
                return f"{{\n  \"symbol\": \"{symbol}\",\n  \"name\": \"{name}\",\n  \"date\": \"{stock_data.get('date', date)}\",\n  \"close\": {close_price},\n  \"open\": {stock_data.get('open', 0)},\n  \"high\": {stock_data.get('high', 0)},\n  \"low\": {stock_data.get('low', 0)}\n}}"
        
        # If we have stock data but query wasn't unclear, ensure we still return the data
        # This handles cases where LLM might not use the stock_context properly
        if symbol and stock_data and "error" not in stock_data and stock_context:
            # We have valid stock data and context - proceed with LLM but with strong instructions
            pass
        
        # Format conversation history
        messages = self._format_history(history)
        
        # Add current user message with stock context if available
        user_message = message + stock_context if stock_context else message
        messages.append(HumanMessage(content=user_message))
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        response_text = response.content
        
        # If we have stock data but LLM didn't mention the price, force include it
        if symbol and stock_data and "error" not in stock_data:
            if not is_historical:
                current_price = stock_data.get('current_price', 0)
                # Check if price is mentioned in response
                price_mentioned = re.search(r'\$?\d+\.?\d*', response_text)
                if not price_mentioned and current_price > 0:
                    # Price not mentioned, prepend it
                    response_text = f"As of {current_time}: {symbol} is ${current_price:.2f}. " + response_text
        
        # VALIDATION: Check if AI mentioned a price that doesn't match our data
        if symbol and stock_context:
            if is_historical:
                actual_price = stock_data.get('close', 0)
                historical_date = stock_data.get('data_timestamp', stock_data.get('date', date))
                # Extract any price mentioned in response
                mentioned_prices = re.findall(r'\$([0-9,]+\.?[0-9]*)', response_text)
                
                for price_str in mentioned_prices:
                    price_str = price_str.replace(',', '')
                    try:
                        mentioned_price = float(price_str)
                        # If AI mentioned a wildly different price, force correct it
                        if abs(mentioned_price - actual_price) > 100:
                            logger.error(f"AI HALLUCINATION DETECTED: Said ${mentioned_price} but actual is ${actual_price}")
                            # Force the correct response
                            response_text = f"On {historical_date}, {symbol} closed at ${actual_price:.2f}"
                            break
                    except ValueError:
                        continue
            else:
                actual_price = stock_data.get('current_price', 0)
                # Extract any price mentioned in response
                mentioned_prices = re.findall(r'\$([0-9,]+\.?[0-9]*)', response_text)
                
                for price_str in mentioned_prices:
                    price_str = price_str.replace(',', '')
                    try:
                        mentioned_price = float(price_str)
                        # If AI mentioned a wildly different price, force correct it
                        if abs(mentioned_price - actual_price) > 100:
                            logger.error(f"AI HALLUCINATION DETECTED: Said ${mentioned_price} but actual is ${actual_price}")
                            # Force the correct response
                            response_text = f"As of {current_time}: {symbol} is ${actual_price:.2f}"
                            if stock_data.get('change'):
                                change = stock_data['change']
                                change_pct = stock_data.get('change_percent', 0)
                                direction = "up" if change > 0 else "down"
                                response_text += f", {direction} ${abs(change):.2f} ({change_pct:+.2f}%)"
                            break
                    except ValueError:
                        continue
        
        return response_text


# Global agent instance
chat_agent = ChatAgent()

