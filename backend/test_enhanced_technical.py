#!/usr/bin/env python3
"""Test script for enhanced technical analysis system."""

import asyncio
import json
from pprint import pprint
from app.services.stock_data import stock_data_service
from app.services.signal_service import signal_service
from app.services.pattern_recognition import pattern_service
from app.agents.technical_agent_enhanced import technical_agent_enhanced, technical_agent_enhanced_async


def test_multi_timeframe_data():
    """Test multi-timeframe data fetching."""
    print("\n" + "="*60)
    print("Testing Multi-Timeframe Data Fetching")
    print("="*60)

    symbol = "AAPL"
    timeframes = ["daily", "weekly", "monthly"]

    print(f"\nFetching data for {symbol} across timeframes: {timeframes}")
    multi_tf_data = stock_data_service.get_multi_timeframe_data(symbol, timeframes)

    for tf_name, tf_data in multi_tf_data.items():
        if tf_data.get('error'):
            print(f"\n❌ {tf_name}: Error - {tf_data['error']}")
        else:
            df = tf_data['df']
            indicators = tf_data['indicators']
            config = tf_data['config']

            print(f"\n✅ {tf_name.upper()} Timeframe:")
            print(f"  - Data points: {len(df)}")
            print(f"  - Trader type: {config['trader_type']}")
            print(f"  - Signal validity: {config['signal_validity']}")
            print(f"  - Current price: ${indicators['price']:.2f}")
            print(f"  - RSI: {indicators['rsi']:.1f}")
            print(f"  - ADX: {indicators.get('adx', 0):.1f}")
            print(f"  - Stochastic K: {indicators.get('stoch_k', 50):.1f}")


def test_signal_generation():
    """Test weighted signal generation."""
    print("\n" + "="*60)
    print("Testing Weighted Signal Generation")
    print("="*60)

    # Get some real data
    symbol = "AAPL"
    df, indicators = stock_data_service.get_stock_data(symbol)

    print(f"\nGenerating signals for {symbol}...")

    # Test with default weights
    signals = signal_service.generate_signals(indicators, timeframe="daily")

    print(f"\n📊 Signal Analysis:")
    print(f"  - Signal Type: {signals['signal_type']}")
    print(f"  - Confidence: {signals['confidence']:.2%}")
    print(f"  - Weighted Score: {signals['weighted_score']:.2%}")
    print(f"  - Confluence Bonus: {signals['confluence_bonus']:.2%}")
    print(f"  - Market Condition: {signals['market_condition']}")
    print(f"  - Valid Until: {signals['valid_until']}")

    print(f"\n🎯 Key Signals:")
    for signal in signals['key_signals'][:5]:
        print(f"  • {signal}")

    if signals.get('entry_zones'):
        zones = signals['entry_zones']
        print(f"\n💰 Entry Zones:")
        if zones.get('optimal_entry') is not None:
            print(f"  - Optimal Entry: ${zones['optimal_entry']:.2f}")
        if zones.get('stop_loss') is not None:
            print(f"  - Stop Loss: ${zones['stop_loss']:.2f}")
        if zones.get('take_profit_1') is not None:
            print(f"  - Take Profit 1: ${zones['take_profit_1']:.2f}")

    # Test with custom weights
    print("\n\nTesting with custom weights (momentum-focused)...")
    custom_weights = {
        "macd": 0.30,
        "rsi": 0.30,
        "stochastic": 0.20,
        "moving_average_crossover": 0.10,
        "volume": 0.10
    }

    custom_signal_service = signal_service.__class__(custom_weights)
    custom_signals = custom_signal_service.generate_signals(
        indicators,
        timeframe="daily",
        selected_indicators=list(custom_weights.keys())
    )

    print(f"  - Custom Signal Type: {custom_signals['signal_type']}")
    print(f"  - Custom Confidence: {custom_signals['confidence']:.2%}")


def test_pattern_recognition():
    """Test pattern recognition."""
    print("\n" + "="*60)
    print("Testing Pattern Recognition")
    print("="*60)

    symbol = "AAPL"
    df, _ = stock_data_service.get_stock_data(symbol)

    print(f"\nDetecting patterns for {symbol}...")
    patterns = pattern_service.detect_all_patterns(df, lookback_periods=50)

    print(f"\n🔍 Patterns Detected: {len(patterns)}")
    for i, pattern in enumerate(patterns[:5], 1):
        print(f"\n{i}. {pattern.pattern_type.value.replace('_', ' ').title()}")
        print(f"   - Confidence: {pattern.confidence:.1%}")
        print(f"   - Signal: {pattern.signal}")
        print(f"   - Description: {pattern.description}")
        if pattern.entry_point:
            print(f"   - Entry: ${pattern.entry_point:.2f}")
        if pattern.stop_loss:
            print(f"   - Stop Loss: ${pattern.stop_loss:.2f}")
        if pattern.take_profit:
            print(f"   - Take Profit: ${pattern.take_profit:.2f}")

    # Test divergence detection
    print("\n\n🔄 Testing Divergence Detection...")
    rsi_divergences = pattern_service.detect_divergences(df, 'RSI', 30)
    macd_divergences = pattern_service.detect_divergences(df, 'MACD', 30)

    all_divergences = rsi_divergences + macd_divergences
    if all_divergences:
        print(f"  Divergences found: {len(all_divergences)}")
        for div in all_divergences:
            print(f"  • {div['description']} (Confidence: {div['confidence']:.1%})")
    else:
        print("  No divergences detected in recent data")


def test_enhanced_technical_agent():
    """Test the enhanced technical agent."""
    print("\n" + "="*60)
    print("Testing Enhanced Technical Agent")
    print("="*60)

    # Create test state
    state = {
        "symbol": "AAPL",
        "investment_style": "balanced",
        "technical_config": {
            "timeframes": ["daily", "weekly"],
            "selected_indicators": None,  # Use all
            "custom_weights": None  # Use defaults
        }
    }

    print(f"\nRunning enhanced technical analysis for {state['symbol']}...")
    print(f"Investment Style: {state['investment_style']}")
    print(f"Timeframes: {state['technical_config']['timeframes']}")

    try:
        result = technical_agent_enhanced(state)

        print("\n✅ Analysis Complete!")

        # Display timeframe alignment
        if result.get('timeframe_alignment'):
            alignment = result['timeframe_alignment']
            print(f"\n📊 Timeframe Alignment:")
            print(f"  - Score: {alignment['score']:.2%}")
            print(f"  - Interpretation: {alignment['interpretation']}")

        # Display signals per timeframe
        if result.get('all_signals'):
            print(f"\n📈 Signals by Timeframe:")
            for tf_name, signals in result['all_signals'].items():
                print(f"\n  {tf_name.upper()}:")
                print(f"    - Signal: {signals.get('signal_type', 'N/A')}")
                print(f"    - Confidence: {signals.get('confidence', 0):.2%}")
                print(f"    - Market: {signals.get('market_condition', 'N/A')}")

        # Display pattern summary
        if result.get('all_patterns'):
            print(f"\n🔍 Patterns Summary:")
            for tf_name, patterns_data in result['all_patterns'].items():
                pattern_count = len(patterns_data.get('patterns', []))
                div_count = len(patterns_data.get('divergences', []))
                print(f"  - {tf_name}: {pattern_count} patterns, {div_count} divergences")

        # Display recommended timeframe
        if result.get('recommended_timeframe'):
            print(f"\n⭐ Recommended Timeframe: {result['recommended_timeframe']}")

        # Show a snippet of the LLM analysis
        if result.get('technical_analysis'):
            print(f"\n🤖 LLM Technical Analysis (snippet):")
            analysis_lines = result['technical_analysis'].split('\n')[:5]
            for line in analysis_lines:
                if line.strip():
                    print(f"  {line}")
            print("  ...")

    except Exception as e:
        print(f"\n❌ Error in enhanced technical agent: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_async_agent():
    """Test async version of enhanced technical agent."""
    print("\n" + "="*60)
    print("Testing Async Enhanced Technical Agent")
    print("="*60)

    state = {
        "symbol": "MSFT",
        "investment_style": "aggressive",
        "technical_config": {
            "timeframes": ["daily"],
            "selected_indicators": ["macd", "rsi", "adx", "stochastic", "volume"],
            "custom_weights": {
                "macd": 0.30,
                "rsi": 0.25,
                "adx": 0.20,
                "stochastic": 0.15,
                "volume": 0.10
            }
        }
    }

    print(f"\nRunning async analysis for {state['symbol']}...")
    print(f"Selected indicators: {state['technical_config']['selected_indicators']}")

    try:
        result = await technical_agent_enhanced_async(state)
        print("✅ Async analysis complete!")

        # Display results
        if result.get('all_signals') and 'daily' in result['all_signals']:
            daily_signals = result['all_signals']['daily']
            print(f"\n📊 Daily Signal:")
            print(f"  - Type: {daily_signals.get('signal_type', 'N/A')}")
            print(f"  - Confidence: {daily_signals.get('confidence', 0):.2%}")

            # Show signal details
            if daily_signals.get('signal_details'):
                print(f"\n📈 Signal Breakdown:")
                for ind_name, details in list(daily_signals['signal_details'].items())[:5]:
                    print(f"  • {ind_name}: {details['signal']} "
                          f"(strength: {details['strength']:.2f}, weight: {details['weight']:.2f})")

    except Exception as e:
        print(f"\n❌ Error in async agent: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ENHANCED TECHNICAL ANALYSIS SYSTEM TEST")
    print("="*60)

    try:
        # Test individual components
        test_multi_timeframe_data()
        test_signal_generation()
        test_pattern_recognition()

        # Test the full enhanced agent
        test_enhanced_technical_agent()

        # Test async version
        print("\nRunning async test...")
        asyncio.run(test_async_agent())

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()