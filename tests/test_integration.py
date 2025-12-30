import pytest
import os
from dotenv import load_dotenv
from agents.workflow import create_bi_workflow

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

@pytest.fixture
def workflow():
    return create_bi_workflow()

def test_full_workflow_integration(workflow):
    """Verifies that the Analysis Agent and Visualization Agent collaborate successfully."""
    db_path = "data/chinook.db"
    query = "Total sales by country"
    
    # Run the connected workflow
    res = workflow.invoke({
        "user_query": query, 
        "db_uri": db_path, 
        "user_role": "admin",
        "viz_hint": "Use a bar chart", 
        "errors": []
    })
    
    # 1. Verify Analysis Agent Output
    assert res['analysis_report'] is not None 
    assert len(res['analysis_report'].data_table_markdown) > 0 
    
    # 2. Verify Visualization Agent Output
    assert "import" in res['viz_code'] 
    assert "plt." in res['viz_code'] or "px." in res['viz_code'] 
    
    # 3. Verify No Workflow Errors
    assert len(res['errors']) == 0