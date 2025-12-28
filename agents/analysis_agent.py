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

    def run_analysis(self, user_query, db_uri):
        schema = self.get_schema(db_uri)
        
        system_prompt = """
        You are an expert Data Analyst Agent for SQLite.
        
        CRITICAL SQL RULES:
        1. If a table or column name is a reserved word (like 'Order', 'Group', 'User', 'Table'), you MUST wrap it in double quotes. 
           Example: SELECT * FROM "Order" WHERE "Group" = 'A'.
        2. Always use standard SQLite syntax.
        
        WORKFLOW:
        1. Analyze the schema and user query.
        2. Internal Logic: Generate and execute SQL to get facts.
        3. executive_summary: Write a professional summary of findings.
        4. data_table_markdown: Provide the raw data rows in a Markdown table.
        5. visualizations: Recommend 1-3 charts based on the data analysis results.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"Database Schema:\n{schema}\n\nUser Request: {user_query}")
        ])

        chain = prompt | self.structured_llm
        return chain.invoke({})