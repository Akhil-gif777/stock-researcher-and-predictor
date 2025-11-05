"""Shared state for LangGraph agents."""
from typing import TypedDict, List, Dict, Optional


class AgentState(TypedDict):
    """Shared state that flows through all agents."""
    
    # Input
    symbol: str
    investment_style: str  # "conservative", "balanced", "aggressive"
    
    # Research Agent outputs
    company_info: str
    financial_data: Dict
    research_sources: List[Dict]
    
    # Technical Agent outputs
    technical_signals: Dict
    chart_data: Dict
    technical_indicators: Dict

    # Enhanced Technical Agent outputs (optional - for enhanced version)
    technical_config: Optional[Dict]  # User configuration for technical analysis
    technical_analyses: Optional[Dict]  # Multi-timeframe analyses
    timeframe_alignment: Optional[Dict]  # Alignment score and interpretation
    all_patterns: Optional[Dict]  # Detected patterns across timeframes
    all_signals: Optional[Dict]  # Weighted signals across timeframes
    technical_analysis: Optional[str]  # LLM's comprehensive technical analysis
    recommended_timeframe: Optional[str]  # Best timeframe for the user's style
    
    # Sentiment Agent outputs
    news_summary: str
    sentiment_score: float
    sentiment_aspects: Dict  # Aspect-based sentiment scores (earnings, guidance, products, management, market)
    sentiment_trend: str  # Sentiment trend: "improving", "declining", "stable"
    sentiment_confidence: float  # Confidence in sentiment analysis (0.0-1.0)
    news_sources: List[Dict]

    # Finnhub sentiment data (pre-computed)
    finnhub_sentiment_score: Optional[float]  # Finnhub company news score (0.0-1.0)
    finnhub_bullish_percent: Optional[float]  # Percentage of bullish articles (0.0-1.0)
    finnhub_bearish_percent: Optional[float]  # Percentage of bearish articles (0.0-1.0)
    finnhub_buzz: Optional[float]  # Buzz score (article volume vs weekly average)
    finnhub_articles_count: Optional[int]  # Number of articles in last week
    
    # Macro Agent outputs
    macro_summary: str
    macro_indicators: Dict
    macro_risk_level: str
    
    # Decision Agent outputs - AI recommendation
    ai_recommendation: str  # "BUY", "HOLD", "SELL"
    ai_confidence: float
    ai_horizon: str
    ai_key_reasons: List[str]
    ai_reasoning: str
    ai_macro_impact: str
    ai_weights: Dict[str, float]
    ai_technical_signals: Dict[str, str]
    ai_entry_price: Optional[float]
    ai_targets: Optional[List[float]]
    ai_stop_loss: Optional[float]
    
    # Decision Agent outputs - User personalized recommendation
    user_recommendation: str  # "BUY", "HOLD", "SELL"
    user_confidence: float
    user_horizon: str
    user_key_reasons: List[str]
    user_reasoning: str
    user_macro_impact: str
    user_weights: Dict[str, float]
    user_technical_signals: Dict[str, str]
    user_entry_price: Optional[float]
    user_targets: Optional[List[float]]
    user_stop_loss: Optional[float]
    
    # Comparison
    comparison_insight: str

