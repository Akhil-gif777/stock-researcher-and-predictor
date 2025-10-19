import { useState, useEffect } from "react";
import { StockInputSection } from "./components/StockInputSection";
import { AgentProgress, getAgentsList } from "./components/AgentProgress";
import { StockChart } from "./components/StockChart";
import { ResultsTabs } from "./components/ResultsTabs";
import { RecommendationSection } from "./components/RecommendationSection";
import { motion } from "motion/react";
import { TrendingUp, Sparkles, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { stockAnalysisAPI } from "./services/api";
import type { 
  InvestmentStyle, 
  StockAnalysisResult, 
  AgentUpdate,
  ChartDataResponse 
} from "./types/api";

export default function App() {
  const [stockName, setStockName] = useState("");
  const [investmentStyle, setInvestmentStyle] = useState<InvestmentStyle>("balanced");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [agentStatuses, setAgentStatuses] = useState<Record<string, "pending" | "processing" | "completed">>({});
  const [analysisResult, setAnalysisResult] = useState<StockAnalysisResult | null>(null);
  const [chartData, setChartData] = useState<ChartDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!stockName.trim()) {
      toast.error("Please enter a stock symbol");
      return;
    }

    // Check backend connectivity first
    console.log("🔄 Checking backend connectivity...");
    const isBackendHealthy = await stockAnalysisAPI.healthCheck();
    if (!isBackendHealthy) {
      toast.error("Backend server is not responding. Please make sure it's running on http://localhost:8000");
      setError("Backend server connection failed. Please check if the server is running.");
      return;
    }
    console.log("✅ Backend is healthy");

    // Test chart data endpoint (but don't block analysis if it fails)
    console.log("🔄 Testing chart data endpoint...");
    try {
      const isChartDataWorking = await stockAnalysisAPI.testChartDataEndpoint();
      if (!isChartDataWorking) {
        console.warn("⚠️ Chart data endpoint test failed, but continuing with analysis");
        toast.warning("Chart data may not be available, but analysis will continue");
      } else {
        console.log("✅ Chart data endpoint is working");
      }
    } catch (testError) {
      console.warn("⚠️ Chart data test failed with error:", testError);
      if (testError instanceof Error && testError.message.includes("MACD")) {
        toast.warning("Chart data is temporarily unavailable due to a backend calculation error");
      } else {
        toast.warning("Chart data endpoint test failed, but analysis will continue");
      }
    }

    setIsAnalyzing(true);
    setShowResults(false);
    setError(null);
    setAnalysisResult(null);
    setChartData(null);

    // Initialize all agents as pending
    const initialStatuses: Record<string, "pending" | "processing" | "completed"> = {
      research: "pending",
      technical: "pending", 
      sentiment: "pending",
      macro: "pending",
      decision: "pending"
    };
    setAgentStatuses(initialStatuses);

    console.log("🚀 Starting WebSocket connection for", stockName);
    console.log("🚀 Investment style:", investmentStyle);

    // Connect to WebSocket
    const cleanup = stockAnalysisAPI.connectWebSocket(
      stockName,
      investmentStyle,
      // On agent update
      (update: AgentUpdate) => {
        console.log("🔄 App received agent update:", update);
        console.log("🔄 onUpdate function called with:", update);
        
        if (update.agent !== "system") {
          console.log(`🔄 Processing agent update for: ${update.agent}`);
          setAgentStatuses(prevStatuses => {
            console.log(`🔄 Mapping status for ${update.agent}: ${update.status}`);
            console.log("🔄 Previous statuses:", prevStatuses);
            
            // Create new object to trigger React re-render
            const newStatuses = { ...prevStatuses };
            
            // Map backend status to frontend status
            if (update.status === "in_progress") {
              console.log(`✅ Setting ${update.agent} to processing`);
              newStatuses[update.agent] = "processing";
            } else if (update.status === "completed") {
              console.log(`✅ Setting ${update.agent} to completed`);
              newStatuses[update.agent] = "completed";
            } else if (update.status === "failed") {
              console.log(`❌ Setting ${update.agent} to pending (failed)`);
              newStatuses[update.agent] = "pending"; // Reset to pending on failure
            }
            
            console.log("🔄 New agent statuses:", newStatuses);
            console.log("🔄 Status keys:", Object.keys(newStatuses));
            console.log("🔄 Returning new statuses from setAgentStatuses");
            
            return newStatuses;
          });
        } else {
          console.log("🔄 Skipping system agent update");
        }

        if (update.message) {
          toast.info(`${update.agent}: ${update.message}`);
        }
      },
      // On complete
      (result: StockAnalysisResult) => {
        console.log("Analysis complete:", result);
        setAnalysisResult(result);
        setIsAnalyzing(false);
        setShowResults(true);
        toast.success("Analysis complete!");
        
        // Fetch chart data
        fetchChartData(result.symbol);
      },
      // On error
      (error: Error) => {
        console.error("WebSocket error:", error);
        setError(error.message);
        setIsAnalyzing(false);
        toast.error(`Analysis failed: ${error.message}`);
      }
    );

    // Cleanup on unmount
    return () => {
      cleanup();
    };
  };

  const fetchChartData = async (symbol: string) => {
    try {
      console.log("💹 Fetching chart data for:", symbol);
      const data = await stockAnalysisAPI.getChartData(symbol);
      console.log("💹 Chart data received:", data);
      console.log("💹 Chart data validation:", {
        hasData: !!data,
        hasChartData: !!data?.chart_data,
        chartDataType: typeof data?.chart_data,
        chartDataLength: Array.isArray(data?.chart_data) ? data.chart_data.length : 'not array',
        firstDataPoint: Array.isArray(data?.chart_data) ? data.chart_data[0] : 'N/A'
      });
      
      if (data && data.chart_data && Array.isArray(data.chart_data) && data.chart_data.length > 0) {
        setChartData(data);
        console.log("✅ Chart data set successfully with", data.chart_data.length, "data points");
      } else {
        console.warn("⚠️ Chart data validation failed:", {
          hasData: !!data,
          hasChartData: !!data?.chart_data,
          isArray: Array.isArray(data?.chart_data),
          length: data?.chart_data?.length || 0
        });
        toast.warning("Chart data format is invalid or empty for this stock");
      }
    } catch (err) {
      console.error("Failed to fetch chart data:", err);
      toast.error(`Failed to fetch chart data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  // Calculate current stage and progress for parallel execution
  const parallelAgents = ["research", "technical", "sentiment", "macro"];
  const completedParallel = parallelAgents.filter(id => agentStatuses[id] === "completed").length;
  const allParallelComplete = completedParallel === 4;

  const currentStage: "parallel" | "decision" | "idle" = 
    isAnalyzing && !allParallelComplete ? "parallel" :
    isAnalyzing && allParallelComplete ? "decision" : 
    "idle";

  const agents = getAgentsList(currentStage, completedParallel, agentStatuses);
  console.log("🔄 Agents list updated:", agents.map(a => `${a.id}:${a.status}`).join(", "));
  console.log("🔄 Current agentStatuses object:", agentStatuses);
  console.log("🔄 Current stage:", currentStage, "Completed parallel:", completedParallel);
  console.log("🔄 Decision agent status:", agentStatuses.decision || "not set");

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl shadow-lg">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-gray-900 dark:text-gray-100 flex items-center gap-2">
                Stock AI Researcher
                <Sparkles className="w-5 h-5 text-purple-500" />
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Multi-agent AI system for comprehensive stock analysis
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <StockInputSection
            stockName={stockName}
            setStockName={setStockName}
            investmentStyle={investmentStyle}
            setInvestmentStyle={setInvestmentStyle}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
          />
        </motion.div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-2xl p-6"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-red-600" />
              <div>
                <h3 className="text-red-900 dark:text-red-300 font-semibold">Error</h3>
                <p className="text-red-700 dark:text-red-400">{error}</p>
              </div>
            </div>
          </motion.div>
        )}

        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <AgentProgress 
              agents={agents} 
            />
          </motion.div>
        )}

        {showResults && analysisResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-8"
          >
            <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-2xl p-6 border-2 border-green-200 dark:border-green-800 shadow-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-green-500 rounded-lg">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-green-900 dark:text-green-300">Analysis Complete</h3>
              </div>
              <p className="text-gray-700 dark:text-gray-300">
                All AI agents have completed their analysis of <span className="font-semibold text-green-700 dark:text-green-300">{analysisResult.symbol}</span> with{" "}
                <span className="font-semibold text-green-700 dark:text-green-300">{investmentStyle}</span> strategy. Review the detailed insights below.
              </p>
            </div>

            {chartData && chartData.chart_data && chartData.chart_data.length > 0 ? (
              <StockChart
                stockName={analysisResult.symbol}
                data={chartData.chart_data}
                indicators={analysisResult.technical_indicators}
                currentPrice={analysisResult.current_price}
              />
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-200 dark:border-yellow-800 rounded-2xl p-6"
              >
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-6 h-6 text-yellow-600" />
                  <div>
                    <h3 className="text-yellow-900 dark:text-yellow-300 font-semibold">Chart Data Unavailable</h3>
                    <p className="text-yellow-700 dark:text-yellow-400">
                      Unable to load stock chart data for {analysisResult.symbol}. The analysis continues below.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            <ResultsTabs 
              analysisResult={analysisResult}
            />

            <RecommendationSection
              analysisResult={analysisResult}
              investmentStyle={investmentStyle}
            />
          </motion.div>
        )}

        {!isAnalyzing && !showResults && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-center py-16"
          >
            <div className="max-w-2xl mx-auto">
              <div className="p-4 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/20 dark:to-blue-900/20 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <TrendingUp className="w-12 h-12 text-purple-600 dark:text-purple-400" />
              </div>
              <h2 className="text-gray-900 dark:text-gray-100 mb-4">
                Ready to Analyze Stocks
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8">
                Enter a stock symbol above and select your investment style to begin AI-powered analysis using our multi-agent system.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                <div className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-3">
                    <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-gray-900 dark:text-gray-100 mb-2">Technical Analysis</h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Advanced indicators and chart patterns
                  </p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                  <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-3">
                    <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <h3 className="text-gray-900 dark:text-gray-100 mb-2">AI Agents</h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    5 specialized agents working together
                  </p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mb-3">
                    <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-gray-900 dark:text-gray-100 mb-2">Real-time Data</h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Latest market data and news sentiment
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 mt-16">
        <div className="container mx-auto px-4 py-8">
          <p className="text-center text-gray-600 dark:text-gray-400 text-sm">
            Stock AI Researcher © 2025 • Powered by Multi-Agent AI System
          </p>
        </div>
      </footer>
    </div>
  );
}
