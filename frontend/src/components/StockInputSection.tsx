import { Search } from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import type { InvestmentStyle } from "../types/api";

interface StockInputSectionProps {
  stockName: string;
  setStockName: (value: string) => void;
  investmentStyle: InvestmentStyle;
  setInvestmentStyle: (value: InvestmentStyle) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
}

export function StockInputSection({
  stockName,
  setStockName,
  investmentStyle,
  setInvestmentStyle,
  onAnalyze,
  isAnalyzing,
}: StockInputSectionProps) {
  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 rounded-2xl p-8 shadow-xl border border-purple-100 dark:border-gray-700">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h2 className="text-purple-900 dark:text-purple-300 mb-2">Stock Analysis</h2>
          <p className="text-gray-600 dark:text-gray-400">Enter a stock symbol to begin AI-powered analysis</p>
        </div>

        <div className="space-y-4">
          <div className="relative">
            <Input
              type="text"
              placeholder="e.g., AAPL, TSLA, GOOGL"
              value={stockName}
              onChange={(e) => setStockName(e.target.value.toUpperCase())}
              className="pl-12 h-14 text-lg bg-white dark:bg-gray-800 border-2 border-purple-200 dark:border-gray-600 focus:border-purple-500 dark:focus:border-purple-400 rounded-xl"
              disabled={isAnalyzing}
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-purple-400 h-5 w-5" />
          </div>

          <div className="space-y-3">
            <Label className="text-gray-700 dark:text-gray-300">Investment Style</Label>
            <RadioGroup
              value={investmentStyle}
              onValueChange={(value) => setInvestmentStyle(value as InvestmentStyle)}
              className="flex gap-4"
              disabled={isAnalyzing}
            >
              <div className="flex-1">
                <RadioGroupItem value="conservative" id="conservative" className="peer sr-only" />
                <Label
                  htmlFor="conservative"
                  className="flex flex-col items-center justify-between rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 cursor-pointer hover:bg-purple-50 dark:hover:bg-gray-700 peer-data-[state=checked]:border-purple-500 peer-data-[state=checked]:bg-purple-50 dark:peer-data-[state=checked]:bg-purple-900/20 transition-all"
                >
                  <span className="text-center">Conservative</span>
                </Label>
              </div>
              <div className="flex-1">
                <RadioGroupItem value="balanced" id="balanced" className="peer sr-only" />
                <Label
                  htmlFor="balanced"
                  className="flex flex-col items-center justify-between rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 cursor-pointer hover:bg-purple-50 dark:hover:bg-gray-700 peer-data-[state=checked]:border-purple-500 peer-data-[state=checked]:bg-purple-50 dark:peer-data-[state=checked]:bg-purple-900/20 transition-all"
                >
                  <span className="text-center">Balanced</span>
                </Label>
              </div>
              <div className="flex-1">
                <RadioGroupItem value="aggressive" id="aggressive" className="peer sr-only" />
                <Label
                  htmlFor="aggressive"
                  className="flex flex-col items-center justify-between rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 cursor-pointer hover:bg-purple-50 dark:hover:bg-gray-700 peer-data-[state=checked]:border-purple-500 peer-data-[state=checked]:bg-purple-50 dark:peer-data-[state=checked]:bg-purple-900/20 transition-all"
                >
                  <span className="text-center">Aggressive</span>
                </Label>
              </div>
            </RadioGroup>
          </div>

          <Button
            onClick={onAnalyze}
            disabled={!stockName || isAnalyzing}
            className="w-full h-14 text-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            {isAnalyzing ? "Analyzing..." : "Analyze Stock"}
          </Button>
        </div>
      </div>
    </div>
  );
}
