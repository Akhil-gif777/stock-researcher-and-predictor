# Stock Research & Prediction Application - Claude Context

## Project Overview

This is a sophisticated multi-agent stock analysis application that provides **dual AI-powered recommendations**: an unbiased AI analysis and a personalized recommendation based on the user's investment style (Conservative/Balanced/Aggressive).

### Key Technologies
- **Backend**: Python 3.10+, FastAPI, LangGraph (multi-agent orchestration)
- **Frontend**: React, TypeScript, Vite, TailwindCSS, Radix UI, Recharts
- **AI/LLM**: Local Ollama models (Llama 3.1, Qwen2.5, DeepSeek R1, Mixtral, etc.)
- **Data Sources**: yfinance (stock data), News API (sentiment), Alpha Vantage (macro data)
- **Real-time**: WebSocket for streaming agent progress
- **Package Manager**: uv (Python), npm (Node.js)

## Architecture

### Multi-Agent System
The application uses **LangGraph** to orchestrate 5 specialized AI agents that run in parallel:

1. **Research Agent** (`backend/app/agents/research_agent.py`)
   - Analyzes company fundamentals, financials, and business metrics
   - Sources: yfinance company info, financial statements

2. **Technical Agent** (`backend/app/agents/technical_agent.py`)
   - Evaluates price patterns, trends, and 10+ technical indicators
   - Indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Volume, OBV, Support/Resistance
   - Uses pandas-ta for calculations

3. **Sentiment Agent** (`backend/app/agents/sentiment_agent.py`)
   - Processes news articles and headlines for sentiment analysis
   - Provides aspect-based sentiment (e.g., earnings, products, management)
   - Sources: News API, yfinance news

4. **Macro Agent** (`backend/app/agents/macro_agent.py`)
   - Analyzes macroeconomic conditions (VIX, Fed Rate, GDP, Inflation, Unemployment)
   - Assesses overall market risk level
   - Sources: yfinance (VIX, ^TNX), Alpha Vantage (fallback)

5. **Decision Agent** (`backend/app/agents/decision_agent.py`)
   - Synthesizes all agent outputs
   - Generates **dual recommendations**:
     - **AI Recommendation**: Equal weighting across all factors
     - **User Recommendation**: Weighted based on investment style
   - Provides confidence scores, key reasons, entry/exit strategies

### Agent Execution Flow
```
┌─────────────────────────────────────────────┐
│  WebSocket Connection Established           │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  4 Agents Execute in Parallel (asyncio)     │
│  ┌──────────────┐  ┌─────────────┐         │
│  │  Research    │  │  Technical  │         │
│  │  Agent       │  │  Agent      │         │
│  └──────────────┘  └─────────────┘         │
│  ┌──────────────┐  ┌─────────────┐         │
│  │  Sentiment   │  │  Macro      │         │
│  │  Agent       │  │  Agent      │         │
│  └──────────────┘  └─────────────┘         │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  Decision Agent (Sequential)                │
│  - Generates AI recommendation              │
│  - Generates User recommendation            │
│  - Provides comparison insight              │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  Final Result Sent to Frontend              │
└─────────────────────────────────────────────┘
```

## Project Structure

```
stock-researcher-and-predictor/
├── backend/
│   ├── app/
│   │   ├── agents/              # All agent implementations
│   │   │   ├── research_agent.py
│   │   │   ├── technical_agent.py
│   │   │   ├── sentiment_agent.py
│   │   │   ├── macro_agent.py
│   │   │   ├── decision_agent.py
│   │   │   ├── graph.py         # LangGraph workflow
│   │   │   └── state.py         # Shared state TypedDict
│   │   ├── services/            # Data services
│   │   │   ├── llm_service.py   # LLM provider abstraction
│   │   │   ├── stock_data.py    # Stock data fetching
│   │   │   ├── news_service.py  # News API integration
│   │   │   └── macro_service.py # Macro data fetching
│   │   ├── main.py              # FastAPI app & endpoints
│   │   ├── config.py            # Settings & env vars
│   │   └── models.py            # Pydantic models
│   ├── pyproject.toml           # uv dependencies
│   └── .env                     # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── StockAnalysis.tsx  # Main analysis view
│   │   │   ├── StockChart.tsx     # Interactive chart
│   │   │   ├── ResultsTabs.tsx    # Tabbed results display
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.ts           # API client
│   │   ├── types/
│   │   │   └── api.ts           # TypeScript types
│   │   └── App.tsx              # Main app component
│   ├── package.json
│   └── .nvmrc                   # Node version (20+)
├── run-dev.sh                   # Quick start script
├── README.md                    # User documentation
└── OLLAMA_SETUP.md              # Ollama installation guide
```

## Key Files & Entry Points

### Backend
- **`backend/app/main.py`**: FastAPI application
  - `POST /api/analyze`: Synchronous stock analysis
  - `WS /ws/analyze/{symbol}`: WebSocket streaming analysis (primary endpoint)
  - `GET /api/stock/{symbol}/chart-data`: Historical data with indicators
  - Lines 92-454: WebSocket handler with parallel agent execution

- **`backend/app/config.py`**: Environment configuration
  - Line 32: `default_llm_provider` - Controls which LLM model to use
  - Supported providers: `ollama-llama3.1`, `ollama-deepseek-r1`, `ollama-qwen2.5`, `openai`, `gemini`, `claude`

- **`backend/app/models.py`**: Pydantic data models
  - `InvestmentStyle` (line 7): CONSERVATIVE/BALANCED/AGGRESSIVE
  - `StockAnalysisResult` (line 78): Complete analysis response
  - `Recommendation` (line 59): Single recommendation with full details

- **`backend/app/agents/state.py`**: Shared agent state (TypedDict)
  - All agents read from and write to this shared state
  - Contains all intermediate and final analysis results

### Frontend
- **`frontend/src/App.tsx`**: Main application component
  - WebSocket connection management
  - Real-time agent progress tracking
  - Stock analysis form

- **`frontend/src/components/StockChart.tsx`**: Interactive charting
  - Recharts-based price chart
  - Toggleable technical indicators
  - 90-day historical data

- **`frontend/src/components/ResultsTabs.tsx`**: Analysis results display
  - Technical tab: All indicators with interpretations
  - Fundamental tab: Company info and financials
  - Macro tab: Economic indicators
  - Sentiment tab: News analysis
  - Sources tab: Data citations

## Development Conventions

### Code Style
- **Backend**:
  - Use type hints for all functions
  - Pydantic models for data validation
  - Async/await for I/O operations (agents run in parallel)
  - Error handling with try/except and graceful fallbacks

- **Frontend**:
  - TypeScript strict mode
  - Functional components with hooks
  - Tailwind utility classes for styling
  - Component composition pattern

### Naming Conventions
- **Agents**: `{name}_agent.py` with `{name}_agent()` and `{name}_agent_async()` functions
- **Services**: `{name}_service.py` with a singleton `{name}_service` instance
- **Components**: PascalCase (e.g., `StockChart.tsx`)
- **State fields**: snake_case (e.g., `technical_indicators`, `ai_recommendation`)

### Agent Implementation Pattern
All agents follow this pattern:
```python
def agent_name(state: AgentState) -> AgentState:
    """Synchronous version (for LangGraph workflow)."""
    # Implementation
    return updated_state

async def agent_name_async(state: AgentState) -> AgentState:
    """Async version (for WebSocket parallel execution)."""
    # Same logic but with await for async operations
    return updated_state
```

## Professional Development Workflow

**Think like a developer, not just a code generator.** Every change should be made thoughtfully with consideration for the entire system.

### 1. Understanding Phase
Before making any changes:

- **Read relevant code first**: Never modify code you haven't read
- **Trace execution flow**: Understand how data flows through the system
  - For backend changes: Follow the request from FastAPI endpoint → agents → services → response
  - For frontend changes: Trace from user interaction → API call → state update → UI render
- **Identify dependencies**: What other parts of the system use this code?
  - Check imports and references
  - Look for shared state or data structures
  - Review type definitions and interfaces

**Example**: Before modifying the technical_agent.py, read:
- `backend/app/agents/state.py` - to understand state structure
- `backend/app/services/stock_data.py` - to see how data is fetched
- `frontend/src/types/api.ts` - to see what the frontend expects
- `backend/app/main.py` - to understand how the agent is called

### 2. Blast Radius Analysis
Before implementing, assess the impact:

- **Direct impact**: What files will you modify?
- **Integration points**: What calls this code? What does this code call?
- **Data contracts**: Are you changing any data structures, API responses, or state fields?
- **Breaking changes**: Will existing functionality break?
  - Frontend expecting specific fields in API response
  - Other agents depending on state fields
  - Downstream consumers of the data

**Risk Assessment Questions**:
- If I change this function signature, what breaks?
- If I add a new required field, where must it be initialized?
- If I modify the response format, does the frontend handle it?
- Are there multiple code paths that need the same update?

### 3. Implementation Strategy
Make changes systematically:

- **Start with data models**: Update TypedDicts, Pydantic models, TypeScript types first
- **Work inside-out**: Core logic → Service layer → API layer → Frontend
- **Maintain backwards compatibility**: Add new fields as optional when possible
- **Follow existing patterns**: Match the style and structure of surrounding code
- **Handle errors gracefully**: Always provide fallbacks and user-friendly error messages

**Implementation Checklist**:
- [ ] Update data models (state.py, models.py, api.ts)
- [ ] Implement core logic changes
- [ ] Update API endpoints if needed
- [ ] Modify frontend components if needed
- [ ] Add error handling and validation
- [ ] Update inline documentation/comments for complex logic

### 4. Integration Verification
Ensure changes work with the full system:

- **Backend Integration**:
  - If modifying agents: Check state initialization in main.py WebSocket handler
  - If changing services: Verify all agents using the service still work
  - If updating models: Ensure serialization/deserialization works correctly
  - Test WebSocket message flow if streaming is affected

- **Frontend Integration**:
  - If changing API responses: Update TypeScript types and component props
  - If modifying state: Verify all components consuming that state
  - Test WebSocket message handling and UI updates
  - Check error states and loading states

- **Cross-Environment Integration**:
  - Backend change affecting frontend: Plan frontend updates
  - New fields in response: Handle gracefully if field is missing (for backwards compatibility)
  - WebSocket protocol changes: Update both sender and receiver

### 5. Regression Prevention
Look for potential regressions:

- **Code that might break**:
  - Functions with similar names or purposes
  - Code in the same file that uses similar patterns
  - Downstream consumers of modified functions

- **Edge cases to test**:
  - Empty or null values
  - Missing optional fields
  - API failures or timeouts
  - Invalid user input
  - Race conditions in async code

- **Common regression areas**:
  - WebSocket message ordering
  - State initialization (missing fields)
  - JSON serialization (NaN, datetime, etc.)
  - Chart data formatting
  - LLM response parsing

### 6. Test Validation
Create test scripts to validate changes:

- **When to create test scripts**:
  - Adding new features or endpoints
  - Modifying critical logic (agents, decision logic)
  - Changing data structures or APIs
  - Fixing bugs (test that the bug is fixed)

- **Types of tests**:
  - **Unit-level**: Test individual functions with sample data
  - **Integration**: Test API endpoints with curl or Python script
  - **End-to-end**: Test full flow through WebSocket (frontend + backend)

- **Test script template**:
```python
# test_my_feature.py
"""
Test script for [feature name]
Tests: [what this validates]
"""
import asyncio
from app.agents.my_agent import my_agent_async

async def test_my_feature():
    # Setup test data
    test_state = {
        'symbol': 'AAPL',
        'investment_style': 'balanced',
        # ... other required fields
    }

    # Execute
    result = await my_agent_async(test_state)

    # Validate
    assert 'expected_field' in result
    assert result['expected_field'] is not None
    print("✓ Test passed")

if __name__ == "__main__":
    asyncio.run(test_my_feature())
```

### 7. End-to-End Validation
Test in the actual environment:

- **Backend changes**:
  1. Start backend with `uv run uvicorn app.main:app --reload`
  2. Check `/docs` for API documentation
  3. Test endpoint with curl or Postman
  4. Check logs for errors or warnings
  5. Verify WebSocket messages if applicable

- **Frontend changes**:
  1. Start frontend with `npm run dev`
  2. Test in browser with real user interactions
  3. Open browser console and check for errors
  4. Verify network requests in DevTools
  5. Test edge cases (loading, errors, empty states)

- **Full stack changes**:
  1. Start both backend and frontend
  2. Perform end-to-end user flow
  3. Test with multiple stock symbols
  4. Verify WebSocket connection and streaming
  5. Check all tabs and UI components
  6. Monitor both backend logs and browser console

### 8. Documentation
Update documentation when needed:

- **When to document**:
  - Adding new features or endpoints
  - Changing public APIs or data structures
  - Adding complex logic that isn't self-explanatory
  - Introducing new patterns or conventions
  - Fixing non-obvious bugs

- **What to document**:
  - Inline comments for complex algorithms
  - Function docstrings for public APIs
  - Update CLAUDE.md if architecture changes
  - Add comments explaining "why" not just "what"

- **Documentation standards**:
  - Use type hints and docstrings in Python
  - Use JSDoc comments for TypeScript functions
  - Explain trade-offs and design decisions
  - Include examples for non-obvious usage

### 9. Pre-Commit Checklist
Before considering a task complete:

- [ ] Code follows existing patterns and conventions
- [ ] All modified files are syntactically correct
- [ ] Added error handling where appropriate
- [ ] Updated TypeScript types if data structures changed
- [ ] Tested changes in actual environment (backend/frontend)
- [ ] Checked for console errors and warnings
- [ ] Verified WebSocket flow if applicable
- [ ] Tested edge cases and error conditions
- [ ] Updated documentation if needed
- [ ] No regressions in existing functionality

### Example Workflow: Adding a New Technical Indicator

**Task**: Add RSI overbought/oversold signals to technical analysis

**1. Understanding Phase**:
- Read `backend/app/agents/technical_agent.py` to see how RSI is calculated
- Check `backend/app/agents/state.py` to see where RSI data is stored
- Review `frontend/src/components/ResultsTabs.tsx` to see how indicators are displayed
- Check `frontend/src/types/api.ts` for type definitions

**2. Blast Radius**:
- Direct: Modify technical_agent.py
- Integration: May need to update state.py, models.py, api.ts
- Breaking changes: Adding new field to existing structure (should be optional)
- Affected areas: Technical analysis display, state serialization

**3. Implementation**:
- Update state.py: Add optional field for RSI signals
- Update technical_agent.py: Calculate overbought (>70) and oversold (<30) signals
- Update models.py: Add field to TechnicalAnalysis Pydantic model
- Update frontend/src/types/api.ts: Add field to TypeScript type
- Update ResultsTabs.tsx: Display the signals in the UI

**4. Integration Check**:
- Verify state initialization in main.py (add default value)
- Check JSON serialization of new field
- Test WebSocket message with new field
- Verify frontend renders new field correctly

**5. Regression Prevention**:
- Test that existing RSI value still works
- Verify other technical indicators aren't affected
- Check that missing RSI signal doesn't break the UI
- Test with stocks that don't have recent data

**6. Test Validation**:
```python
# test_rsi_signals.py
async def test_rsi_signals():
    state = {'symbol': 'AAPL', 'investment_style': 'balanced'}
    result = await technical_agent_async(state)
    assert 'rsi_signal' in result['technical_indicators']
    assert result['technical_indicators']['rsi_signal'] in ['overbought', 'oversold', 'neutral', None]
```

**7. End-to-End**:
- Start backend and frontend
- Analyze a stock with high RSI (e.g., a recently rallied stock)
- Verify signal shows in Technical tab
- Check that chart still renders correctly
- Test with multiple stocks

**8. Documentation**:
- Add docstring comment in technical_agent.py explaining signal logic
- Update CLAUDE.md technical indicators list

**9. Complete**: All checklist items verified ✓

---

**Remember**: The goal is not just to make code work, but to make code that integrates seamlessly, handles errors gracefully, and won't break in unexpected ways.

## Common Tasks & Commands

### Running the Application
```bash
# Quick start (recommended)
./run-dev.sh

# Manual start
# Terminal 1 - Backend
cd backend
export PATH="$HOME/.local/bin:$PATH"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Development
```bash
# Backend
cd backend
uv add <package>              # Add dependency
uv sync                       # Install dependencies
uv run fastapi dev app/main.py  # Run with auto-reload

# Frontend
cd frontend
npm install                   # Install dependencies
npm run dev                   # Development server
npm run build                 # Production build
```

### Testing & Validation
When making changes:
1. **Test backend**:
   - Check `/docs` endpoint for API documentation
   - Test WebSocket with a stock symbol
   - Monitor console logs for errors

2. **Test frontend**:
   - Run analysis for a known symbol (e.g., AAPL)
   - Verify all agents complete successfully
   - Check chart rendering and indicator toggles
   - Inspect browser console for errors

3. **Validate LLM responses**:
   - Ensure JSON output is properly parsed
   - Check for regex parsing in decision_agent.py
   - Verify confidence scores are 0.0-1.0

## Important Context & Design Decisions

### Investment Style Weighting
The **Decision Agent** uses different weights based on user style:
- **Conservative**: Fundamentals 50-60%, Long-term (1-5 years)
- **Balanced**: Equal weighting (25% each), Medium-term (3-12 months)
- **Aggressive**: Technicals 50-70%, Short-term (weeks-months)

### Parallel Execution Strategy
- **WebSocket endpoint** (main.py:92-454): Agents run in parallel using `asyncio.gather()`
  - 4 agents execute simultaneously (research, technical, sentiment, macro)
  - Decision agent runs sequentially after data gathering completes
  - Graceful degradation: If one agent fails, others continue with default values

### LLM Service Abstraction
- `backend/app/services/llm_service.py`: Unified interface for all LLM providers
- Supports: Ollama (local), OpenAI, Gemini, Claude, Proxy endpoints
- Configuration via `DEFAULT_LLM_PROVIDER` environment variable

### Technical Indicator Calculations
- All indicators calculated using `pandas-ta` library
- 90-day historical data for context
- Indicators include: SMA (20/50/200), EMA (12/26), RSI, MACD, Bollinger Bands, ATR, Volume, OBV
- Support/Resistance from 30-day highs/lows

## Things to Avoid & Gotchas

1. **WebSocket Message Ordering**:
   - Always send agent status updates in order: `in_progress` → `completed`/`failed`
   - Use `await asyncio.sleep(0.1)` to ensure messages are sent before connection closes

2. **LLM Response Parsing**:
   - Decision agent expects JSON output from LLM
   - Use regex fallback parsing if JSON fails (see decision_agent.py)
   - Always validate confidence scores are floats between 0.0 and 1.0

3. **State Management**:
   - All agents modify the same `state` dict
   - Fields must be initialized in main.py WebSocket handler (line 112-147)
   - Missing fields will cause KeyError in decision agent

4. **Chart Data Serialization**:
   - pandas DataFrames contain NaN values → convert to None for JSON (main.py:362-364)
   - Always clean chart_data before sending via WebSocket

5. **Agent Failures**:
   - Provide fallback values for all critical fields
   - See main.py:220-281 for default value examples
   - Never let one agent failure crash the entire workflow

6. **Ollama Requirements**:
   - Ollama service must be running: `ollama serve`
   - Model must be pulled: `ollama pull llama3.1:8b`
   - Check connection at `http://localhost:11434`

## Testing Workflow (Like Cursor)

When making code changes, follow this comprehensive workflow:

1. **Write/Modify Code**: Make the requested changes
2. **Create Test Script**: Write a test script to validate the change
3. **Run Tests**: Execute tests and verify functionality
4. **Fix Issues**: If tests fail, debug and fix
5. **Document**: Update relevant docs/comments if needed
6. **Commit**: Create a git commit with descriptive message (Ask the user before creating a commit)

### Example Testing Patterns
```bash
# Test backend API endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "investment_style": "balanced"}'

# Test WebSocket connection
# Use frontend or a WebSocket client tool

# Test agent individually
cd backend
uv run python -c "
from app.agents.research_agent import research_agent
from app.agents.state import AgentState
state = {'symbol': 'AAPL', 'investment_style': 'balanced'}
result = research_agent(state)
print(result)
"
```

## Dependencies & Requirements

### Backend
- Python 3.10+ (3.13 recommended)
- uv package manager
- Ollama (for local LLM models)
- Key packages: fastapi, langchain, langgraph, yfinance, pandas-ta, pydantic

### Frontend
- Node.js 20+ (specified in .nvmrc)
- npm or pnpm
- Key packages: react, vite, tailwindcss, recharts, @radix-ui

### External Services (Optional)
- **News API**: `NEWS_API_KEY` for enhanced sentiment analysis
- **Alpha Vantage**: `ALPHA_VANTAGE_API_KEY` for macro data fallback
- **OpenAI/Gemini/Claude**: API keys if not using Ollama

## API Documentation
Once backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Current State & Recent Changes

### Recent Work (from git status)
Modified files:
- `backend/app/agents/sentiment_agent.py` - Enhanced sentiment analysis
- `backend/app/agents/state.py` - Updated state structure
- `backend/app/config.py` - Added new LLM providers
- `backend/app/main.py` - Improved WebSocket error handling
- `backend/app/models.py` - Extended data models
- `backend/app/services/llm_service.py` - LLM service improvements
- `backend/app/services/macro_service.py` - Macro data enhancements
- `backend/app/services/news_service.py` - News fetching updates
- `frontend/src/App.tsx` - UI improvements
- `frontend/src/components/ResultsTabs.tsx` - Results display updates
- `frontend/src/types/api.ts` - Type definitions

Recent commits:
- `d26bc2b`: Parallelize agents invocation, improve prompting, and regex parsing
- `ae10241`: Parallelize agents' invocation and clean up
- `033b4ed`: Fix indicator values on chart UI

## Troubleshooting Guide

### Backend Issues
- **Ollama not running**: `ollama serve` in separate terminal
- **Model not found**: `ollama pull llama3.1:8b`
- **Import errors**: `cd backend && uv sync`
- **Port already in use**: Kill process on port 8000 or change `API_PORT`

### Frontend Issues
- **Cannot connect to backend**: Verify backend is running on port 8000
- **Chart not rendering**: Check browser console, verify chart_data is present
- **WebSocket errors**: Check CORS settings in backend/app/main.py:31-37

### Agent Failures
- **LLM timeout**: Increase timeout in llm_service.py or use smaller model
- **JSON parsing error**: Check decision_agent.py regex fallback
- **Missing data**: Check agent logs for API rate limits or network issues

---

**Note for AI Assistants**: This project follows a rigorous development workflow. When making changes:
1. Always create or update tests
2. Validate changes work end-to-end
3. Update documentation if public APIs change
4. Follow the established code patterns and conventions
5. Handle errors gracefully with fallback values
