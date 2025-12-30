import pytest
import os
from dotenv import load_dotenv
from agents.analysis_agent import DataAnalysisAgent

load_dotenv()

@pytest.fixture
def agent():
    return DataAnalysisAgent()

def test_chinook_sales_by_country(agent):
    db_path = "data/chinook.db"
    if not os.path.exists(db_path):
        pytest.skip(f"Missing {db_path}")

    result = agent.run_analysis("What is the total sales volume by country?", db_path)
    
    summary = result.executive_summary.lower()
    table_data = result.data_table_markdown
    
    expected_country = "USA"
    expected_value = "523.06"
    
    country_found = (expected_country in result.executive_summary) or (expected_country in table_data)
    value_found = (expected_value in summary) or (expected_value in table_data)
    
    assert country_found, f"Expected country {expected_country} not found."
    assert value_found, f"Expected total {expected_value} not found."

def test_sakila_popular_categories(agent):
    db_path = "data/sakila.db"
    if not os.path.exists(db_path):
        pytest.skip(f"Missing {db_path}")

    result = agent.run_analysis("Which film categories are the most popular by rental count?", db_path)
    
    summary = result.executive_summary.lower()
    table_data = result.data_table_markdown
    
    expected_category = "Sports"   
    category_found = (expected_category in summary) or (expected_category in table_data)
   
    assert category_found, f"Expected category {expected_category} not found."
 

def test_northwind_unitprice(agent):
    db_path = "data/northwind_small.sqlite"
    if not os.path.exists(db_path): 
        pytest.skip(f"Missing {db_path}")
    
    result = agent.run_analysis("Which product has the highest unit price?", db_path)
    
    summary = result.executive_summary.lower()
    table_data = result.data_table_markdown
    
    assert "price" in summary
    
    expected_price = "263.5"
    expected_product = "Côte de Blaye"
    
    price_found = (expected_price in summary) or (expected_price in table_data)
    product_found = ("Blaye" in result.executive_summary) or ("Blaye" in table_data)
    
    assert price_found, f"Expected price {expected_price} not found in result."
    assert product_found, f"Expected product {expected_product} not found in result."