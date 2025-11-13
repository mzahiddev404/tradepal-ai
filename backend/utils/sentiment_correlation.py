"""
Sentiment-Price Correlation Analysis.

Analyzes historical correlation between sentiment scores and stock price movements
to determine if sentiment is a reliable predictor for trading decisions.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.stock_data import stock_data_service
from utils.sentiment_analysis import sentiment_analyzer
import statistics

logger = logging.getLogger(__name__)


class SentimentCorrelationAnalyzer:
    """Analyzes correlation between sentiment and stock price movements."""
    
    def __init__(self):
        """Initialize the correlation analyzer."""
        self.stock_service = stock_data_service
        self.sentiment_service = sentiment_analyzer
    
    def analyze_correlation(
        self,
        symbol: str,
        days: int = 30,
        lookback_days: Optional[int] = None
    ) -> Dict:
        """
        Analyze correlation between sentiment and price movements.
        
        Args:
            symbol: Stock symbol (TSLA or SPY)
            days: Number of days to analyze (default: 30)
            lookback_days: Days to look back for historical analysis (default: days)
            
        Returns:
            Dictionary with correlation analysis results
        """
        try:
            if lookback_days is None:
                lookback_days = days
            
            est_tz = ZoneInfo("America/New_York")
            today = datetime.now(est_tz).date()
            start_date = today - timedelta(days=lookback_days)
            
            # Get historical price data
            price_data = self.stock_service.get_historical_price_range(
                symbol=symbol,
                days=lookback_days
            )
            
            if "error" in price_data:
                return {
                    "symbol": symbol,
                    "error": f"Could not fetch price data: {price_data['error']}"
                }
            
            prices = price_data.get("prices", [])
            if not prices or len(prices) < 5:
                return {
                    "symbol": symbol,
                    "error": f"Insufficient price data for {symbol}. Need at least 5 trading days."
                }
            
            # Analyze price movements
            price_changes = []
            price_change_pcts = []
            dates = []
            
            for i in range(1, len(prices)):
                prev_close = prices[i-1]["close"]
                curr_close = prices[i]["close"]
                change = curr_close - prev_close
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                
                price_changes.append(change)
                price_change_pcts.append(change_pct)
                dates.append(prices[i]["date"])
            
            # For each date, try to get sentiment (note: historical sentiment may be limited)
            # We'll use current sentiment as a proxy and note the limitation
            sentiment_scores = []
            sentiment_labels = []
            
            # Get current sentiment as baseline
            try:
                current_sentiment = self.sentiment_service.get_stock_sentiment(symbol)
                baseline_score = current_sentiment.get("overall_score", 0.0)
                baseline_label = current_sentiment.get("overall_sentiment", "NEUTRAL")
            except Exception as e:
                logger.warning(f"Could not fetch sentiment for {symbol}: {e}")
                baseline_score = 0.0
                baseline_label = "NEUTRAL"
            
            # Calculate correlation metrics
            # Since we don't have historical sentiment data, we'll provide framework
            # for future analysis when historical sentiment becomes available
            
            # Price volatility analysis
            if len(price_change_pcts) > 1:
                price_volatility = statistics.stdev(price_change_pcts) if len(price_change_pcts) > 1 else 0
                avg_price_change = statistics.mean(price_change_pcts)
            else:
                price_volatility = 0
                avg_price_change = 0
            
            # Price trend analysis
            first_price = prices[0]["close"]
            last_price = prices[-1]["close"]
            total_change = last_price - first_price
            total_change_pct = (total_change / first_price * 100) if first_price > 0 else 0
            
            # Determine trend direction
            if total_change_pct > 2:
                trend = "BULLISH"
            elif total_change_pct < -2:
                trend = "BEARISH"
            else:
                trend = "NEUTRAL"
            
            # Calculate days with positive vs negative moves
            positive_days = sum(1 for pct in price_change_pcts if pct > 0)
            negative_days = sum(1 for pct in price_change_pcts if pct < 0)
            neutral_days = len(price_change_pcts) - positive_days - negative_days
            
            return {
                "symbol": symbol,
                "name": price_data.get("name", symbol),
                "analysis_period": {
                    "start_date": prices[0]["date"],
                    "end_date": prices[-1]["date"],
                    "trading_days": len(prices)
                },
                "price_analysis": {
                    "first_close": round(first_price, 2),
                    "last_close": round(last_price, 2),
                    "total_change": round(total_change, 2),
                    "total_change_pct": round(total_change_pct, 2),
                    "trend": trend,
                    "average_daily_change": round(avg_price_change, 2),
                    "volatility": round(price_volatility, 2),
                    "positive_days": positive_days,
                    "negative_days": negative_days,
                    "neutral_days": neutral_days
                },
                "current_sentiment": {
                    "overall_score": baseline_score,
                    "overall_label": baseline_label,
                    "note": "Current sentiment (historical sentiment analysis requires additional data sources)"
                },
                "correlation_insights": self._generate_insights(
                    trend, baseline_score, baseline_label, 
                    price_change_pcts, total_change_pct
                ),
                "recommendations": self._generate_recommendations(
                    trend, baseline_score, price_volatility, total_change_pct
                ),
                "limitations": [
                    "Historical sentiment data is limited - using current sentiment as reference",
                    "Correlation analysis would benefit from historical sentiment time series",
                    "Price movements are influenced by many factors beyond sentiment",
                    "Past correlation does not guarantee future performance"
                ],
                "timestamp": datetime.now(est_tz).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": f"Failed to analyze correlation: {str(e)}"
            }
    
    def _generate_insights(
        self,
        trend: str,
        sentiment_score: float,
        sentiment_label: str,
        price_changes: List[float],
        total_change_pct: float
    ) -> List[str]:
        """Generate insights about sentiment-price correlation."""
        insights = []
        
        # Check if sentiment aligns with price trend
        if trend == "BULLISH" and sentiment_score > 0.2:
            insights.append("✅ Sentiment aligns with bullish price trend - positive correlation observed")
        elif trend == "BEARISH" and sentiment_score < -0.2:
            insights.append("✅ Sentiment aligns with bearish price trend - negative correlation observed")
        elif trend == "BULLISH" and sentiment_score < -0.2:
            insights.append("⚠️ Sentiment contradicts bullish price trend - possible divergence")
        elif trend == "BEARISH" and sentiment_score > 0.2:
            insights.append("⚠️ Sentiment contradicts bearish price trend - possible divergence")
        else:
            insights.append("➡️ Sentiment and price trend are neutral/uncorrelated")
        
        # Volatility analysis
        if len(price_changes) > 1:
            volatility = statistics.stdev(price_changes)
            if volatility > 3.0:
                insights.append("📊 High price volatility observed - sentiment may have stronger impact during volatile periods")
            elif volatility < 1.0:
                insights.append("📊 Low price volatility - sentiment impact may be minimal during stable periods")
        
        # Magnitude analysis
        if abs(total_change_pct) > 5:
            insights.append(f"💹 Significant price movement ({total_change_pct:+.2f}%) - sentiment correlation worth monitoring")
        
        return insights
    
    def _generate_recommendations(
        self,
        trend: str,
        sentiment_score: float,
        volatility: float,
        total_change_pct: float
    ) -> List[str]:
        """Generate trading recommendations based on analysis."""
        recommendations = []
        
        # Sentiment-based recommendations
        if sentiment_score > 0.5:
            recommendations.append("📈 Strong bullish sentiment - Consider CALL options or LONG positions")
        elif sentiment_score > 0.2:
            recommendations.append("📈 Moderate bullish sentiment - Favorable for LONG positions")
        elif sentiment_score < -0.5:
            recommendations.append("📉 Strong bearish sentiment - Consider PUT options or SHORT positions")
        elif sentiment_score < -0.2:
            recommendations.append("📉 Moderate bearish sentiment - Favorable for SHORT positions")
        else:
            recommendations.append("➡️ Neutral sentiment - Wait for clearer signals")
        
        # Trend-based recommendations
        if trend == "BULLISH" and sentiment_score > 0.2:
            recommendations.append("✅ Price trend and sentiment align - Higher confidence in bullish position")
        elif trend == "BEARISH" and sentiment_score < -0.2:
            recommendations.append("✅ Price trend and sentiment align - Higher confidence in bearish position")
        elif trend == "BULLISH" and sentiment_score < -0.2:
            recommendations.append("⚠️ Divergence detected - Sentiment contradicts price trend, exercise caution")
        elif trend == "BEARISH" and sentiment_score > 0.2:
            recommendations.append("⚠️ Divergence detected - Sentiment contradicts price trend, exercise caution")
        
        # Volatility considerations
        if volatility > 3.0:
            recommendations.append("⚡ High volatility - Use appropriate position sizing and risk management")
        
        recommendations.append("⚠️ Always conduct your own research and consider multiple factors before trading")
        
        return recommendations
    
    def compare_symbols(
        self,
        symbols: List[str],
        days: int = 30
    ) -> Dict:
        """
        Compare sentiment-price correlation across multiple symbols.
        
        Args:
            symbols: List of stock symbols (e.g., ['TSLA', 'SPY'])
            days: Number of days to analyze
            
        Returns:
            Dictionary with comparative analysis
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.analyze_correlation(symbol, days=days)
        
        return {
            "symbols": symbols,
            "analysis_period_days": days,
            "results": results,
            "comparison": self._compare_results(results),
            "timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat()
        }
    
    def _compare_results(self, results: Dict) -> Dict:
        """Compare results across symbols."""
        comparison = {
            "trends": {},
            "sentiment_scores": {},
            "volatility": {},
            "key_differences": []
        }
        
        for symbol, result in results.items():
            if "error" not in result:
                comparison["trends"][symbol] = result.get("price_analysis", {}).get("trend", "UNKNOWN")
                comparison["sentiment_scores"][symbol] = result.get("current_sentiment", {}).get("overall_score", 0.0)
                comparison["volatility"][symbol] = result.get("price_analysis", {}).get("volatility", 0.0)
        
        # Find key differences
        if len(comparison["trends"]) >= 2:
            trends = list(comparison["trends"].values())
            if len(set(trends)) > 1:
                comparison["key_differences"].append("Different price trends observed across symbols")
            
            scores = list(comparison["sentiment_scores"].values())
            if max(scores) - min(scores) > 0.5:
                comparison["key_differences"].append("Significant sentiment score differences between symbols")
        
        return comparison


# Global analyzer instance
sentiment_correlation_analyzer = SentimentCorrelationAnalyzer()

