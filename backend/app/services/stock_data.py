"""Stock data service using yfinance and technical indicators."""
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta


class StockDataService:
    """Service for fetching stock data and calculating technical indicators."""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(minutes=5)
    
    def get_stock_data(self, symbol: str, period: str = "90d") -> Tuple[pd.DataFrame, Dict]:
        """
        Fetch stock data and calculate all technical indicators.
        
        Args:
            symbol: Stock ticker symbol
            period: Period for historical data (default: 90d)
            
        Returns:
            Tuple of (dataframe with indicators, dict of current indicator values)
        """
        # Check cache
        cache_key = f"{symbol}_{period}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        # Fetch data from yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        
        # Calculate technical indicators
        df = self._calculate_indicators(df)
        
        # Extract current values
        current_indicators = self._extract_current_indicators(df, ticker)
        
        # Cache the result
        self.cache[cache_key] = (datetime.now(), (df, current_indicators))
        
        return df, current_indicators
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        # Trend indicators
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['SMA_50'] = ta.sma(df['Close'], length=50)
        df['SMA_200'] = ta.sma(df['Close'], length=200)
        df['EMA_12'] = ta.ema(df['Close'], length=12)
        df['EMA_26'] = ta.ema(df['Close'], length=26)
        
        # Momentum indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # MACD
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        if macd is not None:
            df['MACD'] = macd['MACD_12_26_9']
            df['MACD_signal'] = macd['MACDs_12_26_9']
            df['MACD_hist'] = macd['MACDh_12_26_9']
        
        # Bollinger Bands
        bbands = ta.bbands(df['Close'], length=20, std=2)
        if bbands is not None and not bbands.empty:
            # pandas_ta can return different column names, so find them dynamically
            bb_cols = bbands.columns.tolist()
            upper_col = next((col for col in bb_cols if 'BBU' in col), None)
            middle_col = next((col for col in bb_cols if 'BBM' in col), None)
            lower_col = next((col for col in bb_cols if 'BBL' in col), None)
            
            if upper_col:
                df['BB_upper'] = bbands[upper_col]
            if middle_col:
                df['BB_middle'] = bbands[middle_col]
            if lower_col:
                df['BB_lower'] = bbands[lower_col]
        
        # Volatility
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        # Volume indicators
        df['Volume_SMA'] = ta.sma(df['Volume'], length=20)
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        return df
    
    def _extract_current_indicators(self, df: pd.DataFrame, ticker) -> Dict:
        """Extract current indicator values and calculate support/resistance."""
        latest = df.iloc[-1]
        
        # Calculate volume average
        volume_avg = int(df['Volume'].tail(20).mean())
        
        # Simple support/resistance calculation
        recent_prices = df['Close'].tail(30)
        support = float(recent_prices.min())
        resistance = float(recent_prices.max())
        
        return {
            'price': float(latest['Close']),
            'sma_20': float(latest['SMA_20']) if pd.notna(latest['SMA_20']) else 0.0,
            'sma_50': float(latest['SMA_50']) if pd.notna(latest['SMA_50']) else 0.0,
            'sma_200': float(latest['SMA_200']) if pd.notna(latest['SMA_200']) else 0.0,
            'ema_12': float(latest['EMA_12']) if pd.notna(latest['EMA_12']) else 0.0,
            'ema_26': float(latest['EMA_26']) if pd.notna(latest['EMA_26']) else 0.0,
            'rsi': float(latest['RSI']) if pd.notna(latest['RSI']) else 50.0,
            'macd': float(latest['MACD']) if pd.notna(latest['MACD']) else 0.0,
            'macd_signal': float(latest['MACD_signal']) if pd.notna(latest['MACD_signal']) else 0.0,
            'macd_histogram': float(latest['MACD_hist']) if pd.notna(latest['MACD_hist']) else 0.0,
            'bb_upper': float(latest['BB_upper']) if pd.notna(latest['BB_upper']) else 0.0,
            'bb_middle': float(latest['BB_middle']) if pd.notna(latest['BB_middle']) else 0.0,
            'bb_lower': float(latest['BB_lower']) if pd.notna(latest['BB_lower']) else 0.0,
            'volume': int(latest['Volume']),
            'volume_avg': volume_avg,
            'atr': float(latest['ATR']) if pd.notna(latest['ATR']) else 0.0,
            'support': support,
            'resistance': resistance,
        }
    
    def get_chart_data(self, df: pd.DataFrame) -> Dict:
        """Convert dataframe to chart-friendly format."""
        chart_data = {
            'timestamps': df.index.strftime('%Y-%m-%d').tolist(),
            'open': df['Open'].tolist(),
            'high': df['High'].tolist(),
            'low': df['Low'].tolist(),
            'close': df['Close'].tolist(),
            'volume': df['Volume'].tolist(),
            'sma_20': df['SMA_20'].fillna(0).tolist(),
            'sma_50': df['SMA_50'].fillna(0).tolist(),
            'sma_200': df['SMA_200'].fillna(0).tolist(),
            'ema_12': df['EMA_12'].fillna(0).tolist(),
            'ema_26': df['EMA_26'].fillna(0).tolist(),
            'rsi': df['RSI'].fillna(50).tolist(),
            'macd': df['MACD'].fillna(0).tolist(),
            'macd_signal': df['MACD_signal'].fillna(0).tolist(),
            'macd_hist': df['MACD_hist'].fillna(0).tolist(),
            'bb_upper': df['BB_upper'].fillna(0).tolist(),
            'bb_middle': df['BB_middle'].fillna(0).tolist(),
            'bb_lower': df['BB_lower'].fillna(0).tolist(),
        }
        return chart_data
    
    def get_company_info(self, symbol: str) -> Dict:
        """Get basic company information."""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'profit_margin': info.get('profitMargins', 0),
            'debt_ratio': info.get('debtToEquity', 0),
            'description': info.get('longBusinessSummary', ''),
        }


# Global instance
stock_data_service = StockDataService()

