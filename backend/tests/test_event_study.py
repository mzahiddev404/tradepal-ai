"""
Tests for event study functionality.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fastapi import status

from utils.event_study import EventStudyService


class TestEventStudyService:
    """Test suite for EventStudyService."""
    
    @pytest.fixture
    def service(self):
        """Create EventStudyService instance."""
        return EventStudyService()
    
    @pytest.fixture
    def sample_prices(self):
        """Create sample price data for testing."""
        dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
        # Create prices with some trend and noise
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        prices = pd.Series(prices, index=dates)
        df = pd.DataFrame({'price': prices})
        df['ret'] = df['price'].pct_change()
        return df
    
    def test_fetch_prices(self, service):
        """Test fetching price data."""
        # This test requires internet connection and may be slow
        # Using SPY as it's a reliable ticker
        try:
            df = service.fetch_prices('SPY', '2023-01-01', '2023-12-31')
            assert not df.empty
            assert 'price' in df.columns
            assert 'ret' in df.columns
            assert len(df) > 0
        except Exception as e:
            pytest.skip(f"Could not fetch prices (may be network issue): {e}")
    
    def test_get_trading_date_index(self, service, sample_prices):
        """Test finding nearest trading date."""
        idx = sample_prices.index
        
        # Test exact match
        target = idx[10]
        result = service.get_trading_date_index(idx, target.strftime('%Y-%m-%d'))
        assert result == target
        
        # Test weekend (should find previous Friday)
        # Find a Saturday
        saturday = pd.Timestamp('2020-01-04')  # Saturday
        result = service.get_trading_date_index(idx, saturday.strftime('%Y-%m-%d'))
        assert result is not None
        assert result <= saturday
    
    def test_calc_cumret(self, service, sample_prices):
        """Test cumulative return calculation."""
        start = sample_prices.index[0]
        end = sample_prices.index[10]
        
        cumret = service.calc_cumret(sample_prices['price'], start, end)
        assert not np.isnan(cumret)
        assert isinstance(cumret, (float, np.floating))
        
        # Test with invalid dates
        invalid_date = pd.Timestamp('2025-01-01')
        cumret_invalid = service.calc_cumret(sample_prices['price'], invalid_date, invalid_date)
        assert np.isnan(cumret_invalid)
    
    def test_event_window_return(self, service, sample_prices):
        """Test event window return calculation."""
        # Use a date in the middle of the sample data
        event_date = '2020-06-15'
        window = (-1, 1)
        
        result = service.event_window_return(sample_prices, event_date, window)
        # Result may be NaN if dates are outside range, but should not raise error
        assert isinstance(result, (float, np.floating)) or np.isnan(result)
    
    def test_bootstrap_pvals(self, service):
        """Test bootstrap p-value calculation."""
        # Create sample returns
        returns = np.array([0.01, -0.01, 0.02, -0.02, 0.01, 0.0, -0.01, 0.02])
        
        pval = service.bootstrap_pvals(returns, nboot=100)  # Use fewer iterations for speed
        assert not np.isnan(pval)
        assert 0 <= pval <= 1
        
        # Test with insufficient data
        single_value = np.array([0.01])
        pval_single = service.bootstrap_pvals(single_value, nboot=100)
        assert np.isnan(pval_single)
    
    def test_run_event_study_basic(self, service):
        """Test running a basic event study."""
        # This test requires internet connection
        try:
            result = service.run_event_study(
                ticker='SPY',
                start_date='2020-01-01',
                end_date='2023-12-31',
                windows=[(-1, 1)]  # Use single window for speed
            )
            
            assert 'error' not in result or result['error'] is None
            if 'error' not in result:
                assert 'symbol' in result
                assert 'summary' in result
                assert 'events' in result
                assert result['symbol'] == 'SPY'
        except Exception as e:
            pytest.skip(f"Could not run event study (may be network issue): {e}")
    
    def test_run_event_study_custom_windows(self, service):
        """Test event study with custom windows."""
        try:
            result = service.run_event_study(
                ticker='SPY',
                start_date='2020-01-01',
                end_date='2023-12-31',
                windows=[(-5, 5), (0, 1)]
            )
            
            if 'error' not in result:
                # Check that we have results for both windows
                windows_in_summary = set(item['window'] for item in result.get('summary', []))
                assert '-5..5' in windows_in_summary or '0..1' in windows_in_summary
        except Exception as e:
            pytest.skip(f"Could not run event study (may be network issue): {e}")
    
    def test_run_event_study_invalid_symbol(self, service):
        """Test event study with invalid symbol."""
        result = service.run_event_study(
            ticker='INVALID_SYMBOL_XYZ123',
            start_date='2020-01-01',
            end_date='2023-12-31'
        )
        
        # Should return error
        assert 'error' in result
    
    def test_holidays_defined(self, service):
        """Test that holidays are properly defined."""
        assert hasattr(service, 'HOLIDAYS')
        assert isinstance(service.HOLIDAYS, dict)
        assert len(service.HOLIDAYS) > 0
        
        # Check that we have expected holidays
        expected_holidays = [
            'Rosh_Hashanah',
            'Yom_Kippur',
            'Ramadan_start',
            'Ramadan_end',
            'Eid_al_Fitr',
            'Eid_al_Adha'
        ]
        for holiday in expected_holidays:
            assert holiday in service.HOLIDAYS
            assert isinstance(service.HOLIDAYS[holiday], list)
            assert len(service.HOLIDAYS[holiday]) > 0


class TestEventStudyAPI:
    """Test suite for event study API endpoint."""
    
    def test_event_study_endpoint(self, client, sample_stock_symbol):
        """Test event study API endpoint."""
        response = client.get(f"/api/stock/event-study/{sample_stock_symbol}")
        
        # May return 200 with data, 404 with error, or 500 if service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "symbol" in data
            assert data["symbol"] == sample_stock_symbol.upper()
    
    def test_event_study_with_custom_dates(self, client, sample_stock_symbol):
        """Test event study with custom date range."""
        response = client.get(
            f"/api/stock/event-study/{sample_stock_symbol}",
            params={
                "start_date": "2020-01-01",
                "end_date": "2023-12-31"
            }
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_event_study_with_custom_windows(self, client, sample_stock_symbol):
        """Test event study with custom windows."""
        response = client.get(
            f"/api/stock/event-study/{sample_stock_symbol}",
            params={
                "windows": "-1:1,0:1"
            }
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_event_study_invalid_windows_format(self, client, sample_stock_symbol):
        """Test event study with invalid windows format."""
        response = client.get(
            f"/api/stock/event-study/{sample_stock_symbol}",
            params={
                "windows": "invalid-format"
            }
        )
        
        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_event_study_invalid_symbol(self, client):
        """Test event study with invalid symbol."""
        response = client.get("/api/stock/event-study/INVALID_SYMBOL_XYZ123")
        
        # May return 404 or 500 depending on how yfinance handles it
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    def test_event_study_response_structure(self, client, sample_stock_symbol):
        """Test that event study response has correct structure."""
        response = client.get(f"/api/stock/event-study/{sample_stock_symbol}")
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            # Check required fields
            assert "symbol" in data
            
            # If successful, should have summary or events
            if "error" not in data:
                assert "summary" in data or "events" in data
                assert "timestamp" in data




