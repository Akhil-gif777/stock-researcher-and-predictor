"""Sentiment analysis agent for news and market sentiment."""
from typing import Dict, List
from app.agents.state import AgentState
from app.services.news_service import news_service
from app.services.llm_service import get_llm_service


def sentiment_agent(state: AgentState) -> Dict:
    """
    Sentiment agent that analyzes recent news and extracts market sentiment.
    """
    symbol = state["symbol"]
    
    try:
        print(f"📰 Sentiment Agent: Starting analysis for {symbol}")
        
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
            "news_sources": [],
        }
    
    # Build context for LLM with better formatting
    news_context = "=== COMPANY-SPECIFIC NEWS ===\n"
    if company_articles:
        news_context += "\n".join([
            f"{i+1}. {article['title']} ({article['publisher']}) - {article.get('snippet', '')[:100]}..."
            for i, article in enumerate(company_articles[:8])
        ])
    else:
        news_context += "No recent company-specific news found.\n"
    
    news_context += "\n\n=== MARKET NEWS ===\n"
    if market_articles:
        news_context += "\n".join([
            f"{i+1}. {article['title']} ({article['publisher']}) - {article.get('snippet', '')[:100]}..."
            for i, article in enumerate(market_articles[:5])
        ])
    else:
        news_context += "No recent market news found.\n"
    
    # Use LLM to analyze sentiment
    try:
        print(f"🤖 Sentiment Agent: Calling LLM for sentiment analysis...")
        llm = get_llm_service()
        
        system_prompt = f"""You are an expert market sentiment analyst. Analyze the news articles and determine:

1. **Company-Specific Sentiment**: How do the company-specific news articles affect {symbol}?
2. **Market Sentiment**: How do broader market conditions affect {symbol}?
3. **Overall Assessment**: Combine both to determine overall sentiment
4. **Key Catalysts**: What are the main drivers of sentiment (earnings, guidance, market conditions, etc.)?
5. **Risk Factors**: What could negatively impact the stock?

Focus on:
- Financial performance and guidance
- Analyst upgrades/downgrades
- Market conditions (Fed policy, inflation, etc.)
- Industry trends
- Competitive dynamics

Provide a comprehensive analysis that considers both company-specific and market-wide factors.

At the end, provide a sentiment score from -1.0 (very negative) to +1.0 (very positive).
Format the last line as: SENTIMENT_SCORE: [number]"""
        
        user_message = f"Analyze sentiment for {symbol} based on these news articles:\n\n{news_context}"
        
        analysis = llm.invoke(system_prompt, user_message)
        
        # Extract sentiment score from response
        sentiment_score = extract_sentiment_score(analysis)
        print(f"✓ Sentiment Agent: Analysis completed - Sentiment score: {sentiment_score:.2f}")
        print(f"✅ Sentiment Agent: Analysis complete for {symbol}")
        
        # Remove score line from analysis
        clean_analysis = analysis.split("SENTIMENT_SCORE:")[0].strip()
        
        return {
            "news_summary": clean_analysis,
            "sentiment_score": sentiment_score,
            "news_sources": all_articles[:10],  # Top 10 articles
        }
    except Exception as e:
        print(f"❌ Sentiment Agent ERROR: LLM call failed - {str(e)}")
        raise


def extract_sentiment_score(text: str) -> float:
    """Extract sentiment score from LLM response."""
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

