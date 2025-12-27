import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

CUSTOM_SYSTEM_PROMPT = """
You are an expert Data Analyst Agent. 
Goal: Provide accurate insights based on the database.

### Protocols:
1. **Verify Schema**: Always inspect schema before writing SQL.
2. **Business Intent**: Translate vague requests into metrics (e.g. "performance" = revenue).
3. **EDA**: For exploratory requests, check missing values and stats.
4. **Trends**: Use date columns; aggregate by month/year.
5. **Format**: ALWAYS provide specific numbers. Use Markdown tables for data.

### Edge Cases:
- Empty results: "No records found matching criteria."
- Vague query: Ask for clarification.
"""

def run_analysis(db_uri, analysis_type, user_input):
    db = SQLDatabase.from_uri(db_uri)
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    agent = create_sql_agent(
        llm=llm, db=db, agent_type="openai-tools", 
        prefix=CUSTOM_SYSTEM_PROMPT, verbose=True
    )
    
    full_query = f"Template: {analysis_type}. User Request: {user_input}"
    response = agent.invoke({"input": full_query})
    return response["output"]