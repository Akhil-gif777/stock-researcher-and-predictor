import { useState, useEffect } from "react";
import { TechnicalConfigPanel } from "./TechnicalConfigPanel";
import { EnhancedTechnicalTab } from "./EnhancedTechnicalTab";
import { Card } from "./ui/card";
import { motion } from "motion/react";
import { toast } from "sonner";
import type {
  TechnicalConfig,
  EnhancedTechnicalResult,
  StockAnalysisResult,
} from "../types/api";

interface EnhancedTechnicalAnalysisProps {
  symbol: string;
  analysisResult?: StockAnalysisResult;
  onAnalyze?: (config: TechnicalConfig) => Promise<void>;
  isAnalyzing?: boolean;
}

export function EnhancedTechnicalAnalysis({
  symbol,
  analysisResult,
  onAnalyze,
  isAnalyzing = false,
}: EnhancedTechnicalAnalysisProps) {
  const [technicalConfig, setTechnicalConfig] = useState<TechnicalConfig>({
    timeframes: ["daily", "weekly"],
    selected_indicators: undefined,
    custom_weights: undefined,
  });

  const [enhancedResults, setEnhancedResults] =
    useState<EnhancedTechnicalResult | null>(null);

  const handleConfigChange = async (config: TechnicalConfig) => {
    setTechnicalConfig(config);

    if (onAnalyze) {
      try {
        await onAnalyze(config);
        toast.success("Technical configuration applied successfully");
      } catch (error) {
        toast.error("Failed to apply configuration");
        console.error("Config error:", error);
      }
    }
  };

  // Extract enhanced results from analysis result if available
  useEffect(() => {
    if (analysisResult) {
      // Check if the analysis result contains enhanced technical data
      const enhanced: EnhancedTechnicalResult = {
        technical_analyses: (analysisResult as any).technical_analyses,
        timeframe_alignment: (analysisResult as any).timeframe_alignment,
        all_patterns: (analysisResult as any).all_patterns,
        all_signals: (analysisResult as any).all_signals,
        technical_analysis: (analysisResult as any).enhanced_technical_analysis ||
          analysisResult.technical_analysis,
        recommended_timeframe: (analysisResult as any).recommended_timeframe,
      };

      // Only set if we actually have enhanced data
      if (enhanced.technical_analyses || enhanced.all_signals) {
        setEnhancedResults(enhanced);
      }
    }
  }, [analysisResult]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Configuration Panel */}
      <TechnicalConfigPanel
        onConfigChange={handleConfigChange}
        isAnalyzing={isAnalyzing}
      />

      {/* Enhanced Technical Display */}
      {(enhancedResults || analysisResult) && (
        <EnhancedTechnicalTab
          enhancedData={enhancedResults || undefined}
          standardIndicators={analysisResult?.technical_indicators}
        />
      )}

      {/* Placeholder when no data */}
      {!analysisResult && !enhancedResults && (
        <Card className="bg-gray-800/50 border-gray-700 p-8">
          <div className="text-center">
            <p className="text-gray-400 mb-2">
              Configure your technical analysis preferences above
            </p>
            <p className="text-sm text-gray-500">
              Analysis results will appear here after running the analysis
            </p>
          </div>
        </Card>
      )}
    </motion.div>
  );
}