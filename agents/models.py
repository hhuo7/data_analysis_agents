from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

# Structured Output Models (for the Analysis Agent)

class ChartSpecification(BaseModel):
    """Defines the metadata for a single chart."""
    chart_type: str = Field(description="Chart type, e.g., 'bar', 'line', 'pie', 'scatter'")
    title: str = Field(description="A professional title for the chart")
    x_axis: str = Field(description="The column name mapped to the X-axis")
    y_axis: str = Field(description="The column name mapped to the Y-axis")
    explanation: str = Field(description="Why this chart was chosen to represent the data")

class SQLQuery(BaseModel):
    """Internal model for capturing SQL generation."""
    reasoning: str = Field(description="Internal reasoning for the SQL logic")
    sql: str = Field(description="The executable SQLite query")

class AnalysisResponse(BaseModel):
    """Mandatory output format for the Analysis Agent, enabling automated testing."""
    executive_summary: str = Field(description="A written summary of the analysis results")
    data_table_markdown: str = Field(description="A markdown-formatted summary table of the data")
    visualizations: List[ChartSpecification] = Field(description="A list of recommended visualizations")


class AgentState(TypedDict):
    """
    Global state object for LangGraph.
    Stores the user request, database URI, and intermediate artifacts passed between agents.
    """

    user_query: str
    db_uri: str
    user_role: str


    analysis_report: Optional[AnalysisResponse]
    viz_code: Optional[str]  

    errors: List[str]
    retry_count: int
    feedback: Optional[str]