"""
LangChain agent setup and configuration.

This module provides the ChatAgent class that handles AI-powered chat interactions
with integrated stock market data fetching capabilities.
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from core.config import settings
from utils.stock_data import stock_data_service
from utils.sentiment_analysis import sentiment_analyzer
import logging
import re

# Try to import ChromaDB client, handle gracefully if unavailable
try:
    from utils.chromadb_client import chromadb_client, CHROMADB_AVAILABLE
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb_client = None

logger = logging.getLogger(__name__)


class ChatAgent:
    """LangChain chat agent with RAG and stock data capabilities."""
    
    def __init__(self):
        """Initialize the chat agent with OpenAI LLM and RAG retriever."""
        self.llm = ChatOpenAI(
            model=settings.llm_model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )
        
        # Initialize ChromaDB retriever if available
        self.retriever = None
        self.use_rag = False
        if CHROMADB_AVAILABLE and chromadb_client:
            try:
                self.retriever = chromadb_client.get_retriever(k=4)
                self.use_rag = True
                logger.info("ChromaDB RAG retriever initialized")
            except Exception as e:
                logger.warning(f"Could not initialize ChromaDB retriever: {e}")
                self.use_rag = False
        else:
            logger.info("ChromaDB not available, RAG disabled")
        
        # Get current date and time in EST timezone for context
        est_tz = ZoneInfo("America/New_York")
        current_datetime = datetime.now(est_tz)
        current_date = current_datetime.strftime("%B %d, %Y")
        current_time = current_datetime.strftime("%I:%M %p %Z")
        
        # System prompt for the trading assistant - EXTREMELY EXPLICIT
        self.base_system_prompt = f"""You are TradePal AI - a DATA-DRIVEN trading assistant.

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

DOCUMENT CONTEXT (RAG):
- When [DOCUMENT CONTEXT] is provided, use it to answer questions about policies, billing, technical documentation
- Cite specific information from documents when relevant
- If document context contradicts stock data, prioritize stock data for price-related queries
- For general questions, use document context as primary source

MARKET SENTIMENT (CRITICAL - ALWAYS INCLUDE):
- When sentiment data is provided, you MUST include ALL sentiment details in your response
- ALWAYS mention: Overall sentiment score, news sentiment with article count, Reddit sentiment with mention count
- ALWAYS include: Investment guidance and Call/Put recommendation
- Format: "Market Sentiment: [OVERALL_SENTIMENT] (Score: [SCORE])
  - News Sentiment: [LABEL] from [ARTICLE_COUNT] articles analyzed (Score: [SCORE])
  - Reddit Sentiment: [LABEL] from [MENTION_COUNT] posts (Score: [SCORE], Bullish: [X], Bearish: [Y])
  - Investment Guidance: [GUIDANCE]
  - Call/Put Recommendation: [CALL/PUT]"
- These numbers are CRITICAL for investment decisions - NEVER skip them

RESPONSE FORMAT:
- For stock queries: "As of [DATE] at [TIME]: [SYMBOL] is $[EXACT_PRICE_FROM_DATA]. [Sentiment data]"
- For document queries: Use information from [DOCUMENT CONTEXT] and cite sources
- For general questions: Combine available context appropriately

BANNED PHRASES:
- "As of my last update"
- "According to my training data"
- "Approximately"
- "Around"
- "Roughly"

BE DIRECT. BE ACCURATE. USE ONLY THE DATA PROVIDED."""
    
    def _retrieve_documents(self, query: str) -> str:
        """
        Retrieve relevant documents from ChromaDB using RAG.
        
        Args:
            query: User query to search for
            
        Returns:
            Formatted document context string or empty string if no documents found
        """
        if not self.use_rag or not self.retriever:
            return ""
        
        try:
            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(query)
            
            if not docs:
                return ""
            
            # Format documents for context
            context_parts = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                doc_type = doc.metadata.get('document_type', 'general')
                
                context_parts.append(
                    f"[Document {i} - {doc_type}]\n"
                    f"Source: {source} (Page {page})\n"
                    f"Content: {doc.page_content}\n"
                )
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Error retrieving documents: {e}")
            return ""
    
    def _format_history(self, history: List[Dict[str, str]], document_context: str = "") -> List:
        """Convert history dict to LangChain message format."""
        # Build system prompt with document context if available
        system_content = self.base_system_prompt
        if document_context:
            system_content += f"\n\n[DOCUMENT CONTEXT]\n{document_context}"
        
        messages = [SystemMessage(content=system_content)]
        
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
        history: List[Dict[str, str]] = None,
        use_rag: bool = True
    ) -> str:
        """
        Get response from the agent with optional RAG.
        
        Args:
            message: User's message
            history: Conversation history
            use_rag: Whether to use RAG retrieval (default: True)
            
        Returns:
            AI response string
        """
        if history is None:
            history = []
        
        # Check if this is a stock-related query and detect date
        is_stock_query, symbol, date = self._check_for_stock_query(message)
        
        # Retrieve documents using RAG (for non-stock queries or to supplement stock queries)
        document_context = ""
        if use_rag and self.use_rag:
            # Retrieve documents for general queries or to supplement stock queries
            # Skip RAG for very simple stock price queries to avoid unnecessary retrieval
            if not is_stock_query or (is_stock_query and len(message.split()) > 5):
                document_context = self._retrieve_documents(message)
                if document_context:
                    logger.info(f"Retrieved {len(document_context.split('[Document')) - 1} documents for RAG")
        
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
                
                # Fetch sentiment data (only for current quotes, not historical)
                sentiment_data = None
                if not is_historical and "error" not in stock_data:
                    try:
                        sentiment_data = sentiment_analyzer.get_stock_sentiment(symbol)
                    except Exception as e:
                        logger.warning(f"Error fetching sentiment for {symbol}: {e}")
                        sentiment_data = None
                
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
                        
                        # Add sentiment data if available
                        if sentiment_data and "error" not in sentiment_data:
                            overall_sentiment = sentiment_data.get('overall_sentiment', 'NEUTRAL')
                            overall_score = sentiment_data.get('overall_score', 0.0)
                            news_sentiment = sentiment_data.get('news_sentiment')
                            reddit_sentiment = sentiment_data.get('reddit_sentiment')
                            
                            # Determine investment guidance
                            if overall_score >= 0.5:
                                investment_guidance = "STRONG BULLISH - Consider CALL options or LONG positions"
                                call_put_recommendation = "CALL"
                            elif overall_score >= 0.2:
                                investment_guidance = "BULLISH - Consider CALL options or LONG positions"
                                call_put_recommendation = "CALL"
                            elif overall_score <= -0.5:
                                investment_guidance = "STRONG BEARISH - Consider PUT options or SHORT positions"
                                call_put_recommendation = "PUT"
                            elif overall_score <= -0.2:
                                investment_guidance = "BEARISH - Consider PUT options or SHORT positions"
                                call_put_recommendation = "PUT"
                            else:
                                investment_guidance = "NEUTRAL - Wait for clearer signals before taking positions"
                                call_put_recommendation = "NEUTRAL"
                            
                            stock_context += f"\n{'═'*70}\n"
                            stock_context += f"📊 MARKET SENTIMENT ANALYSIS 📊\n"
                            stock_context += f"{'═'*70}\n\n"
                            stock_context += f"╔{'═'*68}╗\n"
                            stock_context += f"║  OVERALL SENTIMENT: {overall_sentiment:<20} Score: {overall_score:+.3f}  ║\n"
                            stock_context += f"╚{'═'*68}╝\n\n"
                            
                            if news_sentiment:
                                news_label = news_sentiment.get('sentiment_label', 'N/A')
                                news_score = news_sentiment.get('sentiment_score', 0)
                                news_count = news_sentiment.get('news_count', 0)
                                news_confidence = news_sentiment.get('confidence', 0)
                                
                                stock_context += f"📰 NEWS SENTIMENT (Alpha Vantage):\n"
                                stock_context += f"   Sentiment Label: {news_label}\n"
                                stock_context += f"   Sentiment Score: {news_score:+.3f} (range: -1.0 to +1.0)\n"
                                stock_context += f"   Articles Analyzed: {news_count} articles\n"
                                stock_context += f"   Confidence Level: {news_confidence:.1%}\n"
                                stock_context += f"   Source: Professional financial news analysis\n\n"
                            
                            if reddit_sentiment:
                                reddit_label = reddit_sentiment.get('sentiment_label', 'N/A')
                                reddit_score = reddit_sentiment.get('sentiment_score', 0)
                                reddit_mentions = reddit_sentiment.get('mentions', 0)
                                reddit_bullish = reddit_sentiment.get('bullish_posts', 0)
                                reddit_bearish = reddit_sentiment.get('bearish_posts', 0)
                                
                                stock_context += f"💬 REDDIT SENTIMENT (r/wallstreetbets):\n"
                                stock_context += f"   Sentiment Label: {reddit_label}\n"
                                stock_context += f"   Sentiment Score: {reddit_score:+.3f} (range: -1.0 to +1.0)\n"
                                stock_context += f"   Total Mentions: {reddit_mentions} posts\n"
                                stock_context += f"   Bullish Posts: {reddit_bullish} posts\n"
                                stock_context += f"   Bearish Posts: {reddit_bearish} posts\n"
                                stock_context += f"   Source: Retail investor sentiment from Reddit\n\n"
                            
                            stock_context += f"{'─'*70}\n"
                            stock_context += f"💡 INVESTMENT GUIDANCE:\n"
                            stock_context += f"{'─'*70}\n"
                            stock_context += f"Recommendation: {investment_guidance}\n"
                            stock_context += f"Call/Put Side: {call_put_recommendation}\n"
                            stock_context += f"\n⚠️  IMPORTANT: This is sentiment analysis only, not financial advice.\n"
                            stock_context += f"Always do your own research and consider risk management.\n"
                            stock_context += f"{'═'*70}\n\n"
                            
                            # Add explicit instruction to include sentiment in response
                            stock_context += f"\n{'🚨'*25}\n"
                            stock_context += f"⚠️  YOU MUST INCLUDE SENTIMENT DATA IN YOUR RESPONSE ⚠️\n"
                            stock_context += f"{'🚨'*25}\n\n"
                            stock_context += f"REQUIRED SENTIMENT INFORMATION TO MENTION:\n"
                            stock_context += f"1. Overall Sentiment: {overall_sentiment} (Score: {overall_score:+.3f})\n"
                            if news_sentiment:
                                stock_context += f"2. News Sentiment: {news_sentiment.get('sentiment_label')} from {news_sentiment.get('news_count', 0)} articles\n"
                            if reddit_sentiment:
                                stock_context += f"3. Reddit Sentiment: {reddit_sentiment.get('sentiment_label')} from {reddit_sentiment.get('mentions', 0)} posts\n"
                            stock_context += f"4. Investment Guidance: {investment_guidance}\n"
                            stock_context += f"5. Call/Put Recommendation: {call_put_recommendation}\n\n"
                            stock_context += f"DO NOT SKIP THESE NUMBERS - THEY ARE CRITICAL FOR INVESTMENT DECISIONS.\n"
                            stock_context += f"{'🚨'*25}\n\n"
                        
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
                # Return simple format: symbol, current price, current time, sentiment
                current_price = stock_data.get('current_price', 0)
                name = stock_data.get('name', symbol)
                
                # Build sentiment string with all details
                sentiment_str = ""
                if sentiment_data and "error" not in sentiment_data:
                    overall_sentiment = sentiment_data.get('overall_sentiment', 'NEUTRAL')
                    overall_score = sentiment_data.get('overall_score', 0.0)
                    news_sentiment = sentiment_data.get('news_sentiment')
                    reddit_sentiment = sentiment_data.get('reddit_sentiment')
                    
                    # Determine call/put recommendation
                    if overall_score >= 0.2:
                        call_put = "CALL"
                    elif overall_score <= -0.2:
                        call_put = "PUT"
                    else:
                        call_put = "NEUTRAL"
                    
                    sentiment_str = f',\n  "sentiment": {{\n    "overall": "{overall_sentiment}",\n    "overall_score": {overall_score}'
                    
                    if news_sentiment:
                        news_label = news_sentiment.get("sentiment_label", "N/A")
                        news_score = news_sentiment.get("sentiment_score", 0)
                        news_count = news_sentiment.get("news_count", 0)
                        sentiment_str += f',\n    "news": {{\n      "label": "{news_label}",\n      "score": {news_score},\n      "articles_analyzed": {news_count}\n    }}'
                    
                    if reddit_sentiment:
                        reddit_label = reddit_sentiment.get("sentiment_label", "N/A")
                        reddit_score = reddit_sentiment.get("sentiment_score", 0)
                        reddit_mentions = reddit_sentiment.get("mentions", 0)
                        reddit_bullish = reddit_sentiment.get("bullish_posts", 0)
                        reddit_bearish = reddit_sentiment.get("bearish_posts", 0)
                        sentiment_str += f',\n    "reddit": {{\n      "label": "{reddit_label}",\n      "score": {reddit_score},\n      "mentions": {reddit_mentions},\n      "bullish_posts": {reddit_bullish},\n      "bearish_posts": {reddit_bearish}\n    }}'
                    
                    sentiment_str += f',\n    "call_put_recommendation": "{call_put}"\n  }}'
                
                return f"{{\n  \"symbol\": \"{symbol}\",\n  \"name\": \"{name}\",\n  \"current_price\": {current_price},\n  \"previous_close\": {stock_data.get('previous_close', 0)},\n  \"change\": {stock_data.get('change', 0)},\n  \"change_percent\": {stock_data.get('change_percent', 0)},\n  \"timestamp\": \"{current_time}\"{sentiment_str}\n}}"
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
        
        # Format conversation history with document context
        messages = self._format_history(history, document_context=document_context)
        
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
                
                # Check if sentiment is mentioned and force include if missing
                if sentiment_data and "error" not in sentiment_data:
                    sentiment_mentioned = re.search(r'(sentiment|bullish|bearish|neutral|call|put)', response_text.lower())
                    if not sentiment_mentioned:
                        # Sentiment not mentioned, append it
                        overall_sentiment = sentiment_data.get('overall_sentiment', 'NEUTRAL')
                        overall_score = sentiment_data.get('overall_score', 0.0)
                        news_sentiment = sentiment_data.get('news_sentiment')
                        reddit_sentiment = sentiment_data.get('reddit_sentiment')
                        
                        sentiment_info = f"\n\nMarket Sentiment: {overall_sentiment} (Score: {overall_score:+.3f})"
                        
                        if news_sentiment:
                            sentiment_info += f"\n- News Sentiment: {news_sentiment.get('sentiment_label')} from {news_sentiment.get('news_count', 0)} articles analyzed (Score: {news_sentiment.get('sentiment_score', 0):+.3f})"
                        
                        if reddit_sentiment:
                            sentiment_info += f"\n- Reddit Sentiment: {reddit_sentiment.get('sentiment_label')} from {reddit_sentiment.get('mentions', 0)} posts (Score: {reddit_sentiment.get('sentiment_score', 0):+.3f}, Bullish: {reddit_sentiment.get('bullish_posts', 0)}, Bearish: {reddit_sentiment.get('bearish_posts', 0)})"
                        
                        # Add investment guidance
                        if overall_score >= 0.2:
                            call_put = "CALL"
                            guidance = "Consider CALL options or LONG positions"
                        elif overall_score <= -0.2:
                            call_put = "PUT"
                            guidance = "Consider PUT options or SHORT positions"
                        else:
                            call_put = "NEUTRAL"
                            guidance = "Wait for clearer signals"
                        
                        sentiment_info += f"\n- Investment Guidance: {guidance}\n- Call/Put Recommendation: {call_put}"
                        
                        response_text += sentiment_info
        
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
    
    async def get_response_stream(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        use_rag: bool = True
    ):
        """
        Get streaming response from the agent.
        
        Args:
            message: User's message
            history: Conversation history
            use_rag: Whether to use RAG retrieval (default: True)
            
        Yields:
            Response chunks as strings
        """
        if history is None:
            history = []
        
        # Check if this is a stock-related query and detect date
        is_stock_query, symbol, date = self._check_for_stock_query(message)
        
        # Retrieve documents using RAG
        document_context = ""
        if use_rag and self.use_rag:
            if not is_stock_query or (is_stock_query and len(message.split()) > 5):
                document_context = self._retrieve_documents(message)
        
        # Format messages with document context
        messages = self._format_history(history, document_context=document_context)
        
        # Add user message (stock context will be added in get_response for non-streaming)
        messages.append(HumanMessage(content=message))
        
        # Stream response from LLM
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content


# Global agent instance
chat_agent = ChatAgent()

