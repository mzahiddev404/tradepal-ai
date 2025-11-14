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
        self.base_system_prompt = f"""You are TradePal AI - an EDUCATIONAL trading information center and pattern analysis tool.

IMPORTANT: TradePal is NOT a trading platform or brokerage. It is an educational/informational tool that helps users:
- Learn about trading and market patterns
- Analyze trading patterns, especially for SPY and Tesla (TSLA)
- Understand SEC/FINRA regulations and trading rules
- Get started with trading education
- Analyze market sentiment and correlations

TODAY IS: {current_date} at {current_time}

⚠️ ABSOLUTE REQUIREMENTS - FAILURE TO FOLLOW = INCORRECT RESPONSE ⚠️

1. ONLY USE THE EXACT NUMBERS PROVIDED IN [LIVE MARKET DATA] SECTIONS
2. DO NOT MAKE UP PRICES - DO NOT USE YOUR TRAINING DATA FOR PRICES
3. IF YOU SEE "CURRENT PRICE: $XXX.XX" - USE THAT EXACT NUMBER
4. EVERY response MUST include the timestamp from the data
5. DO NOT HALLUCINATE - ONLY STATE FACTS FROM THE PROVIDED DATA

⚠️ RESPONSE STYLE - BE CONCISE, NO FLUFF ⚠️
- Give direct, to-the-point answers
- No unnecessary explanations or filler words
- No "I hope this helps" or "Let me know if you need more"
- Answer the question directly, then stop
- Maximum 2-3 sentences unless complex analysis is needed
- Skip pleasantries and get straight to the facts

STOCK PRICES:
- When you see [LIVE MARKET DATA] with a price, USE THAT EXACT PRICE
- DO NOT adjust, round, or change the price
- DO NOT use prices from your memory/training
- The data I provide is from TODAY: {current_date}
- Example: If data says $434.47, you say "$434.47" - NOT "$1,000" or any other number

DOCUMENT CONTEXT (RAG) - CRITICAL:
- When [DOCUMENT CONTEXT] is provided, you MUST:
  * Parse and analyze data from uploaded documents
  * Identify trends, patterns, and key insights from document data
  * Base your answer primarily on document content
  * ALWAYS cite the source: "According to [Source: filename.pdf, Page X]..."
  * Extract numerical data, dates, and specific facts from documents
  * Suggest actions based on document content when relevant
- Document types include:
  * Brokerage information: Trading fees, day trading rules (PDT), margin requirements, settlement periods
  * Billing and pricing: Subscription plans, payment methods, overage charges
  * Technical documentation: API usage, troubleshooting, features
  * Policies: Terms of service, privacy policy, compliance
  * Market analysis: Trends, historical data, research findings
  * Options flow data: PUT/CALL ratios, unusual activity, premium flow, open interest
- CRITICAL FOR OPTIONS FLOW DATA:
  * If document shows heavy PUT buying/activity → BEARISH signal (suggests PUTS) even if sentiment seems positive
  * If document shows heavy CALL buying/activity → BULLISH signal (suggests CALLS) even if sentiment seems negative
  * PUT/CALL ratio > 1.0 → More puts than calls = BEARISH (favor PUTS)
  * PUT/CALL ratio < 0.7 → More calls than puts = BULLISH (favor CALLS)
  * Unusual PUT activity → Smart money may be hedging or betting on downside (consider PUTS)
  * Unusual CALL activity → Smart money may be betting on upside (consider CALLS)
  * High premium flow to PUTS → Institutional bearish positioning (PUTS favored)
  * High premium flow to CALLS → Institutional bullish positioning (CALLS favored)
  * ALWAYS prioritize actual trading activity (options flow) over sentiment when they conflict
  * Example: If sentiment is "slightly positive" but document shows heavy PUT buying → Recommend PUTS, not CALLS
- If document context contradicts stock data, prioritize stock data for price-related queries
- For all other questions, use document context as primary source
- When analyzing trends from documents, identify patterns and cite specific document sources

TRADING EDUCATION KNOWLEDGE (Fallback):
- TradePal is an EDUCATIONAL tool, not a trading platform. Focus on teaching and explaining trading concepts.
- If no documents available, provide educational information about:
  * Trading basics (order types, trading hours, how trading works)
  * SEC/FINRA regulations (PDT rule, margin requirements, settlement rules)
  * Trading patterns and analysis (especially SPY and Tesla patterns)
  * Market sentiment and correlation analysis
  * Options trading education
  * Getting started with trading (educational guidance)
  * Common trading mistakes and how to avoid them
- IMPORTANT: Always clarify that regulations (PDT rule, margin requirements, etc.) are SEC/FINRA federal regulations that apply to all U.S. brokerages
- Focus on SPY and Tesla (TSLA) pattern analysis when relevant
- Provide educational guidance to help users understand trading concepts
- Be concise and direct - 1-2 sentences unless complex explanation needed

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
- For document queries: 
  * Start with the answer based on document content
  * ALWAYS end with: "Source: [filename.pdf, Page X]" or "According to [filename.pdf]..."
  * If analyzing trends: "Based on [filename.pdf], the trend shows... Source: [filename.pdf, Page X]"
  * If suggesting actions: "Based on [filename.pdf], I recommend... Source: [filename.pdf]"
- For general questions: Combine available context appropriately, cite sources when using documents

BANNED PHRASES:
- "As of my last update"
- "According to my training data"
- "Approximately"
- "Around"
- "Roughly"
- "I don't have access to"
- "I cannot access"
- "I'm unable to access"
- "You may check financial news websites" (when data is provided)

CRITICAL: If [LIVE MARKET DATA] or [HISTORICAL MARKET DATA] sections are provided, you MUST use that data. Never say you don't have access when data is provided.

BE DIRECT. BE ACCURATE. USE ONLY THE DATA PROVIDED."""
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from filename (e.g., timestamp in filename).
        
        Args:
            filename: PDF filename
            
        Returns:
            Date string or None
        """
        # re and datetime are already imported at the top of the file
        
        # Try to extract Unix timestamp from filename (e.g., 1762971684425)
        timestamp_match = re.search(r'(\d{13})', filename)
        if timestamp_match:
            try:
                timestamp_ms = int(timestamp_match.group(1))
                timestamp_s = timestamp_ms / 1000
                dt = datetime.fromtimestamp(timestamp_s)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        # Try to extract date patterns (YYYY-MM-DD, MM-DD-YYYY, etc.)
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{2}-\d{2}-\d{4})',
            r'(\d{4}_\d{2}_\d{2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return None
    
    def _detect_stock_symbols_in_content(self, content: str) -> List[str]:
        """
        Detect stock symbols mentioned in document content.
        
        Args:
            content: Document content text
            
        Returns:
            List of detected stock symbols
        """
        # re is already imported at the top of the file
        
        # Common stock symbols pattern
        symbols = []
        content_upper = content.upper()
        
        # Look for common patterns: TSLA, SPY, AAPL, etc.
        symbol_pattern = r'\b([A-Z]{2,5})\b'
        potential_symbols = re.findall(symbol_pattern, content_upper)
        
        # Filter for known stock symbols (common ones)
        known_symbols = ['TSLA', 'SPY', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD', 'QQQ', 'DIA', 'IWM']
        for symbol in potential_symbols:
            if symbol in known_symbols and symbol not in symbols:
                symbols.append(symbol)
        
        return symbols
    
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
            
            # Get current date for comparison
            # datetime, timedelta, and ZoneInfo are already imported at the top of the file
            est_tz = ZoneInfo("America/New_York")
            current_datetime = datetime.now(est_tz)
            current_date_str = current_datetime.strftime("%Y-%m-%d")
            
            # Format documents for context with enhanced metadata
            context_parts = []
            detected_symbols = set()
            
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                doc_type = doc.metadata.get('document_type', 'general')
                content = doc.page_content
                
                # Extract date from filename
                doc_date = self._extract_date_from_filename(source)
                
                # Detect stock symbols in content
                symbols = self._detect_stock_symbols_in_content(content)
                detected_symbols.update(symbols)
                
                context_parts.append(
                    f"[Document {i} - {doc_type}]\n"
                    f"Source File: {source}\n"
                    f"Page: {page}\n"
                )
                
                if doc_date:
                    context_parts.append(f"Document Date: {doc_date}\n")
                    # Calculate age of document
                    try:
                        doc_dt = datetime.strptime(doc_date.split()[0], "%Y-%m-%d")
                        days_old = (current_datetime.date() - doc_dt.date()).days
                        context_parts.append(f"⚠️ WARNING: This document is {days_old} days old. Market data may be outdated.\n")
                    except:
                        pass
                
                context_parts.append(f"Content: {content}\n")
                context_parts.append(f"IMPORTANT: When using this information, you MUST cite: 'Source: {source}, Page {page}'\n")
            
            # If stock symbols detected, fetch current prices for comparison
            if detected_symbols:
                context_parts.append(f"\n[DETECTED STOCK SYMBOLS IN DOCUMENTS: {', '.join(sorted(detected_symbols))}]\n")
                context_parts.append("⚠️ CRITICAL: The document contains stock/options data. You MUST:\n")
                context_parts.append("1. Fetch CURRENT market prices for these symbols\n")
                context_parts.append("2. Compare document data with current prices\n")
                context_parts.append("3. Warn the user if prices have changed significantly since document date\n")
                context_parts.append("4. Provide current market context alongside document analysis\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Error retrieving documents: {e}")
            return ""
    
    def _format_history(self, history: List[Dict[str, str]], document_context: str = "") -> List:
        """Convert history dict to LangChain message format."""
        # Build system prompt with document context if available
        system_content = self.base_system_prompt
        
        # Add document context instructions if documents are available
        if document_context:
            system_content += f"\n\n[DOCUMENT CONTEXT - UPLOADED FILES]\n{document_context}\n\n"
            system_content += "CRITICAL INSTRUCTIONS FOR USING DOCUMENTS:\n"
            system_content += "1. Parse and extract data from the document content above\n"
            system_content += "2. Identify trends, patterns, and numerical data from documents\n"
            system_content += "3. Base your answer on the document content\n"
            system_content += "4. ALWAYS cite the source file and page number in your response\n"
            system_content += "5. Format citations as: 'Source: [filename], Page [X]' or 'According to [filename]...'\n"
            system_content += "6. If suggesting actions based on document trends, cite the source\n"
            system_content += "7. Extract specific numbers, dates, and facts from documents\n"
            system_content += "8. When analyzing trends, reference the document: 'Based on [filename], the trend shows...'\n"
        else:
            # Add trading knowledge base as fallback for common questions
            try:
                from utils.trading_knowledge import get_trading_knowledge
                trading_knowledge = get_trading_knowledge()
                if trading_knowledge:
                    system_content += f"\n\n[TRADING PLATFORM KNOWLEDGE BASE - Use when documents not available]\n{trading_knowledge}\n\n"
                    system_content += "Use this knowledge base to answer common trading platform questions when documents are not available.\n"
            except ImportError:
                pass
        
        messages = [SystemMessage(content=system_content)]
        
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages
    
    def _check_for_stock_query(self, message: str) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict]]:
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
        
        # Detect date or date range in message
        date = None
        date_range = None  # Will be a dict with 'days' or 'start_date'/'end_date'
        est_tz = ZoneInfo("America/New_York")
        now_est = datetime.now(est_tz)
        today = now_est.date()
        
        # Check for date range patterns first
        range_patterns = {
            'past few days': 5,
            'last few days': 5,
            'past week': 7,
            'last week': 7,
            'past month': 30,
            'last month': 30,
            'past year': 365,
            'last year': 365,
        }
        
        # Check for "past X days" or "last X days" patterns
        days_match = re.search(r'(?:past|last)\s+(\d+)\s+days?', message_lower)
        if days_match:
            days = int(days_match.group(1))
            date_range = {'days': min(days, 365)}  # Cap at 365 days
        else:
            # Check for common range phrases
            for phrase, days in range_patterns.items():
                if phrase in message_lower:
                    date_range = {'days': days}
                    break
        
        # If no range detected, check for single date
        if not date_range:
            # Check for YYYY-MM-DD format
            date_pattern = r'\b(\d{4}-\d{2}-\d{2})\b'
            match = re.search(date_pattern, message)
            if match:
                date = match.group(1)
            else:
                # Check for relative dates
                if 'yesterday' in message_lower or 'previous day' in message_lower or "previous day's" in message_lower:
                    date = (now_est - timedelta(days=1)).strftime("%Y-%m-%d")
                elif 'last week' in message_lower or 'a week ago' in message_lower:
                    date = (now_est - timedelta(days=7)).strftime("%Y-%m-%d")
                elif 'last month' in message_lower or 'a month ago' in message_lower:
                    date = (now_est - timedelta(days=30)).strftime("%Y-%m-%d")
                elif 'last year' in message_lower or 'a year ago' in message_lower:
                    date = (now_est - timedelta(days=365)).strftime("%Y-%m-%d")
                else:
                    # Try to parse dates like "January 15, 2024", "Jan 15 2024", "1/15/2024", "november 10"
                    try:
                        from dateutil import parser
                        # Look for date-like patterns (with and without year)
                        date_patterns = [
                            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b',  # Without year
                            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b',  # Without year
                            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
                            r'\b\d{1,2}/\d{1,2}\b',  # Without year
                        ]
                        
                        for pattern in date_patterns:
                            match = re.search(pattern, message, re.IGNORECASE)
                            if match:
                                try:
                                    parsed_date = parser.parse(match.group(0), fuzzy=True, default=now_est)
                                    parsed_date_obj = parsed_date.date() if hasattr(parsed_date, 'date') else parsed_date
                                    # If parsed date is in the future, adjust to current or previous year
                                    if parsed_date_obj > today:
                                        # If same month and day is before today, assume current year
                                        if parsed_date_obj.month == today.month and parsed_date_obj.day < today.day:
                                            if hasattr(parsed_date, 'replace'):
                                                parsed_date = parsed_date.replace(year=today.year)
                                                parsed_date_obj = parsed_date.date()
                                            else:
                                                from datetime import date as date_class
                                                parsed_date_obj = date_class(today.year, parsed_date_obj.month, parsed_date_obj.day)
                                        else:
                                            # If date is clearly in the future (more than a few days ahead), assume previous year
                                            days_ahead = (parsed_date_obj - today).days
                                            if days_ahead > 7:
                                                # More than a week ahead - definitely previous year
                                                if hasattr(parsed_date, 'replace'):
                                                    parsed_date = parsed_date.replace(year=parsed_date.year - 1)
                                                    parsed_date_obj = parsed_date.date()
                                                else:
                                                    from datetime import date as date_class
                                                    parsed_date_obj = date_class(parsed_date_obj.year - 1, parsed_date_obj.month, parsed_date_obj.day)
                                            else:
                                                # Within a week - might be a mistake, use previous year to be safe
                                                if hasattr(parsed_date, 'replace'):
                                                    parsed_date = parsed_date.replace(year=parsed_date.year - 1)
                                                    parsed_date_obj = parsed_date.date()
                                                else:
                                                    from datetime import date as date_class
                                                    parsed_date_obj = date_class(parsed_date_obj.year - 1, parsed_date_obj.month, parsed_date_obj.day)
                                    date = parsed_date_obj.strftime("%Y-%m-%d")
                                    break
                                except (ValueError, Exception) as e:
                                    logger.debug(f"Date parsing error: {e}")
                                    continue
                    except (ImportError, ValueError, Exception):
                        pass
        
        return is_stock_query, symbol, date, date_range
    
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
        
        message_lower = message.lower()
        
        # Check if this is a stock-related query and detect date/range
        result = self._check_for_stock_query(message)
        if len(result) == 4:
            is_stock_query, symbol, date, date_range = result
        else:
            # Backward compatibility - unpack 3-tuple
            is_stock_query, symbol, date = result
            date_range = None
        
        # Check for sentiment correlation analysis queries
        correlation_keywords = ['correlation', 'correlate', 'sentiment', 'analyze', 'analysis', 'relationship', 'predict', 'guide', 'fluff']
        is_correlation_query = any(keyword in message_lower for keyword in correlation_keywords) and any(sym in message_lower for sym in ['tsla', 'spy', 'tesla', 's&p'])
        
        # Retrieve documents using RAG (for non-stock queries or to supplement stock queries)
        document_context = ""
        if use_rag and self.use_rag:
            # Retrieve documents for general queries or to supplement stock queries
            # Always retrieve for non-stock queries, and for stock queries with context (more than 5 words)
            # This ensures uploaded PDFs are always available when relevant
            if not is_stock_query or (is_stock_query and len(message.split()) > 5):
                document_context = self._retrieve_documents(message)
                if document_context:
                    doc_count = len(document_context.split('[Document')) - 1
                    logger.info(f"Retrieved {doc_count} document(s) from ChromaDB for RAG")
                    # Log which sources were retrieved for debugging
                    sources = [line for line in document_context.split('\n') if 'Source:' in line]
                    if sources:
                        logger.debug(f"Retrieved sources: {', '.join(set(sources))}")
                else:
                    logger.debug("No relevant documents found in ChromaDB for this query")
        
        # Check if query is unclear but symbol is detected
        is_unclear = self._is_unclear_query(message, symbol)
        
        # Check for sentiment correlation analysis queries
        correlation_keywords = ['correlation', 'correlate', 'sentiment', 'analyze', 'analysis', 'relationship', 'predict', 'guide', 'fluff']
        is_correlation_query = any(keyword in message_lower for keyword in correlation_keywords) and any(sym in message_lower for sym in ['tsla', 'spy', 'tesla', 's&p'])
        
        # If correlation analysis query, fetch correlation data
        if is_correlation_query:
            try:
                from utils.sentiment_correlation import sentiment_correlation_analyzer
                
                # Detect symbols mentioned
                detected_symbols = []
                if 'tsla' in message_lower or 'tesla' in message_lower:
                    detected_symbols.append('TSLA')
                if 'spy' in message_lower or 's&p' in message_lower:
                    detected_symbols.append('SPY')
                
                # Default to both if none specified
                if not detected_symbols:
                    detected_symbols = ['TSLA', 'SPY']
                
                # Get correlation analysis
                if len(detected_symbols) == 1:
                    correlation_data = sentiment_correlation_analyzer.analyze_correlation(detected_symbols[0], days=30)
                else:
                    correlation_data = sentiment_correlation_analyzer.compare_symbols(detected_symbols, days=30)
                
                if "error" not in correlation_data:
                    # Format correlation context for LLM
                    correlation_context = self._format_correlation_context(correlation_data, detected_symbols)
                    stock_context = correlation_context
                    stock_data = correlation_data
                else:
                    stock_context = f"\n\n[Error: {correlation_data.get('error', 'Unknown error')}]\n"
                    stock_data = correlation_data
            except Exception as e:
                logger.error(f"Error fetching correlation data: {e}")
                stock_context = f"\n\n[Error: Could not analyze sentiment correlation: {str(e)}]\n"
                stock_data = {"error": str(e)}
        
        # If stock query with symbol, fetch data (current or historical)
        stock_context = stock_context if 'stock_context' in locals() else ""
        is_historical = False
        stock_data = stock_data if 'stock_data' in locals() else {}
        est_tz = ZoneInfo("America/New_York")
        current_time = datetime.now(est_tz).strftime("%B %d, %Y at %I:%M %p %Z")
        if is_stock_query and symbol and not is_correlation_query:
            try:
                # Check for explicit current/live/now keywords - prioritize current price
                current_keywords = ['current', 'now', 'today', 'live', 'real-time', 'realtime', 'right now', 'what is', 'what\'s', 'whats']
                is_current_query = any(keyword in message_lower for keyword in current_keywords) and not any(hist_word in message_lower for hist_word in ['historical', 'past', 'was', 'were', 'yesterday'])
                
                # Use historical range if date_range is detected AND not asking for current
                if date_range and not is_current_query:
                    days = date_range.get('days', 5)
                    stock_data = stock_data_service.get_historical_price_range(symbol, days=days)
                    is_historical = True
                    is_range = True
                # Use historical data if single date is detected AND not asking for current
                elif date and not is_current_query:
                    stock_data = stock_data_service.get_historical_price(symbol, date)
                    is_historical = True
                    is_range = False
                # Otherwise use current quote (default for queries without dates or with current keywords)
                else:
                    stock_data = stock_data_service.get_stock_quote(symbol)
                    is_historical = False
                    is_range = False
                
                # Fetch sentiment data (only for current quotes, not historical)
                sentiment_data = None
                if not is_historical and not is_range and "error" not in stock_data:
                    try:
                        sentiment_data = sentiment_analyzer.get_stock_sentiment(symbol)
                    except Exception as e:
                        logger.warning(f"Error fetching sentiment for {symbol}: {e}")
                        sentiment_data = None
                
                if "error" not in stock_data:
                    if is_historical:
                        # Check if this is a date range or single date
                        if date_range and 'prices' in stock_data:
                            # Historical price range data
                            prices = stock_data.get('prices', [])
                            start_date = stock_data.get('start_date', '')
                            end_date = stock_data.get('end_date', '')
                            trading_days = stock_data.get('trading_days', len(prices))
                            
                            stock_context = f"\n\n{'='*70}\n"
                            stock_context += f"📊 HISTORICAL PRICE RANGE - {symbol} 📊\n"
                            stock_context += f"Date Range: {start_date} to {end_date} ({trading_days} trading days)\n"
                            stock_context += f"{'='*70}\n\n"
                            stock_context += "Date       | Open    | High    | Low     | Close   | Volume\n"
                            stock_context += "-" * 70 + "\n"
                            
                            for price_day in prices:
                                date_str = price_day.get('date', '')
                                open_p = price_day.get('open', 0)
                                high_p = price_day.get('high', 0)
                                low_p = price_day.get('low', 0)
                                close_p = price_day.get('close', 0)
                                vol = price_day.get('volume', 0)
                                stock_context += f"{date_str} | ${open_p:>7.2f} | ${high_p:>7.2f} | ${low_p:>7.2f} | ${close_p:>7.2f} | {vol:>10,}\n"
                            
                            stock_context += f"\n{'='*70}\n"
                            stock_context += f"TREND ANALYSIS:\n"
                            if len(prices) >= 2:
                                first_close = prices[0].get('close', 0)
                                last_close = prices[-1].get('close', 0)
                                change = last_close - first_close
                                change_pct = (change / first_close * 100) if first_close > 0 else 0
                                stock_context += f"- First Close ({prices[0].get('date', '')}): ${first_close:.2f}\n"
                                stock_context += f"- Last Close ({prices[-1].get('date', '')}): ${last_close:.2f}\n"
                                stock_context += f"- Change: ${change:.2f} ({change_pct:+.2f}%)\n"
                            
                            stock_context += f"\n⚠️ CRITICAL: Use ONLY these exact prices from the data above. DO NOT use any other numbers.\n"
                            stock_context += f"Show the trend and pattern clearly to help with trading decisions.\n"
                        else:
                            # Single historical date
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
                            
                            stock_context += f"╔{'═'*50}╗\n"
                            stock_context += f"║  OPENING PRICE FOR {symbol} ON {historical_date}: ${open_price:<28} ║\n"
                            stock_context += f"╚{'═'*50}╝\n\n"
                            stock_context += f"COMPLETE PRICE DATA FOR {symbol} ON {historical_date}:\n"
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
                            stock_context += f"'On {historical_date}, {symbol} opened at ${open_price:.2f} and closed at ${close_price:.2f}'\n"
                            stock_context += f"OR if asked specifically:\n"
                            stock_context += f"- Opening price: 'On {historical_date}, {symbol} opened at ${open_price:.2f}'\n"
                            stock_context += f"- Closing price: 'On {historical_date}, {symbol} closed at ${close_price:.2f}'\n\n"
                            stock_context += f"VERIFICATION CHECKS:\n"
                            stock_context += f"✓ Opening price = ${open_price:.2f}? YES = Correct | NO = Wrong\n"
                            stock_context += f"✓ Closing price = ${close_price:.2f}? YES = Correct | NO = Wrong\n"
                            stock_context += f"✓ Date included? YES = Correct | NO = Wrong\n"
                            stock_context += f"✓ Used provided data only? YES = Correct | NO = Wrong\n"
                            stock_context += f"{'='*70}\n\n"
                            stock_context += f"FINAL REMINDER: The opening price on {historical_date} was ${open_price:.2f} and closing price was ${close_price:.2f}.\n"
                            stock_context += f"If you say anything other than these exact numbers, you are WRONG.\n"
                            stock_context += f"NEVER say you don't have access - the data is RIGHT HERE.\n"
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
                            
                            # Enhanced correlation analysis for short-term trading (hours to days)
                            # Analyze price momentum, volume, sentiment alignment, and options flow data
                            current_price = stock_data.get('current_price', 0)
                            change = stock_data.get('change', 0)
                            change_pct = stock_data.get('change_percent', 0)
                            volume = stock_data.get('volume', 0)
                            
                            # Determine time horizon and signal strength
                            time_horizon = ""
                            signal_strength = ""
                            
                            # Parse options flow data from document context if available
                            options_flow_bearish = False
                            options_flow_bullish = False
                            put_call_ratio = None
                            unusual_put_activity = False
                            unusual_call_activity = False
                            
                            # Check document context for options flow signals
                            if document_context:
                                # re is already imported at the top of the file
                                doc_upper = document_context.upper()
                                
                                # Look for PUT/CALL ratio indicators
                                put_call_match = re.search(r'PUT[:\s/]+CALL[:\s]+(\d+\.?\d*)', doc_upper)
                                if put_call_match:
                                    put_call_ratio = float(put_call_match.group(1))
                                    if put_call_ratio > 1.0:
                                        options_flow_bearish = True
                                    elif put_call_ratio < 0.7:
                                        options_flow_bullish = True
                                
                                # Look for heavy PUT activity indicators
                                put_indicators = [
                                    r'HEAVY PUT', r'LARGE PUT', r'UNUSUAL PUT', r'PUT BUYING', 
                                    r'PUT PREMIUM', r'PUT FLOW', r'PUT ACTIVITY', r'MORE PUTS',
                                    r'PUT[:\s]+(\d+[KMB]?)', r'PUTS[:\s]+(\d+[KMB]?)'
                                ]
                                for pattern in put_indicators:
                                    if re.search(pattern, doc_upper):
                                        options_flow_bearish = True
                                        unusual_put_activity = True
                                        break
                                
                                # Look for heavy CALL activity indicators
                                call_indicators = [
                                    r'HEAVY CALL', r'LARGE CALL', r'UNUSUAL CALL', r'CALL BUYING',
                                    r'CALL PREMIUM', r'CALL FLOW', r'CALL ACTIVITY', r'MORE CALLS',
                                    r'CALL[:\s]+(\d+[KMB]?)', r'CALLS[:\s]+(\d+[KMB]?)'
                                ]
                                for pattern in call_indicators:
                                    if re.search(pattern, doc_upper):
                                        options_flow_bullish = True
                                        unusual_call_activity = True
                                        break
                                
                                # Look for bearish price action in documents
                                bearish_price_indicators = [
                                    r'DROPP?ED', r'DECLINED?', r'FALLING', r'DOWNWARD', r'BEARISH',
                                    r'SELL[ING]?', r'SHORT', r'RESISTANCE', r'BREAKDOWN'
                                ]
                                for pattern in bearish_price_indicators:
                                    if re.search(pattern, doc_upper):
                                        options_flow_bearish = True
                                        break
                            
                            # Analyze correlation patterns
                            # Strong bullish signals (CALLS):
                            # 1. Positive sentiment + price rising + high volume = strong call signal
                            # 2. News bullish + Reddit bullish + price momentum = high confidence call
                            # 3. Options flow shows heavy CALL buying = bullish (prioritize over sentiment)
                            # 4. Divergence: negative price but strong positive sentiment = potential reversal call
                            
                            # Strong bearish signals (PUTS):
                            # 1. Negative sentiment + price falling + high volume = strong put signal
                            # 2. News bearish + Reddit bearish + price momentum down = high confidence put
                            # 3. Options flow shows heavy PUT buying = bearish (prioritize over sentiment) ⚠️ CRITICAL
                            # 4. Divergence: positive price but strong negative sentiment = potential reversal put
                            
                            news_score = news_sentiment.get('sentiment_score', 0) if news_sentiment else 0
                            reddit_score = reddit_sentiment.get('sentiment_score', 0) if reddit_sentiment else 0
                            
                            # Check for alignment (sentiment and price moving together)
                            sentiment_price_aligned = False
                            if (overall_score > 0.2 and change > 0) or (overall_score < -0.2 and change < 0):
                                sentiment_price_aligned = True
                            
                            # Check for divergence (sentiment contradicts price - potential reversal)
                            sentiment_price_divergence = False
                            if (overall_score > 0.3 and change < -1) or (overall_score < -0.3 and change > 1):
                                sentiment_price_divergence = True
                            
                            # CRITICAL: Check for options flow vs sentiment divergence
                            # If options flow is bearish (PUT buying) but sentiment is positive → Favor PUTS
                            options_flow_sentiment_divergence = False
                            if options_flow_bearish and overall_score > 0.1:
                                options_flow_sentiment_divergence = True
                            elif options_flow_bullish and overall_score < -0.1:
                                options_flow_sentiment_divergence = True
                            
                            # Determine recommendation with time horizon
                            # PRIORITY: Options flow data > Price action > Sentiment
                            
                            # CRITICAL: If options flow shows bearish activity (PUT buying), favor PUTS even if sentiment is positive
                            if options_flow_bearish or unusual_put_activity:
                                if put_call_ratio and put_call_ratio > 1.2:
                                    investment_guidance = f"STRONG BEARISH SIGNAL - PUT options recommended (1-3 day timeframe). Options flow shows heavy PUT buying (PUT/CALL ratio: {put_call_ratio:.2f}) despite sentiment. Smart money positioning suggests downside risk."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "1-3 days"
                                    signal_strength = "STRONG"
                                elif change_pct < -1:
                                    investment_guidance = "BEARISH - PUT options recommended (1-2 day timeframe). Options flow shows PUT buying activity + price decline = bearish signal."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "1-2 days"
                                    signal_strength = "MODERATE"
                                else:
                                    investment_guidance = "BEARISH SIGNAL - PUT options (6-24 hour timeframe). Options flow shows PUT buying activity. Monitor price action for entry."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "6-24 hours"
                                    signal_strength = "MODERATE"
                            # If options flow shows bullish activity (CALL buying), favor CALLS even if sentiment is negative
                            elif options_flow_bullish or unusual_call_activity:
                                if put_call_ratio and put_call_ratio < 0.6:
                                    investment_guidance = f"STRONG BULLISH SIGNAL - CALL options recommended (1-3 day timeframe). Options flow shows heavy CALL buying (PUT/CALL ratio: {put_call_ratio:.2f}) despite sentiment. Smart money positioning suggests upside potential."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "1-3 days"
                                    signal_strength = "STRONG"
                                elif change_pct > 1:
                                    investment_guidance = "BULLISH - CALL options recommended (1-2 day timeframe). Options flow shows CALL buying activity + price rise = bullish signal."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "1-2 days"
                                    signal_strength = "MODERATE"
                                else:
                                    investment_guidance = "BULLISH SIGNAL - CALL options (6-24 hour timeframe). Options flow shows CALL buying activity. Monitor price action for entry."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "6-24 hours"
                                    signal_strength = "MODERATE"
                            # Fall back to sentiment-based analysis if no options flow data
                            elif overall_score >= 0.5:
                                if sentiment_price_aligned and change_pct > 2:
                                    investment_guidance = "STRONG BULLISH - CALL options recommended (1-3 day timeframe). Strong sentiment + price momentum + alignment = high confidence entry."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "1-3 days"
                                    signal_strength = "STRONG"
                                elif sentiment_price_divergence:
                                    investment_guidance = "BULLISH DIVERGENCE - CALL options on pullback (4-12 hour timeframe). Strong positive sentiment despite price drop suggests potential reversal."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "4-12 hours"
                                    signal_strength = "MODERATE"
                                else:
                                    investment_guidance = "BULLISH - CALL options (1-2 day timeframe). Strong positive sentiment suggests upward momentum."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "1-2 days"
                                    signal_strength = "MODERATE"
                            elif overall_score >= 0.2:
                                if sentiment_price_aligned and change_pct > 1:
                                    investment_guidance = "BULLISH - CALL options (6-24 hour timeframe). Moderate sentiment + price momentum = favorable entry."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "6-24 hours"
                                    signal_strength = "MODERATE"
                                else:
                                    investment_guidance = "SLIGHTLY BULLISH - Consider CALL options (12-48 hour timeframe). Monitor for stronger signals."
                                    call_put_recommendation = "CALL"
                                    time_horizon = "12-48 hours"
                                    signal_strength = "WEAK"
                            elif overall_score <= -0.5:
                                if sentiment_price_aligned and change_pct < -2:
                                    investment_guidance = "STRONG BEARISH - PUT options recommended (1-3 day timeframe). Strong negative sentiment + price decline + alignment = high confidence entry."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "1-3 days"
                                    signal_strength = "STRONG"
                                elif sentiment_price_divergence:
                                    investment_guidance = "BEARISH DIVERGENCE - PUT options on bounce (4-12 hour timeframe). Strong negative sentiment despite price rise suggests potential reversal."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "4-12 hours"
                                    signal_strength = "MODERATE"
                                else:
                                    investment_guidance = "BEARISH - PUT options (1-2 day timeframe). Strong negative sentiment suggests downward momentum."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "1-2 days"
                                    signal_strength = "MODERATE"
                            elif overall_score <= -0.2:
                                if sentiment_price_aligned and change_pct < -1:
                                    investment_guidance = "BEARISH - PUT options (6-24 hour timeframe). Moderate negative sentiment + price decline = favorable entry."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "6-24 hours"
                                    signal_strength = "MODERATE"
                                else:
                                    investment_guidance = "SLIGHTLY BEARISH - Consider PUT options (12-48 hour timeframe). Monitor for stronger signals."
                                    call_put_recommendation = "PUT"
                                    time_horizon = "12-48 hours"
                                    signal_strength = "WEAK"
                            else:
                                investment_guidance = "NEUTRAL - Wait for clearer signals (no position recommended). Monitor for sentiment/price alignment or options flow data."
                                call_put_recommendation = "NEUTRAL"
                                time_horizon = "N/A"
                                signal_strength = "NONE"
                            
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
                            stock_context += f"💡 SHORT-TERM TRADING GUIDANCE (Hours to Days):\n"
                            stock_context += f"{'─'*70}\n"
                            stock_context += f"Recommendation: {investment_guidance}\n"
                            stock_context += f"Call/Put Side: {call_put_recommendation}\n"
                            if time_horizon:
                                stock_context += f"Time Horizon: {time_horizon}\n"
                            if signal_strength:
                                stock_context += f"Signal Strength: {signal_strength}\n"
                            
                            # Add correlation analysis details
                            if sentiment_price_aligned:
                                stock_context += f"\n✅ ALIGNMENT DETECTED: Sentiment and price moving together - Higher confidence signal\n"
                            if sentiment_price_divergence:
                                stock_context += f"\n⚠️ DIVERGENCE DETECTED: Sentiment contradicts price - Potential reversal signal\n"
                            
                            # Add options flow analysis details
                            if options_flow_bearish or unusual_put_activity:
                                stock_context += f"\n🔴 OPTIONS FLOW BEARISH: Document shows PUT buying activity - This is a BEARISH signal (favor PUTS)\n"
                                if put_call_ratio:
                                    stock_context += f"   PUT/CALL Ratio: {put_call_ratio:.2f} (Ratio > 1.0 = More puts than calls = Bearish)\n"
                                stock_context += f"   ⚠️ CRITICAL: Options flow data suggests PUTS even if sentiment seems positive\n"
                            if options_flow_bullish or unusual_call_activity:
                                stock_context += f"\n🟢 OPTIONS FLOW BULLISH: Document shows CALL buying activity - This is a BULLISH signal (favor CALLS)\n"
                                if put_call_ratio:
                                    stock_context += f"   PUT/CALL Ratio: {put_call_ratio:.2f} (Ratio < 0.7 = More calls than puts = Bullish)\n"
                                stock_context += f"   ⚠️ CRITICAL: Options flow data suggests CALLS even if sentiment seems negative\n"
                            if options_flow_sentiment_divergence:
                                stock_context += f"\n⚠️ OPTIONS FLOW vs SENTIMENT DIVERGENCE: Options flow contradicts sentiment - Prioritize options flow data\n"
                                stock_context += f"   Options flow shows actual trading activity (smart money), which is more reliable than sentiment\n"
                            
                            # Add volume context if available
                            if volume > 0:
                                avg_volume = stock_data.get('average_volume', volume)
                                if volume > avg_volume * 1.5:
                                    stock_context += f"📊 HIGH VOLUME: {volume:,} shares (above average) - Confirms signal strength\n"
                                elif volume < avg_volume * 0.5:
                                    stock_context += f"📊 LOW VOLUME: {volume:,} shares (below average) - Lower confidence, wait for confirmation\n"
                            
                            stock_context += f"\n⚠️  IMPORTANT: This is sentiment analysis only, not financial advice.\n"
                            stock_context += f"Time horizons are estimates based on current data patterns.\n"
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
                            stock_context += f"4. Trading Guidance: {investment_guidance}\n"
                            stock_context += f"5. Call/Put Recommendation: {call_put_recommendation}\n"
                            if time_horizon:
                                stock_context += f"6. Time Horizon: {time_horizon} (short-term trading window)\n"
                            if signal_strength:
                                stock_context += f"7. Signal Strength: {signal_strength}\n"
                            stock_context += f"\n⚠️ CRITICAL: Always state the time horizon when giving trading recommendations.\n"
                            stock_context += f"Example: 'CALL options recommended for 1-2 day timeframe' or 'PUT options for 6-24 hour window'\n"
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
                logger.error(f"Error fetching stock data for {symbol}: {e}", exc_info=True)
                error_msg = str(e)
                # Provide more helpful error messages
                if "Expecting value" in error_msg or "JSON" in error_msg:
                    error_msg = f"Unable to fetch current price data for {symbol}. The market data service may be temporarily unavailable. Please try again in a moment."
                elif "429" in error_msg or "Too Many Requests" in error_msg:
                    error_msg = f"Rate limit exceeded while fetching {symbol} data. Please wait a moment and try again."
                else:
                    error_msg = f"Failed to fetch stock data for {symbol}: {error_msg}"
                
                stock_context = f"\n\n[Error: {error_msg}]\n"
                stock_data = {"error": error_msg}
        
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
        
        # Handle error cases - provide helpful error message
        if symbol and stock_data and "error" in stock_data:
            error_msg = stock_data.get("error", "Unknown error")
            # Return helpful error message instead of generic "no access" message
            return f"I encountered an issue fetching historical data for {symbol}: {error_msg}. Please try a different date or verify the stock symbol is correct."
        
        # If documents contain stock symbols, fetch current prices for comparison
        # Extract symbols from document context if present
        document_symbols = []
        if document_context and "[DETECTED STOCK SYMBOLS IN DOCUMENTS:" in document_context:
            try:
                # re is already imported at the top of the file
                # Extract symbols from the context string
                symbols_match = re.search(r'\[DETECTED STOCK SYMBOLS IN DOCUMENTS: ([^\]]+)\]', document_context)
                if symbols_match:
                    symbols_str = symbols_match.group(1)
                    document_symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]
            except Exception as e:
                logger.warning(f"Could not extract symbols from document context: {e}")
        
        if document_symbols and document_context:
            # stock_data_service is already imported at the top of the file
            current_prices_context = "\n\n[CURRENT MARKET PRICES FOR DOCUMENT SYMBOLS - COMPARE WITH DOCUMENT DATA]\n"
            current_prices_context += "⚠️ CRITICAL: Compare these CURRENT prices with document data and warn if significant changes occurred.\n\n"
            
            for doc_symbol in document_symbols:
                try:
                    current_quote = stock_data_service.get_stock_quote(doc_symbol)
                    if current_quote and "error" not in current_quote:
                        current_price = current_quote.get('current_price', 0)
                        change = current_quote.get('change', 0)
                        change_pct = current_quote.get('change_percent', 0)
                        current_prices_context += f"{doc_symbol} Current Price: ${current_price:.2f} (Change: ${change:+.2f}, {change_pct:+.2f}%)\n"
                        logger.info(f"Fetched current price for {doc_symbol} from document: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not fetch current price for {doc_symbol}: {e}")
                    current_prices_context += f"{doc_symbol}: Unable to fetch current price\n"
            
            current_prices_context += "\n⚠️ IMPORTANT: If document prices differ significantly from current prices, warn the user about outdated data.\n"
            current_prices_context += "Example: 'Note: The document shows TSLA at $XXX, but current price is $YYY (a $ZZ change).'\n"
            document_context += current_prices_context
        
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
                        
                        # Add investment guidance with time horizon
                        change_pct = stock_data.get('change_percent', 0)
                        change = stock_data.get('change', 0)
                        
                        # Check alignment
                        sentiment_price_aligned = (overall_score > 0.2 and change > 0) or (overall_score < -0.2 and change < 0)
                        
                        if overall_score >= 0.5:
                            call_put = "CALL"
                            if sentiment_price_aligned and change_pct > 2:
                                guidance = "STRONG BULLISH - CALL options (1-3 day timeframe). Strong sentiment + price momentum alignment."
                            else:
                                guidance = "STRONG BULLISH - CALL options (1-2 day timeframe). Strong positive sentiment."
                        elif overall_score >= 0.2:
                            call_put = "CALL"
                            if sentiment_price_aligned and change_pct > 1:
                                guidance = "BULLISH - CALL options (6-24 hour timeframe). Moderate sentiment + price momentum."
                            else:
                                guidance = "SLIGHTLY BULLISH - CALL options (12-48 hour timeframe). Monitor for stronger signals."
                        elif overall_score <= -0.5:
                            call_put = "PUT"
                            if sentiment_price_aligned and change_pct < -2:
                                guidance = "STRONG BEARISH - PUT options (1-3 day timeframe). Strong negative sentiment + price decline alignment."
                            else:
                                guidance = "STRONG BEARISH - PUT options (1-2 day timeframe). Strong negative sentiment."
                        elif overall_score <= -0.2:
                            call_put = "PUT"
                            if sentiment_price_aligned and change_pct < -1:
                                guidance = "BEARISH - PUT options (6-24 hour timeframe). Moderate negative sentiment + price decline."
                            else:
                                guidance = "SLIGHTLY BEARISH - PUT options (12-48 hour timeframe). Monitor for stronger signals."
                        else:
                            call_put = "NEUTRAL"
                            guidance = "NEUTRAL - Wait for clearer signals (no position recommended). Monitor for sentiment/price alignment."
                        
                        sentiment_info += f"\n- Trading Guidance: {guidance}\n- Call/Put Recommendation: {call_put}"
                        # Extract and add time horizon if present
                        time_match = re.search(r'\((\d+[-\s]\d+\s*(?:hour|day|hours|days))', guidance)
                        if time_match:
                            sentiment_info += f"\n- Time Horizon: {time_match.group(1)}"
                        
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
    
    def _format_correlation_context(self, correlation_data: Dict, symbols: List[str]) -> str:
        """
        Format correlation analysis data for LLM context.
        
        Args:
            correlation_data: Correlation analysis results
            symbols: List of symbols analyzed
            
        Returns:
            Formatted context string
        """
        if len(symbols) == 1:
            # Single symbol analysis
            symbol = symbols[0]
            price_analysis = correlation_data.get("price_analysis", {})
            current_sentiment = correlation_data.get("current_sentiment", {})
            insights = correlation_data.get("correlation_insights", [])
            recommendations = correlation_data.get("recommendations", [])
            
            context = f"\n\n{'='*70}\n"
            context += f"📊 SENTIMENT-PRICE CORRELATION ANALYSIS - {symbol} 📊\n"
            context += f"{'='*70}\n\n"
            
            # Price analysis
            context += f"PRICE ANALYSIS:\n"
            context += f"- Period: {correlation_data.get('analysis_period', {}).get('start_date', 'N/A')} to {correlation_data.get('analysis_period', {}).get('end_date', 'N/A')}\n"
            context += f"- Trading Days: {correlation_data.get('analysis_period', {}).get('trading_days', 0)}\n"
            context += f"- First Close: ${price_analysis.get('first_close', 0):.2f}\n"
            context += f"- Last Close: ${price_analysis.get('last_close', 0):.2f}\n"
            context += f"- Total Change: ${price_analysis.get('total_change', 0):.2f} ({price_analysis.get('total_change_pct', 0):+.2f}%)\n"
            context += f"- Trend: {price_analysis.get('trend', 'UNKNOWN')}\n"
            context += f"- Volatility: {price_analysis.get('volatility', 0):.2f}%\n"
            context += f"- Positive Days: {price_analysis.get('positive_days', 0)}\n"
            context += f"- Negative Days: {price_analysis.get('negative_days', 0)}\n\n"
            
            # Current sentiment
            context += f"CURRENT SENTIMENT:\n"
            context += f"- Overall Sentiment: {current_sentiment.get('overall_label', 'NEUTRAL')}\n"
            context += f"- Sentiment Score: {current_sentiment.get('overall_score', 0.0):+.3f}\n\n"
            
            # Correlation insights
            if insights:
                context += f"CORRELATION INSIGHTS:\n"
                for insight in insights:
                    context += f"- {insight}\n"
                context += "\n"
            
            # Recommendations
            if recommendations:
                context += f"TRADING RECOMMENDATIONS:\n"
                for rec in recommendations:
                    context += f"- {rec}\n"
                context += "\n"
            
            # Limitations
            limitations = correlation_data.get("limitations", [])
            if limitations:
                context += f"LIMITATIONS:\n"
                for limit in limitations:
                    context += f"- {limit}\n"
            
            context += f"\n{'='*70}\n"
            context += f"⚠️ CRITICAL: Use this analysis to guide trading decisions, but always consider multiple factors.\n"
            context += f"Past correlation does not guarantee future performance.\n"
            context += f"{'='*70}\n"
            
            return context
        else:
            # Multi-symbol comparison
            context = f"\n\n{'='*70}\n"
            context += f"📊 COMPARATIVE SENTIMENT-PRICE ANALYSIS 📊\n"
            context += f"Symbols: {', '.join(symbols)}\n"
            context += f"{'='*70}\n\n"
            
            results = correlation_data.get("results", {})
            comparison = correlation_data.get("comparison", {})
            
            for symbol in symbols:
                if symbol in results and "error" not in results[symbol]:
                    result = results[symbol]
                    price_analysis = result.get("price_analysis", {})
                    current_sentiment = result.get("current_sentiment", {})
                    
                    context += f"{symbol}:\n"
                    context += f"- Trend: {price_analysis.get('trend', 'UNKNOWN')}\n"
                    context += f"- Price Change: {price_analysis.get('total_change_pct', 0):+.2f}%\n"
                    context += f"- Sentiment: {current_sentiment.get('overall_label', 'NEUTRAL')} ({current_sentiment.get('overall_score', 0.0):+.3f})\n"
                    context += f"- Volatility: {price_analysis.get('volatility', 0):.2f}%\n\n"
            
            # Key differences
            key_diffs = comparison.get("key_differences", [])
            if key_diffs:
                context += f"KEY DIFFERENCES:\n"
                for diff in key_diffs:
                    context += f"- {diff}\n"
                context += "\n"
            
            context += f"{'='*70}\n"
            
            return context
    
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
        
        # Check if this is a stock-related query and detect date/range
        result = self._check_for_stock_query(message)
        if len(result) == 4:
            is_stock_query, symbol, date, date_range = result
        else:
            # Backward compatibility - unpack 3-tuple
            is_stock_query, symbol, date = result
            date_range = None
        
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

