"""LangGraph workflow for orchestrating all agents."""
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.research_agent import research_agent
from app.agents.technical_agent import technical_agent
from app.agents.sentiment_agent import sentiment_agent
from app.agents.decision_agent import decision_agent


def create_analysis_workflow():
    """Create the LangGraph workflow for stock analysis."""
    
    # Create graph with AgentState
    workflow = StateGraph(AgentState)
    
    # Add all agent nodes
    workflow.add_node("research", research_agent)
    workflow.add_node("technical", technical_agent)
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("decision", decision_agent)
    
    # Define the workflow
    # Start with research as entry point
    workflow.set_entry_point("research")
    
    # After research, run technical and sentiment in parallel
    workflow.add_edge("research", "technical")
    workflow.add_edge("research", "sentiment")
    
    # After both technical and sentiment complete, run decision
    workflow.add_edge("technical", "decision")
    workflow.add_edge("sentiment", "decision")
    
    # End after decision
    workflow.add_edge("decision", END)
    
    # Compile the graph
    return workflow.compile()


# Global workflow instance
analysis_workflow = create_analysis_workflow()

