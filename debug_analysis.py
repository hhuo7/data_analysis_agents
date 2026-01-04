import os
from dotenv import load_dotenv
from agents.analysis_agent import DataAnalysisAgent

load_dotenv()

agent = DataAnalysisAgent()
db_path = "data/northwind_small.sqlite"
query = "Which product has the highest unit price?"

print(f"Running query: {query}")
result = agent.run_analysis(query, db_path)

print("\n--- EXECUTIVE SUMMARY ---")
print(result.executive_summary)
print("\n--- DATA TABLE MARKDOWN ---")
print(result.data_table_markdown)
print("\n--- VISUALIZATIONS ---")
print(result.visualizations)
