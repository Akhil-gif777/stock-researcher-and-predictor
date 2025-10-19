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
  const parallelAgents = agents.slice(0, 4);
  const decisionAgent = agents[4];

  console.log("🔄 AgentProgress rendering with agents:", agents.map(a => `${a.id}:${a.status}`));
  console.log("🔄 Parallel agents:", parallelAgents.map(a => `${a.id}:${a.status}`));
  console.log("🔄 Decision agent:", decisionAgent?.id, decisionAgent?.status);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-200 dark:border-gray-700">
      <div className="mb-8">
        <h3 className="text-gray-900 dark:text-gray-100 mb-2">Multi-Agent Analysis</h3>
        <p className="text-gray-600 dark:text-gray-400">AI agents working in parallel, converging to decision agent</p>
      </div>

      <div className="relative">
        {/* Parallel Agents Grid */}
        <div 
          className="grid grid-cols-2 gap-4 mb-8"
          style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr', 
            gap: '1rem',
            marginBottom: '2rem'
          }}
        >
          {parallelAgents.map((agent, index) => {
            console.log(`🔄 Rendering agent card ${index}:`, agent.id, agent.status);
            return <AgentCard key={agent.id} agent={agent} index={index} />;
          })}
        </div>

        {/* Connection Lines */}
        <div className="relative h-16 mb-4">
          <svg className="absolute inset-0 w-full h-full" style={{ overflow: 'visible' }}>
            {/* Lines from bottom two agents (Research and Sentiment) to decision agent */}
            {parallelAgents.slice(2, 4).map((agent, index) => {
              const isCompleted = agent.status === "completed";
              const isProcessing = agent.status === "processing";
              
              // Bottom row agents: Research (index 2) and Sentiment (index 3)
              const col = index % 2;
              const startX = col === 0 ? '25%' : '75%';
              const startY = '0%';
              
              return (
                <motion.line
                  key={`line-${agent.id}`}
                  x1={startX}
                  y1={startY}
                  x2="50%"
                  y2="100%"
                  stroke={
                    isCompleted
                      ? "#22c55e"
                      : isProcessing
                      ? "#a855f7"
                      : "#d1d5db"
                  }
                  strokeWidth="3"
                  strokeDasharray={isCompleted ? "0" : "8,4"}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ 
                    pathLength: isCompleted || isProcessing ? 1 : 0,
                    opacity: isCompleted || isProcessing ? 1 : 0.3
                  }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                />
              );
            })}
            
            {/* Central convergence point indicator */}
            <motion.circle
              cx="50%"
              cy="100%"
              r="6"
              fill={
                decisionAgent.status === "completed"
                  ? "#22c55e"
                  : decisionAgent.status === "processing"
                  ? "#a855f7"
                  : "#9ca3af"
              }
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            />
          </svg>
        </div>

        {/* Decision Agent */}
        <div className="flex justify-center">
          <div className="w-full md:w-2/3">
            <AgentCard agent={decisionAgent} index={4} isDecisionAgent />
          </div>
        </div>
      </div>
    </div>
  );
}

interface AgentCardProps {
  agent: Agent;
  index: number;
  isDecisionAgent?: boolean;
}

function AgentCard({ agent, index, isDecisionAgent = false }: AgentCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.1 }}
      className={`relative flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
        isDecisionAgent ? 'shadow-lg' : ''
      } ${
        agent.status === "completed"
          ? "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20"
          : agent.status === "processing"
          ? "border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/20"
          : "border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
      }`}
    >
      <div
        className={`flex items-center justify-center w-10 h-10 rounded-full flex-shrink-0 ${
          agent.status === "completed"
            ? "bg-green-500"
            : agent.status === "processing"
            ? agent.color
            : "bg-gray-300 dark:bg-gray-700"
        }`}
      >
        {agent.status === "completed" ? (
          <Check className="w-5 h-5 text-white" />
        ) : agent.status === "processing" ? (
          <Loader2 className="w-5 h-5 text-white animate-spin" />
        ) : (
          <div className="text-white">{agent.icon}</div>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <span className="text-gray-900 dark:text-gray-100 text-sm">{agent.name}</span>
          <Badge
            variant={
              agent.status === "completed"
                ? "default"
                : agent.status === "processing"
                ? "secondary"
                : "outline"
            }
            className={`text-xs ${
              agent.status === "completed"
                ? "bg-green-500 text-white"
                : agent.status === "processing"
                ? "bg-purple-500 text-white"
                : ""
            }`}
          >
            {agent.status === "completed"
              ? "Done"
              : agent.status === "processing"
              ? "Running"
              : "Waiting"}
          </Badge>
        </div>
        <p className="text-gray-600 dark:text-gray-400 text-xs">
          {agent.status === "completed"
            ? "Complete"
            : agent.status === "processing"
            ? "Analyzing..."
            : "In queue"}
        </p>
      </div>

      {agent.status === "processing" && (
        <div className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none">
          <motion.div
            className="h-full bg-gradient-to-r from-transparent via-purple-200/30 to-transparent"
            initial={{ x: "-100%" }}
            animate={{ x: "200%" }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
          />
        </div>
      )}
    </motion.div>
  );
}

export function getAgentsList(currentStage: "parallel" | "decision" | "idle", parallelProgress: number = 0, agentStatuses?: Record<string, "pending" | "processing" | "completed">): Agent[] {
  const allAgents = [
    {
      id: "technical",
      name: "Technical Agent",
      icon: <BarChart3 className="w-5 h-5" />,
      color: "bg-blue-500",
    },
    {
      id: "macro",
      name: "Macro Agent",
      icon: <TrendingUp className="w-5 h-5" />,
      color: "bg-purple-500",
    },
    {
      id: "research",
      name: "Research Agent",
      icon: <FileText className="w-5 h-5" />,
      color: "bg-orange-500",
    },
    {
      id: "sentiment",
      name: "Sentiment Agent",
      icon: <MessageSquare className="w-5 h-5" />,
      color: "bg-pink-500",
    },
    {
      id: "decision",
      name: "Decision Agent",
      icon: <Brain className="w-5 h-5" />,
      color: "bg-green-500",
    },
  ];

  // For parallel agents (first 4) - use actual status from agentStatuses if available
  const parallelAgents = allAgents.slice(0, 4).map((agent) => ({
    ...agent,
    status: agentStatuses?.[agent.id] || (
      currentStage === "idle"
        ? "pending"
        : currentStage === "parallel"
        ? "processing"
        : "completed" // All parallel agents completed when decision stage starts
    ),
  })) as Agent[];

  // For decision agent - use actual status from agentStatuses if available
  const decisionAgentStatus: Agent = {
    ...allAgents[4],
    status: agentStatuses?.decision || (
      currentStage === "decision"
        ? "processing"
        : currentStage === "idle"
        ? "pending"
        : "pending"
    ),
  } as Agent;

  return [...parallelAgents, decisionAgentStatus];
}