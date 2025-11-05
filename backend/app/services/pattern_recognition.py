"""Pattern recognition service for candlestick and chart patterns."""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    """Types of patterns detected."""
    # Candlestick patterns
    HAMMER = "hammer"
    INVERTED_HAMMER = "inverted_hammer"
    SHOOTING_STAR = "shooting_star"
    HANGING_MAN = "hanging_man"
    DOJI = "doji"
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"

    # Chart patterns
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    HEAD_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_SHOULDERS = "inverse_head_and_shoulders"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"

    # Moving average patterns
    GOLDEN_CROSS = "golden_cross"
    DEATH_CROSS = "death_cross"


@dataclass
class Pattern:
    """Pattern detection result."""
    pattern_type: PatternType
    confidence: float
    signal: str  # bullish/bearish/neutral
    description: str
    validity_periods: int  # in candles
    entry_point: float = None
    stop_loss: float = None
    take_profit: float = None


class PatternRecognitionService:
    """Service for recognizing trading patterns."""

    def __init__(self):
        """Initialize the pattern recognition service."""
        self.min_pattern_confidence = 0.6

    def detect_all_patterns(
        self,
        df: pd.DataFrame,
        lookback_periods: int = 50
    ) -> List[Pattern]:
        """
        Detect all patterns in the given DataFrame.

        Args:
            df: DataFrame with OHLCV data
            lookback_periods: Number of periods to look back for pattern detection

        Returns:
            List of detected patterns
        """
        patterns = []

        # Ensure we have enough data
        if len(df) < lookback_periods:
            return patterns

        # Detect candlestick patterns
        candlestick_patterns = self._detect_candlestick_patterns(df)
        patterns.extend(candlestick_patterns)

        # Detect chart patterns
        chart_patterns = self._detect_chart_patterns(df, lookback_periods)
        patterns.extend(chart_patterns)

        # Detect moving average patterns
        ma_patterns = self._detect_ma_patterns(df)
        patterns.extend(ma_patterns)

        # Sort by confidence
        patterns.sort(key=lambda x: x.confidence, reverse=True)

        return patterns

    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect candlestick patterns in the last few candles."""
        patterns = []

        if len(df) < 3:
            return patterns

        # Get last 3 candles for pattern detection
        last_3 = df.tail(3).copy()
        last_3['body'] = last_3['Close'] - last_3['Open']
        last_3['body_size'] = abs(last_3['body'])
        last_3['upper_shadow'] = last_3['High'] - last_3[['Open', 'Close']].max(axis=1)
        last_3['lower_shadow'] = last_3[['Open', 'Close']].min(axis=1) - last_3['Low']
        last_3['range'] = last_3['High'] - last_3['Low']

        # Current candle (most recent)
        curr = last_3.iloc[-1]
        if len(last_3) >= 2:
            prev = last_3.iloc[-2]
        else:
            prev = None
        if len(last_3) >= 3:
            prev2 = last_3.iloc[-3]
        else:
            prev2 = None

        # Hammer (bullish reversal at bottom)
        if curr['lower_shadow'] > 2 * curr['body_size'] and curr['upper_shadow'] < curr['body_size'] * 0.3:
            confidence = min(0.9, curr['lower_shadow'] / (curr['body_size'] + 0.001) / 3)
            patterns.append(Pattern(
                pattern_type=PatternType.HAMMER,
                confidence=confidence,
                signal="bullish",
                description="Hammer pattern - potential bullish reversal",
                validity_periods=3,
                entry_point=curr['Close'] * 1.01,
                stop_loss=curr['Low'] * 0.99,
                take_profit=curr['Close'] * 1.05
            ))

        # Shooting Star (bearish reversal at top)
        if curr['upper_shadow'] > 2 * curr['body_size'] and curr['lower_shadow'] < curr['body_size'] * 0.3:
            confidence = min(0.9, curr['upper_shadow'] / (curr['body_size'] + 0.001) / 3)
            patterns.append(Pattern(
                pattern_type=PatternType.SHOOTING_STAR,
                confidence=confidence,
                signal="bearish",
                description="Shooting star pattern - potential bearish reversal",
                validity_periods=3,
                entry_point=curr['Close'] * 0.99,
                stop_loss=curr['High'] * 1.01,
                take_profit=curr['Close'] * 0.95
            ))

        # Doji (indecision)
        if curr['body_size'] < curr['range'] * 0.1:
            patterns.append(Pattern(
                pattern_type=PatternType.DOJI,
                confidence=0.7,
                signal="neutral",
                description="Doji pattern - market indecision",
                validity_periods=2
            ))

        # Bullish Engulfing
        if prev is not None:
            if (prev['body'] < 0 and  # Previous was bearish
                curr['body'] > 0 and  # Current is bullish
                curr['Open'] < prev['Close'] and  # Opens lower
                curr['Close'] > prev['Open']):  # Closes higher
                patterns.append(Pattern(
                    pattern_type=PatternType.BULLISH_ENGULFING,
                    confidence=0.8,
                    signal="bullish",
                    description="Bullish engulfing pattern - strong bullish signal",
                    validity_periods=5,
                    entry_point=curr['Close'] * 1.01,
                    stop_loss=min(prev['Low'], curr['Low']) * 0.99,
                    take_profit=curr['Close'] * 1.08
                ))

            # Bearish Engulfing
            if (prev['body'] > 0 and  # Previous was bullish
                curr['body'] < 0 and  # Current is bearish
                curr['Open'] > prev['Close'] and  # Opens higher
                curr['Close'] < prev['Open']):  # Closes lower
                patterns.append(Pattern(
                    pattern_type=PatternType.BEARISH_ENGULFING,
                    confidence=0.8,
                    signal="bearish",
                    description="Bearish engulfing pattern - strong bearish signal",
                    validity_periods=5,
                    entry_point=curr['Close'] * 0.99,
                    stop_loss=max(prev['High'], curr['High']) * 1.01,
                    take_profit=curr['Close'] * 0.92
                ))

        # Morning Star (bullish reversal - 3 candles)
        if prev2 is not None and prev is not None:
            if (prev2['body'] < -curr['range'] * 0.5 and  # First: large bearish
                abs(prev['body']) < prev['range'] * 0.3 and  # Second: small body (star)
                curr['body'] > curr['range'] * 0.5 and  # Third: large bullish
                curr['Close'] > prev2['Open']):  # Closes above first candle open
                patterns.append(Pattern(
                    pattern_type=PatternType.MORNING_STAR,
                    confidence=0.85,
                    signal="bullish",
                    description="Morning star pattern - strong bullish reversal",
                    validity_periods=7,
                    entry_point=curr['Close'] * 1.01,
                    stop_loss=min(prev2['Low'], prev['Low'], curr['Low']) * 0.98,
                    take_profit=curr['Close'] * 1.10
                ))

        # Evening Star (bearish reversal - 3 candles)
        if prev2 is not None and prev is not None:
            if (prev2['body'] > curr['range'] * 0.5 and  # First: large bullish
                abs(prev['body']) < prev['range'] * 0.3 and  # Second: small body (star)
                curr['body'] < -curr['range'] * 0.5 and  # Third: large bearish
                curr['Close'] < prev2['Open']):  # Closes below first candle open
                patterns.append(Pattern(
                    pattern_type=PatternType.EVENING_STAR,
                    confidence=0.85,
                    signal="bearish",
                    description="Evening star pattern - strong bearish reversal",
                    validity_periods=7,
                    entry_point=curr['Close'] * 0.99,
                    stop_loss=max(prev2['High'], prev['High'], curr['High']) * 1.02,
                    take_profit=curr['Close'] * 0.90
                ))

        return patterns

    def _detect_chart_patterns(
        self,
        df: pd.DataFrame,
        lookback_periods: int
    ) -> List[Pattern]:
        """Detect chart patterns like double top/bottom, triangles."""
        patterns = []

        if len(df) < lookback_periods:
            return patterns

        # Get recent data
        recent = df.tail(lookback_periods).copy()

        # Find local peaks and troughs
        highs = self._find_peaks(recent['High'].values, order=5)
        lows = self._find_troughs(recent['Low'].values, order=5)

        # Double Top
        if len(highs) >= 2:
            last_high = recent['High'].iloc[highs[-1]]
            prev_high = recent['High'].iloc[highs[-2]]

            if abs(last_high - prev_high) / last_high < 0.03:  # Within 3%
                # Check for valley between peaks
                valley_start = highs[-2]
                valley_end = highs[-1]
                valley_low = recent['Low'].iloc[valley_start:valley_end].min()

                if (last_high - valley_low) / last_high > 0.05:  # At least 5% dip
                    patterns.append(Pattern(
                        pattern_type=PatternType.DOUBLE_TOP,
                        confidence=0.75,
                        signal="bearish",
                        description="Double top pattern - bearish reversal",
                        validity_periods=10,
                        entry_point=valley_low * 0.99,
                        stop_loss=last_high * 1.02,
                        take_profit=valley_low - (last_high - valley_low) * 0.8
                    ))

        # Double Bottom
        if len(lows) >= 2:
            last_low = recent['Low'].iloc[lows[-1]]
            prev_low = recent['Low'].iloc[lows[-2]]

            if abs(last_low - prev_low) / last_low < 0.03:  # Within 3%
                # Check for peak between troughs
                peak_start = lows[-2]
                peak_end = lows[-1]
                peak_high = recent['High'].iloc[peak_start:peak_end].max()

                if (peak_high - last_low) / last_low > 0.05:  # At least 5% rise
                    patterns.append(Pattern(
                        pattern_type=PatternType.DOUBLE_BOTTOM,
                        confidence=0.75,
                        signal="bullish",
                        description="Double bottom pattern - bullish reversal",
                        validity_periods=10,
                        entry_point=peak_high * 1.01,
                        stop_loss=last_low * 0.98,
                        take_profit=peak_high + (peak_high - last_low) * 0.8
                    ))

        # Triangle Patterns (simplified detection)
        if len(recent) >= 20:
            # Check for converging trend lines
            high_trend = np.polyfit(range(len(recent)), recent['High'], 1)[0]
            low_trend = np.polyfit(range(len(recent)), recent['Low'], 1)[0]

            # Ascending Triangle (flat top, rising bottom)
            if abs(high_trend) < 0.001 and low_trend > 0.001:
                patterns.append(Pattern(
                    pattern_type=PatternType.ASCENDING_TRIANGLE,
                    confidence=0.7,
                    signal="bullish",
                    description="Ascending triangle - bullish continuation",
                    validity_periods=15
                ))

            # Descending Triangle (flat bottom, falling top)
            elif high_trend < -0.001 and abs(low_trend) < 0.001:
                patterns.append(Pattern(
                    pattern_type=PatternType.DESCENDING_TRIANGLE,
                    confidence=0.7,
                    signal="bearish",
                    description="Descending triangle - bearish continuation",
                    validity_periods=15
                ))

            # Symmetrical Triangle (converging lines)
            elif high_trend < -0.001 and low_trend > 0.001:
                patterns.append(Pattern(
                    pattern_type=PatternType.SYMMETRICAL_TRIANGLE,
                    confidence=0.65,
                    signal="neutral",
                    description="Symmetrical triangle - breakout pending",
                    validity_periods=10
                ))

        # Breakout/Breakdown Detection
        if len(recent) >= 30:
            resistance = recent['High'].iloc[-30:-1].max()
            support = recent['Low'].iloc[-30:-1].min()
            current_price = recent['Close'].iloc[-1]
            current_volume = recent['Volume'].iloc[-1]
            avg_volume = recent['Volume'].iloc[-30:-1].mean()

            # Breakout above resistance
            if current_price > resistance * 1.02 and current_volume > avg_volume * 1.5:
                patterns.append(Pattern(
                    pattern_type=PatternType.BREAKOUT,
                    confidence=0.8,
                    signal="bullish",
                    description=f"Breakout above resistance at {resistance:.2f}",
                    validity_periods=5,
                    entry_point=current_price,
                    stop_loss=resistance * 0.98,
                    take_profit=current_price + (current_price - support) * 0.5
                ))

            # Breakdown below support
            elif current_price < support * 0.98 and current_volume > avg_volume * 1.5:
                patterns.append(Pattern(
                    pattern_type=PatternType.BREAKDOWN,
                    confidence=0.8,
                    signal="bearish",
                    description=f"Breakdown below support at {support:.2f}",
                    validity_periods=5,
                    entry_point=current_price,
                    stop_loss=support * 1.02,
                    take_profit=current_price - (resistance - current_price) * 0.5
                ))

        return patterns

    def _detect_ma_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect moving average crossover patterns."""
        patterns = []

        # Check if we have the required moving averages
        if 'SMA_50' not in df.columns or 'SMA_200' not in df.columns:
            return patterns

        if len(df) < 2:
            return patterns

        # Get current and previous values
        curr_50 = df['SMA_50'].iloc[-1]
        curr_200 = df['SMA_200'].iloc[-1]
        prev_50 = df['SMA_50'].iloc[-2]
        prev_200 = df['SMA_200'].iloc[-2]

        # Check for NaN values
        if pd.isna(curr_50) or pd.isna(curr_200) or pd.isna(prev_50) or pd.isna(prev_200):
            return patterns

        # Golden Cross (50 crosses above 200)
        if prev_50 <= prev_200 and curr_50 > curr_200:
            patterns.append(Pattern(
                pattern_type=PatternType.GOLDEN_CROSS,
                confidence=0.9,
                signal="bullish",
                description="Golden Cross - 50 SMA crossed above 200 SMA",
                validity_periods=50,
                entry_point=df['Close'].iloc[-1] * 1.01,
                stop_loss=curr_200 * 0.98,
                take_profit=df['Close'].iloc[-1] * 1.15
            ))

        # Death Cross (50 crosses below 200)
        elif prev_50 >= prev_200 and curr_50 < curr_200:
            patterns.append(Pattern(
                pattern_type=PatternType.DEATH_CROSS,
                confidence=0.9,
                signal="bearish",
                description="Death Cross - 50 SMA crossed below 200 SMA",
                validity_periods=50,
                entry_point=df['Close'].iloc[-1] * 0.99,
                stop_loss=curr_200 * 1.02,
                take_profit=df['Close'].iloc[-1] * 0.85
            ))

        return patterns

    def _find_peaks(self, data: np.ndarray, order: int = 5) -> List[int]:
        """Find local peaks in data."""
        peaks = []
        for i in range(order, len(data) - order):
            if all(data[i] >= data[i-j] for j in range(1, order+1)):
                if all(data[i] >= data[i+j] for j in range(1, order+1)):
                    peaks.append(i)
        return peaks

    def _find_troughs(self, data: np.ndarray, order: int = 5) -> List[int]:
        """Find local troughs in data."""
        troughs = []
        for i in range(order, len(data) - order):
            if all(data[i] <= data[i-j] for j in range(1, order+1)):
                if all(data[i] <= data[i+j] for j in range(1, order+1)):
                    troughs.append(i)
        return troughs

    def detect_divergences(
        self,
        df: pd.DataFrame,
        indicator_column: str = 'RSI',
        lookback: int = 30
    ) -> List[Dict]:
        """
        Detect divergences between price and an indicator.

        Args:
            df: DataFrame with price and indicator data
            indicator_column: Name of the indicator column
            lookback: Number of periods to look back

        Returns:
            List of divergence signals
        """
        divergences = []

        if indicator_column not in df.columns or len(df) < lookback:
            return divergences

        recent = df.tail(lookback)

        # Find price peaks and troughs
        price_peaks = self._find_peaks(recent['High'].values, order=3)
        price_troughs = self._find_troughs(recent['Low'].values, order=3)

        # Find indicator peaks and troughs
        ind_peaks = self._find_peaks(recent[indicator_column].values, order=3)
        ind_troughs = self._find_troughs(recent[indicator_column].values, order=3)

        # Check for bullish divergence (price makes lower low, indicator makes higher low)
        if len(price_troughs) >= 2 and len(ind_troughs) >= 2:
            if (recent['Low'].iloc[price_troughs[-1]] < recent['Low'].iloc[price_troughs[-2]] and
                recent[indicator_column].iloc[ind_troughs[-1]] > recent[indicator_column].iloc[ind_troughs[-2]]):
                divergences.append({
                    'type': 'bullish_divergence',
                    'indicator': indicator_column,
                    'confidence': 0.75,
                    'description': f'Bullish divergence detected on {indicator_column}'
                })

        # Check for bearish divergence (price makes higher high, indicator makes lower high)
        if len(price_peaks) >= 2 and len(ind_peaks) >= 2:
            if (recent['High'].iloc[price_peaks[-1]] > recent['High'].iloc[price_peaks[-2]] and
                recent[indicator_column].iloc[ind_peaks[-1]] < recent[indicator_column].iloc[ind_peaks[-2]]):
                divergences.append({
                    'type': 'bearish_divergence',
                    'indicator': indicator_column,
                    'confidence': 0.75,
                    'description': f'Bearish divergence detected on {indicator_column}'
                })

        return divergences


# Global instance
pattern_service = PatternRecognitionService()