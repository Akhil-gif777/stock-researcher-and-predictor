"""FastAPI main application."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import asyncio
from datetime import datetime
import pandas as pd

from app.config import settings
from app.models import (
    StockRequest, StockAnalysisResult, Source, TechnicalIndicators,
    MacroIndicators, Recommendation, AgentUpdate
)
from app.agents.graph import analysis_workflow
from app.agents.research_agent import research_agent, research_agent_async
from app.agents.technical_agent import technical_agent, technical_agent_async
from app.agents.sentiment_agent import sentiment_agent, sentiment_agent_async
from app.agents.macro_agent import macro_agent, macro_agent_async
from app.agents.decision_agent import decision_agent
from app.agents.state import AgentState
from app.services.stock_data import stock_data_service

# Initialize FastAPI app
app = FastAPI(
    title="Stock Research & Prediction API",
    description="Multi-agent stock analysis with AI-powered recommendations",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    try:
        settings.validate_llm_config()
        print(f"✓ LLM configured: {settings.default_llm_provider}")
        print(f"✓ API server starting on {settings.api_host}:{settings.api_port}")
    except ValueError as e:
        print(f"⚠ Configuration warning: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Stock Research & Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/analyze", response_model=StockAnalysisResult)
async def analyze_stock(request: StockRequest):
    """
    Analyze a stock and return comprehensive analysis with dual recommendations.
    
    This endpoint runs the full multi-agent workflow synchronously.
    For real-time progress updates, use the WebSocket endpoint instead.
    """
    try:
        # Initialize state
        state = {
            "symbol": request.symbol.upper(),
            "investment_style": request.investment_style.value,
        }
        
        # Run the workflow
        result = analysis_workflow.invoke(state)
        
        # Build response
        return build_analysis_result(result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/analyze/{symbol}")
async def analyze_stream(websocket: WebSocket, symbol: str, style: str = "balanced"):
    """
    WebSocket endpoint for streaming agent progress in real-time.

    Sends updates as each agent completes its analysis.
    """
    try:
        print(f"🔄 WebSocket: Accepting connection for {symbol}")
        await websocket.accept()
        print(f"✅ WebSocket: Connection accepted for {symbol}")

        try:
            print(f"🔄 WebSocket: Starting analysis for {symbol}")

            # Initialize state
            state: AgentState = {
                "symbol": symbol.upper(),
                "investment_style": style,
                # Initialize all required fields with defaults
                "company_info": "",
                "financial_data": {},
                "research_sources": [],
                "technical_signals": {},
                "chart_data": {},
                "technical_indicators": {},
                "news_summary": "",
                "sentiment_score": 0.0,
                "news_sources": [],
                "macro_summary": "",
                "macro_indicators": {},
                "macro_risk_level": "medium",
                "ai_recommendation": "HOLD",
                "ai_confidence": 0.5,
                "ai_horizon": "Medium-term",
                "ai_key_reasons": [],
                "ai_reasoning": "",
                "ai_macro_impact": "",
                "ai_weights": {},
                "ai_technical_signals": {},
                "ai_entry_price": None,
                "ai_targets": None,
                "ai_stop_loss": None,
                "user_recommendation": "HOLD",
                "user_confidence": 0.5,
                "user_horizon": "Medium-term",
                "user_key_reasons": [],
                "user_reasoning": "",
                "user_macro_impact": "",
                "user_weights": {},
                "user_technical_signals": {},
                "user_entry_price": None,
                "user_targets": None,
                "user_stop_loss": None,
                "comparison_insight": "",
            }

        except Exception as e:
            print(f"❌ WebSocket ERROR: State initialization failed for {symbol}: {str(e)}")
            import traceback
            print(f"❌ WebSocket FULL TRACEBACK: {traceback.format_exc()}")
            return

        # Send initial update
        try:
            await websocket.send_json({
                "agent": "system",
                "status": "started",
                "message": f"Starting analysis for {symbol}",
            })
        except Exception as e:
            print(f"❌ WebSocket ERROR: Failed to send initial update - {str(e)}")
            return

        # Run workflow with real-time progress updates
        try:
            print(f"🔄 Starting parallel workflow execution for {symbol}")

            # Send initial "in_progress" for all parallel agents
            parallel_agents = ["research", "technical", "sentiment", "macro"]
            for agent_name in parallel_agents:
                try:
                    await websocket.send_json({
                        "agent": agent_name,
                        "status": "in_progress",
                        "message": f"Starting {agent_name} analysis...",
                    })
                except Exception as e:
                    print(f"❌ WebSocket ERROR: Failed to send {agent_name} start - {str(e)}")
                    return

            # Execute 4 agents in parallel using asyncio.gather
            print(f"🚀 Executing parallel agents: {', '.join(parallel_agents)}")
            results = await asyncio.gather(
                research_agent_async(state),
                technical_agent_async(state),
                sentiment_agent_async(state),
                macro_agent_async(state),
                return_exceptions=True  # Continue if one fails
            )

            # Process results and send completion messages
            failed_agents = []
            for i, (agent_name, result) in enumerate(zip(parallel_agents, results)):
                if isinstance(result, Exception):
                    print(f"❌ {agent_name.title()} Agent ERROR: {str(result)}")
                    failed_agents.append(agent_name)
                    try:
                        await websocket.send_json({
                            "agent": agent_name,
                            "status": "failed",
                            "message": f"{agent_name} failed: {str(result)}",
                        })
                    except Exception as e:
                        print(f"❌ WebSocket ERROR: Failed to send {agent_name} failure - {str(e)}")
                else:
                    state.update(result)
                    print(f"✅ {agent_name.title()} agent completed for {symbol}")
                    try:
                        await websocket.send_json({
                            "agent": agent_name,
                            "status": "completed",
                            "message": f"{agent_name.title()} analysis complete",
                        })
                    except Exception as e:
                        print(f"❌ WebSocket ERROR: Failed to send {agent_name} completion - {str(e)}")
            
            # If critical agents failed, provide default values
            if "technical" in failed_agents:
                print(f"⚠️ Technical agent failed, providing default technical indicators")
                
                # Try to get current price even if technical analysis failed
                current_price = 0.0
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
                    if current_price == 0:
                        current_price = info.get('previousClose', 0.0)
                    print(f"✓ Retrieved current price: ${current_price:.2f}")
                except Exception as e:
                    print(f"⚠️ Could not retrieve current price: {str(e)}")
                    # Try one more fallback - get from historical data
                    try:
                        hist = ticker.history(period="1d")
                        if not hist.empty:
                            current_price = float(hist['Close'].iloc[-1])
                            print(f"✓ Retrieved current price from history: ${current_price:.2f}")
                    except Exception as e2:
                        print(f"⚠️ Could not retrieve current price from history: {str(e2)}")
                
                state["technical_indicators"] = {
                    "price": current_price,
                    "sma_20": 0.0,
                    "sma_50": 0.0,
                    "sma_200": 0.0,
                    "ema_12": 0.0,
                    "ema_26": 0.0,
                    "rsi": 50.0,
                    "macd": 0.0,
                    "macd_signal": 0.0,
                    "macd_histogram": 0.0,
                    "bb_upper": 0.0,
                    "bb_middle": 0.0,
                    "bb_lower": 0.0,
                    "volume": 0,
                    "volume_avg": 0,
                    "atr": 0.0,
                }
                state["technical_signals"] = {"overall": "N/A", "trend": "N/A", "momentum": "N/A", "volume": "N/A"}
                state["chart_data"] = {}
            
            if "research" in failed_agents:
                print(f"⚠️ Research agent failed, providing default research data")
                state["company_info"] = "Research data unavailable"
                state["financial_data"] = {}
                state["research_sources"] = []
            
            if "sentiment" in failed_agents:
                print(f"⚠️ Sentiment agent failed, providing default sentiment data")
                state["news_summary"] = "Sentiment analysis unavailable"
                state["sentiment_score"] = 0.0
                state["news_sources"] = []
            
            if "macro" in failed_agents:
                print(f"⚠️ Macro agent failed, providing default macro data")
                state["macro_summary"] = "Macro analysis unavailable"
                state["macro_indicators"] = {}
                state["macro_risk_level"] = "medium"

            # Send decision agent start
            try:
                await websocket.send_json({
                    "agent": "decision",
                    "status": "in_progress",
                    "message": "Generating recommendations...",
                })
                await asyncio.sleep(0.1)  # Small delay to ensure message is sent
            except Exception as e:
                print(f"❌ WebSocket ERROR: Failed to send decision start - {str(e)}")
                return

            # Execute decision agent
            try:
                print(f"🎯 Executing decision agent...")
                decision_result = decision_agent(state)
                state.update(decision_result)
                print(f"✅ Decision agent completed for {symbol}")
            except Exception as e:
                print(f"❌ Decision Agent ERROR: {str(e)}")
                await websocket.send_json({
                    "agent": "decision",
                    "status": "failed",
                    "message": f"Decision analysis failed: {str(e)}",
                })
                
                # Provide fallback values for decision agent failure
                print(f"⚠️ Decision agent failed, providing default recommendations")
                state.update({
                    "ai_recommendation": "HOLD",
                    "ai_confidence": 0.5,
                    "ai_horizon": "Medium-term",
                    "ai_key_reasons": ["Analysis incomplete due to technical error"],
                    "ai_reasoning": "Unable to generate recommendation due to system error",
                    "ai_macro_impact": "",
                    "ai_weights": {"fundamental": 0.25, "technical": 0.25, "sentiment": 0.25, "macro": 0.25},
                    "ai_technical_signals": {},
                    "ai_entry_price": None,
                    "ai_targets": None,
                    "ai_stop_loss": None,
                    "user_recommendation": "HOLD",
                    "user_confidence": 0.5,
                    "user_horizon": "Medium-term",
                    "user_key_reasons": ["Analysis incomplete due to technical error"],
                    "user_reasoning": "Unable to generate recommendation due to system error",
                    "user_macro_impact": "",
                    "user_weights": {"fundamental": 0.25, "technical": 0.25, "sentiment": 0.25, "macro": 0.25},
                    "user_technical_signals": {},
                    "user_entry_price": None,
                    "user_targets": None,
                    "user_stop_loss": None,
                    "comparison_insight": "Both AI and user recommendations are unavailable due to system error",
                })

            # Send decision completion
            try:
                await websocket.send_json({
                    "agent": "decision",
                    "status": "completed",
                    "message": "Recommendations complete",
                })
                await asyncio.sleep(0.1)  # Small delay to ensure message is sent
            except Exception as e:
                print(f"❌ WebSocket ERROR: Failed to send decision completion - {str(e)}")
                return

            print(f"✅ Workflow completed successfully for {symbol}")

            # Send final result
            try:
                final_result = build_analysis_result(state)
                
                # Convert to dict and handle any serialization issues
                result_dict = final_result.dict()
                
                # Clean chart_data to ensure JSON serialization
                if 'chart_data' in result_dict and result_dict['chart_data']:
                    chart_data = result_dict['chart_data']
                    # Convert any NaN values to None for JSON serialization
                    for key, value in chart_data.items():
                        if isinstance(value, list):
                            chart_data[key] = [None if pd.isna(v) else v for v in value]
                
                await websocket.send_json({
                    "agent": "system",
                    "status": "completed",
                    "message": "Analysis complete",
                    "data": result_dict,
                })
                print(f"📨 Final result sent for {symbol}")
            except Exception as e:
                print(f"❌ WebSocket ERROR: Failed to send final result - {str(e)}")
                import traceback
                print(f"❌ WebSocket SERIALIZATION TRACEBACK: {traceback.format_exc()}")
                
                # Try to send a simplified result without chart_data
                try:
                    simplified_result = {
                        "symbol": state.get("symbol", symbol),
                        "current_price": state.get("technical_indicators", {}).get("price", 0),
                        "error": "Chart data serialization failed, but analysis completed"
                    }
                    await websocket.send_json({
                        "agent": "system",
                        "status": "completed",
                        "message": "Analysis complete (simplified result due to serialization issue)",
                        "data": simplified_result,
                    })
                    print(f"📨 Simplified result sent for {symbol}")
                except Exception as fallback_error:
                    print(f"❌ WebSocket ERROR: Even simplified result failed - {str(fallback_error)}")

            # Keep connection open briefly to ensure frontend receives all messages
            await asyncio.sleep(0.5)
            print(f"🔄 Keeping WebSocket open for {symbol} to ensure message delivery")

        except Exception as workflow_error:
            print(f"❌ Workflow ERROR for {symbol}: {str(workflow_error)}")
            import traceback
            print(f"❌ Workflow FULL TRACEBACK: {traceback.format_exc()}")
            # Send error notification to frontend
            try:
                await websocket.send_json({
                    "agent": "system",
                    "status": "failed",
                    "message": f"Analysis failed: {str(workflow_error)}",
                })
            except Exception as e:
                print(f"❌ WebSocket ERROR: Failed to send error notification - {str(e)}")

        except Exception as e:
            print(f"❌ WebSocket ERROR: Workflow failed for {symbol}: {str(e)}")
            import traceback
            print(f"❌ WebSocket FULL TRACEBACK: {traceback.format_exc()}")

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for {symbol}")
    except Exception as e:
        print(f"❌ WebSocket ERROR for {symbol}: {str(e)}")
        import traceback
        print(f"❌ WebSocket FULL TRACEBACK: {traceback.format_exc()}")
        try:
            await websocket.send_json({
                "agent": "system",
                "status": "failed",
                "message": f"WebSocket error: {str(e)}",
            })
        except Exception as send_error:
            print(f"❌ WebSocket ERROR: Failed to send error notification - {str(send_error)}")
        finally:
            try:
                await websocket.close()
            except:
                pass  # Already closed

    except Exception as e:
        print(f"❌ WEBSOCKET HANDLER ERROR for {symbol}: {str(e)}")
        import traceback
        print(f"❌ WEBSOCKET HANDLER FULL TRACEBACK: {traceback.format_exc()}")
        try:
            await websocket.send_json({
                "agent": "system",
                "status": "failed",
                "message": f"Handler error: {str(e)}",
            })
        except:
            pass
        finally:
            try:
                await websocket.close()
            except:
                pass


@app.get("/api/stock/{symbol}/chart-data")
async def get_chart_data(symbol: str, period: str = "90d"):
    """
    Get historical stock data with technical indicators for charting.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (e.g., "90d", "1y", "5y")
    """
    try:
        df, indicators = stock_data_service.get_stock_data(symbol, period)
        chart_data = stock_data_service.get_chart_data(df)
        
        return {
            "symbol": symbol,
            "period": period,
            "current_price": indicators['price'],
            "chart_data": chart_data,
            "indicators": indicators,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def build_analysis_result(state: Dict) -> StockAnalysisResult:
    """Build StockAnalysisResult from workflow state."""
    
    # Build sources list
    sources = []
    for source in state.get("research_sources", []):
        sources.append(Source(**source))
    for source in state.get("news_sources", []):
        sources.append(Source(**source))
    
    # Build technical indicators
    indicators_data = state.get("technical_indicators", {})
    technical_indicators = TechnicalIndicators(**indicators_data)
    
    # Build macro indicators
    macro_data = state.get("macro_indicators", {})
    macro_indicators = MacroIndicators(**macro_data)
    
    # Build AI recommendation
    ai_recommendation = Recommendation(
        type="AI",
        action=state.get("ai_recommendation", "HOLD"),
        confidence=state.get("ai_confidence", 0.5),
        horizon=state.get("ai_horizon", "Medium-term"),
        key_reasons=state.get("ai_key_reasons", []),
        reasoning=state.get("ai_reasoning", ""),
        macro_impact=state.get("ai_macro_impact", ""),
        agent_weights=state.get("ai_weights", {}),
        technical_signals=state.get("ai_technical_signals", {}),
        entry_price=state.get("ai_entry_price"),
        target_prices=state.get("ai_targets"),
        stop_loss=state.get("ai_stop_loss"),
        entry_price_strategy=state.get("ai_entry_price_strategy"),
        reassessment_timeline=state.get("ai_reassessment_timeline"),
        target_strategy=state.get("ai_target_strategy"),
    )
    
    # Build User recommendation
    user_recommendation = Recommendation(
        type="USER",
        action=state.get("user_recommendation", "HOLD"),
        confidence=state.get("user_confidence", 0.5),
        horizon=state.get("user_horizon", "Medium-term"),
        key_reasons=state.get("user_key_reasons", []),
        reasoning=state.get("user_reasoning", ""),
        macro_impact=state.get("user_macro_impact", ""),
        agent_weights=state.get("user_weights", {}),
        technical_signals=state.get("user_technical_signals", {}),
        entry_price=state.get("user_entry_price"),
        target_prices=state.get("user_targets"),
        stop_loss=state.get("user_stop_loss"),
        entry_price_strategy=state.get("user_entry_price_strategy"),
        reassessment_timeline=state.get("user_reassessment_timeline"),
        target_strategy=state.get("user_target_strategy"),
    )
    
    return StockAnalysisResult(
        symbol=state["symbol"],
        current_price=indicators_data.get("price", 0),
        research_summary=state.get("company_info", ""),
        technical_analysis=f"Overall trend: {state.get('technical_signals', {}).get('overall', 'N/A')}",
        sentiment_analysis=state.get("news_summary", ""),
        macro_summary=state.get("macro_summary", ""),
        ai_recommendation=ai_recommendation,
        user_recommendation=user_recommendation,
        comparison_insight=state.get("comparison_insight", ""),
        sources=sources,
        technical_indicators=technical_indicators,
        macro_indicators=macro_indicators,
        chart_data=state.get("chart_data", {}),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )

