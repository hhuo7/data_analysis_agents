import sqlite3
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .models import AnalysisResponse, SQLQuery

class DataAnalysisAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.sql_llm = self.llm.with_structured_output(SQLQuery)
        self.structured_llm = self.llm.with_structured_output(AnalysisResponse)

    def get_schema(self, db_uri):
        conn = sqlite3.connect(db_uri)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema_info = ""
        for table in tables:
            table_name = table[0]
            # Get columns
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            col_desc = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
            
            # Get relationships (Foreign Keys)
            cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
            fks = cursor.fetchall()
            fk_desc = ""
            if fks:
                fk_desc = " | Relationships: " + ", ".join([f"{fk[3]} references {fk[2]}({fk[4]})" for fk in fks])
                
            schema_info += f"Table: {table_name} | Columns: {col_desc}{fk_desc}\n"
        conn.close()
        return schema_info

    def execute_sql(self, db_uri, sql):
        try:
            conn = sqlite3.connect(db_uri)
            # Use pandas for easy markdown conversion and handling
            df = pd.read_sql_query(sql, conn)
            conn.close()
            if df.empty:
                return "No data found for this query."
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error executing SQL: {str(e)}"

    def run_analysis(self, user_query, db_uri, state: dict = None):
        schema = self.get_schema(db_uri)
        
        # Simple guardrail: basic input validation
        if len(user_query) > 1000:
            raise ValueError("Query too long")
        dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter']
        if any(word in user_query.lower() for word in dangerous_keywords):
            raise ValueError("Query contains potentially dangerous keywords")
        
        # Step 1: Generate SQL
        sql_system_prompt = """
        You are an expert SQL generator for SQLite. 
        Your task is to write a single, optimized SQL query that answers the user's request based on the provided schema.
        
        CRITICAL RULES FOR COMPLETE ANALYSIS:
        1. DATA EXPLORATION: Always consider all tables in the schema. If a query about "sales" can be enriched by joining "products" or "customers", do so.
        2. FULL DATA UTILIZATION: Your queries must analyze the entire available dataset (e.g., use SUM/AVG on the whole table) before limiting the output rows.
        3. AGGREGATION MANDATE: Use aggregation (SUM, COUNT, etc.) to provide high-level insights unless raw data is specifically requested.
        4. QUOTING: Always use double quotes for table or column names that are reserved words (e.g., "Order", "Group").
        5. TOP RESULTS: Limit your final output to 30 rows using 'ORDER BY ... DESC LIMIT 30' to ensure we see the most significant data.
        """
        sql_prompt = ChatPromptTemplate.from_messages([
            ("system", sql_system_prompt),
            ("human", f"Database Schema:\n{schema}\n\nUser Request: {user_query}")
        ])
        sql_chain = sql_prompt | self.sql_llm
        sql_res = sql_chain.invoke({})
        
        # Step 2: Execute SQL
        data_results = self.execute_sql(db_uri, sql_res.sql)
        
        # Step 3: Generate Final Report
        report_system_prompt = """
You are an expert Data Analyst Agent for SQLite. Your goal is to provide 100% accurate, aggregated insights based on ACTUAL data results.

### PHASE 1: WORKFLOW 
1. Use the 'Data Results' provided to answer the user query.
2. If the 'Data Results' contains an error or is empty, explain that in the summary.
3. executive_summary: Follow this exact format:

##### 1. Data Retrieval & Process
- **Source Tables**: [List specific tables used]
- **Process**: [1-sentence explanation of logic, e.g., Joined "Invoice" with "InvoiceLine" to calculate totals by country]

##### 2. Basic Descriptive Statistics
- **Volume**: [e.g., Total records analyzed from the full dataset]
- **Key Metrics**: [e.g., Mean/Max/Min/Sum of the primary numeric columns]

##### 3. Summary of Findings
- **Key Insights**: [Bullet points answering the user's query directly using the actual data]
- **Data Quality**: [Note on missing values, duplicates, or anomalies detected]

##### 4. Recommendations for Visualizations
- **Types**: [e.g., Bar Chart, Pie Chart]
- **Reason**: [Explain why this visual best represents the data for the user]

4. data_table_markdown: Provide the aggregated data rows in a Markdown table (copy the Data Results provided).
5. visualizations: Recommend plots and charts (Bar, Line, Pie, or Scatter) for the Visualization Agent.
"""
        report_prompt = ChatPromptTemplate.from_messages([
            ("system", report_system_prompt),
            ("human", f"User Request: {user_query}\n\nSQL Used: {sql_res.sql}\n\nData Results:\n{data_results}")
        ])

        report_chain = report_prompt | self.structured_llm
        return report_chain.invoke({})
