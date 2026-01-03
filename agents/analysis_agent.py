import sqlite3
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .models import AnalysisResponse

class DataAnalysisAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.structured_llm = self.llm.with_structured_output(AnalysisResponse)

    def get_schema(self, db_uri):
        conn = sqlite3.connect(db_uri)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema_info = ""
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            col_desc = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
            schema_info += f"Table: {table_name} | Columns: {col_desc}\n"
        conn.close()
        return schema_info

    def run_analysis(self, user_query, db_uri, state: dict = None):
        schema = self.get_schema(db_uri)
        
        # Simple guardrail: basic input validation
        if len(user_query) > 1000:
            raise ValueError("Query too long")
        dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter']
        if any(word in user_query.lower() for word in dangerous_keywords):
            raise ValueError("Query contains potentially dangerous keywords")
        
        system_prompt = """
You are an expert Data Analyst Agent for SQLite. Your goal is to provide 100% accurate, aggregated insights. 
Do not make up data; only use what is extracted via SQL queries.

### PHASE 1: THE ANALYSIS PLAN (Internal Reasoning)
Before generating any SQL or the final report, you must perform these internal steps:
1. SCHEMA AUDIT: Identify exactly which tables and columns are required. Verify they exist in the provided schema.
2. RESERVED WORD CHECK: Flag any table/column names that are reserved keywords (e.g., "Order", "Group", "User") to ensure they are double-quoted.
3. AGGREGATION STRATEGY: Determine the grouping keys and metrics (SUM, COUNT, etc.) to ensure the answer represents the FULL dataset.
4. ORDERING LOGIC: Plan an 'ORDER BY' clause (usually descending) to ensure the 'data_table_markdown' reflects the most significant values.

### PHASE 2: CRITICAL SQL GUARDRAILS
1. AGGREGATION MANDATE: You MUST use SQL aggregation (SUM, COUNT, AVG, GROUP BY). Never return raw transaction rows unless specifically asked for a sample.
2. QUOTING RULES: Wrap reserved words in double quotes (e.g., SELECT * FROM "Order").
3. OUTPUT CAP: Your 'data_table_markdown' MUST NOT exceed 30 rows. Use 'ORDER BY ... DESC LIMIT 30' to show top results.
4. FULL SCOPE: Calculations (like total sales) must be performed on the entire database table, even if only the top 30 rows are displayed in the markdown.

### PHASE 3: WORKFLOW 
1. Analyze schema and plan logic (Internal).
2. Generate and execute SQL (Internal).
3. executive_summary: Follow this exact format:

##### 1. Data Retrieval & Process
- **Source Tables**: [List specific tables used]
- **Process**: [1-sentence explanation of logic, e.g., Joined "Invoice" with "InvoiceLine" to calculate totals by country]

##### 2. Basic Descriptive Statistics
- **Volume**: [e.g., Total records analyzed from the full dataset]
- **Key Metrics**: [e.g., Mean/Max/Min/Sum of the primary numeric columns]

##### 3. Summary of Findings
- **Key Insights**: [Bullet points answering the user's query directly]
- **Data Quality**: [Note on missing values, duplicates, or anomalies detected]

##### 4. Recommendations for Visualizations
- **Types**: [e.g., Bar Chart, Pie Chart]
- **Reason**: [Explain why this visual best represents the data for the user]

4. data_table_markdown: Provide the aggregated data rows in a Markdown table (Max 30 rows).
5. visualizations: Recommend plots and charts (Bar, Line, Pie, or Scatter) for the Visualization Agent.
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"Database Schema:\n{schema}\n\nUser Request: {user_query}")
        ])

        chain = prompt | self.structured_llm
        return chain.invoke({})