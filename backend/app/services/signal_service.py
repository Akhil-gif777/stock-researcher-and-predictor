"""Advanced signal generation service with weighted scoring and pattern recognition."""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum


class SignalType(Enum):
    """Signal types for trading decisions."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class TimeframeValidity:
    """Signal validity periods for different timeframes."""
    VALIDITY_PERIODS = {
        "1hour": timedelta(hours=4),
        "4hour": timedelta(days=1),
        "daily": timedelta(days=5),
        "weekly": timedelta(weeks=2),
        "monthly": timedelta(weeks=8)
    }


class SignalService:
    """Service for generating and managing trading signals."""

    # Default indicator weights (can be customized by user)
    DEFAULT_WEIGHTS = {
        # Trend indicators
        "macd": 0.25,
        "moving_average_crossover": 0.15,
        "adx": 0.15,
        # Momentum indicators
        "rsi": 0.20,
        "stochastic": 0.15,
        # Volume indicators
        "volume": 0.15,
        "obv": 0.10,
        # Support/Resistance
        "support_resistance": 0.15,
        "pivot_points": 0.10,
        # Patterns (bonus weights)
        "candlestick_pattern": 0.10,
        "chart_pattern": 0.15,
        # Special signals
        "divergence": 0.12,
        "ichimoku": 0.20,
        "fibonacci": 0.10
    }

    # Signal strength thresholds
    SIGNAL_THRESHOLDS = {
        "strong_buy": 0.70,
        "buy": 0.55,
        "neutral_high": 0.54,
        "neutral_low": 0.46,
        "sell": 0.45,
        "strong_sell": 0.30
    }

    def __init__(self, custom_weights: Dict[str, float] = None):
        """Initialize with optional custom weights."""
        self.weights = custom_weights if custom_weights else self.DEFAULT_WEIGHTS.copy()

    def generate_signals(
        self,
        indicators: Dict,
        timeframe: str = "daily",
        selected_indicators: List[str] = None
    ) -> Dict:
        """
        Generate weighted trading signals from indicators.

        Args:
            indicators: Dict of current indicator values
            timeframe: Timeframe for signal validity
            selected_indicators: List of indicators to use (None = use all)

        Returns:
            Dict containing signal analysis
        """
        # Calculate individual signals
        signals = self._calculate_individual_signals(indicators, selected_indicators)

        # Apply market condition adjustments (ADX-based)
        signals = self._apply_market_conditions(signals, indicators)

        # Check for divergences
        divergence_signals = self._detect_divergences(indicators)
        if divergence_signals:
            signals.update(divergence_signals)

        # Check for pattern signals
        pattern_signals = self._detect_patterns(indicators)
        if pattern_signals:
            signals.update(pattern_signals)

        # Calculate weighted score
        weighted_score, signal_details = self._calculate_weighted_score(signals, selected_indicators)

        # Apply confluence bonus
        confluence_bonus = self._calculate_confluence_bonus(signals)
        final_score = min(1.0, weighted_score + confluence_bonus)

        # Determine signal type
        signal_type = self._determine_signal_type(final_score)

        # Calculate signal validity
        valid_until = datetime.now() + TimeframeValidity.VALIDITY_PERIODS.get(
            timeframe, timedelta(days=3)
        )

        return {
            "signal_type": signal_type.value,
            "confidence": final_score,
            "weighted_score": weighted_score,
            "confluence_bonus": confluence_bonus,
            "signal_details": signal_details,
            "timeframe": timeframe,
            "valid_until": valid_until.isoformat(),
            "key_signals": self._get_key_signals(signals),
            "market_condition": self._get_market_condition(indicators),
            "entry_zones": self._calculate_entry_zones(indicators, signal_type),
            "risk_reward": self._calculate_risk_reward(indicators, signal_type)
        }

    def _calculate_individual_signals(
        self,
        indicators: Dict,
        selected_indicators: List[str] = None
    ) -> Dict[str, Dict]:
        """Calculate signals from individual indicators."""
        signals = {}

        # If no specific indicators selected, use all available
        if selected_indicators is None:
            selected_indicators = list(self.weights.keys())

        # MACD Signal
        if "macd" in selected_indicators and "macd_histogram" in indicators:
            macd_hist = indicators.get("macd_histogram", 0)
            macd_strength = min(1.0, abs(macd_hist) / 2.0)  # Normalize
            signals["macd"] = {
                "signal": "bullish" if macd_hist > 0 else "bearish",
                "strength": macd_strength,
                "value": macd_hist
            }

        # RSI Signal
        if "rsi" in selected_indicators and "rsi" in indicators:
            rsi = indicators.get("rsi", 50)
            if rsi < 30:
                signals["rsi"] = {"signal": "oversold", "strength": (30 - rsi) / 30, "value": rsi}
            elif rsi > 70:
                signals["rsi"] = {"signal": "overbought", "strength": (rsi - 70) / 30, "value": rsi}
            else:
                signals["rsi"] = {"signal": "neutral", "strength": 0.5, "value": rsi}

        # ADX Signal (trend strength)
        if "adx" in selected_indicators and "adx" in indicators:
            adx = indicators.get("adx", 0)
            di_plus = indicators.get("di_plus", 0)
            di_minus = indicators.get("di_minus", 0)

            if adx > 25:  # Trending market
                if di_plus > di_minus:
                    signals["adx"] = {"signal": "strong_trend_up", "strength": min(1.0, adx / 50), "value": adx}
                else:
                    signals["adx"] = {"signal": "strong_trend_down", "strength": min(1.0, adx / 50), "value": adx}
            else:
                signals["adx"] = {"signal": "ranging", "strength": 0.3, "value": adx}

        # Stochastic Signal
        if "stochastic" in selected_indicators and "stoch_k" in indicators:
            stoch_k = indicators.get("stoch_k", 50)
            stoch_d = indicators.get("stoch_d", 50)

            if stoch_k < 20:
                signals["stochastic"] = {"signal": "oversold", "strength": (20 - stoch_k) / 20, "value": stoch_k}
            elif stoch_k > 80:
                signals["stochastic"] = {"signal": "overbought", "strength": (stoch_k - 80) / 20, "value": stoch_k}
            else:
                # Check for crossover
                if stoch_k > stoch_d:
                    signals["stochastic"] = {"signal": "bullish_cross", "strength": 0.6, "value": stoch_k}
                else:
                    signals["stochastic"] = {"signal": "bearish_cross", "strength": 0.4, "value": stoch_k}

        # Moving Average Crossover
        if "moving_average_crossover" in selected_indicators:
            sma_20 = indicators.get("sma_20", 0)
            sma_50 = indicators.get("sma_50", 0)
            sma_200 = indicators.get("sma_200", 0)
            price = indicators.get("price", 0)

            # Golden/Death Cross
            if sma_50 > 0 and sma_200 > 0:
                cross_ratio = sma_50 / sma_200 if sma_200 > 0 else 1
                if cross_ratio > 1.02:  # Golden cross
                    signals["moving_average_crossover"] = {
                        "signal": "golden_cross",
                        "strength": min(1.0, (cross_ratio - 1) * 10),
                        "value": cross_ratio
                    }
                elif cross_ratio < 0.98:  # Death cross
                    signals["moving_average_crossover"] = {
                        "signal": "death_cross",
                        "strength": min(1.0, (1 - cross_ratio) * 10),
                        "value": cross_ratio
                    }
                else:
                    # Check price vs MAs
                    if price > sma_20 > sma_50 > sma_200:
                        signals["moving_average_crossover"] = {
                            "signal": "strong_uptrend",
                            "strength": 0.8,
                            "value": cross_ratio
                        }
                    elif price < sma_20 < sma_50 < sma_200:
                        signals["moving_average_crossover"] = {
                            "signal": "strong_downtrend",
                            "strength": 0.8,
                            "value": cross_ratio
                        }

        # Volume Signal
        if "volume" in selected_indicators and "volume" in indicators:
            volume = indicators.get("volume", 0)
            volume_avg = indicators.get("volume_avg", volume)

            if volume_avg > 0:
                volume_ratio = volume / volume_avg
                if volume_ratio > 1.5:
                    signals["volume"] = {"signal": "high_volume", "strength": min(1.0, volume_ratio / 2), "value": volume_ratio}
                elif volume_ratio < 0.5:
                    signals["volume"] = {"signal": "low_volume", "strength": 0.3, "value": volume_ratio}
                else:
                    signals["volume"] = {"signal": "normal_volume", "strength": 0.5, "value": volume_ratio}

        # Support/Resistance Signal
        if "support_resistance" in selected_indicators:
            price = indicators.get("price", 0)
            support = indicators.get("support", 0)
            resistance = indicators.get("resistance", 0)

            if support > 0 and resistance > 0:
                position = (price - support) / (resistance - support) if resistance > support else 0.5

                if position < 0.2:  # Near support
                    signals["support_resistance"] = {"signal": "near_support", "strength": 0.7, "value": position}
                elif position > 0.8:  # Near resistance
                    signals["support_resistance"] = {"signal": "near_resistance", "strength": 0.7, "value": position}
                else:
                    signals["support_resistance"] = {"signal": "mid_range", "strength": 0.4, "value": position}

        # Pivot Points Signal
        if "pivot_points" in selected_indicators and "pivot" in indicators:
            price = indicators.get("price", 0)
            pivot = indicators.get("pivot", 0)
            r1 = indicators.get("resistance1", 0)
            s1 = indicators.get("support1", 0)

            if pivot > 0:
                if price > r1:
                    signals["pivot_points"] = {"signal": "above_r1", "strength": 0.8, "value": price/pivot}
                elif price > pivot:
                    signals["pivot_points"] = {"signal": "above_pivot", "strength": 0.6, "value": price/pivot}
                elif price > s1:
                    signals["pivot_points"] = {"signal": "below_pivot", "strength": 0.4, "value": price/pivot}
                else:
                    signals["pivot_points"] = {"signal": "below_s1", "strength": 0.2, "value": price/pivot}

        # Ichimoku Signal
        if "ichimoku" in selected_indicators and "ichimoku_spana" in indicators:
            price = indicators.get("price", 0)
            span_a = indicators.get("ichimoku_spana", 0)
            span_b = indicators.get("ichimoku_spanb", 0)
            base = indicators.get("ichimoku_base", 0)
            conversion = indicators.get("ichimoku_conversion", 0)

            if span_a > 0 and span_b > 0:
                # Price above/below cloud
                cloud_top = max(span_a, span_b)
                cloud_bottom = min(span_a, span_b)

                if price > cloud_top:
                    signals["ichimoku"] = {"signal": "above_cloud", "strength": 0.8, "value": price/cloud_top}
                elif price < cloud_bottom:
                    signals["ichimoku"] = {"signal": "below_cloud", "strength": 0.2, "value": price/cloud_bottom}
                else:
                    signals["ichimoku"] = {"signal": "in_cloud", "strength": 0.5, "value": price/cloud_top}

        return signals

    def _apply_market_conditions(self, signals: Dict, indicators: Dict) -> Dict:
        """Adjust signal weights based on market conditions (ADX)."""
        adx = indicators.get("adx", 20)

        # Determine market condition
        if adx > 25:  # Trending market
            trend_multiplier = 1.2
            oscillator_multiplier = 0.8
        else:  # Ranging market
            trend_multiplier = 0.8
            oscillator_multiplier = 1.2

        # Apply multipliers
        trend_indicators = ["macd", "moving_average_crossover", "ichimoku"]
        oscillator_indicators = ["rsi", "stochastic"]

        for signal_name, signal_data in signals.items():
            if signal_name in trend_indicators:
                signal_data["strength"] *= trend_multiplier
            elif signal_name in oscillator_indicators:
                signal_data["strength"] *= oscillator_multiplier

        return signals

    def _detect_divergences(self, indicators: Dict) -> Dict:
        """Detect divergences between price and indicators."""
        divergences = {}

        # This would require historical data to properly detect
        # For now, we'll return empty (to be implemented with historical data)
        # In a real implementation, you would compare price highs/lows with indicator highs/lows

        return divergences

    def _detect_patterns(self, indicators: Dict) -> Dict:
        """Detect chart and candlestick patterns."""
        patterns = {}

        # Simplified pattern detection based on current indicators
        # Real implementation would require OHLC data analysis

        # Check for potential breakout
        price = indicators.get("price", 0)
        resistance = indicators.get("resistance", 0)
        support = indicators.get("support", 0)
        volume = indicators.get("volume", 0)
        volume_avg = indicators.get("volume_avg", volume)

        if resistance > 0 and price > resistance * 0.98 and volume > volume_avg * 1.5:
            patterns["chart_pattern"] = {
                "signal": "resistance_breakout",
                "strength": 0.8,
                "value": price/resistance
            }
        elif support > 0 and price < support * 1.02 and volume > volume_avg * 1.5:
            patterns["chart_pattern"] = {
                "signal": "support_breakdown",
                "strength": 0.8,
                "value": price/support
            }

        return patterns

    def _calculate_weighted_score(
        self,
        signals: Dict[str, Dict],
        selected_indicators: List[str] = None
    ) -> Tuple[float, Dict]:
        """Calculate weighted score from all signals."""
        total_score = 0
        total_weight = 0
        signal_details = {}

        for signal_name, signal_data in signals.items():
            # Skip if indicator not selected
            if selected_indicators and signal_name not in selected_indicators:
                continue

            weight = self.weights.get(signal_name, 0.1)
            strength = signal_data.get("strength", 0.5)
            signal_type = signal_data.get("signal", "neutral")

            # Convert signal to directional score (0 = bearish, 1 = bullish)
            if signal_type in ["bullish", "oversold", "golden_cross", "above_cloud",
                              "strong_trend_up", "bullish_cross", "near_support",
                              "above_pivot", "above_r1", "strong_uptrend", "resistance_breakout"]:
                directional_score = strength
            elif signal_type in ["bearish", "overbought", "death_cross", "below_cloud",
                                "strong_trend_down", "bearish_cross", "near_resistance",
                                "below_pivot", "below_s1", "strong_downtrend", "support_breakdown"]:
                directional_score = 1 - strength
            else:  # neutral signals
                directional_score = 0.5

            weighted_contribution = weight * directional_score
            total_score += weighted_contribution
            total_weight += weight

            signal_details[signal_name] = {
                "signal": signal_type,
                "strength": strength,
                "weight": weight,
                "contribution": weighted_contribution,
                "value": signal_data.get("value")
            }

        # Normalize score
        final_score = total_score / total_weight if total_weight > 0 else 0.5

        return final_score, signal_details

    def _calculate_confluence_bonus(self, signals: Dict[str, Dict]) -> float:
        """Calculate bonus for signal confluence (agreement)."""
        if len(signals) < 3:
            return 0

        # Count bullish and bearish signals
        bullish_count = 0
        bearish_count = 0

        for signal_data in signals.values():
            signal_type = signal_data.get("signal", "")
            if signal_type in ["bullish", "oversold", "golden_cross", "above_cloud",
                              "strong_trend_up", "bullish_cross", "near_support",
                              "above_pivot", "above_r1", "resistance_breakout"]:
                bullish_count += 1
            elif signal_type in ["bearish", "overbought", "death_cross", "below_cloud",
                                "strong_trend_down", "bearish_cross", "near_resistance",
                                "below_pivot", "below_s1", "support_breakdown"]:
                bearish_count += 1

        total_signals = len(signals)

        # Calculate confluence ratio
        if bullish_count > bearish_count:
            confluence_ratio = bullish_count / total_signals
        else:
            confluence_ratio = bearish_count / total_signals

        # Award bonus for high confluence
        if confluence_ratio > 0.8:
            return 0.15
        elif confluence_ratio > 0.7:
            return 0.10
        elif confluence_ratio > 0.6:
            return 0.05
        else:
            return 0

    def _determine_signal_type(self, score: float) -> SignalType:
        """Determine signal type from score."""
        if score >= self.SIGNAL_THRESHOLDS["strong_buy"]:
            return SignalType.STRONG_BUY
        elif score >= self.SIGNAL_THRESHOLDS["buy"]:
            return SignalType.BUY
        elif score <= self.SIGNAL_THRESHOLDS["strong_sell"]:
            return SignalType.STRONG_SELL
        elif score <= self.SIGNAL_THRESHOLDS["sell"]:
            return SignalType.SELL
        else:
            return SignalType.NEUTRAL

    def _get_key_signals(self, signals: Dict[str, Dict]) -> List[str]:
        """Extract key signals for summary."""
        key_signals = []

        for signal_name, signal_data in signals.items():
            signal_type = signal_data.get("signal", "")
            strength = signal_data.get("strength", 0)

            # Only include strong signals
            if strength > 0.6:
                key_signals.append(f"{signal_name}: {signal_type}")

        return key_signals[:5]  # Return top 5 signals

    def _get_market_condition(self, indicators: Dict) -> str:
        """Determine overall market condition."""
        adx = indicators.get("adx", 20)

        if adx > 40:
            return "Strong Trend"
        elif adx > 25:
            return "Trending"
        elif adx > 20:
            return "Weak Trend"
        else:
            return "Ranging/Choppy"

    def _calculate_entry_zones(
        self,
        indicators: Dict,
        signal_type: SignalType
    ) -> Dict:
        """Calculate optimal entry zones based on signal."""
        price = indicators.get("price", 0)
        atr = indicators.get("atr", 0)
        support = indicators.get("support", price)
        resistance = indicators.get("resistance", price)

        if signal_type in [SignalType.STRONG_BUY, SignalType.BUY]:
            return {
                "optimal_entry": support + (price - support) * 0.2,
                "entry_range": [support, price - atr * 0.5],
                "stop_loss": support - atr * 1.5,
                "take_profit_1": resistance,
                "take_profit_2": resistance + (resistance - support) * 0.5
            }
        elif signal_type in [SignalType.STRONG_SELL, SignalType.SELL]:
            return {
                "optimal_entry": resistance - (resistance - price) * 0.2,
                "entry_range": [price + atr * 0.5, resistance],
                "stop_loss": resistance + atr * 1.5,
                "take_profit_1": support,
                "take_profit_2": support - (resistance - support) * 0.5
            }
        else:
            return {
                "optimal_entry": price,
                "entry_range": [price - atr * 0.5, price + atr * 0.5],
                "stop_loss": None,
                "take_profit_1": None,
                "take_profit_2": None
            }

    def _calculate_risk_reward(
        self,
        indicators: Dict,
        signal_type: SignalType
    ) -> Dict:
        """Calculate risk/reward ratio."""
        entry_zones = self._calculate_entry_zones(indicators, signal_type)

        if entry_zones["stop_loss"] and entry_zones["take_profit_1"]:
            entry = entry_zones["optimal_entry"]
            stop_loss = entry_zones["stop_loss"]
            take_profit = entry_zones["take_profit_1"]

            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)

            ratio = reward / risk if risk > 0 else 0

            return {
                "risk_amount": risk,
                "reward_amount": reward,
                "risk_reward_ratio": round(ratio, 2),
                "favorable": ratio >= 2.0
            }

        return {
            "risk_amount": 0,
            "reward_amount": 0,
            "risk_reward_ratio": 0,
            "favorable": False
        }


# Global instance
signal_service = SignalService()