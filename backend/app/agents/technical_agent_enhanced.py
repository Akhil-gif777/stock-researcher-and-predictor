"""Enhanced technical analysis agent with multi-timeframe analysis, pattern recognition, and weighted signals."""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from app.agents.state import AgentState
from app.services.stock_data import stock_data_service
from app.services.signal_service import signal_service, SignalType
from app.services.pattern_recognition import pattern_service
from app.services.llm_service import get_llm_service
import json


def technical_agent_enhanced(state: AgentState) -> Dict:
    """
    Enhanced technical analysis agent with multi-timeframe analysis and advanced signals.
    """
    symbol = state["symbol"]
    investment_style = state.get("investment_style", "balanced")

    # Get user preferences if provided
    user_config = state.get("technical_config", {})
    selected_timeframes = user_config.get("timeframes", ["daily", "weekly"])
    selected_indicators = user_config.get("selected_indicators", None)
    custom_weights = user_config.get("custom_weights", None)

    try:
        print(f"📈 Technical Agent Enhanced: Starting multi-timeframe analysis for {symbol}")

        # Fetch multi-timeframe data
        print(f"📊 Technical Agent: Fetching data for timeframes: {selected_timeframes}")
        multi_tf_data = stock_data_service.get_multi_timeframe_data(symbol, selected_timeframes)

        # Process each timeframe
        all_analyses = {}
        all_patterns = {}
        all_signals = {}

        for tf_name, tf_data in multi_tf_data.items():
            if tf_data.get('error'):
                print(f"⚠️ Technical Agent: Error in {tf_name} timeframe - {tf_data['error']}")
                continue

            df = tf_data['df']
            indicators = tf_data['indicators']
            config = tf_data['config']

            if df.empty:
                continue

            print(f"🔍 Technical Agent: Analyzing {tf_name} timeframe...")

            # Generate weighted signals for this timeframe
            if custom_weights:
                signal_gen = signal_service.__class__(custom_weights)
            else:
                signal_gen = signal_service

            signals = signal_gen.generate_signals(
                indicators,
                timeframe=tf_name,
                selected_indicators=selected_indicators
            )
            all_signals[tf_name] = signals

            # Detect patterns for this timeframe
            patterns = pattern_service.detect_all_patterns(df, lookback_periods=50)

            # Detect divergences
            rsi_divergences = pattern_service.detect_divergences(df, 'RSI', 30)
            macd_divergences = pattern_service.detect_divergences(df, 'MACD', 30)

            all_patterns[tf_name] = {
                'patterns': [
                    {
                        'type': p.pattern_type.value,
                        'confidence': p.confidence,
                        'signal': p.signal,
                        'description': p.description
                    }
                    for p in patterns[:5]  # Top 5 patterns
                ],
                'divergences': rsi_divergences + macd_divergences
            }

            # Store analysis for this timeframe
            all_analyses[tf_name] = {
                'indicators': indicators,
                'signals': signals,
                'patterns': all_patterns[tf_name],
                'config': config
            }

            print(f"✓ Technical Agent: {tf_name} - Signal: {signals['signal_type']}, Confidence: {signals['confidence']:.2%}")

        # Calculate timeframe alignment
        alignment_score = _calculate_timeframe_alignment(all_signals)

        # Generate comprehensive technical context for LLM
        technical_context = _generate_enhanced_context(
            symbol,
            all_analyses,
            alignment_score,
            investment_style
        )

        # Use LLM for advanced interpretation
        print(f"🤖 Technical Agent: Calling LLM for comprehensive technical interpretation...")
        llm = get_llm_service()

        system_prompt = """You are an expert technical analyst with deep knowledge of multi-timeframe analysis.

Analyze the provided multi-timeframe technical data and provide:

1. **Multi-Timeframe Synopsis**: How different timeframes align or diverge
2. **Key Technical Levels**: Critical support/resistance across timeframes
3. **Pattern Recognition Insights**: Most significant patterns detected
4. **Signal Confluence**: Where multiple indicators/timeframes agree
5. **Trading Strategy**: Specific entry, stop-loss, and take-profit levels
6. **Risk Assessment**: Technical risk factors and mitigation
7. **Time Horizon Recommendation**: Based on the strongest signals

Format your response in clear sections. Be specific with price levels and percentages.
Consider the user's investment style when making recommendations."""

        analysis = llm.invoke(system_prompt, technical_context)

        print(f"✅ Technical Agent Enhanced: Multi-timeframe analysis complete for {symbol}")

        # Prepare the final result
        result = {
            "technical_analyses": all_analyses,
            "timeframe_alignment": {
                "score": alignment_score,
                "interpretation": _interpret_alignment(alignment_score)
            },
            "all_patterns": all_patterns,
            "all_signals": all_signals,
            "technical_analysis": analysis,
            "recommended_timeframe": _get_recommended_timeframe(all_signals, investment_style),
            "chart_data": {}  # Will be populated per timeframe if needed
        }

        # Add chart data for the primary timeframe
        primary_tf = selected_timeframes[0] if selected_timeframes else "daily"
        if primary_tf in multi_tf_data and not multi_tf_data[primary_tf]['df'].empty:
            result["chart_data"] = stock_data_service.get_chart_data(multi_tf_data[primary_tf]['df'])

        return result

    except Exception as e:
        print(f"❌ Technical Agent Enhanced ERROR: {str(e)}")
        raise


async def technical_agent_enhanced_async(state: AgentState) -> Dict:
    """
    Async version of enhanced technical analysis agent.
    """
    symbol = state["symbol"]
    investment_style = state.get("investment_style", "balanced")

    # Get user preferences if provided
    user_config = state.get("technical_config", {})
    selected_timeframes = user_config.get("timeframes", ["daily", "weekly"])
    selected_indicators = user_config.get("selected_indicators", None)
    custom_weights = user_config.get("custom_weights", None)

    try:
        print(f"📈 Technical Agent Enhanced: Starting async multi-timeframe analysis for {symbol}")

        # Fetch multi-timeframe data (this is already parallelized internally)
        multi_tf_data = await asyncio.get_event_loop().run_in_executor(
            None,
            stock_data_service.get_multi_timeframe_data,
            symbol,
            selected_timeframes
        )

        # Process each timeframe
        all_analyses = {}
        all_patterns = {}
        all_signals = {}

        for tf_name, tf_data in multi_tf_data.items():
            if tf_data.get('error'):
                print(f"⚠️ Technical Agent: Error in {tf_name} timeframe - {tf_data['error']}")
                continue

            df = tf_data['df']
            indicators = tf_data['indicators']
            config = tf_data['config']

            if df.empty:
                continue

            print(f"🔍 Technical Agent: Analyzing {tf_name} timeframe...")

            # Generate weighted signals for this timeframe
            if custom_weights:
                signal_gen = signal_service.__class__(custom_weights)
            else:
                signal_gen = signal_service

            signals = signal_gen.generate_signals(
                indicators,
                timeframe=tf_name,
                selected_indicators=selected_indicators
            )
            all_signals[tf_name] = signals

            # Detect patterns for this timeframe
            patterns = pattern_service.detect_all_patterns(df, lookback_periods=50)

            # Detect divergences
            rsi_divergences = pattern_service.detect_divergences(df, 'RSI', 30)
            macd_divergences = pattern_service.detect_divergences(df, 'MACD', 30)

            all_patterns[tf_name] = {
                'patterns': [
                    {
                        'type': p.pattern_type.value,
                        'confidence': p.confidence,
                        'signal': p.signal,
                        'description': p.description
                    }
                    for p in patterns[:5]  # Top 5 patterns
                ],
                'divergences': rsi_divergences + macd_divergences
            }

            # Store analysis for this timeframe
            all_analyses[tf_name] = {
                'indicators': indicators,
                'signals': signals,
                'patterns': all_patterns[tf_name],
                'config': config
            }

            print(f"✓ Technical Agent: {tf_name} - Signal: {signals['signal_type']}, Confidence: {signals['confidence']:.2%}")

        # Calculate timeframe alignment
        alignment_score = _calculate_timeframe_alignment(all_signals)

        # Generate comprehensive technical context for LLM
        technical_context = _generate_enhanced_context(
            symbol,
            all_analyses,
            alignment_score,
            investment_style
        )

        # Use async LLM for advanced interpretation
        print(f"🤖 Technical Agent: Calling async LLM for comprehensive technical interpretation...")
        llm = get_llm_service()

        system_prompt = """You are an expert technical analyst with deep knowledge of multi-timeframe analysis.

Analyze the provided multi-timeframe technical data and provide:

1. **Multi-Timeframe Synopsis**: How different timeframes align or diverge
2. **Key Technical Levels**: Critical support/resistance across timeframes
3. **Pattern Recognition Insights**: Most significant patterns detected
4. **Signal Confluence**: Where multiple indicators/timeframes agree
5. **Trading Strategy**: Specific entry, stop-loss, and take-profit levels
6. **Risk Assessment**: Technical risk factors and mitigation
7. **Time Horizon Recommendation**: Based on the strongest signals

Format your response in clear sections. Be specific with price levels and percentages.
Consider the user's investment style when making recommendations."""

        analysis = await llm.ainvoke(system_prompt, technical_context)

        print(f"✅ Technical Agent Enhanced: Async multi-timeframe analysis complete for {symbol}")

        # Prepare the final result
        result = {
            "technical_analyses": all_analyses,
            "timeframe_alignment": {
                "score": alignment_score,
                "interpretation": _interpret_alignment(alignment_score)
            },
            "all_patterns": all_patterns,
            "all_signals": all_signals,
            "technical_analysis": analysis,
            "recommended_timeframe": _get_recommended_timeframe(all_signals, investment_style),
            "chart_data": {}  # Will be populated per timeframe if needed
        }

        # Add chart data for the primary timeframe
        primary_tf = selected_timeframes[0] if selected_timeframes else "daily"
        if primary_tf in multi_tf_data and not multi_tf_data[primary_tf]['df'].empty:
            result["chart_data"] = stock_data_service.get_chart_data(multi_tf_data[primary_tf]['df'])

        return result

    except Exception as e:
        print(f"❌ Technical Agent Enhanced Async ERROR: {str(e)}")
        raise


def _calculate_timeframe_alignment(all_signals: Dict) -> float:
    """Calculate how well different timeframes align."""
    if len(all_signals) < 2:
        return 0.5

    scores = []
    for tf_name, signals in all_signals.items():
        confidence = signals.get('confidence', 0.5)
        signal_type = signals.get('signal_type', 'neutral')

        # Convert signal to directional score
        if 'buy' in signal_type:
            directional_score = confidence
        elif 'sell' in signal_type:
            directional_score = 1 - confidence
        else:
            directional_score = 0.5

        scores.append(directional_score)

    # Calculate standard deviation of scores
    import numpy as np
    std_dev = np.std(scores)

    # Lower std dev means better alignment
    # Convert to 0-1 score where 1 is perfect alignment
    alignment_score = max(0, 1 - (std_dev * 2))

    return alignment_score


def _interpret_alignment(score: float) -> str:
    """Interpret timeframe alignment score."""
    if score >= 0.8:
        return "Strong alignment - High conviction signal"
    elif score >= 0.6:
        return "Moderate alignment - Good confirmation"
    elif score >= 0.4:
        return "Weak alignment - Mixed signals"
    else:
        return "Divergence - Conflicting timeframes"


def _get_recommended_timeframe(all_signals: Dict, investment_style: str) -> str:
    """Recommend the best timeframe based on signals and investment style."""
    # Map investment styles to preferred timeframes
    style_preferences = {
        "conservative": ["monthly", "weekly", "daily"],
        "balanced": ["weekly", "daily", "4hour"],
        "aggressive": ["daily", "4hour", "1hour"]
    }

    preferred_tfs = style_preferences.get(investment_style.lower(), ["daily", "weekly"])

    # Find the timeframe with highest confidence that matches preferences
    best_tf = None
    best_confidence = 0

    for tf_name, signals in all_signals.items():
        if tf_name in preferred_tfs:
            confidence = signals.get('confidence', 0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_tf = tf_name

    return best_tf or preferred_tfs[0]


def _generate_enhanced_context(
    symbol: str,
    all_analyses: Dict,
    alignment_score: float,
    investment_style: str
) -> str:
    """Generate comprehensive context for LLM analysis."""
    context = f"""
Stock: {symbol}
Investment Style: {investment_style}
Timeframe Alignment Score: {alignment_score:.2%} - {_interpret_alignment(alignment_score)}

=== MULTI-TIMEFRAME ANALYSIS ===
"""

    for tf_name, analysis in all_analyses.items():
        indicators = analysis['indicators']
        signals = analysis['signals']
        patterns = analysis['patterns']
        config = analysis['config']

        context += f"""
--- {tf_name.upper()} TIMEFRAME ---
Trader Type: {config.get('trader_type', 'N/A')}
Signal Validity: {config.get('signal_validity', 'N/A')}

Current Price: ${indicators.get('price', 0):.2f}

Signal: {signals.get('signal_type', 'N/A')}
Confidence: {signals.get('confidence', 0):.2%}
Weighted Score: {signals.get('weighted_score', 0):.2%}
Confluence Bonus: {signals.get('confluence_bonus', 0):.2%}

Key Indicators:
- RSI: {indicators.get('rsi', 50):.1f}
- MACD Histogram: {indicators.get('macd_histogram', 0):.3f}
- ADX: {indicators.get('adx', 0):.1f} (Market: {signals.get('market_condition', 'N/A')})
- Stochastic K: {indicators.get('stoch_k', 50):.1f}
- Volume Ratio: {indicators.get('volume', 0) / max(indicators.get('volume_avg', 1), 1):.2f}x

Support/Resistance:
- Support1: ${indicators.get('support1', 0):.2f}
- Pivot: ${indicators.get('pivot', 0):.2f}
- Resistance1: ${indicators.get('resistance1', 0):.2f}

Patterns Detected: {len(patterns.get('patterns', []))}
"""

        # Add top patterns
        for pattern in patterns.get('patterns', [])[:3]:
            context += f"  • {pattern['description']} (Confidence: {pattern['confidence']:.1%})\n"

        # Add divergences
        for div in patterns.get('divergences', [])[:2]:
            context += f"  • {div['description']} (Confidence: {div['confidence']:.1%})\n"

        # Add entry zones if available
        if 'entry_zones' in signals:
            zones = signals['entry_zones']
            if zones.get('optimal_entry'):
                context += f"\nSuggested Entry: ${zones['optimal_entry']:.2f}\n"
                if zones.get('stop_loss'):
                    context += f"Stop Loss: ${zones['stop_loss']:.2f}\n"
                if zones.get('take_profit_1'):
                    context += f"Take Profit: ${zones['take_profit_1']:.2f}\n"

    return context