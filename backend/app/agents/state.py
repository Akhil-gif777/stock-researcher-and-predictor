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
    
    # Sentiment Agent outputs
    news_summary: str
    sentiment_score: float
    news_sources: List[Dict]
    
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

