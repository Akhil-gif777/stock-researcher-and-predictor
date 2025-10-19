import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { motion } from "motion/react";
import ReactMarkdown from "react-markdown";
import {
  Brain,
  TrendingUp,
  TrendingDown,
  Target,
  BarChart3,
  FileText,
  MessageSquare,
  CheckCircle2,
  AlertCircle,
  DollarSign,
} from "lucide-react";
import type { StockAnalysisResult, InvestmentStyle } from "../types/api";

interface RecommendationSectionProps {
  analysisResult: StockAnalysisResult;
  investmentStyle: InvestmentStyle;
}

const getRecommendationDetails = (action: string) => {
  switch (action) {
    case "BUY":
      return {
        text: "Strong Buy",
        color: "text-green-600 dark:text-green-400",
        bgColor: "bg-green-500",
        icon: <TrendingUp className="w-6 h-6" />,
      };
    case "HOLD":
      return {
        text: "Hold",
        color: "text-yellow-600 dark:text-yellow-400",
        bgColor: "bg-yellow-500",
        icon: <Target className="w-6 h-6" />,
      };
    case "SELL":
      return {
        text: "Sell",
        color: "text-red-600 dark:text-red-400",
        bgColor: "bg-red-500",
        icon: <TrendingDown className="w-6 h-6" />,
      };
    default:
      return {
        text: "Hold",
        color: "text-yellow-600 dark:text-yellow-400",
        bgColor: "bg-yellow-500",
        icon: <Target className="w-6 h-6" />,
      };
  }
};

const WeightageCard = ({
  name,
  icon,
  percentage,
  color,
}: {
  name: string;
  icon: React.ReactNode;
  percentage: number;
  color: string;
}) => {
  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`p-2 ${color} rounded-lg`}>
            {icon}
          </div>
          <span className="text-gray-900 dark:text-gray-100 text-sm">{name}</span>
        </div>
        <Badge className="bg-purple-100 dark:bg-purple-900/30 text-purple-900 dark:text-purple-300 border border-purple-300 dark:border-purple-700">
          {percentage}%
        </Badge>
      </div>
      <Progress value={percentage} className="h-2" />
    </div>
  );
};

export function RecommendationSection({ analysisResult, investmentStyle }: RecommendationSectionProps) {
  const { ai_recommendation, user_recommendation, comparison_insight, symbol } = analysisResult;
  
  const aiDetails = getRecommendationDetails(ai_recommendation.action);
  const userDetails = getRecommendationDetails(user_recommendation.action);

  const weightageItems = [
    {
      key: "technical",
      name: "Technical",
      icon: <BarChart3 className="w-4 h-4 text-white" />,
      color: "bg-blue-500",
    },
    {
      key: "fundamental",
      name: "Research",
      icon: <FileText className="w-4 h-4 text-white" />,
      color: "bg-orange-500",
    },
    {
      key: "sentiment",
      name: "Sentiment",
      icon: <MessageSquare className="w-4 h-4 text-white" />,
      color: "bg-pink-500",
    },
    {
      key: "macro",
      name: "Macro",
      icon: <TrendingUp className="w-4 h-4 text-white" />,
      color: "bg-purple-500",
    },
  ];

  // Convert agent weights to percentages
  const getWeightPercentage = (weights: { [key: string]: number }, key: string) => {
    return Math.round((weights[key] || 0) * 100);
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-gray-900 dark:text-gray-100 mb-6 text-2xl font-bold">Final Recommendations</h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* AI Recommendation */}
          <Card className="border-2 border-blue-200 dark:border-blue-800 shadow-xl">
            <CardHeader className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-800 border-b border-blue-100 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500 rounded-xl">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-blue-900 dark:text-blue-300">
                  AI Recommendation
                </CardTitle>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Balanced analysis across all factors
              </p>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              {/* Overall Score */}
              <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-2xl border-2 border-blue-200 dark:border-blue-800">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Confidence</p>
                    <p className="text-blue-900 dark:text-blue-300 text-2xl font-bold">{Math.round(ai_recommendation.confidence * 100)}%</p>
                  </div>
                  <div className={`flex items-center gap-2 ${aiDetails.color}`}>
                    {aiDetails.icon}
                    <span className="text-xl font-bold">{aiDetails.text}</span>
                  </div>
                </div>
                <Progress value={ai_recommendation.confidence * 100} className="h-3" />
              </div>

              {/* Key Reasons */}
              <div>
                <h4 className="text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2 font-semibold">
                  <CheckCircle2 className="w-5 h-5 text-blue-500" />
                  Key Reasons
                </h4>
                <ul className="space-y-2">
                  {ai_recommendation.key_reasons.map((reason, index) => (
                    <li key={index} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Weightage Breakdown */}
              <div>
                <h4 className="text-gray-900 dark:text-gray-100 mb-4 font-semibold">
                  Analysis Weightage
                </h4>
                <div className="space-y-3">
                  {weightageItems.map((item) => (
                    <WeightageCard
                      key={item.key}
                      name={item.name}
                      icon={item.icon}
                      percentage={getWeightPercentage(ai_recommendation.agent_weights, item.key)}
                      color={item.color}
                    />
                  ))}
                </div>
              </div>

              {/* Price Targets */}
              {(ai_recommendation.entry_price || ai_recommendation.target_prices || ai_recommendation.stop_loss) && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-3 font-semibold flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-blue-500" />
                    Price Targets
                  </h4>
                  <div className="space-y-2 text-sm">
                    {ai_recommendation.entry_price && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Entry Price:</span>
                        <span className="text-gray-900 dark:text-gray-100 font-semibold">${ai_recommendation.entry_price.toFixed(2)}</span>
                      </div>
                    )}
                    {ai_recommendation.target_prices && ai_recommendation.target_prices.length > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Targets:</span>
                        <span className="text-gray-900 dark:text-gray-100 font-semibold">
                          {ai_recommendation.target_prices.map(t => `$${t.toFixed(2)}`).join(", ")}
                        </span>
                      </div>
                    )}
                    {ai_recommendation.stop_loss && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Stop Loss:</span>
                        <span className="text-red-600 dark:text-red-400 font-semibold">${ai_recommendation.stop_loss.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Entry Price Strategy */}
              {ai_recommendation.entry_price_strategy && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Entry Strategy</h4>
                  <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{ai_recommendation.entry_price_strategy}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Reassessment Timeline */}
              {ai_recommendation.reassessment_timeline && (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Reassessment Timeline</h4>
                  <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{ai_recommendation.reassessment_timeline}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Target Strategy */}
              {ai_recommendation.target_strategy && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Target Strategy</h4>
                  <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{ai_recommendation.target_strategy}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* AI Insights */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">AI Reasoning</h4>
                <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{ai_recommendation.reasoning}</ReactMarkdown>
                </div>
              </div>

              {/* Horizon */}
              <div className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-400 text-sm">Time Horizon:</span>
                <Badge className="bg-blue-500 text-white">{ai_recommendation.horizon}</Badge>
              </div>
            </CardContent>
          </Card>

          {/* User Strategy Recommendation */}
          <Card className="border-2 border-purple-200 dark:border-purple-800 shadow-xl">
            <CardHeader className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-800 border-b border-purple-100 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-purple-500 rounded-xl">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-purple-900 dark:text-purple-300">
                  {investmentStyle.charAt(0).toUpperCase() + investmentStyle.slice(1)} Strategy
                </CardTitle>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Tailored to your investment style
              </p>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              {/* Overall Score */}
              <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-2xl border-2 border-purple-200 dark:border-purple-800">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Confidence</p>
                    <p className="text-purple-900 dark:text-purple-300 text-2xl font-bold">{Math.round(user_recommendation.confidence * 100)}%</p>
                  </div>
                  <div className={`flex items-center gap-2 ${userDetails.color}`}>
                    {userDetails.icon}
                    <span className="text-xl font-bold">{userDetails.text}</span>
                  </div>
                </div>
                <Progress value={user_recommendation.confidence * 100} className="h-3" />
              </div>

              {/* Key Reasons */}
              <div>
                <h4 className="text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2 font-semibold">
                  <CheckCircle2 className="w-5 h-5 text-purple-500" />
                  Key Reasons
                </h4>
                <ul className="space-y-2">
                  {user_recommendation.key_reasons.map((reason, index) => (
                    <li key={index} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                      <span className="text-purple-500 mt-1">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Weightage Breakdown */}
              <div>
                <h4 className="text-gray-900 dark:text-gray-100 mb-4 font-semibold">
                  Analysis Weightage
                </h4>
                <div className="space-y-3">
                  {weightageItems.map((item) => (
                    <WeightageCard
                      key={item.key}
                      name={item.name}
                      icon={item.icon}
                      percentage={getWeightPercentage(user_recommendation.agent_weights, item.key)}
                      color={item.color}
                    />
                  ))}
                </div>
              </div>

              {/* Price Targets */}
              {(user_recommendation.entry_price || user_recommendation.target_prices || user_recommendation.stop_loss) && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-3 font-semibold flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-purple-500" />
                    Price Targets
                  </h4>
                  <div className="space-y-2 text-sm">
                    {user_recommendation.entry_price && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Entry Price:</span>
                        <span className="text-gray-900 dark:text-gray-100 font-semibold">${user_recommendation.entry_price.toFixed(2)}</span>
                      </div>
                    )}
                    {user_recommendation.target_prices && user_recommendation.target_prices.length > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Targets:</span>
                        <span className="text-gray-900 dark:text-gray-100 font-semibold">
                          {user_recommendation.target_prices.map(t => `$${t.toFixed(2)}`).join(", ")}
                        </span>
                      </div>
                    )}
                    {user_recommendation.stop_loss && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Stop Loss:</span>
                        <span className="text-red-600 dark:text-red-400 font-semibold">${user_recommendation.stop_loss.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Entry Price Strategy */}
              {user_recommendation.entry_price_strategy && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Entry Strategy</h4>
                  <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{user_recommendation.entry_price_strategy}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Reassessment Timeline */}
              {user_recommendation.reassessment_timeline && (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Reassessment Timeline</h4>
                  <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{user_recommendation.reassessment_timeline}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Target Strategy */}
              {user_recommendation.target_strategy && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Target Strategy</h4>
                  <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{user_recommendation.target_strategy}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Strategy Insights */}
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Strategy Reasoning</h4>
                <div className="text-gray-700 dark:text-gray-300 text-sm prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{user_recommendation.reasoning}</ReactMarkdown>
                </div>
              </div>

              {/* Horizon */}
              <div className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-400 text-sm">Time Horizon:</span>
                <Badge className="bg-purple-500 text-white">{user_recommendation.horizon}</Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Comparison Alert */}
        <Card className="border-2 border-yellow-200 dark:border-yellow-800 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/10 dark:to-orange-900/10 mt-6">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="p-2 bg-yellow-500 rounded-lg">
                <AlertCircle className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="text-gray-900 dark:text-gray-100 mb-2 font-semibold">Recommendation Comparison</h4>
                <div className="text-gray-700 dark:text-gray-300 mb-4 prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{comparison_insight}</ReactMarkdown>
                </div>
                <div className="flex gap-3 flex-wrap">
                  <Badge className={`${aiDetails.bgColor} text-white`}>
                    AI: {aiDetails.text} ({Math.round(ai_recommendation.confidence * 100)}%)
                  </Badge>
                  <Badge className={`${userDetails.bgColor} text-white`}>
                    {investmentStyle.charAt(0).toUpperCase() + investmentStyle.slice(1)}: {userDetails.text} ({Math.round(user_recommendation.confidence * 100)}%)
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

