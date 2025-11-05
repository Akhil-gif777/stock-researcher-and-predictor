import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { ScrollArea } from "./ui/scroll-area";
import { motion } from "motion/react";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  Clock,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Layers,
  Zap,
  Eye,
  ArrowUp,
  ArrowDown,
  Minus,
} from "lucide-react";
import type {
  EnhancedTechnicalResult,
  TimeframeAnalysis,
  SignalAnalysis,
  PatternData,
} from "../types/api";

interface EnhancedTechnicalTabProps {
  enhancedData?: EnhancedTechnicalResult;
  standardIndicators?: any; // Fallback to standard indicators
}

export function EnhancedTechnicalTab({
  enhancedData,
  standardIndicators,
}: EnhancedTechnicalTabProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>("daily");

  // Helper function to get signal color
  const getSignalColor = (signal: string) => {
    if (signal.includes("strong_buy")) return "text-green-500";
    if (signal.includes("buy")) return "text-green-400";
    if (signal.includes("strong_sell")) return "text-red-500";
    if (signal.includes("sell")) return "text-red-400";
    return "text-gray-400";
  };

  // Helper function to get signal icon
  const getSignalIcon = (signal: string) => {
    if (signal.includes("buy")) return <ArrowUp className="w-4 h-4" />;
    if (signal.includes("sell")) return <ArrowDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  // Helper function to format confidence
  const formatConfidence = (confidence: number) => {
    const percentage = (confidence * 100).toFixed(1);
    let color = "bg-gray-500";
    if (confidence > 0.7) color = "bg-green-500";
    else if (confidence > 0.55) color = "bg-yellow-500";
    else if (confidence < 0.3) color = "bg-red-500";

    return { percentage, color };
  };

  // If no enhanced data, show standard indicators
  if (!enhancedData?.technical_analyses) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white">Technical Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400">
            Enhanced technical analysis data not available. Showing standard indicators.
          </p>
          {/* You can add standard indicator display here */}
        </CardContent>
      </Card>
    );
  }

  const timeframes = Object.keys(enhancedData.technical_analyses);
  const currentAnalysis = enhancedData.technical_analyses[selectedTimeframe];

  return (
    <div className="space-y-6">
      {/* Timeframe Alignment Score */}
      {enhancedData.timeframe_alignment && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 border-blue-700">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Layers className="w-5 h-5 text-blue-400" />
                  <CardTitle className="text-white">
                    Multi-Timeframe Alignment
                  </CardTitle>
                </div>
                <Badge
                  variant="outline"
                  className={`
                    ${enhancedData.timeframe_alignment.score > 0.7
                      ? "bg-green-500/20 text-green-400 border-green-500"
                      : enhancedData.timeframe_alignment.score > 0.4
                      ? "bg-yellow-500/20 text-yellow-400 border-yellow-500"
                      : "bg-red-500/20 text-red-400 border-red-500"
                    }
                  `}
                >
                  {(enhancedData.timeframe_alignment.score * 100).toFixed(0)}% Aligned
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Progress
                  value={enhancedData.timeframe_alignment.score * 100}
                  className="h-2"
                />
                <p className="text-sm text-gray-300">
                  {enhancedData.timeframe_alignment.interpretation}
                </p>
                {enhancedData.recommended_timeframe && (
                  <div className="flex items-center gap-2 mt-2">
                    <Target className="w-4 h-4 text-yellow-400" />
                    <span className="text-sm text-gray-300">
                      Recommended focus:{" "}
                      <span className="text-white font-medium">
                        {enhancedData.recommended_timeframe.toUpperCase()}
                      </span>
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Timeframe Selector */}
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Timeframe Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
            <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 bg-gray-700">
              {timeframes.map((tf) => (
                <TabsTrigger
                  key={tf}
                  value={tf}
                  className="data-[state=active]:bg-blue-500 data-[state=active]:text-white"
                >
                  {tf.toUpperCase()}
                </TabsTrigger>
              ))}
            </TabsList>

            {timeframes.map((tf) => {
              const analysis = enhancedData.technical_analyses![tf];
              const signal = analysis.signals;
              const patterns = analysis.patterns;
              const indicators = analysis.indicators;

              return (
                <TabsContent key={tf} value={tf} className="space-y-6 mt-6">
                  {/* Signal Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="bg-gray-900/50 border-gray-700">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-gray-300">
                          Signal Analysis
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Signal:</span>
                          <div className="flex items-center gap-2">
                            {getSignalIcon(signal.signal_type)}
                            <span
                              className={`font-medium ${getSignalColor(
                                signal.signal_type
                              )}`}
                            >
                              {signal.signal_type.replace("_", " ").toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Confidence:</span>
                          <div className="flex items-center gap-2">
                            <Progress
                              value={signal.confidence * 100}
                              className="w-20 h-2"
                            />
                            <Badge
                              variant="outline"
                              className={`${
                                formatConfidence(signal.confidence).color
                              } bg-opacity-20`}
                            >
                              {formatConfidence(signal.confidence).percentage}%
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Market:</span>
                          <Badge variant="outline" className="bg-gray-700">
                            {signal.market_condition}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Valid Until:</span>
                          <span className="text-sm text-gray-300">
                            {new Date(signal.valid_until).toLocaleDateString()}
                          </span>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Entry/Exit Zones */}
                    {signal.entry_zones && (
                      <Card className="bg-gray-900/50 border-gray-700">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-sm text-gray-300">
                            Trading Zones
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          {signal.entry_zones.optimal_entry && (
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400">Entry:</span>
                              <span className="text-green-400 font-medium">
                                ${signal.entry_zones.optimal_entry.toFixed(2)}
                              </span>
                            </div>
                          )}
                          {signal.entry_zones.stop_loss && (
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400">Stop Loss:</span>
                              <span className="text-red-400 font-medium">
                                ${signal.entry_zones.stop_loss.toFixed(2)}
                              </span>
                            </div>
                          )}
                          {signal.entry_zones.take_profit_1 && (
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400">Target 1:</span>
                              <span className="text-blue-400 font-medium">
                                ${signal.entry_zones.take_profit_1.toFixed(2)}
                              </span>
                            </div>
                          )}
                          {signal.risk_reward && (
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400">Risk/Reward:</span>
                              <Badge
                                variant="outline"
                                className={
                                  signal.risk_reward.favorable
                                    ? "bg-green-500/20 text-green-400"
                                    : "bg-yellow-500/20 text-yellow-400"
                                }
                              >
                                1:{signal.risk_reward.risk_reward_ratio}
                              </Badge>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )}
                  </div>

                  {/* Key Indicators */}
                  <Card className="bg-gray-900/50 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-blue-400" />
                        Key Indicators
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                        <IndicatorCard
                          label="RSI"
                          value={indicators.rsi?.toFixed(1) || "N/A"}
                          status={
                            indicators.rsi > 70
                              ? "overbought"
                              : indicators.rsi < 30
                              ? "oversold"
                              : "neutral"
                          }
                        />
                        <IndicatorCard
                          label="ADX"
                          value={indicators.adx?.toFixed(1) || "N/A"}
                          status={
                            indicators.adx > 25 ? "trending" : "ranging"
                          }
                        />
                        <IndicatorCard
                          label="Stochastic"
                          value={indicators.stoch_k?.toFixed(1) || "N/A"}
                          status={
                            indicators.stoch_k > 80
                              ? "overbought"
                              : indicators.stoch_k < 20
                              ? "oversold"
                              : "neutral"
                          }
                        />
                        <IndicatorCard
                          label="MACD"
                          value={indicators.macd_histogram?.toFixed(3) || "N/A"}
                          status={
                            indicators.macd_histogram > 0
                              ? "bullish"
                              : "bearish"
                          }
                        />
                      </div>
                    </CardContent>
                  </Card>

                  {/* Patterns Detected */}
                  {patterns && patterns.patterns.length > 0 && (
                    <Card className="bg-gray-900/50 border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
                          <Eye className="w-4 h-4 text-blue-400" />
                          Patterns Detected
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {patterns.patterns.map((pattern, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
                            >
                              <div className="flex-1">
                                <p className="text-white font-medium">
                                  {pattern.description}
                                </p>
                                <div className="flex items-center gap-2 mt-1">
                                  <Badge
                                    variant="outline"
                                    className={`text-xs ${
                                      pattern.signal === "bullish"
                                        ? "text-green-400 border-green-500"
                                        : pattern.signal === "bearish"
                                        ? "text-red-400 border-red-500"
                                        : "text-gray-400 border-gray-500"
                                    }`}
                                  >
                                    {pattern.signal}
                                  </Badge>
                                  <span className="text-xs text-gray-400">
                                    Confidence: {(pattern.confidence * 100).toFixed(0)}%
                                  </span>
                                </div>
                              </div>
                              {pattern.signal === "bullish" ? (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                              ) : pattern.signal === "bearish" ? (
                                <XCircle className="w-5 h-5 text-red-400" />
                              ) : (
                                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                              )}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Key Signals */}
                  {signal.key_signals && signal.key_signals.length > 0 && (
                    <Card className="bg-gray-900/50 border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
                          <Zap className="w-4 h-4 text-yellow-400" />
                          Active Signals
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {signal.key_signals.map((sig, idx) => (
                            <Badge
                              key={idx}
                              variant="outline"
                              className="bg-gray-800 text-gray-200 border-gray-600"
                            >
                              {sig}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>
              );
            })}
          </Tabs>
        </CardContent>
      </Card>

      {/* LLM Analysis */}
      {enhancedData.technical_analysis && (
        <Card className="bg-gray-900/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              Comprehensive Technical Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64 w-full rounded-md">
              <div className="text-gray-300 whitespace-pre-wrap">
                {enhancedData.technical_analysis}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Helper component for indicator cards
function IndicatorCard({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: string;
}) {
  const getStatusColor = () => {
    switch (status) {
      case "overbought":
        return "text-orange-400";
      case "oversold":
        return "text-blue-400";
      case "bullish":
        return "text-green-400";
      case "bearish":
        return "text-red-400";
      case "trending":
        return "text-purple-400";
      case "ranging":
        return "text-gray-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case "overbought":
      case "bullish":
      case "trending":
        return <TrendingUp className="w-4 h-4" />;
      case "oversold":
      case "bearish":
        return <TrendingDown className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="p-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{label}</span>
        {getStatusIcon()}
      </div>
      <p className={`text-lg font-bold ${getStatusColor()}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{status}</p>
    </div>
  );
}