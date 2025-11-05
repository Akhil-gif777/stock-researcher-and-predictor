// TypeScript types matching backend Pydantic models

export type InvestmentStyle = "conservative" | "balanced" | "aggressive";

export interface Source {
  type: string; // "news", "filing", "data"
  title: string;
  url: string;
  timestamp?: string;
}

export interface TechnicalIndicators {
  price: number;
  sma_20: number;
  sma_50: number;
  sma_200: number;
  ema_12: number;
  ema_26: number;
  rsi: number;
  macd: number;
  macd_signal: number;
  macd_histogram: number;
  bb_upper: number;
  bb_middle: number;
  bb_lower: number;
  volume: number;
  volume_avg: number;
  atr: number;
  support?: number;
  resistance?: number;
  // Advanced indicators
  adx?: number;
  di_plus?: number;
  di_minus?: number;
  stoch_k?: number;
  stoch_d?: number;
  obv?: number;
  pivot?: number;
  resistance1?: number;
  support1?: number;
  resistance2?: number;
  support2?: number;
  vwap?: number;
  ichimoku_spana?: number;
  ichimoku_spanb?: number;
  ichimoku_base?: number;
  ichimoku_conversion?: number;
  fib_236?: number;
  fib_382?: number;
  fib_500?: number;
  fib_618?: number;
  fib_786?: number;
}

// Enhanced Technical Analysis Types
export interface TechnicalConfig {
  timeframes: string[];
  selected_indicators?: string[];
  custom_weights?: Record<string, number>;
}

export interface SignalAnalysis {
  signal_type: string;
  confidence: number;
  weighted_score: number;
  confluence_bonus: number;
  signal_details: Record<string, any>;
  timeframe: string;
  valid_until: string;
  key_signals: string[];
  market_condition: string;
  entry_zones?: {
    optimal_entry?: number;
    entry_range?: number[];
    stop_loss?: number;
    take_profit_1?: number;
    take_profit_2?: number;
  };
  risk_reward?: {
    risk_amount: number;
    reward_amount: number;
    risk_reward_ratio: number;
    favorable: boolean;
  };
}

export interface PatternData {
  patterns: Array<{
    type: string;
    confidence: number;
    signal: string;
    description: string;
  }>;
  divergences: Array<{
    type: string;
    indicator: string;
    confidence: number;
    description: string;
  }>;
}

export interface TimeframeAnalysis {
  indicators: TechnicalIndicators;
  signals: SignalAnalysis;
  patterns: PatternData;
  config: {
    period: string;
    interval: string;
    description: string;
    trader_type: string;
    signal_validity: string;
  };
}

export interface EnhancedTechnicalResult {
  technical_analyses?: Record<string, TimeframeAnalysis>;
  timeframe_alignment?: {
    score: number;
    interpretation: string;
  };
  all_patterns?: Record<string, PatternData>;
  all_signals?: Record<string, SignalAnalysis>;
  technical_analysis?: string;
  recommended_timeframe?: string;
}

export interface MacroIndicators {
  vix?: number;
  fed_rate?: number;
  gdp_growth?: number;
  inflation_cpi?: number;
  unemployment?: number;
}

export interface Recommendation {
  type: string; // "AI" or "USER"
  action: "BUY" | "HOLD" | "SELL";
  confidence: number;
  horizon: string;
  key_reasons: string[];
  reasoning: string;
  macro_impact: string;
  agent_weights: {
    [key: string]: number;
  };
  technical_signals: {
    [key: string]: string;
  };
  entry_price?: number;
  target_prices?: number[];
  stop_loss?: number;
  entry_price_strategy?: string;
  reassessment_timeline?: string;
  target_strategy?: string;
}

export interface SentimentAspects {
  earnings: number;
  guidance: number;
  products: number;
  management: number;
  market: number;
}

export interface StockAnalysisResult {
  symbol: string;
  current_price: number;
  research_summary: string;
  technical_analysis: string;
  sentiment_analysis: string;
  sentiment_aspects?: SentimentAspects;
  sentiment_trend?: "improving" | "declining" | "stable";
  sentiment_confidence?: number;

  // Finnhub pre-computed sentiment data
  finnhub_sentiment_score?: number; // 0.0-1.0
  finnhub_bullish_percent?: number; // 0.0-1.0
  finnhub_bearish_percent?: number; // 0.0-1.0
  finnhub_buzz?: number; // Buzz score
  finnhub_articles_count?: number; // Article count

  macro_summary: string;
  ai_recommendation: Recommendation;
  user_recommendation: Recommendation;
  comparison_insight: string;
  sources: Source[];
  technical_indicators: TechnicalIndicators;
  macro_indicators: MacroIndicators;
  chart_data: {
    [key: string]: any;
  };
}

export interface ChartDataPoint {
  date: string;
  price: number;
  sma20?: number;
  sma50?: number;
  sma200?: number;
  ema12?: number;
  ema26?: number;
  volume?: number;
}

export interface ChartDataResponse {
  symbol: string;
  period: string;
  current_price: number;
  chart_data: ChartDataPoint[];
  indicators: TechnicalIndicators;
}

export interface AgentUpdate {
  agent: string; // "research", "technical", "sentiment", "macro", "decision", "system"
  status: "started" | "in_progress" | "completed" | "failed";
  message?: string;
  data?: StockAnalysisResult;
}

