"""
Financial news fetcher using RSS feeds.
Free, no API keys required.

Uses Yahoo Finance RSS feed - financial-focused, reliable, and less prone to marketing fluff.
Yahoo Finance provides stock-specific news headlines for TSLA, SPY, and other symbols.
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches financial news from RSS feeds."""
    
    def __init__(self):
        """Initialize the news fetcher."""
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def _parse_rss_feed(self, url: str, max_items: int = 5) -> List[Dict[str, str]]:
        """
        Parse RSS feed and return list of news items.
        
        Args:
            url: RSS feed URL
            max_items: Maximum number of items to return
            
        Returns:
            List of news items with title, link, and pubDate
        """
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Handle both RSS 2.0 and Atom feeds
            items = []
            if root.tag == 'rss':
                items = root.findall('.//item')
            elif root.tag == '{http://www.w3.org/2005/Atom}feed':
                items = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            news_items = []
            for item in items[:max_items]:
                try:
                    if root.tag == 'rss':
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        pub_date_elem = item.find('pubDate')
                    else:  # Atom
                        title_elem = item.find('{http://www.w3.org/2005/Atom}title')
                        link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                        pub_date_elem = item.find('{http://www.w3.org/2005/Atom}published')
                    
                    title = title_elem.text if title_elem is not None and title_elem.text else ""
                    link = link_elem.text if link_elem is not None and link_elem.text else (link_elem.get('href') if link_elem is not None else "")
                    pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else ""
                    
                    if title:
                        news_items.append({
                            'title': title.strip(),
                            'link': link.strip() if link else '',
                            'pubDate': pub_date.strip() if pub_date else ''
                        })
                except Exception as e:
                    logger.warning(f"Error parsing RSS item: {e}")
                    continue
            
            return news_items
        except Exception as e:
            logger.error(f"Error fetching RSS feed {url}: {e}")
            return []
    
    def get_stock_news(self, symbol: str, max_items: int = 5) -> List[str]:
        """
        Get recent news headlines for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., TSLA, AAPL)
            max_items: Maximum number of headlines to return
            
        Returns:
            List of news headline strings
        """
        symbol_upper = symbol.upper()
        
        # Check cache
        cache_key = f"{symbol_upper}_news"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['headlines']
        
        headlines = []
        
        # Fetch from Yahoo Finance RSS (primary source - financial-focused, reliable)
        # Yahoo Finance provides stock-specific financial news and is less prone to marketing fluff
        try:
            yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol_upper}&region=US&lang=en-US"
            yahoo_items = self._parse_rss_feed(yahoo_url, max_items=max_items)
            headlines.extend([item['title'] for item in yahoo_items])
            logger.info(f"Successfully fetched {len(yahoo_items)} headlines from Yahoo Finance for {symbol_upper}")
        except Exception as e:
            logger.warning(f"Error fetching Yahoo Finance news for {symbol_upper}: {e}")
        
        # Remove duplicates and limit
        unique_headlines = []
        seen = set()
        for headline in headlines:
            headline_lower = headline.lower()
            if headline_lower not in seen and len(headline) > 10:  # Filter out very short items
                seen.add(headline_lower)
                unique_headlines.append(headline)
                if len(unique_headlines) >= max_items:
                    break
        
        # Cache the results
        self.cache[cache_key] = {
            'headlines': unique_headlines,
            'timestamp': datetime.now()
        }
        
        return unique_headlines


# Global instance
news_fetcher = NewsFetcher()

