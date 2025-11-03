"""
Finnhub API Service for news sentiment and market data.

This service provides access to Finnhub's pre-computed sentiment scores,
buzz metrics, and social sentiment data.
"""

import requests
from typing import Dict, Optional
from app.config import settings


class FinnhubService:
    """Service for interacting with Finnhub API."""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        """Initialize Finnhub service."""
        self.api_key = settings.finnhub_api_key
        self.session = requests.Session()

    def get_news_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Fetch pre-computed news sentiment for a stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dictionary containing:
                - companyNewsScore: Overall news sentiment (0-1)
                - sentiment: {bullishPercent, bearishPercent}
                - buzz: {articlesInLastWeek, buzz, weeklyAverage}
                - sectorAverageNewsScore: Sector comparison
                - sectorAverageBullishPercent: Sector bullish %

        Example response:
        {
            "symbol": "AAPL",
            "companyNewsScore": 0.4489,
            "sentiment": {
                "bearishPercent": 0.28,
                "bullishPercent": 0.72
            },
            "buzz": {
                "articlesInLastWeek": 48,
                "buzz": 0.6075,
                "weeklyAverage": 79
            },
            "sectorAverageNewsScore": 0.5035,
            "sectorAverageBullishPercent": 0.6138
        }
        """
        if not self.api_key:
            print("⚠️ Finnhub API key not configured, skipping sentiment fetch")
            return None

        try:
            url = f"{self.BASE_URL}/news-sentiment"
            params = {
                "symbol": symbol.upper(),
                "token": self.api_key
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Validate response has expected fields
            if "buzz" not in data or "sentiment" not in data:
                print(f"⚠️ Finnhub returned incomplete data for {symbol}")
                return None

            print(f"✅ Finnhub sentiment fetched for {symbol}: "
                  f"Score={data.get('companyNewsScore', 0):.2f}, "
                  f"Buzz={data.get('buzz', {}).get('buzz', 0):.2f}")

            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"⚠️ Finnhub rate limit exceeded for {symbol}")
            elif e.response.status_code == 404:
                print(f"⚠️ Symbol {symbol} not found in Finnhub")
            else:
                print(f"⚠️ Finnhub HTTP error for {symbol}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Finnhub request failed for {symbol}: {str(e)}")
            return None

        except Exception as e:
            print(f"❌ Unexpected error fetching Finnhub sentiment for {symbol}: {str(e)}")
            return None

    def get_company_news(self, symbol: str, from_date: str, to_date: str, limit: int = 50) -> Optional[list]:
        """
        Fetch company-specific news from Finnhub.

        Args:
            symbol: Stock ticker
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Maximum number of articles (default 50)

        Returns:
            List of news articles with headline, summary, source, url
        """
        if not self.api_key:
            return None

        try:
            url = f"{self.BASE_URL}/company-news"
            params = {
                "symbol": symbol.upper(),
                "from": from_date,
                "to": to_date,
                "token": self.api_key
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            articles = response.json()
            return articles[:limit] if articles else []

        except Exception as e:
            print(f"⚠️ Error fetching Finnhub company news: {str(e)}")
            return None


# Singleton instance
finnhub_service = FinnhubService()
