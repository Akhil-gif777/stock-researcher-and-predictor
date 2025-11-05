"""Stock data service using yfinance and technical indicators."""
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import aiohttp
import asyncio
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
import numpy as np
from concurrent.futures import ThreadPoolExecutor


class StockDataService:
    """Service for fetching stock data and calculating technical indicators."""

    # Timeframe configurations
    TIMEFRAME_CONFIGS = {
        "1hour": {
            "period": "60d",
            "interval": "1h",
            "description": "Intraday (last 60 days)",
            "trader_type": "Day Trader",
            "signal_validity": "2-8 hours"
        },
        "4hour": {
            # 4h not supported by yfinance, we'll aggregate 1h data
            "period": "60d",
            "interval": "1h",
            "aggregate_to": "4h",
            "description": "Short-term (last 60 days)",
            "trader_type": "Day/Swing Trader",
            "signal_validity": "1-3 days"
        },
        "daily": {
            "period": "2y",
            "interval": "1d",
            "description": "Medium-term (last 2 years)",
            "trader_type": "Swing Trader",
            "signal_validity": "3-10 days"
        },
        "weekly": {
            "period": "5y",
            "interval": "1wk",
            "description": "Long-term (last 5 years)",
            "trader_type": "Position Trader",
            "signal_validity": "2-4 weeks"
        },
        "monthly": {
            "period": "max",
            "interval": "1mo",
            "description": "Very long-term (all available)",
            "trader_type": "Investor",
            "signal_validity": "1-3 months"
        }
    }

    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(minutes=5)
        self.executor = ThreadPoolExecutor(max_workers=5)  # For parallel fetching
    
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
    
    def get_multi_timeframe_data(
        self,
        symbol: str,
        timeframes: List[str] = None
    ) -> Dict[str, Dict]:
        """
        Fetch data for multiple timeframes with indicators.

        Args:
            symbol: Stock ticker symbol
            timeframes: List of timeframe names to fetch.
                       If None, uses ['daily', 'weekly', 'monthly']

        Returns:
            Dict mapping timeframe name to data dict containing:
                - df: DataFrame with OHLCV and indicators
                - indicators: Current indicator values
                - config: Timeframe configuration
        """
        if timeframes is None:
            timeframes = ['daily', 'weekly', 'monthly']

        results = {}

        # Parallel fetching for better performance
        futures = []
        with ThreadPoolExecutor(max_workers=len(timeframes)) as executor:
            for tf_name in timeframes:
                if tf_name not in self.TIMEFRAME_CONFIGS:
                    continue

                config = self.TIMEFRAME_CONFIGS[tf_name]
                future = executor.submit(
                    self._fetch_timeframe_data,
                    symbol,
                    tf_name,
                    config
                )
                futures.append((tf_name, future, config))

            # Collect results
            for tf_name, future, config in futures:
                try:
                    df, indicators = future.result(timeout=30)
                    results[tf_name] = {
                        'df': df,
                        'indicators': indicators,
                        'config': config
                    }
                except Exception as e:
                    print(f"Error fetching {tf_name} data for {symbol}: {e}")
                    results[tf_name] = {
                        'df': pd.DataFrame(),
                        'indicators': {},
                        'config': config,
                        'error': str(e)
                    }

        return results

    def _fetch_timeframe_data(
        self,
        symbol: str,
        timeframe_name: str,
        config: Dict
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Fetch data for a specific timeframe.

        Args:
            symbol: Stock ticker symbol
            timeframe_name: Name of the timeframe
            config: Timeframe configuration dict

        Returns:
            Tuple of (DataFrame with indicators, current indicator values)
        """
        # Check cache
        cache_key = f"{symbol}_{timeframe_name}_{config['period']}_{config['interval']}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data

        # Fetch data from yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=config['period'], interval=config['interval'])

        if df.empty:
            return pd.DataFrame(), {}

        # Handle 4-hour aggregation if needed
        if config.get('aggregate_to') == '4h':
            df = self._aggregate_to_4h(df)

        # Calculate indicators appropriate for the timeframe
        df = self._calculate_timeframe_indicators(df, timeframe_name)

        # Extract current values
        current_indicators = self._extract_current_indicators(df, ticker)

        # Cache the result
        self.cache[cache_key] = (datetime.now(), (df, current_indicators))

        return df, current_indicators

    def _aggregate_to_4h(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate 1-hour data to 4-hour bars."""
        return df.resample('4h').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

    def _calculate_timeframe_indicators(
        self,
        df: pd.DataFrame,
        timeframe_name: str
    ) -> pd.DataFrame:
        """
        Calculate indicators appropriate for the specific timeframe.

        Args:
            df: DataFrame with OHLCV data
            timeframe_name: Name of the timeframe

        Returns:
            DataFrame with calculated indicators
        """
        # Always calculate basic indicators
        df = self._calculate_indicators(df)

        # Add advanced indicators
        df = self._calculate_advanced_indicators(df, timeframe_name)

        return df

    def _calculate_advanced_indicators(
        self,
        df: pd.DataFrame,
        timeframe_name: str
    ) -> pd.DataFrame:
        """
        Calculate advanced technical indicators.

        Args:
            df: DataFrame with OHLCV data
            timeframe_name: Name of the timeframe

        Returns:
            DataFrame with additional indicators
        """
        # ADX - Average Directional Index (trend strength)
        try:
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None and not adx.empty:
                df['ADX'] = adx['ADX_14']
                df['DI_plus'] = adx['DMP_14']
                df['DI_minus'] = adx['DMN_14']
        except:
            df['ADX'] = np.nan
            df['DI_plus'] = np.nan
            df['DI_minus'] = np.nan

        # Stochastic Oscillator
        try:
            stoch = ta.stoch(df['High'], df['Low'], df['Close'])
            if stoch is not None and not stoch.empty:
                df['Stoch_K'] = stoch['STOCHk_14_3_3']
                df['Stoch_D'] = stoch['STOCHd_14_3_3']
        except:
            df['Stoch_K'] = np.nan
            df['Stoch_D'] = np.nan

        # VWAP (only for intraday timeframes)
        if timeframe_name in ['1hour', '4hour']:
            try:
                df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
            except:
                df['VWAP'] = np.nan

        # Ichimoku Cloud (for all timeframes)
        try:
            ichimoku = ta.ichimoku(df['High'], df['Low'], df['Close'])
            if ichimoku is not None and not ichimoku.empty:
                # ichimoku returns a tuple of DataFrames
                if isinstance(ichimoku, tuple):
                    ichi_df = ichimoku[0]
                else:
                    ichi_df = ichimoku

                # Extract Ichimoku components
                for col in ichi_df.columns:
                    if 'ISA' in col:  # Senkou Span A (Leading Span A)
                        df['Ichimoku_SpanA'] = ichi_df[col]
                    elif 'ISB' in col:  # Senkou Span B (Leading Span B)
                        df['Ichimoku_SpanB'] = ichi_df[col]
                    elif 'IKS' in col:  # Kijun-sen (Base Line)
                        df['Ichimoku_Base'] = ichi_df[col]
                    elif 'ITS' in col:  # Tenkan-sen (Conversion Line)
                        df['Ichimoku_Conversion'] = ichi_df[col]
        except:
            df['Ichimoku_SpanA'] = np.nan
            df['Ichimoku_SpanB'] = np.nan
            df['Ichimoku_Base'] = np.nan
            df['Ichimoku_Conversion'] = np.nan

        # Pivot Points (useful for all timeframes)
        try:
            # Calculate pivot points using previous period's data
            if len(df) > 1:
                prev_high = df['High'].shift(1)
                prev_low = df['Low'].shift(1)
                prev_close = df['Close'].shift(1)

                df['Pivot'] = (prev_high + prev_low + prev_close) / 3
                df['Resistance1'] = 2 * df['Pivot'] - prev_low
                df['Support1'] = 2 * df['Pivot'] - prev_high
                df['Resistance2'] = df['Pivot'] + (prev_high - prev_low)
                df['Support2'] = df['Pivot'] - (prev_high - prev_low)
        except:
            df['Pivot'] = np.nan
            df['Resistance1'] = np.nan
            df['Support1'] = np.nan
            df['Resistance2'] = np.nan
            df['Support2'] = np.nan

        # Fibonacci Retracement Levels (calculate for last major swing)
        try:
            if len(df) > 30:
                # Find recent high and low
                recent_data = df['Close'].tail(60) if len(df) > 60 else df['Close']
                recent_high = recent_data.max()
                recent_low = recent_data.min()
                diff = recent_high - recent_low

                # Only add as the latest value (not a series)
                if len(df) > 0:
                    df['Fib_0'] = recent_high
                    df['Fib_236'] = recent_high - 0.236 * diff
                    df['Fib_382'] = recent_high - 0.382 * diff
                    df['Fib_500'] = recent_high - 0.500 * diff
                    df['Fib_618'] = recent_high - 0.618 * diff
                    df['Fib_786'] = recent_high - 0.786 * diff
                    df['Fib_1000'] = recent_low
        except:
            pass  # Fibonacci levels are optional

        return df

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
        if df.empty:
            return {}

        latest = df.iloc[-1]

        # Calculate volume average
        volume_avg = int(df['Volume'].tail(20).mean()) if len(df) >= 20 else int(latest['Volume'])

        # Simple support/resistance calculation
        recent_prices = df['Close'].tail(30)
        support = float(recent_prices.min())
        resistance = float(recent_prices.max())

        indicators = {
            'price': float(latest['Close']),
            'sma_20': float(latest['SMA_20']) if pd.notna(latest.get('SMA_20')) else 0.0,
            'sma_50': float(latest['SMA_50']) if pd.notna(latest.get('SMA_50')) else 0.0,
            'sma_200': float(latest['SMA_200']) if pd.notna(latest.get('SMA_200')) else 0.0,
            'ema_12': float(latest['EMA_12']) if pd.notna(latest.get('EMA_12')) else 0.0,
            'ema_26': float(latest['EMA_26']) if pd.notna(latest.get('EMA_26')) else 0.0,
            'rsi': float(latest['RSI']) if pd.notna(latest.get('RSI')) else 50.0,
            'macd': float(latest['MACD']) if pd.notna(latest.get('MACD')) else 0.0,
            'macd_signal': float(latest['MACD_signal']) if pd.notna(latest.get('MACD_signal')) else 0.0,
            'macd_histogram': float(latest['MACD_hist']) if pd.notna(latest.get('MACD_hist')) else 0.0,
            'bb_upper': float(latest['BB_upper']) if pd.notna(latest.get('BB_upper')) else 0.0,
            'bb_middle': float(latest['BB_middle']) if pd.notna(latest.get('BB_middle')) else 0.0,
            'bb_lower': float(latest['BB_lower']) if pd.notna(latest.get('BB_lower')) else 0.0,
            'volume': int(latest['Volume']),
            'volume_avg': volume_avg,
            'atr': float(latest['ATR']) if pd.notna(latest.get('ATR')) else 0.0,
            'support': support,
            'resistance': resistance,
            # Advanced indicators
            'adx': float(latest['ADX']) if pd.notna(latest.get('ADX')) else 0.0,
            'di_plus': float(latest['DI_plus']) if pd.notna(latest.get('DI_plus')) else 0.0,
            'di_minus': float(latest['DI_minus']) if pd.notna(latest.get('DI_minus')) else 0.0,
            'stoch_k': float(latest['Stoch_K']) if pd.notna(latest.get('Stoch_K')) else 50.0,
            'stoch_d': float(latest['Stoch_D']) if pd.notna(latest.get('Stoch_D')) else 50.0,
            'obv': float(latest['OBV']) if pd.notna(latest.get('OBV')) else 0.0,
            # Pivot points
            'pivot': float(latest['Pivot']) if pd.notna(latest.get('Pivot')) else 0.0,
            'resistance1': float(latest['Resistance1']) if pd.notna(latest.get('Resistance1')) else 0.0,
            'support1': float(latest['Support1']) if pd.notna(latest.get('Support1')) else 0.0,
            'resistance2': float(latest['Resistance2']) if pd.notna(latest.get('Resistance2')) else 0.0,
            'support2': float(latest['Support2']) if pd.notna(latest.get('Support2')) else 0.0,
        }

        # Add optional indicators if they exist
        if 'VWAP' in df.columns:
            indicators['vwap'] = float(latest['VWAP']) if pd.notna(latest['VWAP']) else 0.0

        # Ichimoku indicators
        if 'Ichimoku_SpanA' in df.columns:
            indicators['ichimoku_spana'] = float(latest['Ichimoku_SpanA']) if pd.notna(latest['Ichimoku_SpanA']) else 0.0
            indicators['ichimoku_spanb'] = float(latest['Ichimoku_SpanB']) if pd.notna(latest['Ichimoku_SpanB']) else 0.0
            indicators['ichimoku_base'] = float(latest['Ichimoku_Base']) if pd.notna(latest['Ichimoku_Base']) else 0.0
            indicators['ichimoku_conversion'] = float(latest['Ichimoku_Conversion']) if pd.notna(latest['Ichimoku_Conversion']) else 0.0

        # Fibonacci levels
        if 'Fib_236' in df.columns:
            indicators['fib_236'] = float(latest['Fib_236']) if pd.notna(latest['Fib_236']) else 0.0
            indicators['fib_382'] = float(latest['Fib_382']) if pd.notna(latest['Fib_382']) else 0.0
            indicators['fib_500'] = float(latest['Fib_500']) if pd.notna(latest['Fib_500']) else 0.0
            indicators['fib_618'] = float(latest['Fib_618']) if pd.notna(latest['Fib_618']) else 0.0
            indicators['fib_786'] = float(latest['Fib_786']) if pd.notna(latest['Fib_786']) else 0.0

        return indicators
    
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
    
    async def get_company_info_async(self, symbol: str, session: aiohttp.ClientSession) -> Dict:
        """
        Async version of get_company_info using aiohttp.
        Maintains the same return format as the sync version.
        """
        # For now, we'll use the sync version in a thread to maintain compatibility
        # In a full async implementation, you'd replace yfinance calls with direct API calls
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_company_info, symbol)
    
    async def get_stock_data_async(self, symbol: str, session: aiohttp.ClientSession, period: str = "90d") -> Tuple[pd.DataFrame, Dict]:
        """
        Async version of get_stock_data using aiohttp.
        Maintains the same return format as the sync version.
        """
        # For now, we'll use the sync version in a thread to maintain compatibility
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_stock_data, symbol, period)


# Global instance
stock_data_service = StockDataService()

