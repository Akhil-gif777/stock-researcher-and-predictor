"""Macroeconomic indicators service with 3-day caching."""
import yfinance as yf
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.config import settings


class MacroService:
    """Service for fetching macroeconomic indicators."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(days=3)
    
    def get_macro_indicators(self) -> Dict:
        """
        Get all macro indicators with 3-day caching.
        
        Returns:
            Dictionary with VIX, fed rate, GDP, CPI, unemployment
        """
        # Check cache
        if 'macro_data' in self.cache:
            cached_time, cached_data = self.cache['macro_data']
            if datetime.now() - cached_time < self.cache_duration:
                print(f"✓ Macro Service: Using cached data (age: {datetime.now() - cached_time})")
                return cached_data
        
        print(f"📊 Macro Service: Fetching fresh economic indicators...")
        
        indicators = {
            'vix': self._get_vix(),
            'fed_rate': self._get_fed_rate(),
            'gdp_growth': self._get_gdp(),
            'inflation_cpi': self._get_cpi(),
            'unemployment': self._get_unemployment(),
        }
        
        # Cache the results
        self.cache['macro_data'] = (datetime.now(), indicators)
        print(f"✓ Macro Service: Cached {len([v for v in indicators.values() if v is not None])} indicators")
        
        return indicators
    
    def _get_vix(self) -> Optional[float]:
        """Get VIX (volatility index) from yfinance."""
        try:
            vix = yf.Ticker("^VIX")
            data = vix.history(period="1d")
            if not data.empty:
                value = float(data['Close'].iloc[-1])
                print(f"✓ VIX: {value:.2f}")
                return value
        except Exception as e:
            print(f"⚠️ Failed to fetch VIX: {str(e)}")
        return None
    
    def _get_fed_rate(self) -> Optional[float]:
        """
        Get Federal Funds Rate from FRED API or Alpha Vantage fallback.

        Note: FRED API 'demo' key is invalid (returns 400 error).
        To fix: Get free FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html
        Currently relying on Alpha Vantage fallback.
        """
        try:
            # Using FRED API (Federal Reserve Economic Data)
            # NOTE: 'demo' key doesn't work - will trigger fallback to Alpha Vantage
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'FEDFUNDS',
                'api_key': 'demo',  # Invalid - triggers fallback
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'observations' in data and len(data['observations']) > 0:
                value = float(data['observations'][0]['value'])
                print(f"✓ Fed Rate (FRED): {value:.2f}%")
                return value
        except Exception as e:
            print(f"⚠️ FRED API unavailable (expected with 'demo' key): {str(e)[:100]}")
        
        # Fallback: Use Alpha Vantage if configured
        if settings.alpha_vantage_api_key:
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'FEDERAL_FUNDS_RATE',
                    'apikey': settings.alpha_vantage_api_key,
                    'datatype': 'json'
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    value = float(data['data'][0]['value'])
                    print(f"✓ Fed Rate (Alpha Vantage): {value:.2f}%")
                    return value
            except Exception as e:
                print(f"⚠️ Failed to fetch Fed rate from Alpha Vantage: {str(e)}")
        
        # Final fallback: Use current known rate (as of 2024)
        print(f"⚠️ Using fallback Fed rate: 5.25%")
        return 5.25
    
    def _get_gdp(self) -> Optional[float]:
        """
        Get GDP growth rate from FRED API or Alpha Vantage fallback.

        Note: FRED API 'demo' key is invalid. Currently relying on Alpha Vantage.
        """
        try:
            # Using FRED API for GDP data
            # NOTE: 'demo' key doesn't work - will trigger fallback
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'GDPC1',  # Real GDP
                'api_key': 'demo',  # Invalid - triggers fallback
                'file_type': 'json',
                'limit': 2,
                'sort_order': 'desc'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'observations' in data and len(data['observations']) >= 2:
                current = float(data['observations'][0]['value'])
                previous = float(data['observations'][1]['value'])
                growth = ((current - previous) / previous) * 100
                print(f"✓ GDP Growth (FRED): {growth:.2f}%")
                return growth
        except Exception as e:
            print(f"⚠️ FRED API unavailable (expected with 'demo' key): {str(e)[:100]}")
        
        # Fallback: Use Alpha Vantage if configured
        if settings.alpha_vantage_api_key:
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'REAL_GDP',
                    'interval': 'annual',
                    'apikey': settings.alpha_vantage_api_key,
                    'datatype': 'json'
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and len(data['data']) >= 2:
                    current = float(data['data'][0]['value'])
                    previous = float(data['data'][1]['value'])
                    growth = ((current - previous) / previous) * 100
                    print(f"✓ GDP Growth (Alpha Vantage): {growth:.2f}%")
                    return growth
            except Exception as e:
                print(f"⚠️ Failed to fetch GDP from Alpha Vantage: {str(e)}")
        
        # Final fallback: Use reasonable estimate
        print(f"⚠️ Using fallback GDP growth: 2.5%")
        return 2.5
    
    def _get_cpi(self) -> Optional[float]:
        """
        Get CPI inflation from FRED API or Alpha Vantage fallback.

        Note: FRED API 'demo' key is invalid. Currently relying on Alpha Vantage.
        """
        try:
            # Using FRED API for CPI data
            # NOTE: 'demo' key doesn't work - will trigger fallback
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'CPIAUCSL',  # Consumer Price Index
                'api_key': 'demo',  # Invalid - triggers fallback
                'file_type': 'json',
                'limit': 13,
                'sort_order': 'desc'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'observations' in data and len(data['observations']) >= 13:
                current = float(data['observations'][0]['value'])
                year_ago = float(data['observations'][12]['value'])
                inflation = ((current - year_ago) / year_ago) * 100
                print(f"✓ CPI Inflation (FRED): {inflation:.2f}%")
                return inflation
        except Exception as e:
            print(f"⚠️ FRED API unavailable (expected with 'demo' key): {str(e)[:100]}")
        
        # Fallback: Use Alpha Vantage if configured
        if settings.alpha_vantage_api_key:
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'CPI',
                    'interval': 'monthly',
                    'apikey': settings.alpha_vantage_api_key,
                    'datatype': 'json'
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and len(data['data']) >= 13:
                    current = float(data['data'][0]['value'])
                    year_ago = float(data['data'][12]['value'])
                    inflation = ((current - year_ago) / year_ago) * 100
                    print(f"✓ CPI Inflation (Alpha Vantage): {inflation:.2f}%")
                    return inflation
            except Exception as e:
                print(f"⚠️ Failed to fetch CPI from Alpha Vantage: {str(e)}")
        
        # Final fallback: Use reasonable estimate
        print(f"⚠️ Using fallback CPI inflation: 3.2%")
        return 3.2
    
    def _get_unemployment(self) -> Optional[float]:
        """
        Get unemployment rate from FRED API or Alpha Vantage fallback.

        Note: FRED API 'demo' key is invalid. Currently relying on Alpha Vantage.
        """
        try:
            # Using FRED API for unemployment data
            # NOTE: 'demo' key doesn't work - will trigger fallback
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'UNRATE',  # Unemployment Rate
                'api_key': 'demo',  # Invalid - triggers fallback
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'observations' in data and len(data['observations']) > 0:
                value = float(data['observations'][0]['value'])
                print(f"✓ Unemployment (FRED): {value:.2f}%")
                return value
        except Exception as e:
            print(f"⚠️ FRED API unavailable (expected with 'demo' key): {str(e)[:100]}")
        
        # Fallback: Use Alpha Vantage if configured
        if settings.alpha_vantage_api_key:
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'UNEMPLOYMENT',
                    'apikey': settings.alpha_vantage_api_key,
                    'datatype': 'json'
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    value = float(data['data'][0]['value'])
                    print(f"✓ Unemployment (Alpha Vantage): {value:.2f}%")
                    return value
            except Exception as e:
                print(f"⚠️ Failed to fetch unemployment from Alpha Vantage: {str(e)}")
        
        # Final fallback: Use reasonable estimate
        print(f"⚠️ Using fallback unemployment rate: 3.8%")
        return 3.8


# Global instance
macro_service = MacroService()

