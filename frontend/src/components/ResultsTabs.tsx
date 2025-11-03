import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import ReactMarkdown from "react-markdown";
import {
  BarChart3,
  Building2,
  TrendingUp,
  MessageSquare,
  Database,
  ExternalLink,
  Calendar,
  Globe,
} from "lucide-react";
import type { StockAnalysisResult } from "../types/api";

interface ResultsTabsProps {
  analysisResult: StockAnalysisResult;
}

export function ResultsTabs({ analysisResult }: ResultsTabsProps) {
  const { 
    symbol,
    technical_indicators,
    macro_indicators,
    sources,
    research_summary,
    sentiment_analysis,
    technical_analysis,
    macro_summary,
  } = analysisResult;

  // Helper function to get signal badge
  const getSignalBadge = (signal: string) => {
    const lowerSignal = signal?.toLowerCase() || "";
    
    if (lowerSignal.includes("bullish") || lowerSignal.includes("buy") || lowerSignal.includes("strong") || lowerSignal.includes("above")) {
      return <Badge 
        variant="outline"
        className="mt-2 !bg-green-600 hover:!bg-green-700 !text-white font-semibold !border-2 !border-green-700 shadow-md"
        style={{ backgroundColor: '#16a34a', color: 'white', borderColor: '#15803d' }}
      >
        {lowerSignal.includes("crossover") ? "✓ Bullish" : lowerSignal.includes("above") ? "Above" : "Bullish"}
      </Badge>;
    } else if (lowerSignal.includes("bearish") || lowerSignal.includes("sell") || lowerSignal.includes("weak") || lowerSignal.includes("below")) {
      return <Badge 
        variant="outline"
        className="mt-2 !bg-red-600 hover:!bg-red-700 !text-white font-semibold !border-2 !border-red-700 shadow-md"
        style={{ backgroundColor: '#dc2626', color: 'white', borderColor: '#b91c1c' }}
      >
        {lowerSignal.includes("crossover") ? "✗ Bearish" : lowerSignal.includes("below") ? "Below" : "Bearish"}
      </Badge>;
    } else if (lowerSignal.includes("overbought")) {
      return <Badge 
        variant="outline"
        className="mt-2 !bg-orange-600 hover:!bg-orange-700 !text-white font-semibold !border-2 !border-orange-700 shadow-md"
        style={{ backgroundColor: '#ea580c', color: 'white', borderColor: '#c2410c' }}
      >
        Overbought
      </Badge>;
    } else if (lowerSignal.includes("oversold")) {
      return <Badge 
        variant="outline"
        className="mt-2 !bg-blue-600 hover:!bg-blue-700 !text-white font-semibold !border-2 !border-blue-700 shadow-md"
        style={{ backgroundColor: '#2563eb', color: 'white', borderColor: '#1d4ed8' }}
      >
        Oversold
      </Badge>;
    }
    
    return <Badge 
      variant="outline"
      className="mt-2 !bg-gray-700 hover:!bg-gray-800 !text-white font-semibold !border-2 !border-gray-800 shadow-md"
      style={{ backgroundColor: '#374151', color: 'white', borderColor: '#1f2937' }}
    >
      {signal || "Neutral"}
    </Badge>;
  };

  return (
    <Tabs defaultValue="technical" className="w-full">
      <TabsList className="grid w-full grid-cols-5 h-auto p-1 bg-gray-100 dark:bg-gray-800 rounded-xl">
        <TabsTrigger
          value="technical"
          className="flex items-center gap-2 data-[state=active]:bg-blue-500 data-[state=active]:text-white rounded-lg py-3"
        >
          <BarChart3 className="w-4 h-4" />
          <span className="hidden sm:inline">Technical</span>
        </TabsTrigger>
        <TabsTrigger
          value="fundamental"
          className="flex items-center gap-2 data-[state=active]:bg-purple-500 data-[state=active]:text-white rounded-lg py-3"
        >
          <Building2 className="w-4 h-4" />
          <span className="hidden sm:inline">Fundamental</span>
        </TabsTrigger>
        <TabsTrigger
          value="macro"
          className="flex items-center gap-2 data-[state=active]:bg-green-500 data-[state=active]:text-white rounded-lg py-3"
        >
          <TrendingUp className="w-4 h-4" />
          <span className="hidden sm:inline">Macro</span>
        </TabsTrigger>
        <TabsTrigger
          value="sentiment"
          className="flex items-center gap-2 data-[state=active]:bg-pink-500 data-[state=active]:text-white rounded-lg py-3"
        >
          <MessageSquare className="w-4 h-4" />
          <span className="hidden sm:inline">Sentiment</span>
        </TabsTrigger>
        <TabsTrigger
          value="sources"
          className="flex items-center gap-2 data-[state=active]:bg-orange-500 data-[state=active]:text-white rounded-lg py-3"
        >
          <Database className="w-4 h-4" />
          <span className="hidden sm:inline">Sources</span>
        </TabsTrigger>
      </TabsList>

      <TabsContent value="technical" className="mt-6">
        <Card className="border-2 border-blue-200 dark:border-blue-800">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-gray-800 dark:to-gray-800 border-b">
            <CardTitle className="flex items-center gap-2 text-blue-900 dark:text-blue-300">
              <BarChart3 className="w-5 h-5" />
              Technical Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 flex flex-col h-full">
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">RSI (14)</p>
                  <p className="text-blue-900 dark:text-blue-300 text-xl font-semibold mb-2">
                    {technical_indicators.rsi !== null && technical_indicators.rsi !== undefined 
                      ? technical_indicators.rsi.toFixed(2) 
                      : 'N/A'}
                  </p>
                  <div className="mt-auto">
                    {getSignalBadge(
                      technical_indicators.rsi !== null && technical_indicators.rsi > 70 ? "Overbought" : 
                      technical_indicators.rsi !== null && technical_indicators.rsi < 30 ? "Oversold" : "Neutral"
                    )}
                  </div>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 flex flex-col h-full">
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">MACD</p>
                  <p className="text-blue-900 dark:text-blue-300 text-xl font-semibold mb-1">
                    {technical_indicators.macd !== null && technical_indicators.macd !== undefined 
                      ? technical_indicators.macd.toFixed(2) 
                      : 'N/A'}
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs mb-2">
                    Signal: {technical_indicators.macd_signal !== null && technical_indicators.macd_signal !== undefined 
                      ? technical_indicators.macd_signal.toFixed(2) 
                      : 'N/A'}
                  </p>
                  <div className="mt-auto">
                    {getSignalBadge(
                      technical_indicators.macd !== null && technical_indicators.macd_signal !== null && 
                      technical_indicators.macd > technical_indicators.macd_signal ? "Bullish Crossover" : "Bearish Crossover"
                    )}
                  </div>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 flex flex-col h-full">
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">SMA (50)</p>
                  <p className="text-blue-900 dark:text-blue-300 text-xl font-semibold mb-2">
                    ${technical_indicators.sma_50 !== null && technical_indicators.sma_50 !== undefined 
                      ? technical_indicators.sma_50.toFixed(2) 
                      : 'N/A'}
                  </p>
                  <div className="mt-auto">
                    {getSignalBadge(
                      technical_indicators.price !== null && technical_indicators.sma_50 !== null && 
                      technical_indicators.price > technical_indicators.sma_50 ? "Above MA" : "Below MA"
                    )}
                  </div>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 flex flex-col h-full">
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Bollinger Bands</p>
                  <p className="text-blue-900 dark:text-blue-300 text-sm mb-2">
                    Upper: ${technical_indicators.bb_upper !== null && technical_indicators.bb_upper !== undefined 
                      ? technical_indicators.bb_upper.toFixed(2) 
                      : 'N/A'}<br/>
                    Lower: ${technical_indicators.bb_lower !== null && technical_indicators.bb_lower !== undefined 
                      ? technical_indicators.bb_lower.toFixed(2) 
                      : 'N/A'}
                  </p>
                  <div className="mt-auto">
                    {getSignalBadge(
                      technical_indicators.price !== null && technical_indicators.bb_upper !== null && 
                      technical_indicators.price > technical_indicators.bb_upper ? "Overbought" :
                      technical_indicators.price !== null && technical_indicators.bb_lower !== null && 
                      technical_indicators.price < technical_indicators.bb_lower ? "Oversold" : "Neutral"
                    )}
                  </div>
                </div>
              </div>
              <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-800 rounded-lg border border-blue-200 dark:border-blue-800">
                <h4 className="text-gray-900 dark:text-gray-100 mb-4 font-semibold text-lg">Summary</h4>
                <div className="text-gray-700 dark:text-gray-300 prose prose-lg dark:prose-invert max-w-none leading-relaxed">
                  <ReactMarkdown 
                    components={{
                      h1: ({children}) => <h1 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">{children}</h1>,
                      h2: ({children}) => <h2 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">{children}</h2>,
                      h3: ({children}) => <h3 className="text-base font-semibold mb-2 text-gray-900 dark:text-gray-100">{children}</h3>,
                      p: ({children}) => <p className="mb-4 leading-relaxed">{children}</p>,
                      ul: ({children}) => <ul className="mb-4 ml-4 space-y-2">{children}</ul>,
                      ol: ({children}) => <ol className="mb-4 ml-4 space-y-2">{children}</ol>,
                      li: ({children}) => <li className="leading-relaxed">{children}</li>,
                      strong: ({children}) => <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>,
                    }}
                  >
                    {technical_analysis}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="fundamental" className="mt-6">
        <Card className="border-2 border-purple-200 dark:border-purple-800">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-purple-100 dark:from-gray-800 dark:to-gray-800 border-b">
            <CardTitle className="flex items-center gap-2 text-purple-900 dark:text-purple-300">
              <Building2 className="w-5 h-5" />
              Fundamental Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-6">
              <div className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-gray-800 dark:to-gray-800 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="text-gray-900 dark:text-gray-100 mb-4 font-semibold text-lg">Company Overview</h4>
                <div className="text-gray-700 dark:text-gray-300 prose prose-lg dark:prose-invert max-w-none leading-relaxed">
                  <ReactMarkdown 
                    components={{
                      h1: ({children}) => <h1 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">{children}</h1>,
                      h2: ({children}) => <h2 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">{children}</h2>,
                      h3: ({children}) => <h3 className="text-base font-semibold mb-2 text-gray-900 dark:text-gray-100">{children}</h3>,
                      p: ({children}) => <p className="mb-4 leading-relaxed">{children}</p>,
                      ul: ({children}) => <ul className="mb-4 ml-4 space-y-2">{children}</ul>,
                      ol: ({children}) => <ol className="mb-4 ml-4 space-y-2">{children}</ol>,
                      li: ({children}) => <li className="leading-relaxed">{children}</li>,
                      strong: ({children}) => <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>,
                    }}
                  >
                    {research_summary}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="macro" className="mt-6">
        <Card className="border-2 border-green-200 dark:border-green-800">
          <CardHeader className="bg-gradient-to-r from-green-50 to-green-100 dark:from-gray-800 dark:to-gray-800 border-b">
            <CardTitle className="flex items-center gap-2 text-green-900 dark:text-green-300">
              <TrendingUp className="w-5 h-5" />
              Macro Economic Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {macro_indicators.vix !== undefined && macro_indicators.vix !== null && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Market Volatility (VIX)</p>
                    <p className="text-green-900 dark:text-green-300 text-xl font-semibold">
                      {macro_indicators.vix !== null && macro_indicators.vix !== undefined 
                        ? macro_indicators.vix.toFixed(2) 
                        : 'N/A'}
                    </p>
                    {getSignalBadge(
                      macro_indicators.vix !== null && macro_indicators.vix < 20 ? "Low" : 
                      macro_indicators.vix !== null && macro_indicators.vix > 30 ? "High" : "Moderate"
                    )}
                  </div>
                )}
                {macro_indicators.fed_rate !== undefined && macro_indicators.fed_rate !== null && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Fed Interest Rate</p>
                    <p className="text-green-900 dark:text-green-300 text-xl font-semibold">
                      {macro_indicators.fed_rate !== null && macro_indicators.fed_rate !== undefined 
                        ? macro_indicators.fed_rate.toFixed(2) 
                        : 'N/A'}%
                    </p>
                    <Badge className="mt-2 bg-blue-500 text-white">Current</Badge>
                  </div>
                )}
                {macro_indicators.gdp_growth !== undefined && macro_indicators.gdp_growth !== null && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">GDP Growth</p>
                    <p className="text-green-900 dark:text-green-300 text-xl font-semibold">
                      {macro_indicators.gdp_growth !== null && macro_indicators.gdp_growth !== undefined 
                        ? `${macro_indicators.gdp_growth > 0 ? '+' : ''}${macro_indicators.gdp_growth.toFixed(2)}%`
                        : 'N/A'}
                    </p>
                    {getSignalBadge(
                      macro_indicators.gdp_growth !== null && macro_indicators.gdp_growth > 2 ? "Strong" : "Weak"
                    )}
                  </div>
                )}
                {macro_indicators.inflation_cpi !== undefined && macro_indicators.inflation_cpi !== null && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Inflation (CPI)</p>
                    <p className="text-green-900 dark:text-green-300 text-xl font-semibold">
                      {macro_indicators.inflation_cpi !== null && macro_indicators.inflation_cpi !== undefined 
                        ? macro_indicators.inflation_cpi.toFixed(2) 
                        : 'N/A'}%
                    </p>
                    <Badge className="mt-2 bg-orange-500 text-white">Annual</Badge>
                  </div>
                )}
              </div>
              <div className="p-6 bg-gradient-to-r from-green-50 to-blue-50 dark:from-gray-800 dark:to-gray-800 rounded-lg border border-green-200 dark:border-green-800">
                <h4 className="text-gray-900 dark:text-gray-100 mb-4 font-semibold text-lg">Macro Outlook</h4>
                <div className="text-gray-700 dark:text-gray-300 prose prose-lg dark:prose-invert max-w-none leading-relaxed">
                  <ReactMarkdown 
                    components={{
                      h1: ({children}) => <h1 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">{children}</h1>,
                      h2: ({children}) => <h2 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">{children}</h2>,
                      h3: ({children}) => <h3 className="text-base font-semibold mb-2 text-gray-900 dark:text-gray-100">{children}</h3>,
                      p: ({children}) => <p className="mb-4 leading-relaxed">{children}</p>,
                      ul: ({children}) => <ul className="mb-4 ml-4 space-y-2">{children}</ul>,
                      ol: ({children}) => <ol className="mb-4 ml-4 space-y-2">{children}</ol>,
                      li: ({children}) => <li className="leading-relaxed">{children}</li>,
                      strong: ({children}) => <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>,
                    }}
                  >
                    {macro_summary}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="sentiment" className="mt-6">
        <Card className="border-2 border-pink-200 dark:border-pink-800">
          <CardHeader className="bg-gradient-to-r from-pink-50 to-pink-100 dark:from-gray-800 dark:to-gray-800 border-b">
            <CardTitle className="flex items-center gap-2 text-pink-900 dark:text-pink-300">
              <MessageSquare className="w-5 h-5" />
              Sentiment Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-6">
              <div className="p-6 bg-gradient-to-r from-pink-50 to-purple-50 dark:from-gray-800 dark:to-gray-800 rounded-lg border border-pink-200 dark:border-pink-800">
                <h4 className="text-gray-900 dark:text-gray-100 mb-4 font-semibold text-lg">Sentiment Summary</h4>
                <div className="text-gray-700 dark:text-gray-300 prose prose-lg dark:prose-invert max-w-none leading-relaxed">
                  <ReactMarkdown 
                    components={{
                      h1: ({children}) => <h1 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">{children}</h1>,
                      h2: ({children}) => <h2 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">{children}</h2>,
                      h3: ({children}) => <h3 className="text-base font-semibold mb-2 text-gray-900 dark:text-gray-100">{children}</h3>,
                      p: ({children}) => <p className="mb-4 leading-relaxed">{children}</p>,
                      ul: ({children}) => <ul className="mb-4 ml-4 space-y-2">{children}</ul>,
                      ol: ({children}) => <ol className="mb-4 ml-4 space-y-2">{children}</ol>,
                      li: ({children}) => <li className="leading-relaxed">{children}</li>,
                      strong: ({children}) => <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>,
                    }}
                  >
                    {sentiment_analysis}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Finnhub Pre-Computed Sentiment */}
              {(analysisResult.finnhub_sentiment_score !== undefined && analysisResult.finnhub_sentiment_score !== null) && (
                <Card className="border-2 border-blue-200 dark:border-blue-800 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-gray-800 dark:to-gray-800">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold text-blue-900 dark:text-blue-300 flex items-center gap-2">
                      <Globe className="w-4 h-4" />
                      Finnhub News Sentiment (Pre-Computed)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Overall Sentiment Score */}
                      <div className="p-4 bg-white dark:bg-gray-900/50 rounded-lg">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">News Score</p>
                        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          {(analysisResult.finnhub_sentiment_score * 100).toFixed(0)}%
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {analysisResult.finnhub_sentiment_score > 0.6 ? 'Positive' :
                           analysisResult.finnhub_sentiment_score > 0.4 ? 'Neutral' : 'Negative'}
                        </p>
                      </div>

                      {/* Bullish/Bearish Breakdown */}
                      {(analysisResult.finnhub_bullish_percent !== undefined && analysisResult.finnhub_bearish_percent !== undefined) && (
                        <div className="p-4 bg-white dark:bg-gray-900/50 rounded-lg">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Sentiment Breakdown</p>
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-green-600 dark:text-green-400">Bullish</span>
                              <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                                {(analysisResult.finnhub_bullish_percent * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-green-500 h-2 rounded-full"
                                style={{ width: `${analysisResult.finnhub_bullish_percent * 100}%` }}
                              />
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-red-600 dark:text-red-400">Bearish</span>
                              <span className="text-sm font-semibold text-red-600 dark:text-red-400">
                                {(analysisResult.finnhub_bearish_percent * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-red-500 h-2 rounded-full"
                                style={{ width: `${analysisResult.finnhub_bearish_percent * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Buzz Indicator */}
                      {analysisResult.finnhub_buzz !== undefined && (
                        <div className="p-4 bg-white dark:bg-gray-900/50 rounded-lg">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Article Buzz</p>
                          <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                            {analysisResult.finnhub_buzz.toFixed(2)}x
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            vs Weekly Average
                          </p>
                          {analysisResult.finnhub_articles_count !== undefined && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                              {analysisResult.finnhub_articles_count} articles this week
                            </p>
                          )}
                          {analysisResult.finnhub_buzz > 1.5 && (
                            <Badge className="mt-2 !bg-orange-600 !text-white">
                              High Activity
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Enhanced Sentiment Metrics */}
              {analysisResult.sentiment_aspects && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Sentiment Trend & Confidence */}
                  <Card className="border-2 border-pink-200 dark:border-pink-800">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Sentiment Trend & Confidence
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Trend Indicator */}
                      {analysisResult.sentiment_trend && (
                        <div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">7-Day Trend</p>
                          <div className="flex items-center gap-2">
                            {analysisResult.sentiment_trend === "improving" && (
                              <>
                                <TrendingUp className="w-5 h-5 text-green-600" />
                                <Badge className="!bg-green-600 !text-white">
                                  Improving
                                </Badge>
                              </>
                            )}
                            {analysisResult.sentiment_trend === "declining" && (
                              <>
                                <TrendingUp className="w-5 h-5 text-red-600 transform rotate-180" />
                                <Badge className="!bg-red-600 !text-white">
                                  Declining
                                </Badge>
                              </>
                            )}
                            {analysisResult.sentiment_trend === "stable" && (
                              <>
                                <MessageSquare className="w-5 h-5 text-gray-600" />
                                <Badge className="!bg-gray-600 !text-white">
                                  Stable
                                </Badge>
                              </>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Confidence Score */}
                      {analysisResult.sentiment_confidence !== undefined && (
                        <div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Analysis Confidence</p>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full transition-all"
                                style={{ width: `${analysisResult.sentiment_confidence * 100}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                              {(analysisResult.sentiment_confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Aspect-Based Sentiment Breakdown */}
                  <Card className="border-2 border-purple-200 dark:border-purple-800">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Sentiment by Aspect
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {Object.entries(analysisResult.sentiment_aspects).map(([aspect, score]) => {
                        const percentage = ((score + 1) / 2) * 100; // Convert -1 to 1 scale to 0-100%
                        const isPositive = score > 0.2;
                        const isNegative = score < -0.2;
                        const color = isPositive ? 'bg-green-500' : isNegative ? 'bg-red-500' : 'bg-gray-500';

                        return (
                          <div key={aspect}>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium text-gray-600 dark:text-gray-400 capitalize">
                                {aspect === 'market' ? 'Market & Competition' : aspect}
                              </span>
                              <span className={`text-xs font-bold ${isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-600'}`}>
                                {score > 0 ? '+' : ''}{score.toFixed(2)}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 relative">
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <div className="w-0.5 h-full bg-gray-400" style={{ marginLeft: '50%' }} />
                                </div>
                                <div
                                  className={`${color} h-1.5 rounded-full transition-all`}
                                  style={{
                                    width: `${Math.abs(percentage - 50)}%`,
                                    marginLeft: score < 0 ? `${percentage}%` : '50%'
                                  }}
                                />
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </CardContent>
                  </Card>
                </div>
              )}

              {sources.filter(s => s.type === "news").length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-gray-900 dark:text-gray-100 font-semibold">Recent News</h4>
                  {sources.filter(s => s.type === "news").slice(0, 5).map((source, index) => (
                    <div key={index} className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-pink-300 dark:hover:border-pink-700 transition-colors">
                      <a href={source.url} target="_blank" rel="noopener noreferrer" className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <p className="text-gray-900 dark:text-gray-100 font-medium">{source.title}</p>
                          {source.timestamp && (
                            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">{source.timestamp}</p>
                          )}
                        </div>
                        <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="sources" className="mt-6">
        <Card className="border-2 border-orange-200 dark:border-orange-800">
          <CardHeader className="bg-gradient-to-r from-orange-50 to-orange-100 dark:from-gray-800 dark:to-gray-800 border-b">
            <CardTitle className="flex items-center gap-2 text-orange-900 dark:text-orange-300">
              <Database className="w-5 h-5" />
              Data Sources ({sources.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <ScrollArea className="h-[600px] pr-4">
              <div className="space-y-3">
                {sources.map((source, index) => (
                  <Card
                    key={index}
                    className="border-2 border-orange-200 dark:border-orange-800/50 hover:border-orange-400 dark:hover:border-orange-600 transition-all hover:shadow-lg"
                  >
                    <CardContent className="pt-4">
                      <a href={source.url} target="_blank" rel="noopener noreferrer" className="block">
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-orange-500 rounded-lg">
                              <Globe className="w-4 h-4 text-white" />
                            </div>
                            <div className="flex-1">
                              <p className="text-gray-900 dark:text-gray-100 font-medium">{source.title}</p>
                              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">{source.url}</p>
                            </div>
                          </div>
                          <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge className="bg-orange-500 text-white capitalize">{source.type}</Badge>
                          {source.timestamp && (
                            <div className="flex items-center gap-1 text-gray-700 dark:text-gray-300 text-sm">
                              <Calendar className="w-3 h-3" />
                              {source.timestamp}
                            </div>
                          )}
                        </div>
                      </a>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
