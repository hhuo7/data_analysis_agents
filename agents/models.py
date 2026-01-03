from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

# --- 1. Structured Output Models (for the Analysis Agent) ---

class ChartSpecification(BaseModel):
    """Defines the metadata for a single chart."""
    chart_type: str = Field(description="Chart type, e.g., 'bar', 'line', 'pie', 'scatter'")
    title: str = Field(description="A professional title for the chart")
    x_axis: str = Field(description="The column name mapped to the X-axis")
    y_axis: str = Field(description="The column name mapped to the Y-axis")
    explanation: str = Field(description="Why this chart was chosen to represent the data")

class AnalysisResponse(BaseModel):
    """Mandatory output format for the Analysis Agent, enabling automated testing."""
    executive_summary: str = Field(description="A written summary of the analysis results")
    data_table_markdown: str = Field(description="A markdown-formatted summary table of the data")
    visualizations: List[ChartSpecification] = Field(description="A list of recommended visualizations")

# --- 2. State Definition 

class AgentState(TypedDict):
    """
    Global state object for LangGraph.
    Stores the user request, database URI, and intermediate artifacts passed between agents.
    """
    # Inputs
    user_query: str
    db_uri: str
    user_role: str

    # Output from the Analysis Agent
    analysis_report: Optional[AnalysisResponse]
    viz_code: Optional[str]  # Stores the generated Python plotting code

    # Feedback and Reflection Loop Tracking
    errors: List[str]
    retry_count: int
    feedback: Optional[str]