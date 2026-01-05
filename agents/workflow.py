from langgraph.graph import StateGraph, END
from .models import AgentState
from .analysis_agent import DataAnalysisAgent
from .visualization_agent import VisualizationAgent


def call_analysis_node(state: AgentState):
    analysis_agent = DataAnalysisAgent() 
    try:
        report = analysis_agent.run_analysis(state["user_query"], state["db_uri"], state)
        return {"analysis_report": report} 
    except Exception as e:
        return {"errors": [str(e)]}

def call_visualization_node(state: AgentState):
    if state.get("errors"): return state
    viz_agent = VisualizationAgent() 
    try:
        code = viz_agent.generate_viz_code(
            state["analysis_report"]
        )
        return {"viz_code": code}
    except Exception as e:
        return {"errors": state["errors"] + [str(e)]}


def call_reflection_node(state: AgentState):
    """Analyzes the current state and determines if a retry is needed."""
    errors = state.get("errors", [])
    report = state.get("analysis_report")
    retry_count = state.get("retry_count", 0)
    
    if errors:
        if retry_count < 3:
            feedback = f"Subsequent attempts should fix these issues: {'; '.join(errors)}"
            return {"retry_count": retry_count + 1, "feedback": feedback, "errors": []}
        return {"feedback": None}


    if report:
        summary = report.executive_summary.lower()
        table = report.data_table_markdown.strip()
        
        is_empty = not table or len(table.split('\n')) <= 2 
        mentions_missing = "does not exist" in summary or "not found" in summary or "no such table" in summary
        
        if (is_empty or mentions_missing) and retry_count < 3:
            feedback = "The previous analysis failed to find data or reported missing tables. Please verify the schema and try a different query."
            return {"retry_count": retry_count + 1, "feedback": feedback}

    return {"feedback": None}

def should_retry(state: AgentState):
    """Decision function for conditional routing."""
    if state.get("feedback"):
        return "analyst"
    return END

def create_bi_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyst", call_analysis_node)
    workflow.add_node("visualizer", call_visualization_node)
    workflow.add_node("reflector", call_reflection_node)
    
    workflow.set_entry_point("analyst")
    
    workflow.add_edge("analyst", "visualizer")
    workflow.add_edge("visualizer", "reflector")
    
    workflow.add_conditional_edges(
        "reflector",
        should_retry,
        {
            "analyst": "analyst",
            END: END
        }
    )
    
    return workflow.compile()

