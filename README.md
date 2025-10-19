# Stock Research & Prediction Application

A sophisticated multi-agent stock analysis application powered by AI that provides dual recommendations: an unbiased AI analysis and a personalized recommendation based on your investment style.

## 🌟 Features

- **Local AI Models via Ollama**:
  - Llama 3.1 8B - Excellent reasoning and analysis (recommended)
  - Qwen2.5 7B - Strong multilingual support
  - Mixtral 8x7B - Advanced mixture of experts model
  - Code Llama 7B - Specialized for technical analysis
  - All models run locally for privacy and cost efficiency

- **Multi-Agent Analysis System**:
  - Research Agent: Analyzes company fundamentals and financials
  - Technical Agent: Evaluates price patterns and technical indicators
  - Sentiment Agent: Processes news sentiment
  - Decision Agent: Generates dual recommendations with dynamic weighting

- **Dual Recommendations**:
  - **AI's Independent Analysis**: Unbiased, data-driven recommendation
  - **Your Personalized Recommendation**: Tailored to your investment style (Conservative/Balanced/Aggressive)

- **Interactive Features**:
  - Real-time agent progress via WebSocket
  - Interactive stock charts with toggleable technical indicators
  - Comprehensive source citations
  - Detailed technical analysis with 10+ indicators

- **Technical Indicators**:
  - **Trend Indicators**: SMA (20, 50, 200), EMA (12, 26)
  - **Momentum Indicators**: RSI (14), MACD (12, 26, 9) with signal and histogram
  - **Volatility Indicators**: Bollinger Bands (20, 2), ATR (14)
  - **Volume Indicators**: Volume SMA (20), OBV (On-Balance Volume)
  - **Support/Resistance**: Dynamic levels based on recent 30-day price action

## 🏗️ Architecture

### Backend (Python/FastAPI + LangGraph)
- **FastAPI** for REST API and WebSocket endpoints
- **LangGraph** for multi-agent orchestration
- **yfinance** for stock data
- **pandas-ta** for technical indicators
- **Ollama** for local LLM-powered analysis

### Frontend (React + Vite + TypeScript)
- **Vite** for blazing-fast development
- **TailwindCSS** + **Radix UI** for modern, accessible styling
- **Recharts** for interactive stock charting
- **WebSocket** for real-time agent progress updates
- **Framer Motion** for smooth animations
- **Sonner** for toast notifications

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (Python 3.13 recommended)
- **Node.js 20+** and npm
- **uv** (Python package manager) - will be installed automatically if missing
- **Ollama** for local AI models (see [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for installation)

### Installation

#### 1. Clone the repository
```bash
git clone <repository-url>
cd stock-researcher-and-predictor
```

#### 2. Backend Setup

```bash
cd backend

# If uv is not installed, install it:
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env  # Add uv to PATH

# Install dependencies (uv will create a virtual environment automatically)
export PATH="$HOME/.local/bin:$PATH"
uv sync

# Create .env file
touch .env
```

**Configure Ollama** - Edit `backend/.env`:

```env
# Set the default LLM provider to Ollama
DEFAULT_LLM_PROVIDER=ollama-llama3.1

# Ollama configuration (optional, defaults to localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434

# Optional API keys for enhanced data
NEWS_API_KEY=your-news-api-key-here  # For sentiment analysis
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key-here  # For macroeconomic data fallback
```

See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed Ollama installation and model setup.

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### Running the Application

**Option A: Use the Quick Start Script** (Recommended)
```bash
# From project root
./run-dev.sh
```

This will start both backend and frontend in the same terminal with proper configuration.

**Option B: Manual Start**

#### Start Backend (Terminal 1)
```bash
cd backend
export PATH="$HOME/.local/bin:$PATH"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- WebSocket: `ws://localhost:8000/ws/analyze/{symbol}`

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

## 📖 Usage

1. Open `http://localhost:5173` in your browser
2. Enter a stock symbol (e.g., AAPL, TSLA, NVDA)
3. Select your investment style:
   - **Conservative**: Long-term, fundamentals-focused
   - **Balanced**: Moderate risk, balanced approach
   - **Aggressive**: Short-term, technical/momentum-focused
4. Click "Analyze Stock"
5. Watch as agents work in real-time via WebSocket:
   - Research Agent → Analyzes fundamentals
   - Technical Agent → Evaluates price patterns
   - Sentiment Agent → Processes news
   - Macro Agent → Analyzes market conditions
   - Decision Agent → Generates recommendations
6. Review dual recommendations:
   - **AI's independent analysis**: Balanced across all factors
   - **Your personalized recommendation**: Weighted by your style
7. Explore interactive charts and detailed analysis tabs:
   - **Technical**: RSI, MACD, Bollinger Bands, etc.
   - **Fundamental**: Company overview and financials
   - **Macro**: VIX, Fed Rate, GDP, Inflation
   - **Sentiment**: News analysis and headlines
   - **Sources**: All data sources with citations

## 🎯 Investment Styles

### Conservative
- Prioritizes fundamentals (50-60%)
- Longer time horizons (1-5 years)
- Focus on capital preservation
- Lower risk tolerance

### Balanced
- Equal weighting of all factors
- Medium time horizons (3-12 months)
- Balanced risk/reward

### Aggressive
- Prioritizes technicals (50-70%)
- Shorter time horizons (weeks-months)
- Focus on momentum
- Higher risk tolerance

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_LLM_PROVIDER` | Ollama model to use | `ollama-llama3.1` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `NEWS_API_KEY` | News API key for sentiment analysis (optional) | - |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key for macro data fallback (optional) | - |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |

**Available Ollama Models:**
- `ollama-llama3.1` - Llama 3.1 8B (recommended)
- `ollama-qwen2.5` - Qwen2.5 7B
- `ollama-mixtral` - Mixtral 8x7B
- `ollama-codellama` - Code Llama 7B

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## 📊 Technical Indicators Explained

### Trend Indicators
- **SMA (Simple Moving Average)**: Average price over a period
  - SMA(20): Short-term trend
  - SMA(50): Medium-term trend  
  - SMA(200): Long-term trend
- **EMA (Exponential Moving Average)**: Weighted average giving more weight to recent prices
  - EMA(12): Short-term momentum
  - EMA(26): Medium-term momentum

### Momentum Indicators
- **RSI (Relative Strength Index)**: Momentum indicator (0-100)
  - < 30: Oversold (potential buy)
  - > 70: Overbought (potential sell)
- **MACD (Moving Average Convergence Divergence)**: Trend-following momentum indicator
  - MACD Line: EMA(12) - EMA(26)
  - Signal Line: 9-period EMA of MACD
  - Histogram: MACD - Signal Line

### Volatility Indicators
- **Bollinger Bands**: Volatility indicator with 3 lines
  - Upper Band: SMA(20) + 2 standard deviations
  - Middle Band: SMA(20)
  - Lower Band: SMA(20) - 2 standard deviations
- **ATR (Average True Range)**: Volatility measure
  - Higher ATR = Higher volatility

### Volume Indicators
- **Volume SMA**: 20-period average of trading volume
- **OBV (On-Balance Volume)**: Cumulative volume indicator
  - Rising OBV: Buying pressure
  - Falling OBV: Selling pressure

### Support/Resistance
- **Dynamic Levels**: Calculated from recent 30-day price action
  - Support: Lowest price in recent 30-day period
  - Resistance: Highest price in recent 30-day period

## 🛠️ Development

### Backend Development

```bash
cd backend
export PATH="$HOME/.local/bin:$PATH"

# Run with hot reload
uv run fastapi dev app/main.py

# Add new dependencies
uv add <package-name>

# Run tests (once implemented)
uv run pytest
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/analyze` - Synchronous stock analysis
- `WS /ws/analyze/{symbol}` - Real-time streaming analysis
- `GET /api/stock/{symbol}/chart-data` - Chart data with indicators

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgments

- **LangGraph** for multi-agent orchestration
- **yfinance** for stock data
- **FastAPI** for the excellent web framework
- **Vite** for lightning-fast development
- **Ollama** for local AI model hosting
- **pandas-ta** for technical indicators

## 🐛 Troubleshooting

### Backend Issues

**Error: Ollama not running**
- Ensure Ollama service is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Install a model: `ollama pull llama3.1:8b`

**Error: ModuleNotFoundError**
- Ensure you're in the backend directory
- Run `uv sync` to install dependencies
- Activate the virtual environment: `source .venv/bin/activate`

### Frontend Issues

**Error: Cannot connect to backend**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in backend if accessing from different origin
- Verify `VITE_API_URL` in frontend `.env` if needed

**Chart not displaying**
- Check browser console for errors
- Ensure stock data was successfully fetched
- Try refreshing the page

## 🚀 Future Enhancements

- [ ] Add more technical indicators (Stochastic, ADX, Ichimoku)
- [ ] Pattern recognition (Head & Shoulders, Cup & Handle)
- [ ] Backtesting capabilities
- [ ] Portfolio tracking
- [ ] Price alerts
- [ ] Mobile app
- [ ] Historical recommendation tracking

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Disclaimer**: This application is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.
