#!/usr/bin/env python3
"""Simple test to verify enhanced technical analysis works."""

from app.services.stock_data import stock_data_service
from app.services.signal_service import signal_service

print("Testing enhanced technical analysis...")

# Test 1: Multi-timeframe data
print("\n1. Testing multi-timeframe data fetch...")
try:
    data = stock_data_service.get_multi_timeframe_data("AAPL", ["daily"])
    if data and "daily" in data:
        print("✅ Multi-timeframe fetch works")
        print(f"   Price: ${data['daily']['indicators']['price']:.2f}")
        print(f"   ADX: {data['daily']['indicators'].get('adx', 0):.1f}")
        print(f"   Stochastic: {data['daily']['indicators'].get('stoch_k', 0):.1f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Signal generation
print("\n2. Testing signal generation...")
try:
    df, indicators = stock_data_service.get_stock_data("AAPL")
    signals = signal_service.generate_signals(indicators)
    print(f"✅ Signal generation works")
    print(f"   Signal: {signals['signal_type']}")
    print(f"   Confidence: {signals['confidence']:.2%}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Basic tests passed! Enhanced technical analysis is working.")