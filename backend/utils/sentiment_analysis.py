"""
Market sentiment analysis utilities.

This module provides sentiment analysis for stocks using various public APIs.
Integrates with Alpha Vantage News Sentiment and Reddit WallStreetBets sentiment.
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import re
from core.config import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze market sentiment for stocks using public APIs."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradePal-AI/1.0'
        })
        self.alpha_vantage_api_key = settings.alpha_vantage_api_key
        self.use_alpha_vantage = self.alpha_vantage_api_key is not None and len(self.alpha_vantage_api_key) > 0
        
        # Bullish and bearish keywords for Reddit sentiment
        self.bullish_keywords = ['moon', 'rocket', 'bull', 'buy', 'long', 'hold', 'diamond', 'hands', 'tendies', 
                                 'gains', 'profit', 'pump', 'rally', 'surge', 'soar', 'breakout', 'yolo', 'to the moon']
        self.bearish_keywords = ['crash', 'dump', 'bear', 'sell', 'short', 'drop', 'fall', 'plunge', 'tank', 
                                'red', 'loss', 'bag', 'holder', 'rekt', 'crash', 'correction', 'bubble']
    
    def get_stock_sentiment(self, symbol: str) -> Dict:
        """
        Get comprehensive sentiment analysis for a stock symbol.
        Combines Alpha Vantage news sentiment and Reddit WallStreetBets sentiment.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with combined sentiment data
        """
        try:
            est_tz = ZoneInfo("America/New_York")
            timestamp = datetime.now(est_tz).isoformat()
            
            sentiment_data = {
                "symbol": symbol,
                "timestamp": timestamp,
                "overall_sentiment": "NEUTRAL",
                "overall_score": 0.0,
                "news_sentiment": None,
                "reddit_sentiment": None,
                "sources": []
            }
            
            # Get Alpha Vantage news sentiment
            news_sentiment = self._get_alpha_vantage_sentiment(symbol)
            if news_sentiment:
                sentiment_data["news_sentiment"] = news_sentiment
                sentiment_data["sources"].append("Alpha Vantage News")
            
            # Get Reddit sentiment
            reddit_sentiment = self._get_reddit_sentiment(symbol)
            if reddit_sentiment:
                sentiment_data["reddit_sentiment"] = reddit_sentiment
                sentiment_data["sources"].append("Reddit r/wallstreetbets")
            
            # Combine sentiments (weight Alpha Vantage more heavily)
            if news_sentiment and reddit_sentiment:
                # Weight: 70% news, 30% Reddit
                news_weight = 0.7
                reddit_weight = 0.3
                
                combined_score = (news_sentiment["sentiment_score"] * news_weight + 
                                reddit_sentiment["sentiment_score"] * reddit_weight)
                
                if combined_score >= 0.2:
                    overall_label = "BULLISH"
                elif combined_score <= -0.2:
                    overall_label = "BEARISH"
                else:
                    overall_label = "NEUTRAL"
                
                sentiment_data["overall_sentiment"] = overall_label
                sentiment_data["overall_score"] = round(combined_score, 3)
                
            elif news_sentiment:
                # Only news sentiment available
                sentiment_data["overall_sentiment"] = news_sentiment["sentiment_label"]
                sentiment_data["overall_score"] = news_sentiment["sentiment_score"]
                
            elif reddit_sentiment:
                # Only Reddit sentiment available
                sentiment_data["overall_sentiment"] = reddit_sentiment["sentiment_label"]
                sentiment_data["overall_score"] = reddit_sentiment["sentiment_score"]
            
            # Legacy fields for compatibility
            sentiment_data["sentiment_score"] = sentiment_data["overall_score"]
            sentiment_data["sentiment_label"] = sentiment_data["overall_sentiment"]
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "sentiment_label": "UNKNOWN",
                "overall_sentiment": "UNKNOWN"
            }
    
    def _get_alpha_vantage_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Fetch news sentiment from Alpha Vantage News & Sentiment API.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with sentiment data or None if failed
        """
        if not self.use_alpha_vantage:
            return None
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": self.alpha_vantage_api_key,
                "limit": 50  # Get up to 50 articles
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.warning(f"Alpha Vantage sentiment error: {data['Error Message']}")
                return None
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            feed = data.get("feed", [])
            if not feed:
                return None
            
            # Calculate overall sentiment
            total_sentiment = 0.0
            total_relevance = 0.0
            article_count = 0
            
            for article in feed:
                ticker_sentiments = article.get("ticker_sentiment", [])
                for ticker_sent in ticker_sentiments:
                    if ticker_sent.get("ticker") == symbol:
                        relevance_score = float(ticker_sent.get("relevance_score", 0))
                        sentiment_score = float(ticker_sent.get("ticker_sentiment_score", 0))
                        
                        if relevance_score > 0.5:  # Only count relevant articles
                            total_sentiment += sentiment_score * relevance_score
                            total_relevance += relevance_score
                            article_count += 1
                        break
            
            if article_count == 0:
                return None
            
            # Calculate weighted average sentiment
            avg_sentiment = total_sentiment / total_relevance if total_relevance > 0 else 0.0
            
            # Convert to label (-1 to 1 scale)
            if avg_sentiment >= 0.35:
                label = "BULLISH"
            elif avg_sentiment <= -0.35:
                label = "BEARISH"
            else:
                label = "NEUTRAL"
            
            return {
                "sentiment_score": round(avg_sentiment, 3),
                "sentiment_label": label,
                "confidence": min(total_relevance / article_count, 1.0) if article_count > 0 else 0.0,
                "news_count": article_count,
                "source": "Alpha Vantage News"
            }
        except Exception as e:
            logger.warning(f"Alpha Vantage sentiment API error for {symbol}: {e}")
            return None
    
    def _get_reddit_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Fetch sentiment from Reddit WallStreetBets.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with Reddit sentiment data or None if failed
        """
        try:
            # Reddit API endpoint (no auth required for read-only)
            url = f"https://www.reddit.com/r/wallstreetbets/search.json"
            params = {
                "q": symbol,
                "limit": 25,
                "sort": "relevance",
                "t": "week"  # Last week
            }
            
            headers = {
                'User-Agent': 'TradePal-AI/1.0 (by /u/tradepal-ai)'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            posts = data.get("data", {}).get("children", [])
            if not posts:
                return None
            
            bullish_count = 0
            bearish_count = 0
            total_mentions = 0
            
            for post in posts:
                post_data = post.get("data", {})
                title = post_data.get("title", "").lower()
                selftext = post_data.get("selftext", "").lower()
                combined_text = f"{title} {selftext}"
                
                # Count bullish/bearish keywords
                bullish_matches = sum(1 for keyword in self.bullish_keywords if keyword in combined_text)
                bearish_matches = sum(1 for keyword in self.bearish_keywords if keyword in combined_text)
                
                if bullish_matches > bearish_matches:
                    bullish_count += 1
                elif bearish_matches > bullish_matches:
                    bearish_count += 1
                
                total_mentions += 1
            
            if total_mentions == 0:
                return None
            
            # Calculate sentiment score (-1 to 1)
            sentiment_score = (bullish_count - bearish_count) / total_mentions if total_mentions > 0 else 0.0
            
            # Determine label
            if sentiment_score >= 0.2:
                label = "BULLISH"
            elif sentiment_score <= -0.2:
                label = "BEARISH"
            else:
                label = "NEUTRAL"
            
            return {
                "sentiment_score": round(sentiment_score, 3),
                "sentiment_label": label,
                "mentions": total_mentions,
                "bullish_posts": bullish_count,
                "bearish_posts": bearish_count,
                "source": "Reddit r/wallstreetbets"
            }
        except Exception as e:
            logger.warning(f"Reddit sentiment API error for {symbol}: {e}")
            return None
    
    def _get_news_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Fetch news sentiment from Alpha Vantage.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with news sentiment data
        """
        return self._get_alpha_vantage_sentiment(symbol)
    
    def analyze_market_mood(self) -> Dict:
        """
        Get overall market sentiment/mood.
        
        Returns:
            Dictionary with market sentiment indicators
        """
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "market_mood": "NEUTRAL",
                "fear_greed_index": None,
                "volatility_index": None,
                "trending_positive": [],
                "trending_negative": []
            }
        except Exception as e:
            logger.error(f"Error analyzing market mood: {e}")
            return {"error": str(e)}


# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer()


# Free Public APIs that can be integrated:
# 
# 1. NewsAPI (https://newsapi.org/) - Financial news
#    - Free tier: 100 requests/day
#    - Good for company-specific news
#
# 2. Alpha Vantage News Sentiment (https://www.alphavantage.co/)
#    - Free tier: 25 requests/day
#    - Provides sentiment scores for stocks
#
# 3. Reddit API (https://www.reddit.com/dev/api/)
#    - Free access
#    - Can scrape r/wallstreetbets for retail sentiment
#
# 4. Fear & Greed Index (https://alternative.me/crypto/fear-and-greed-index/)
#    - Free API
#    - Overall market sentiment indicator
#
# 5. Finnhub (https://finnhub.io/)
#    - Free tier: 60 calls/minute
#    - Company news and sentiment

