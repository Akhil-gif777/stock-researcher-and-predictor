"""Pydantic models for API requests and responses."""
from typing import List, Optional, Dict
from pydantic import BaseModel
from enum import Enum


class InvestmentStyle(str, Enum):
    """User investment style preferences."""
    CONSERVATIVE = "conservative"  # Long-term, fundamental-focused
    BALANCED = "balanced"  # Even weighting
    AGGRESSIVE = "aggressive"  # Technical/momentum-focused


class StockRequest(BaseModel):
    """Request model for stock analysis."""
    symbol: str
    investment_style: Optional[InvestmentStyle] = InvestmentStyle.BALANCED


class Source(BaseModel):
    """Source citation model."""
    type: str  # "news", "filing", "data"
    title: str
    url: str
    timestamp: Optional[str] = None


class TechnicalIndicators(BaseModel):
    """All technical indicator values with interpretations."""
    price: float
    sma_20: float
    sma_50: float
    sma_200: float
    ema_12: float
    ema_26: float
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    volume: int
    volume_avg: int
    atr: float
    support: Optional[float] = None
    resistance: Optional[float] = None


class MacroIndicators(BaseModel):
    """Macroeconomic indicators."""
    vix: Optional[float] = None
    fed_rate: Optional[float] = None
    gdp_growth: Optional[float] = None
    inflation_cpi: Optional[float] = None
    unemployment: Optional[float] = None


class Recommendation(BaseModel):
    """Single recommendation with full details."""
    type: str  # "AI" or "USER"
    action: str  # "BUY", "HOLD", "SELL"
    confidence: float
    horizon: str  # e.g., "2-8 weeks" or "2-5 years"
    key_reasons: List[str]
    reasoning: str
    macro_impact: str  # How macro factors influenced this recommendation
    agent_weights: Dict[str, float]  # {"technical": 0.5, "fundamental": 0.3, "sentiment": 0.2, "macro": 0.1}
    technical_signals: Dict[str, str]  # Indicator interpretations
    entry_price: Optional[float] = None
    target_prices: Optional[List[float]] = None
    stop_loss: Optional[float] = None
    entry_price_strategy: Optional[str] = None
    reassessment_timeline: Optional[str] = None
    target_strategy: Optional[str] = None


class StockAnalysisResult(BaseModel):
    """Complete stock analysis result with dual recommendations."""
    symbol: str
    current_price: float
    research_summary: str
    technical_analysis: str
    sentiment_analysis: str
    sentiment_aspects: Optional[Dict[str, float]] = None  # Aspect-based sentiment scores
    sentiment_trend: Optional[str] = None  # "improving", "declining", "stable"
    sentiment_confidence: Optional[float] = None  # Confidence in sentiment analysis (0.0-1.0)

    # Finnhub pre-computed sentiment data
    finnhub_sentiment_score: Optional[float] = None  # Finnhub company news score (0.0-1.0)
    finnhub_bullish_percent: Optional[float] = None  # Percentage of bullish articles
    finnhub_bearish_percent: Optional[float] = None  # Percentage of bearish articles
    finnhub_buzz: Optional[float] = None  # Article volume buzz score
    finnhub_articles_count: Optional[int] = None  # Number of articles in last week

    macro_summary: str

    # Dual recommendations
    ai_recommendation: Recommendation  # AI's unbiased analysis
    user_recommendation: Recommendation  # Personalized to user style
    comparison_insight: str  # How they differ

    sources: List[Source]
    technical_indicators: TechnicalIndicators
    macro_indicators: MacroIndicators
    chart_data: Dict  # OHLCV + all indicators for charting


class AgentUpdate(BaseModel):
    """WebSocket update for agent progress."""
    agent: str  # "research", "technical", "sentiment", "decision"
    status: str  # "started", "in_progress", "completed", "failed"
    message: Optional[str] = None
    data: Optional[Dict] = None

