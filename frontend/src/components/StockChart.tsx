import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { TrendingUp, Activity } from "lucide-react";
import type { ChartDataPoint, TechnicalIndicators } from "../types/api";

interface StockChartProps {
  stockName: string;
  data: ChartDataPoint[];
  indicators: TechnicalIndicators;
  currentPrice: number;
}

export function StockChart({ stockName, data, indicators, currentPrice }: StockChartProps) {
  // Debug logging
  console.log("📊 StockChart received data:", { 
    stockName, 
    dataLength: data?.length, 
    firstDataPoint: data?.[0],
    indicators,
    currentPrice 
  });
  
  // Extract indicator names based on what's available in the data
  const availableIndicators = [
    "SMA 20",
    "SMA 50", 
    "SMA 200",
    "EMA 12",
    "EMA 26",
    "RSI (14)",
    "MACD",
    "Bollinger Bands",
    "Volume",
    "ATR",
  ];

  return (
    <div className="space-y-6">
      <Card className="border-2 border-blue-200 dark:border-blue-800 shadow-xl">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-800 border-b border-blue-100 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500 rounded-lg">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-gray-900 dark:text-gray-100">
                  {stockName} Price Chart
                </CardTitle>
                <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                  Technical analysis with indicators • Current: ${currentPrice.toFixed(2)}
                </p>
              </div>
            </div>
            <Badge className="bg-blue-500 text-white">Live Data</Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                tick={{ fill: "#6b7280" }}
              />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: "#6b7280" }}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#ffffff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={false}
                name="Price"
              />
              {data[0]?.sma20 && (
                <Line
                  type="monotone"
                  dataKey="sma20"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="5 5"
                  name="SMA 20"
                />
              )}
              {data[0]?.sma50 && (
                <Line
                  type="monotone"
                  dataKey="sma50"
                  stroke="#ec4899"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="5 5"
                  name="SMA 50"
                />
              )}
              {data[0]?.ema12 && (
                <Line
                  type="monotone"
                  dataKey="ema12"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="3 3"
                  name="EMA 12"
                />
              )}
              {data[0]?.sma200 && (
                <Line
                  type="monotone"
                  dataKey="sma200"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="8 8"
                  name="SMA 200"
                />
              )}
              {data[0]?.ema26 && (
                <Line
                  type="monotone"
                  dataKey="ema26"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="4 4"
                  name="EMA 26"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="border-2 border-purple-200 dark:border-purple-800 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-gray-800 dark:to-gray-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500 rounded-lg">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <CardTitle className="text-gray-900 dark:text-gray-100">
              Applied Indicators
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-3">
            {availableIndicators.map((indicator, index) => (
              <Badge
                key={index}
                className="px-4 py-2 text-sm bg-gradient-to-r from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 text-purple-900 dark:text-purple-300 border border-purple-300 dark:border-purple-700"
              >
                {indicator}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
