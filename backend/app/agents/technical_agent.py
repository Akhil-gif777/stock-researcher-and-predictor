"""Technical analysis agent for evaluating price patterns and indicators."""
from typing import Dict
from app.agents.state import AgentState
from app.services.stock_data import stock_data_service
from app.services.llm_service import get_llm_service


def technical_agent(state: AgentState) -> Dict:
    """
    Technical analysis agent that evaluates technical indicators and generates signals.
    """
    symbol = state["symbol"]
    
    try:
        print(f"📈 Technical Agent: Starting analysis for {symbol}")
        
        # Get stock data with indicators
        print(f"📊 Technical Agent: Fetching stock data and calculating indicators...")
        df, indicators = stock_data_service.get_stock_data(symbol)
        chart_data = stock_data_service.get_chart_data(df)
        print(f"✓ Technical Agent: Calculated {len(indicators)} technical indicators")
        
        # Generate technical signals
        print(f"🔍 Technical Agent: Generating technical signals...")
        signals = generate_technical_signals(indicators)
        print(f"✓ Technical Agent: Generated signals - Overall: {signals.get('overall', 'N/A')}")
        
        # Use LLM to interpret technical setup
        print(f"🤖 Technical Agent: Calling LLM for technical interpretation...")
        llm = get_llm_service()
    except Exception as e:
        print(f"❌ Technical Agent ERROR: Failed during setup - {str(e)}")
        raise
    
    technical_context = f"""
Stock: {symbol}
Current Price: ${indicators['price']:.2f}

Trend Indicators:
- SMA(20): ${indicators['sma_20']:.2f} - Price is {_position_relative(indicators['price'], indicators['sma_20'])}
- SMA(50): ${indicators['sma_50']:.2f} - Price is {_position_relative(indicators['price'], indicators['sma_50'])}
- SMA(200): ${indicators['sma_200']:.2f} - Price is {_position_relative(indicators['price'], indicators['sma_200'])}

Momentum Indicators:
- RSI(14): {indicators['rsi']:.1f} - {_rsi_interpretation(indicators['rsi'])}
- MACD: {indicators['macd']:.2f}
- MACD Signal: {indicators['macd_signal']:.2f}
- MACD Histogram: {indicators['macd_histogram']:.2f} - {_macd_interpretation(indicators['macd_histogram'])}

Volatility:
- Bollinger Bands: Lower=${indicators['bb_lower']:.2f}, Middle=${indicators['bb_middle']:.2f}, Upper=${indicators['bb_upper']:.2f}
- ATR(14): ${indicators['atr']:.2f}

Volume:
- Current: {indicators['volume']:,}
- 20-day Average: {indicators['volume_avg']:,}
- Volume Status: {_volume_interpretation(indicators['volume'], indicators['volume_avg'])}

Support/Resistance:
- Support: ${indicators['support']:.2f}
- Resistance: ${indicators['resistance']:.2f}
"""
    
    system_prompt = """You are a technical analysis expert. Analyze the technical setup and provide:
1. Overall trend direction (bullish, bearish, or neutral)
2. Key technical signals (breakouts, crossovers, divergences)
3. Potential entry points and price targets
4. Risk levels and stop-loss considerations

Be specific and actionable. Keep it concise (2-3 paragraphs)."""
    
    try:
        analysis = llm.invoke(system_prompt, technical_context)
        print(f"✓ Technical Agent: LLM analysis completed")
        print(f"✅ Technical Agent: Analysis complete for {symbol}")
        
        return {
            "technical_signals": signals,
            "chart_data": chart_data,
            "technical_indicators": indicators,
        }
    except Exception as e:
        print(f"❌ Technical Agent ERROR: LLM call failed - {str(e)}")
        raise


def generate_technical_signals(indicators: Dict) -> Dict:
    """Generate buy/sell signals from technical indicators."""
    signals = {}
    
    # Trend signals
    price = indicators['price']
    if price > indicators['sma_200']:
        signals['long_term_trend'] = 'bullish'
    elif price < indicators['sma_200']:
        signals['long_term_trend'] = 'bearish'
    else:
        signals['long_term_trend'] = 'neutral'
    
    # Moving average crossover
    if indicators['sma_20'] > indicators['sma_50']:
        signals['ma_crossover'] = 'golden_cross'
    elif indicators['sma_20'] < indicators['sma_50']:
        signals['ma_crossover'] = 'death_cross'
    else:
        signals['ma_crossover'] = 'neutral'
    
    # RSI signals
    rsi = indicators['rsi']
    if rsi < 30:
        signals['rsi_signal'] = 'oversold_buy'
    elif rsi > 70:
        signals['rsi_signal'] = 'overbought_sell'
    else:
        signals['rsi_signal'] = 'neutral'
    
    # MACD signals
    if indicators['macd_histogram'] > 0:
        signals['macd_signal'] = 'bullish'
    else:
        signals['macd_signal'] = 'bearish'
    
    # Overall signal strength (simple scoring)
    bullish_count = sum(1 for s in signals.values() if 'bullish' in str(s) or 'buy' in str(s) or 'golden' in str(s))
    bearish_count = sum(1 for s in signals.values() if 'bearish' in str(s) or 'sell' in str(s) or 'death' in str(s))
    
    if bullish_count > bearish_count + 1:
        signals['overall'] = 'strong_buy'
    elif bullish_count > bearish_count:
        signals['overall'] = 'buy'
    elif bearish_count > bullish_count + 1:
        signals['overall'] = 'strong_sell'
    elif bearish_count > bullish_count:
        signals['overall'] = 'sell'
    else:
        signals['overall'] = 'hold'
    
    return signals


def _position_relative(price: float, ma: float) -> str:
    """Describe price position relative to moving average."""
    if ma == 0 or price == 0:
        return "near (neutral)"

    pct_diff = ((price - ma) / ma) * 100
    if pct_diff > 2:
        return f"above by {pct_diff:.1f}% (bullish)"
    elif pct_diff < -2:
        return f"below by {abs(pct_diff):.1f}% (bearish)"
    else:
        return "near (neutral)"


def _rsi_interpretation(rsi: float) -> str:
    """Interpret RSI value."""
    if rsi < 30:
        return "Oversold - potential bounce"
    elif rsi > 70:
        return "Overbought - potential pullback"
    elif 40 <= rsi <= 60:
        return "Neutral - healthy"
    else:
        return "Trending"


def _macd_interpretation(hist: float) -> str:
    """Interpret MACD histogram."""
    if hist > 0.5:
        return "Strong bullish momentum"
    elif hist > 0:
        return "Bullish momentum"
    elif hist < -0.5:
        return "Strong bearish momentum"
    else:
        return "Bearish momentum"


def _volume_interpretation(current: int, avg: int) -> str:
    """Interpret volume relative to average."""
    ratio = current / avg if avg > 0 else 1
    if ratio > 1.5:
        return f"High ({ratio:.1f}x average) - strong conviction"
    elif ratio < 0.5:
        return f"Low ({ratio:.1f}x average) - weak conviction"
    else:
        return "Normal"

