import pytest
import os
from unittest.mock import Mock, patch
from agents.visualization_agent import VisualizationAgent
from agents.models import AnalysisResponse, ChartSpecification
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

@pytest.fixture
def agent():
    with patch('agents.visualization_agent.ChatOpenAI') as mock_llm:
        mock_llm.return_value = Mock()
        agent = VisualizationAgent()
        agent.llm = mock_llm.return_value
        return agent

@pytest.fixture
def mock_analysis_report():
    return AnalysisResponse(
        executive_summary="Sales data shows USA leading with $523.06 in total sales.",
        data_table_markdown="| Country | Total Sales |\n|---------|-------------|\n| USA     | 523.06     |\n| Canada  | 303.96     |",
        visualizations=[
            ChartSpecification(
                chart_type="bar",
                title="Sales by Country",
                x_axis="Country",
                y_axis="Total Sales",
                explanation="Bar chart to show sales distribution by country"
            )
        ]
    )

def test_generate_viz_code_returns_code_block(agent, mock_analysis_report):
    """Test that generate_viz_code returns a string containing Python code markers."""
    mock_response = Mock()
    mock_response.content = "```python\nimport matplotlib.pyplot as plt\nplt.plot([1,2,3])\n```"
    
    with patch.object(RunnableSequence, 'invoke', return_value=mock_response):
        result = agent.generate_viz_code(mock_analysis_report)
        
        assert isinstance(result, str)
        assert "```python" in result
        assert "import matplotlib" in result

def test_generate_viz_code_includes_plotting_calls(agent, mock_analysis_report):
    """Test that the generated code includes basic plotting functionality."""
    mock_response = Mock()
    mock_response.content = """```python
import pandas as pd
import matplotlib.pyplot as plt

# Sample code
df = pd.DataFrame({'x': [1,2,3], 'y': [4,5,6]})
plt.figure(figsize=(10,6))
plt.bar(df['x'], df['y'])
plt.title('Test Chart')
plt.show()
```"""
    
    with patch.object(RunnableSequence, 'invoke', return_value=mock_response):
        result = agent.generate_viz_code(mock_analysis_report)
        
        assert "plt.figure" in result
        assert "plt.bar" in result
        assert "plt.title" in result

def test_generate_viz_code_guardrail_blocks_dangerous_code(agent, mock_analysis_report):
    """Test that dangerous code patterns are blocked and safe fallback is returned."""
    mock_response = Mock()
    mock_response.content = "```python\nimport os\nos.system('rm -rf /')\n```"
    
    with patch.object(RunnableSequence, 'invoke', return_value=mock_response):
        result = agent.generate_viz_code(mock_analysis_report)
        
        assert "Visualization blocked for safety" in result
        assert "os.system" not in result