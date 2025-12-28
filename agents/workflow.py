from langgraph.graph import StateGraph, END
from .models import AgentState
from .analysis_agent import DataAnalysisAgent
from .visualization_agent import VisualizationAgent


def call_analysis_node(state: AgentState):
    # Initialize inside the node to ensure Env Vars are loaded
    analysis_agent = DataAnalysisAgent() 
    try:
        report = analysis_agent.run_analysis(state["user_query"], state["db_uri"])
        return {"analysis_report": report, "errors": []}
    except Exception as e:
        return {"errors": [str(e)]}

def call_visualization_node(state: AgentState):
    if state.get("errors"): return state
    viz_agent = VisualizationAgent() # Initialize inside the node
    try:
        code = viz_agent.generate_viz_code(
            state["analysis_report"], 
            state.get("chart_preference", "Auto"), 
            state.get("viz_hint", "")
        )
        return {"viz_code": code}
    except Exception as e:
        return {"errors": state["errors"] + [str(e)]}

def create_bi_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("analyst", call_analysis_node)
    workflow.add_node("visualizer", call_visualization_node)
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "visualizer")
    workflow.add_edge("visualizer", END)
    return workflow.compile()

