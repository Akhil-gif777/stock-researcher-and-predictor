# Frontend-Backend Integration Guide

This document explains how the React frontend has been integrated with the FastAPI backend.

## Architecture Overview

- **Frontend**: React 18 + TypeScript + Vite (Port 5173)
- **Backend**: FastAPI + Python (Port 8000)
- **Communication**: WebSocket for real-time updates, REST API for data fetching

## Key Features Implemented

### 1. Real-time Agent Progress
- WebSocket connection to `/ws/analyze/{symbol}?style={style}`
- Live updates as each agent (research, technical, sentiment, macro, decision) completes
- Visual progress indicators in the UI

### 2. Investment Styles
Updated to match backend:
- **Conservative**: Long-term, fundamental-focused
- **Balanced**: Even weighting across all factors
- **Aggressive**: Technical/momentum-focused

### 3. Data Flow

```
User Input (Symbol + Style)
    ↓
WebSocket Connection
    ↓
Backend Multi-Agent Analysis
    ↓
Real-time Progress Updates → UI Agent Progress Component
    ↓
Final Analysis Result → UI Results Display
    ↓
Chart Data Fetch (REST) → Stock Chart Component
```

## File Structure

```
src/
├── types/
│   └── api.ts                    # TypeScript types matching backend models
├── services/
│   └── api.ts                    # API service layer (WebSocket + REST)
├── components/
│   ├── StockInputSection.tsx     # Updated with correct investment styles
│   ├── AgentProgress.tsx         # Real-time agent progress
│   ├── StockChart.tsx            # Real chart data from backend
│   ├── ResultsTabs.tsx           # Technical, Fundamental, Macro, Sentiment tabs
│   └── RecommendationSection.tsx # AI vs User recommendations
├── App.tsx                       # Main app with WebSocket integration
└── main.tsx                      # App entry with Toaster for notifications
```

## Running the Application

### 1. Start Backend (Terminal 1)
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend (Terminal 2)
```bash
cd "Stock Researcher UI Design (1)"
npm install  # First time only
npm run dev
```

### 3. Access Application
Open browser to: http://localhost:5173

## Data Mapping

### WebSocket Messages
Backend sends updates in this format:
```json
{
  "agent": "research|technical|sentiment|macro|decision|system",
  "status": "started|in_progress|completed|failed",
  "message": "Agent status message",
  "data": {StockAnalysisResult}  // Only on final completion
}
```

### Analysis Result Structure
```typescript
{
  symbol: string,
  current_price: number,
  technical_indicators: {
    rsi, macd, sma_20, sma_50, bb_upper, bb_lower, ...
  },
  macro_indicators: {
    vix, fed_rate, gdp_growth, inflation_cpi, unemployment
  },
  ai_recommendation: {
    action: "BUY|HOLD|SELL",
    confidence: 0.0-1.0,
    key_reasons: string[],
    agent_weights: {...},
    ...
  },
  user_recommendation: { ... },
  sources: Source[],
  ...
}
```

## Error Handling

- **WebSocket Connection Errors**: Displayed via toast notifications
- **Analysis Failures**: Error state shown in UI with details
- **Missing Data**: Graceful fallbacks with empty states
- **Network Issues**: Toast notifications with error messages

## Features

### Real-time Updates
- Agent progress updates as each agent completes
- Toast notifications for important events
- Smooth transitions between states

### Dual Recommendations
- **AI Recommendation**: Balanced analysis across all factors
- **User Recommendation**: Tailored to selected investment style
- Comparison insight explaining differences

### Comprehensive Analysis Tabs
1. **Technical**: RSI, MACD, SMA, Bollinger Bands, etc.
2. **Fundamental**: Company overview and financial data
3. **Macro**: VIX, Fed Rate, GDP, Inflation, Unemployment
4. **Sentiment**: News analysis and sentiment scoring
5. **Sources**: All data sources used in the analysis

### Interactive Charts
- Price chart with technical indicators
- SMA 20, SMA 50, EMA 12, EMA 26 overlays
- Responsive design with Recharts

## Environment Variables

The API endpoints are configured in `src/services/api.ts`:
- `API_BASE_URL`: http://localhost:8000
- `WS_BASE_URL`: ws://localhost:8000

To change these, update the constants in `api.ts`.

## CORS Configuration

Backend is configured to accept requests from:
- http://localhost:5173 (Vite dev server)
- http://localhost:3000 (alternate)

## Troubleshooting

### WebSocket Connection Fails
1. Ensure backend is running on port 8000
2. Check browser console for connection errors
3. Verify CORS settings in backend

### No Data Displayed
1. Check browser network tab for failed requests
2. Verify backend API responses
3. Check console for parsing errors

### Agent Progress Not Updating
1. Verify WebSocket connection is established
2. Check backend logs for agent execution
3. Ensure all agents complete without errors

## Technologies Used

### Frontend
- React 18.3
- TypeScript
- Vite 6.3
- TailwindCSS
- Radix UI Components
- Recharts (Charts)
- Framer Motion (Animations)
- Sonner (Toast Notifications)

### Backend
- FastAPI
- WebSocket
- Pydantic (Data Validation)
- LangGraph (Multi-Agent System)

## Next Steps

Potential enhancements:
1. Add historical analysis comparison
2. Implement portfolio tracking
3. Add watchlist functionality
4. Export analysis as PDF
5. Add dark mode toggle
6. Implement user authentication
7. Save analysis history

