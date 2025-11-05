"""Test Finnhub integration."""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.finnhub_service import finnhub_service

def test_finnhub_sentiment():
    """Test Finnhub news sentiment for AAPL."""
    print("Testing Finnhub News Sentiment API...")
    print("=" * 50)

    symbol = "AAPL"
    print(f"\nFetching sentiment for {symbol}...")

    data = finnhub_service.get_news_sentiment(symbol)

    if data:
        print(f"\n✅ Finnhub API call successful!")
        print(f"\nCompany News Score: {data.get('companyNewsScore', 'N/A')}")

        sentiment = data.get('sentiment', {})
        print(f"Bullish Percent: {sentiment.get('bullishPercent', 'N/A'):.2%}")
        print(f"Bearish Percent: {sentiment.get('bearishPercent', 'N/A'):.2%}")

        buzz = data.get('buzz', {})
        print(f"\nBuzz Score: {buzz.get('buzz', 'N/A')}")
        print(f"Articles in Last Week: {buzz.get('articlesInLastWeek', 'N/A')}")
        print(f"Weekly Average: {buzz.get('weeklyAverage', 'N/A')}")

        print(f"\nSector Average Score: {data.get('sectorAverageNewsScore', 'N/A')}")
        print(f"Sector Average Bullish: {data.get('sectorAverageBullishPercent', 'N/A'):.2%}")

        return True
    else:
        print("❌ Finnhub API call failed")
        return False

if __name__ == "__main__":
    success = test_finnhub_sentiment()
    sys.exit(0 if success else 1)
