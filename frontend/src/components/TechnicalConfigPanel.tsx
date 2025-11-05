import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Slider } from "./ui/slider";
import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { motion, AnimatePresence } from "motion/react";
import {
  Settings,
  TrendingUp,
  Activity,
  BarChart3,
  Zap,
  ChevronDown,
  ChevronUp,
  Info,
  Save,
  RotateCcw,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import type { TechnicalConfig } from "../types/api";

interface TechnicalConfigPanelProps {
  onConfigChange: (config: TechnicalConfig) => void;
  isAnalyzing?: boolean;
}

// Default indicator weights
const DEFAULT_WEIGHTS: Record<string, number> = {
  macd: 0.25,
  moving_average_crossover: 0.15,
  adx: 0.15,
  rsi: 0.20,
  stochastic: 0.15,
  volume: 0.15,
  obv: 0.10,
  support_resistance: 0.15,
  pivot_points: 0.10,
  candlestick_pattern: 0.10,
  chart_pattern: 0.15,
  divergence: 0.12,
  ichimoku: 0.20,
  fibonacci: 0.10,
};

const INDICATOR_CATEGORIES = {
  trend: ["macd", "moving_average_crossover", "adx", "ichimoku"],
  momentum: ["rsi", "stochastic"],
  volume: ["volume", "obv"],
  support_resistance: ["support_resistance", "pivot_points", "fibonacci"],
  patterns: ["candlestick_pattern", "chart_pattern", "divergence"],
};

const INDICATOR_INFO: Record<string, { name: string; description: string }> = {
  macd: {
    name: "MACD",
    description: "Moving Average Convergence Divergence - Trend and momentum indicator",
  },
  moving_average_crossover: {
    name: "MA Crossover",
    description: "Golden/Death cross signals from moving average crossovers",
  },
  adx: {
    name: "ADX",
    description: "Average Directional Index - Measures trend strength",
  },
  rsi: {
    name: "RSI",
    description: "Relative Strength Index - Identifies overbought/oversold conditions",
  },
  stochastic: {
    name: "Stochastic",
    description: "Momentum indicator comparing closing price to price range",
  },
  volume: {
    name: "Volume Analysis",
    description: "Volume relative to average - Confirms price movements",
  },
  obv: {
    name: "OBV",
    description: "On-Balance Volume - Cumulative volume flow indicator",
  },
  support_resistance: {
    name: "Support/Resistance",
    description: "Key price levels based on historical data",
  },
  pivot_points: {
    name: "Pivot Points",
    description: "Potential support/resistance levels calculated from previous period",
  },
  candlestick_pattern: {
    name: "Candlestick Patterns",
    description: "Hammer, Doji, Engulfing, and other reversal patterns",
  },
  chart_pattern: {
    name: "Chart Patterns",
    description: "Double top/bottom, triangles, breakouts",
  },
  divergence: {
    name: "Divergence",
    description: "Price vs indicator divergences signaling reversals",
  },
  ichimoku: {
    name: "Ichimoku Cloud",
    description: "Comprehensive trend following system",
  },
  fibonacci: {
    name: "Fibonacci",
    description: "Retracement levels for support/resistance",
  },
};

const TIMEFRAME_OPTIONS = [
  { value: "1hour", label: "1 Hour", description: "Day Trading" },
  { value: "4hour", label: "4 Hour", description: "Day/Swing Trading" },
  { value: "daily", label: "Daily", description: "Swing Trading" },
  { value: "weekly", label: "Weekly", description: "Position Trading" },
  { value: "monthly", label: "Monthly", description: "Long-term Investing" },
];

const PRESET_CONFIGS = {
  dayTrader: {
    name: "Day Trader",
    timeframes: ["1hour", "4hour"],
    weights: {
      rsi: 0.30,
      stochastic: 0.25,
      volume: 0.20,
      vwap: 0.15,
      support_resistance: 0.10,
    },
  },
  swingTrader: {
    name: "Swing Trader",
    timeframes: ["daily", "weekly"],
    weights: DEFAULT_WEIGHTS,
  },
  investor: {
    name: "Investor",
    timeframes: ["weekly", "monthly"],
    weights: {
      moving_average_crossover: 0.30,
      macd: 0.25,
      adx: 0.20,
      ichimoku: 0.25,
    },
  },
};

export function TechnicalConfigPanel({
  onConfigChange,
  isAnalyzing = false,
}: TechnicalConfigPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedTimeframes, setSelectedTimeframes] = useState<string[]>([
    "daily",
    "weekly",
  ]);
  const [selectedIndicators, setSelectedIndicators] = useState<Set<string>>(
    new Set(Object.keys(DEFAULT_WEIGHTS))
  );
  const [customWeights, setCustomWeights] = useState<Record<string, number>>(
    DEFAULT_WEIGHTS
  );
  const [activePreset, setActivePreset] = useState<string | null>(null);

  const handleTimeframeToggle = (timeframe: string) => {
    setSelectedTimeframes((prev) =>
      prev.includes(timeframe)
        ? prev.filter((t) => t !== timeframe)
        : [...prev, timeframe]
    );
  };

  const handleIndicatorToggle = (indicator: string) => {
    setSelectedIndicators((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(indicator)) {
        newSet.delete(indicator);
      } else {
        newSet.add(indicator);
      }
      return newSet;
    });
  };

  const handleWeightChange = (indicator: string, value: number[]) => {
    setCustomWeights((prev) => ({
      ...prev,
      [indicator]: value[0],
    }));
    setActivePreset(null); // Clear preset when manually adjusting
  };

  const applyPreset = (presetKey: string) => {
    const preset = PRESET_CONFIGS[presetKey as keyof typeof PRESET_CONFIGS];
    if (preset) {
      setSelectedTimeframes(preset.timeframes);
      setCustomWeights({ ...DEFAULT_WEIGHTS, ...preset.weights });
      setSelectedIndicators(new Set(Object.keys(preset.weights)));
      setActivePreset(presetKey);
    }
  };

  const resetToDefaults = () => {
    setSelectedTimeframes(["daily", "weekly"]);
    setSelectedIndicators(new Set(Object.keys(DEFAULT_WEIGHTS)));
    setCustomWeights(DEFAULT_WEIGHTS);
    setActivePreset(null);
  };

  const applyConfiguration = () => {
    const config: TechnicalConfig = {
      timeframes: selectedTimeframes,
      selected_indicators: Array.from(selectedIndicators),
      custom_weights: customWeights,
    };
    onConfigChange(config);
  };

  // Calculate normalized weights
  const normalizeWeights = () => {
    const activeWeights = Array.from(selectedIndicators).reduce(
      (acc, ind) => ({
        ...acc,
        [ind]: customWeights[ind] || 0.1,
      }),
      {} as Record<string, number>
    );

    const total = Object.values(activeWeights).reduce((sum, w) => sum + w, 0);

    return Object.entries(activeWeights).reduce(
      (acc, [key, value]) => ({
        ...acc,
        [key]: value / total,
      }),
      {} as Record<string, number>
    );
  };

  const normalizedWeights = normalizeWeights();

  return (
    <Card className="w-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border-gray-700">
      <CardHeader
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="w-5 h-5 text-blue-400" />
            <CardTitle className="text-lg font-semibold text-white">
              Advanced Technical Configuration
            </CardTitle>
            <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
              Enhanced Analysis
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white"
          >
            {isExpanded ? <ChevronUp /> : <ChevronDown />}
          </Button>
        </div>
      </CardHeader>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <CardContent className="space-y-6">
              {/* Preset Templates */}
              <div className="space-y-3">
                <Label className="text-sm font-medium text-gray-300">
                  Quick Templates
                </Label>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(PRESET_CONFIGS).map(([key, preset]) => (
                    <Button
                      key={key}
                      variant={activePreset === key ? "default" : "outline"}
                      size="sm"
                      onClick={() => applyPreset(key)}
                      className={
                        activePreset === key
                          ? "bg-blue-500 hover:bg-blue-600"
                          : "border-gray-600 text-gray-300 hover:bg-gray-700"
                      }
                    >
                      <Zap className="w-4 h-4 mr-1" />
                      {preset.name}
                    </Button>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={resetToDefaults}
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    <RotateCcw className="w-4 h-4 mr-1" />
                    Reset
                  </Button>
                </div>
              </div>

              {/* Timeframe Selection */}
              <div className="space-y-3">
                <Label className="text-sm font-medium text-gray-300">
                  Timeframes
                </Label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {TIMEFRAME_OPTIONS.map((tf) => (
                    <div
                      key={tf.value}
                      onClick={() => handleTimeframeToggle(tf.value)}
                      className={`
                        cursor-pointer rounded-lg border-2 p-3 transition-all
                        ${
                          selectedTimeframes.includes(tf.value)
                            ? "border-blue-500 bg-blue-500/10"
                            : "border-gray-600 hover:border-gray-500"
                        }
                      `}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-white">{tf.label}</p>
                          <p className="text-xs text-gray-400">
                            {tf.description}
                          </p>
                        </div>
                        <Checkbox
                          checked={selectedTimeframes.includes(tf.value)}
                          className="data-[state=checked]:bg-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Indicator Selection and Weights */}
              <Tabs defaultValue="selection" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-gray-800">
                  <TabsTrigger value="selection">Select Indicators</TabsTrigger>
                  <TabsTrigger value="weights">Adjust Weights</TabsTrigger>
                </TabsList>

                <TabsContent value="selection" className="space-y-4 mt-4">
                  {Object.entries(INDICATOR_CATEGORIES).map(
                    ([category, indicators]) => (
                      <div key={category} className="space-y-2">
                        <Label className="text-sm font-medium text-gray-300 capitalize">
                          {category.replace("_", " ")} Indicators
                        </Label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {indicators.map((ind) => (
                            <div
                              key={ind}
                              className="flex items-center space-x-2"
                            >
                              <Checkbox
                                id={ind}
                                checked={selectedIndicators.has(ind)}
                                onCheckedChange={() =>
                                  handleIndicatorToggle(ind)
                                }
                                className="data-[state=checked]:bg-blue-500"
                              />
                              <Label
                                htmlFor={ind}
                                className="flex-1 cursor-pointer"
                              >
                                <div className="flex items-center gap-2">
                                  <span className="text-white">
                                    {INDICATOR_INFO[ind]?.name || ind}
                                  </span>
                                  <TooltipProvider>
                                    <Tooltip>
                                      <TooltipTrigger>
                                        <Info className="w-3 h-3 text-gray-400" />
                                      </TooltipTrigger>
                                      <TooltipContent>
                                        <p className="max-w-xs">
                                          {INDICATOR_INFO[ind]?.description}
                                        </p>
                                      </TooltipContent>
                                    </Tooltip>
                                  </TooltipProvider>
                                </div>
                              </Label>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                </TabsContent>

                <TabsContent value="weights" className="space-y-4 mt-4">
                  <div className="space-y-3">
                    <p className="text-sm text-gray-400">
                      Adjust the importance of each selected indicator (weights
                      will be normalized)
                    </p>
                    {Array.from(selectedIndicators).map((ind) => (
                      <div key={ind} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm text-gray-300">
                            {INDICATOR_INFO[ind]?.name || ind}
                          </Label>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant="outline"
                              className="bg-gray-700 text-gray-200"
                            >
                              {(normalizedWeights[ind] * 100).toFixed(0)}%
                            </Badge>
                            <Badge
                              variant="outline"
                              className="bg-blue-500/10 text-blue-400"
                            >
                              Raw: {customWeights[ind]?.toFixed(2)}
                            </Badge>
                          </div>
                        </div>
                        <Slider
                          value={[customWeights[ind] || 0.1]}
                          onValueChange={(value) =>
                            handleWeightChange(ind, value)
                          }
                          min={0.05}
                          max={0.5}
                          step={0.05}
                          className="w-full"
                        />
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>

              {/* Configuration Summary */}
              <div className="p-4 bg-gray-800/50 rounded-lg space-y-2">
                <h4 className="text-sm font-medium text-gray-300">
                  Configuration Summary
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Selected Timeframes:</p>
                    <p className="text-white font-medium">
                      {selectedTimeframes.join(", ")}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400">Active Indicators:</p>
                    <p className="text-white font-medium">
                      {selectedIndicators.size} indicators
                    </p>
                  </div>
                </div>
              </div>

              {/* Apply Button */}
              <Button
                onClick={applyConfiguration}
                disabled={isAnalyzing}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
              >
                <Save className="w-4 h-4 mr-2" />
                Apply Configuration
              </Button>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}