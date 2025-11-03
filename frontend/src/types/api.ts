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

