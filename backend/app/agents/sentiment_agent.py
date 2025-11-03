"""Sentiment analysis agent for news and market sentiment."""
import asyncio
import aiohttp
from typing import Dict, List
from app.agents.state import AgentState
from app.services.news_service import news_service
from app.services.llm_service import get_llm_service
from app.services.finnhub_service import finnhub_service


def sentiment_agent(state: AgentState) -> Dict:
    """
    Sentiment agent that analyzes recent news and extracts market sentiment.
    Combines Finnhub pre-computed scores with LLM-based analysis.
    """
    symbol = state["symbol"]

    try:
        print(f"📰 Sentiment Agent: Starting analysis for {symbol}")

        # Fetch Finnhub pre-computed sentiment (fast, no LLM needed)
        print(f"📊 Sentiment Agent: Fetching Finnhub pre-computed sentiment...")
        finnhub_data = finnhub_service.get_news_sentiment(symbol)

        # Get company-specific news
        print(f"🔍 Sentiment Agent: Fetching company-specific news...")
        company_articles = news_service.get_recent_news(symbol, max_articles=10)
        print(f"✓ Sentiment Agent: Found {len(company_articles)} company-specific articles")
        
        # Get broader market news
        print(f"🔍 Sentiment Agent: Fetching market news...")
        market_articles = news_service.get_market_news(max_articles=5)
        print(f"✓ Sentiment Agent: Found {len(market_articles)} market articles")
        
        # Combine all articles
        all_articles = company_articles + market_articles
        
    except Exception as e:
        print(f"❌ Sentiment Agent ERROR: Failed to fetch news - {str(e)}")
        raise
    
    if not all_articles:
        return {
            "news_summary": "No recent news found for analysis.",
            "sentiment_score": 0.0,
            "sentiment_aspects": {},
            "sentiment_trend": "stable",
            "sentiment_confidence": 0.0,
            "news_sources": [],
        }

    # Build context for LLM with credibility weighting and timestamps
    news_context = "=== COMPANY-SPECIFIC NEWS (7-day lookback) ===\n"
    if company_articles:
        news_context += "\n".join([
            f"{i+1}. [{article.get('credibility_tier', 3)}★] {article['title']}\n"
            f"   Publisher: {article['publisher']} (Credibility Weight: {article.get('credibility_weight', 0.5):.0%})\n"
            f"   Date: {article['timestamp'][:10]}\n"
            f"   Snippet: {article.get('snippet', '')[:150]}..."
            for i, article in enumerate(company_articles[:8])
        ])
    else:
        news_context += "No recent company-specific news found.\n"

    news_context += "\n\n=== MARKET NEWS (7-day lookback) ===\n"
    if market_articles:
        news_context += "\n".join([
            f"{i+1}. [{article.get('credibility_tier', 3)}★] {article['title']}\n"
            f"   Publisher: {article['publisher']} (Weight: {article.get('credibility_weight', 0.5):.0%})\n"
            f"   Date: {article['timestamp'][:10]}\n"
            f"   Snippet: {article.get('snippet', '')[:150]}..."
            for i, article in enumerate(market_articles[:5])
        ])
    else:
        news_context += "No recent market news found.\n"

    # Use LLM to analyze sentiment
    try:
        print(f"🤖 Sentiment Agent: Calling LLM for sentiment analysis...")
        llm = get_llm_service()

        system_prompt = f"""You are an expert market sentiment analyst with 7 days of news history. Analyze the articles and provide:

## ASPECT-BASED SENTIMENT ANALYSIS

For each aspect, provide a score from -1.0 (very negative) to +1.0 (very positive):

1. **Earnings & Financial Performance**: Revenue, profit, earnings beats/misses
2. **Guidance & Outlook**: Forward guidance, management commentary, future expectations
3. **Products & Innovation**: Product launches, R&D, competitive positioning
4. **Management & Leadership**: Executive changes, strategic decisions
5. **Market & Competition**: Industry trends, competitive threats, market share

## CREDIBILITY-WEIGHTED ANALYSIS

Weight your analysis by source credibility:
- Tier 1 sources (1★) like Bloomberg, Reuters, WSJ: 100% weight
- Tier 2 sources (2★) like CNBC, MarketWatch: 75% weight
- Tier 3 sources (3★) other sources: 50% weight

## TEMPORAL TREND ANALYSIS

Based on the 7-day timeline:
- **Sentiment Trend**: Is sentiment improving, declining, or stable?
- **Key Events**: What specific events drove sentiment changes?
- **Momentum**: Is there accelerating positive/negative momentum?

## OVERALL ASSESSMENT

Combine all factors to determine overall sentiment for {symbol}.

## OUTPUT FORMAT

Provide your analysis, then on separate lines at the end:
EARNINGS_SENTIMENT: [number]
GUIDANCE_SENTIMENT: [number]
PRODUCTS_SENTIMENT: [number]
MANAGEMENT_SENTIMENT: [number]
MARKET_SENTIMENT: [number]
TREND: [improving/declining/stable]
CONFIDENCE: [0.0-1.0]
OVERALL_SENTIMENT: [number]"""

        user_message = f"Analyze sentiment for {symbol} based on these news articles:\n\n{news_context}"

        analysis = llm.invoke(system_prompt, user_message)

        # Extract all sentiment metrics
        sentiment_data = extract_enhanced_sentiment(analysis)
        print(f"✓ Sentiment Agent: Analysis completed - Overall: {sentiment_data['overall']:.2f}, Trend: {sentiment_data['trend']}, Confidence: {sentiment_data['confidence']:.2f}")
        print(f"✅ Sentiment Agent: Analysis complete for {symbol}")

        # Remove score lines from analysis
        clean_analysis = analysis.split("EARNINGS_SENTIMENT:")[0].strip()

        # Extract Finnhub metrics
        finnhub_sentiment_score = None
        finnhub_bullish_percent = None
        finnhub_bearish_percent = None
        finnhub_buzz = None
        finnhub_articles_count = None

        if finnhub_data:
            finnhub_sentiment_score = finnhub_data.get('companyNewsScore')
            sentiment_breakdown = finnhub_data.get('sentiment', {})
            finnhub_bullish_percent = sentiment_breakdown.get('bullishPercent')
            finnhub_bearish_percent = sentiment_breakdown.get('bearishPercent')
            buzz_data = finnhub_data.get('buzz', {})
            finnhub_buzz = buzz_data.get('buzz')
            finnhub_articles_count = buzz_data.get('articlesInLastWeek')

        return {
            "news_summary": clean_analysis,
            "sentiment_score": sentiment_data['overall'],
            "sentiment_aspects": sentiment_data['aspects'],
            "sentiment_trend": sentiment_data['trend'],
            "sentiment_confidence": sentiment_data['confidence'],
            "news_sources": all_articles[:10],  # Top 10 articles
            # Finnhub pre-computed data
            "finnhub_sentiment_score": finnhub_sentiment_score,
            "finnhub_bullish_percent": finnhub_bullish_percent,
            "finnhub_bearish_percent": finnhub_bearish_percent,
            "finnhub_buzz": finnhub_buzz,
            "finnhub_articles_count": finnhub_articles_count,
        }
    except Exception as e:
        print(f"❌ Sentiment Agent ERROR: LLM call failed - {str(e)}")
        raise


def extract_sentiment_score(text: str) -> float:
    """Extract sentiment score from LLM response (legacy function)."""
    try:
        if "SENTIMENT_SCORE:" in text:
            score_text = text.split("SENTIMENT_SCORE:")[-1].strip()
            # Extract first number found
            import re
            match = re.search(r'-?[01]\.?\d*', score_text)
            if match:
                score = float(match.group())
                # Clamp between -1 and 1
                return max(-1.0, min(1.0, score))
    except:
        pass

    # Default to neutral if extraction fails
    return 0.0


def extract_enhanced_sentiment(text: str) -> Dict:
    """Extract all sentiment metrics from enhanced LLM response."""
    import re

    def extract_score(pattern: str, default: float = 0.0) -> float:
        try:
            match = re.search(pattern + r':\s*(-?[01]\.?\d*)', text)
            if match:
                score = float(match.group(1))
                return max(-1.0, min(1.0, score))
        except:
            pass
        return default

    def extract_trend() -> str:
        try:
            match = re.search(r'TREND:\s*(improving|declining|stable)', text, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        except:
            pass
        return "stable"

    aspects = {
        "earnings": extract_score("EARNINGS_SENTIMENT"),
        "guidance": extract_score("GUIDANCE_SENTIMENT"),
        "products": extract_score("PRODUCTS_SENTIMENT"),
        "management": extract_score("MANAGEMENT_SENTIMENT"),
        "market": extract_score("MARKET_SENTIMENT"),
    }

    return {
        "overall": extract_score("OVERALL_SENTIMENT"),
        "aspects": aspects,
        "trend": extract_trend(),
        "confidence": extract_score("CONFIDENCE"),
    }


async def sentiment_agent_async(state: AgentState) -> Dict:
    """
    Pure async sentiment analysis agent that analyzes recent news and extracts market sentiment.
    Uses async HTTP calls and async LLM calls for optimal performance.
    Combines Finnhub pre-computed scores with LLM-based analysis.
    """
    symbol = state["symbol"]

    try:
        print(f"📰 Sentiment Agent: Starting async analysis for {symbol}")

        # Fetch Finnhub pre-computed sentiment in parallel with news
        print(f"🔍 Sentiment Agent: Fetching Finnhub sentiment and news with async calls...")
        async with aiohttp.ClientSession() as session:
            loop = asyncio.get_event_loop()
            # Fetch Finnhub and news in parallel
            finnhub_task = loop.run_in_executor(None, finnhub_service.get_news_sentiment, symbol)
            company_articles_task = loop.run_in_executor(None, news_service.get_recent_news, symbol, 10)
            market_articles_task = loop.run_in_executor(None, news_service.get_market_news, 5)

            # Wait for all to complete
            finnhub_data, company_articles, market_articles = await asyncio.gather(
                finnhub_task,
                company_articles_task,
                market_articles_task
            )

            print(f"✓ Sentiment Agent: Found {len(company_articles)} company-specific articles")
            print(f"✓ Sentiment Agent: Found {len(market_articles)} market articles")
        
        # Combine all articles
        all_articles = company_articles + market_articles
        
    except Exception as e:
        print(f"❌ Sentiment Agent ERROR: Failed to fetch news - {str(e)}")
        raise
    
    if not all_articles:
        return {
            "news_summary": "No recent news found for analysis.",
            "sentiment_score": 0.0,
            "sentiment_aspects": {},
            "sentiment_trend": "stable",
            "sentiment_confidence": 0.0,
            "news_sources": [],
        }

    # Build context for LLM with credibility weighting and timestamps
    news_context = "=== COMPANY-SPECIFIC NEWS (7-day lookback) ===\n"
    if company_articles:
        news_context += "\n".join([
            f"{i+1}. [{article.get('credibility_tier', 3)}★] {article['title']}\n"
            f"   Publisher: {article['publisher']} (Credibility Weight: {article.get('credibility_weight', 0.5):.0%})\n"
            f"   Date: {article['timestamp'][:10]}\n"
            f"   Snippet: {article.get('snippet', '')[:150]}..."
            for i, article in enumerate(company_articles[:8])
        ])
    else:
        news_context += "No recent company-specific news found.\n"

    news_context += "\n\n=== MARKET NEWS (7-day lookback) ===\n"
    if market_articles:
        news_context += "\n".join([
            f"{i+1}. [{article.get('credibility_tier', 3)}★] {article['title']}\n"
            f"   Publisher: {article['publisher']} (Weight: {article.get('credibility_weight', 0.5):.0%})\n"
            f"   Date: {article['timestamp'][:10]}\n"
            f"   Snippet: {article.get('snippet', '')[:150]}..."
            for i, article in enumerate(market_articles[:5])
        ])
    else:
        news_context += "No recent market news found.\n"

    # Use async LLM to analyze sentiment
    try:
        print(f"🤖 Sentiment Agent: Calling async LLM for sentiment analysis...")
        llm = get_llm_service()

        system_prompt = f"""You are an expert market sentiment analyst with 7 days of news history. Analyze the articles and provide:

## ASPECT-BASED SENTIMENT ANALYSIS

For each aspect, provide a score from -1.0 (very negative) to +1.0 (very positive):

1. **Earnings & Financial Performance**: Revenue, profit, earnings beats/misses
2. **Guidance & Outlook**: Forward guidance, management commentary, future expectations
3. **Products & Innovation**: Product launches, R&D, competitive positioning
4. **Management & Leadership**: Executive changes, strategic decisions
5. **Market & Competition**: Industry trends, competitive threats, market share

## CREDIBILITY-WEIGHTED ANALYSIS

Weight your analysis by source credibility:
- Tier 1 sources (1★) like Bloomberg, Reuters, WSJ: 100% weight
- Tier 2 sources (2★) like CNBC, MarketWatch: 75% weight
- Tier 3 sources (3★) other sources: 50% weight

## TEMPORAL TREND ANALYSIS

Based on the 7-day timeline:
- **Sentiment Trend**: Is sentiment improving, declining, or stable?
- **Key Events**: What specific events drove sentiment changes?
- **Momentum**: Is there accelerating positive/negative momentum?

## OVERALL ASSESSMENT

Combine all factors to determine overall sentiment for {symbol}.

## OUTPUT FORMAT

Provide your analysis, then on separate lines at the end:
EARNINGS_SENTIMENT: [number]
GUIDANCE_SENTIMENT: [number]
PRODUCTS_SENTIMENT: [number]
MANAGEMENT_SENTIMENT: [number]
MARKET_SENTIMENT: [number]
TREND: [improving/declining/stable]
CONFIDENCE: [0.0-1.0]
OVERALL_SENTIMENT: [number]"""

        user_message = f"Analyze sentiment for {symbol} based on these news articles:\n\n{news_context}"

        analysis = await llm.ainvoke(system_prompt, user_message)

        # Extract all sentiment metrics
        sentiment_data = extract_enhanced_sentiment(analysis)
        print(f"✓ Sentiment Agent: Async analysis completed - Overall: {sentiment_data['overall']:.2f}, Trend: {sentiment_data['trend']}, Confidence: {sentiment_data['confidence']:.2f}")
        print(f"✅ Sentiment Agent: Async analysis complete for {symbol}")

        # Remove score lines from analysis
        clean_analysis = analysis.split("EARNINGS_SENTIMENT:")[0].strip()

        # Extract Finnhub metrics
        finnhub_sentiment_score = None
        finnhub_bullish_percent = None
        finnhub_bearish_percent = None
        finnhub_buzz = None
        finnhub_articles_count = None

        if finnhub_data:
            finnhub_sentiment_score = finnhub_data.get('companyNewsScore')
            sentiment_breakdown = finnhub_data.get('sentiment', {})
            finnhub_bullish_percent = sentiment_breakdown.get('bullishPercent')
            finnhub_bearish_percent = sentiment_breakdown.get('bearishPercent')
            buzz_data = finnhub_data.get('buzz', {})
            finnhub_buzz = buzz_data.get('buzz')
            finnhub_articles_count = buzz_data.get('articlesInLastWeek')

        return {
            "news_summary": clean_analysis,
            "sentiment_score": sentiment_data['overall'],
            "sentiment_aspects": sentiment_data['aspects'],
            "sentiment_trend": sentiment_data['trend'],
            "sentiment_confidence": sentiment_data['confidence'],
            "news_sources": all_articles[:10],  # Top 10 articles
            # Finnhub pre-computed data
            "finnhub_sentiment_score": finnhub_sentiment_score,
            "finnhub_bullish_percent": finnhub_bullish_percent,
            "finnhub_bearish_percent": finnhub_bearish_percent,
            "finnhub_buzz": finnhub_buzz,
            "finnhub_articles_count": finnhub_articles_count,
        }
    except Exception as e:
        print(f"❌ Sentiment Agent ERROR: Async LLM call failed - {str(e)}")
        raise

