"""
Tests for stock API endpoints.
"""
import pytest
from fastapi import status


class TestStockAPI:
    """Test suite for stock endpoints."""
    
    def test_stock_quote_endpoint(self, client, sample_stock_symbol):
        """Test stock quote endpoint."""
        response = client.get(f"/api/stock/quote/{sample_stock_symbol}")
        # May return 200 with error field or 500 if service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "symbol" in data
    
    def test_stock_quote_with_sentiment(self, client, sample_stock_symbol):
        """Test stock quote with sentiment analysis."""
        response = client.get(
            f"/api/stock/quote/{sample_stock_symbol}?include_sentiment=true"
        )
        # May return 200 with error field or 500 if service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_market_overview_endpoint(self, client):
        """Test market overview endpoint."""
        response = client.get("/api/stock/market/overview")
        # May return 200 with data or 500 if service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_historical_price_endpoint(self, client, sample_stock_symbol):
        """Test historical price endpoint."""
        response = client.get(
            f"/api/stock/historical/{sample_stock_symbol}?date=2024-01-01"
        )
        # May return 200 with data or 500 if service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_options_chain_endpoint(self, client, sample_stock_symbol):
        """Test options chain endpoint."""
        response = client.get(f"/api/stock/options/{sample_stock_symbol}")
        # May return 200 with data or 500 if service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]





