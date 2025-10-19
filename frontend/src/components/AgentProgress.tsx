import { Check, Loader2, Brain, TrendingUp, FileText, BarChart3, MessageSquare } from "lucide-react";
import { motion } from "motion/react";
import { Badge } from "./ui/badge";

interface Agent {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  status: "pending" | "processing" | "completed";
}

interface AgentProgressProps {
  agents: Agent[];
}

export function AgentProgress({ agents }: AgentProgressProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-200 dark:border-gray-700">
      <div className="mb-6">
        <h3 className="text-gray-900 dark:text-gray-100 mb-2">Multi-Agent Analysis</h3>
        <p className="text-gray-600 dark:text-gray-400">AI agents working sequentially to analyze your stock</p>
      </div>

      <div className="space-y-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`relative flex items-center gap-4 p-4 rounded-xl border-2 transition-all ${
              agent.status === "completed"
                ? "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20"
                : agent.status === "processing"
                ? "border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/20"
                : "border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
            }`}
          >
            <div
              className={`flex items-center justify-center w-12 h-12 rounded-full ${
                agent.status === "completed"
                  ? "bg-green-500"
                  : agent.status === "processing"
                  ? agent.color
                  : "bg-gray-300 dark:bg-gray-700"
              }`}
            >
              {agent.status === "completed" ? (
                <Check className="w-6 h-6 text-white" />
              ) : agent.status === "processing" ? (
                <Loader2 className="w-6 h-6 text-white animate-spin" />
              ) : (
                <div className="text-white">{agent.icon}</div>
              )}
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-gray-900 dark:text-gray-100">{agent.name}</span>
                <Badge
                  variant={
                    agent.status === "completed"
                      ? "default"
                      : agent.status === "processing"
                      ? "secondary"
                      : "outline"
                  }
                  className={
                    agent.status === "completed"
                      ? "bg-green-500 text-white"
                      : agent.status === "processing"
                      ? "bg-purple-500 text-white"
                      : ""
                  }
                >
                  {agent.status === "completed"
                    ? "Completed"
                    : agent.status === "processing"
                    ? "Processing"
                    : "Pending"}
                </Badge>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                {agent.status === "completed"
                  ? "Analysis complete"
                  : agent.status === "processing"
                  ? "Analyzing data..."
                  : "Waiting in queue"}
              </p>
            </div>

            {agent.status === "processing" && (
              <div className="absolute inset-0 rounded-xl overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-transparent via-purple-200/30 to-transparent"
                  initial={{ x: "-100%" }}
                  animate={{ x: "200%" }}
                  transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                />
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export function getAgentsList(currentAgent: number): Agent[] {
  const allAgents = [
    {
      id: "research",
      name: "Research Agent",
      icon: <FileText className="w-6 h-6" />,
      color: "bg-orange-500",
    },
    {
      id: "technical",
      name: "Technical Agent",
      icon: <BarChart3 className="w-6 h-6" />,
      color: "bg-blue-500",
    },
    {
      id: "sentiment",
      name: "Sentiment Agent",
      icon: <MessageSquare className="w-6 h-6" />,
      color: "bg-pink-500",
    },
    {
      id: "macro",
      name: "Macro Agent",
      icon: <TrendingUp className="w-6 h-6" />,
      color: "bg-purple-500",
    },
    {
      id: "decision",
      name: "Decision Agent",
      icon: <Brain className="w-6 h-6" />,
      color: "bg-green-500",
    },
  ];

  return allAgents.map((agent, index) => ({
    ...agent,
    status:
      index < currentAgent
        ? "completed"
        : index === currentAgent
        ? "processing"
        : "pending",
  })) as Agent[];
}
