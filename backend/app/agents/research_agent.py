"""Research agent for fundamental analysis and company research."""
import aiohttp
from typing import Dict
from app.agents.state import AgentState
from app.services.llm_service import get_llm_service
from app.services.stock_data import stock_data_service


def research_agent(state: AgentState) -> Dict:
    """
    Research agent that analyzes company fundamentals, financials, and recent news.
    Tracks all sources for transparency.
    """
    symbol = state["symbol"]
    
    try:
        print(f"🔍 Research Agent: Starting analysis for {symbol}")
        
        # Get company information
        print(f"📊 Research Agent: Fetching company data from yfinance...")
        company_info = stock_data_service.get_company_info(symbol)
        print(f"✓ Research Agent: Company data received for {company_info.get('name', symbol)}")
    except Exception as e:
        print(f"❌ Research Agent ERROR: Failed to fetch company data - {str(e)}")
        raise
    
    # Build comprehensive context for LLM
    context = f"""
Company: {company_info['name']}
Sector: {company_info['sector']}
Industry: {company_info['industry']}
Market Cap: ${company_info['market_cap']:,.0f}
P/E Ratio: {company_info['pe_ratio']:.2f}
Revenue Growth: {company_info['revenue_growth']:.2%}
Profit Margin: {company_info['profit_margin']:.2%}
Debt-to-Equity: {company_info['debt_ratio']:.2f}

Business Description:
{company_info['description'][:500]}...
"""
    
    # Use LLM to analyze fundamentals
    try:
        print(f"🤖 Research Agent: Calling LLM for fundamental analysis...")
        llm = get_llm_service()
        
        system_prompt = """You are a fundamental analysis expert. Analyze the company's 
financial health, competitive position, and investment potential. Focus on:
1. Financial strength (margins, growth, debt levels)
2. Competitive advantages or moats
3. Industry position and trends
4. Key risks and opportunities

Provide a concise but comprehensive summary (3-4 paragraphs)."""
        
        analysis = llm.invoke(system_prompt, context)
        print(f"✓ Research Agent: LLM analysis completed")
    except Exception as e:
        print(f"❌ Research Agent ERROR: LLM call failed - {str(e)}")
        raise
    
    # Track sources
    sources = [
        {
            'type': 'data',
            'title': f'{company_info["name"]} - Company Profile',
            'url': f'https://finance.yahoo.com/quote/{symbol}',
        },
        {
            'type': 'data',
            'title': f'{symbol} - Financial Data',
            'url': f'https://finance.yahoo.com/quote/{symbol}/financials',
        }
    ]
    
    print(f"✅ Research Agent: Analysis complete for {symbol}")
    
    return {
        "company_info": analysis,
        "financial_data": company_info,
        "research_sources": sources,
    }


async def research_agent_async(state: AgentState) -> Dict:
    """
    Pure async research agent that analyzes company fundamentals, financials, and recent news.
    Uses async HTTP calls and async LLM calls for optimal performance.
    """
    symbol = state["symbol"]
    
    try:
        print(f"🔍 Research Agent: Starting async analysis for {symbol}")
        
        # Get company information using async HTTP
        print(f"📊 Research Agent: Fetching company data with aiohttp...")
        async with aiohttp.ClientSession() as session:
            # Use the same stock_data_service but with async HTTP
            company_info = await stock_data_service.get_company_info_async(symbol, session)
            print(f"✓ Research Agent: Company data received for {company_info.get('name', symbol)}")
    except Exception as e:
        print(f"❌ Research Agent ERROR: Failed to fetch company data - {str(e)}")
        raise
    
    # Build comprehensive context for LLM
    context = f"""
Company: {company_info['name']}
Sector: {company_info['sector']}
Industry: {company_info['industry']}
Market Cap: ${company_info['market_cap']:,.0f}
P/E Ratio: {company_info['pe_ratio']:.2f}
Revenue Growth: {company_info['revenue_growth']:.2%}
Profit Margin: {company_info['profit_margin']:.2%}
Debt-to-Equity: {company_info['debt_ratio']:.2f}

Business Description:
{company_info['description'][:500]}...
"""
    
    # Use async LLM to analyze fundamentals
    try:
        print(f"🤖 Research Agent: Calling async LLM for fundamental analysis...")
        llm = get_llm_service()
        
        system_prompt = """You are a fundamental analysis expert. Analyze the company's 
financial health, competitive position, and investment potential. Focus on:
1. Financial strength (margins, growth, debt levels)
2. Competitive advantages or moats
3. Industry position and trends
4. Key risks and opportunities

Provide a concise but comprehensive summary (3-4 paragraphs)."""
        
        # Use async LLM call
        analysis = await llm.ainvoke(system_prompt, context)
        print(f"✓ Research Agent: Async LLM analysis completed")
    except Exception as e:
        print(f"❌ Research Agent ERROR: Async LLM call failed - {str(e)}")
        raise
    
    # Track sources
    sources = [
        {
            'type': 'data',
            'title': f'{company_info["name"]} - Company Profile',
            'url': f'https://finance.yahoo.com/quote/{symbol}',
        },
        {
            'type': 'data',
            'title': f'{symbol} - Financial Data',
            'url': f'https://finance.yahoo.com/quote/{symbol}/financials',
        }
    ]
    
    print(f"✅ Research Agent: Async analysis complete for {symbol}")
    
    return {
        "company_info": analysis,
        "financial_data": company_info,
        "research_sources": sources,
    }

