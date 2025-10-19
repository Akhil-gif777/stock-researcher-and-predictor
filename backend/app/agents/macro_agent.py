"""Macro agent for analyzing macroeconomic indicators."""
import asyncio
import aiohttp
from typing import Dict
from app.agents.state import AgentState
from app.services.macro_service import macro_service
from app.services.llm_service import get_llm_service


def macro_agent(state: AgentState) -> Dict:
    """
    Macro agent that analyzes macroeconomic environment and assesses market risk.
    
    Fetches indicators: VIX, Fed Rate, GDP, CPI, Unemployment
    """
    symbol = state["symbol"]
    
    try:
        print(f"🌐 Macro Agent: Starting macroeconomic analysis")
        
        # Get macro indicators (with 3-day caching)
        print(f"📊 Macro Agent: Fetching economic indicators...")
        indicators = macro_service.get_macro_indicators()
        
        # Log the indicators
        vix = indicators.get('vix')
        fed_rate = indicators.get('fed_rate')
        gdp = indicators.get('gdp_growth')
        cpi = indicators.get('inflation_cpi')
        unemployment = indicators.get('unemployment')
        
        print(f"✓ Macro Agent: Retrieved indicators:")
        print(f"  - VIX: {vix if vix else 'N/A'}")
        print(f"  - Fed Rate: {fed_rate}%" if fed_rate else "  - Fed Rate: N/A")
        print(f"  - GDP Growth: {gdp:.2f}%" if gdp else "  - GDP Growth: N/A")
        print(f"  - CPI Inflation: {cpi:.2f}%" if cpi else "  - CPI Inflation: N/A")
        print(f"  - Unemployment: {unemployment:.2f}%" if unemployment else "  - Unemployment: N/A")
        
        # Build context for LLM
        context = build_macro_context(indicators)
        
        # Get LLM analysis
        print(f"🤖 Macro Agent: Analyzing macroeconomic environment...")
        llm = get_llm_service()
        
        system_prompt = """You are a macroeconomic analyst. Analyze the current economic environment and its implications for stock market investing.

Given the macroeconomic indicators, assess:
1. Overall market risk level (LOW, MEDIUM, HIGH)
2. Key economic trends and concerns
3. Impact on stock market outlook
4. Specific considerations for individual stock analysis

Provide your analysis in this format:

RISK LEVEL: [LOW/MEDIUM/HIGH]

ECONOMIC ENVIRONMENT:
[2-3 paragraphs analyzing the current macroeconomic conditions, trends, and their implications for the stock market]

KEY FACTORS:
- [Factor 1]
- [Factor 2]
- [Factor 3]

INVESTMENT IMPLICATIONS:
[Brief guidance on how these conditions should influence investment decisions]"""
        
        try:
            analysis = llm.invoke(system_prompt, context)
        except Exception as e:
            print(f"⚠️ Macro Agent: LLM analysis failed: {str(e)}, using default")
            analysis = generate_default_macro_analysis(indicators)
        
        # Determine risk level from analysis or indicators
        risk_level = extract_risk_level(analysis, indicators)
        
        print(f"✅ Macro Agent: Analysis complete - Risk level: {risk_level}")
        
        return {
            "macro_summary": analysis,
            "macro_indicators": indicators,
            "macro_risk_level": risk_level,
        }
        
    except Exception as e:
        print(f"❌ Macro Agent ERROR: {str(e)}")
        # Return default values on error
        return {
            "macro_summary": "Macroeconomic data unavailable",
            "macro_indicators": {},
            "macro_risk_level": "medium",
        }


def build_macro_context(indicators: Dict) -> str:
    """Build context string for LLM from indicators."""
    vix = indicators.get('vix')
    fed_rate = indicators.get('fed_rate')
    gdp = indicators.get('gdp_growth')
    cpi = indicators.get('inflation_cpi')
    unemployment = indicators.get('unemployment')
    
    context = f"""
Current Macroeconomic Indicators:

VIX (Market Volatility Index): {f"{vix:.2f}" if vix else "Not available"}
{f"(Low risk: <15, Moderate: 15-25, High risk: >25)" if vix else ""}

Federal Funds Rate: {f"{fed_rate:.2f}%" if fed_rate else "Not available"}
{f"(Current monetary policy stance)" if fed_rate else ""}

GDP Growth (YoY): {f"{gdp:.2f}%" if gdp else "Not available"}
{f"(Economic expansion rate)" if gdp else ""}

CPI Inflation (YoY): {f"{cpi:.2f}%" if cpi else "Not available"}
{f"(Price pressure indicator)" if cpi else ""}

Unemployment Rate: {f"{unemployment:.2f}%" if unemployment else "Not available"}
{f"(Labor market health)" if unemployment else ""}

Analyze these indicators and assess the current macroeconomic environment for stock investing.
"""
    return context


def extract_risk_level(analysis: str, indicators: Dict) -> str:
    """Extract or determine risk level from analysis."""
    import re
    
    # Try to extract from LLM response
    risk_match = re.search(r'RISK LEVEL:\s*(LOW|MEDIUM|HIGH)', analysis, re.IGNORECASE)
    if risk_match:
        return risk_match.group(1).lower()
    
    # Fallback: Determine from indicators
    return determine_risk_from_indicators(indicators)


def determine_risk_from_indicators(indicators: Dict) -> str:
    """Determine risk level algorithmically from indicators."""
    risk_score = 0
    
    # VIX assessment
    vix = indicators.get('vix')
    if vix:
        if vix > 25:
            risk_score += 2  # High volatility
        elif vix > 20:
            risk_score += 1  # Elevated volatility
    
    # Inflation assessment
    cpi = indicators.get('inflation_cpi')
    if cpi:
        if cpi > 4:
            risk_score += 2  # High inflation
        elif cpi > 3:
            risk_score += 1  # Elevated inflation
    
    # Unemployment assessment
    unemployment = indicators.get('unemployment')
    if unemployment:
        if unemployment > 6:
            risk_score += 1  # Weak labor market
    
    # GDP assessment
    gdp = indicators.get('gdp_growth')
    if gdp:
        if gdp < 0:
            risk_score += 2  # Recession
        elif gdp < 1:
            risk_score += 1  # Weak growth
    
    # Convert score to level
    if risk_score >= 4:
        return "high"
    elif risk_score >= 2:
        return "medium"
    else:
        return "low"


def generate_default_macro_analysis(indicators: Dict) -> str:
    """Generate a basic macro analysis if LLM fails."""
    vix = indicators.get('vix')
    risk_level = determine_risk_from_indicators(indicators)
    
    analysis = f"""RISK LEVEL: {risk_level.upper()}

ECONOMIC ENVIRONMENT:
The current macroeconomic environment shows a {risk_level} risk level for stock market investing. """
    
    if vix:
        analysis += f"Market volatility (VIX) is at {vix:.2f}, indicating {'heightened' if vix > 20 else 'moderate'} uncertainty. "
    
    analysis += """

KEY FACTORS:
- Monitoring economic indicators for trend changes
- Assessing market volatility and risk appetite
- Evaluating impact on corporate earnings

INVESTMENT IMPLICATIONS:
Consider the current macroeconomic conditions when making investment decisions. """
    
    if risk_level == "high":
        analysis += "Higher risk environment suggests defensive positioning and careful stock selection."
    elif risk_level == "medium":
        analysis += "Moderate risk environment allows for balanced portfolio approach with selective opportunities."
    else:
        analysis += "Lower risk environment supports more aggressive positioning in growth opportunities."
    
    return analysis


async def macro_agent_async(state: AgentState) -> Dict:
    """
    Pure async macro agent that analyzes macroeconomic environment and assesses market risk.
    Uses async HTTP calls and async LLM calls for optimal performance.
    """
    symbol = state["symbol"]
    
    try:
        print(f"🌐 Macro Agent: Starting async macroeconomic analysis")
        
        # Get macro indicators using async
        print(f"📊 Macro Agent: Fetching economic indicators with async calls...")
        async with aiohttp.ClientSession() as session:
            # For now, use the sync version in a thread to maintain compatibility
            loop = asyncio.get_event_loop()
            indicators = await loop.run_in_executor(None, macro_service.get_macro_indicators)
            
            # Log the indicators
            vix = indicators.get('vix')
            fed_rate = indicators.get('fed_rate')
            gdp = indicators.get('gdp_growth')
            cpi = indicators.get('inflation_cpi')
            unemployment = indicators.get('unemployment')
            
            print(f"✓ Macro Agent: Retrieved indicators:")
            print(f"  - VIX: {vix if vix else 'N/A'}")
            print(f"  - Fed Rate: {fed_rate}%" if fed_rate else "  - Fed Rate: N/A")
            print(f"  - GDP Growth: {gdp:.2f}%" if gdp else "  - GDP Growth: N/A")
            print(f"  - CPI Inflation: {cpi:.2f}%" if cpi else "  - CPI Inflation: N/A")
            print(f"  - Unemployment: {unemployment:.2f}%" if unemployment else "  - Unemployment: N/A")
        
        # Build context for LLM
        context = build_macro_context(indicators)
        
        # Get async LLM analysis
        print(f"🤖 Macro Agent: Analyzing macroeconomic environment with async LLM...")
        llm = get_llm_service()
        
        system_prompt = """You are a macroeconomic analyst. Analyze the current economic environment and its implications for stock market investing.

Given the macroeconomic indicators, assess:
1. Overall market risk level (LOW, MEDIUM, HIGH)
2. Key economic trends and concerns
3. Impact on stock market outlook
4. Specific considerations for individual stock analysis

Provide your analysis in this format:

RISK LEVEL: [LOW/MEDIUM/HIGH]

ECONOMIC ENVIRONMENT:
[2-3 paragraphs analyzing the current macroeconomic conditions, trends, and their implications for the stock market]

KEY FACTORS:
- [Factor 1]
- [Factor 2]
- [Factor 3]

INVESTMENT IMPLICATIONS:
[Brief guidance on how these conditions should influence investment decisions]"""
        
        try:
            analysis = await llm.ainvoke(system_prompt, context)
        except Exception as e:
            print(f"⚠️ Macro Agent: Async LLM analysis failed: {str(e)}, using default")
            analysis = generate_default_macro_analysis(indicators)
        
        # Determine risk level from analysis or indicators
        risk_level = extract_risk_level(analysis, indicators)
        
        print(f"✅ Macro Agent: Async analysis complete - Risk level: {risk_level}")
        
        return {
            "macro_summary": analysis,
            "macro_indicators": indicators,
            "macro_risk_level": risk_level,
        }
        
    except Exception as e:
        print(f"❌ Macro Agent ERROR: {str(e)}")
        # Return default values on error
        return {
            "macro_summary": "Macroeconomic data unavailable",
            "macro_indicators": {},
            "macro_risk_level": "medium",
        }

