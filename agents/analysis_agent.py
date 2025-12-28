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
        Do not make up any data; only use what you can extract via SQL queries.

        CRITICAL SQL RULES:
        1. If a table or column name is a reserved word (like 'Order', 'Group', 'User', 'Table'), you MUST wrap it in double quotes. 
           Example: SELECT * FROM "Order" WHERE "Group" = 'A'.
        2. Always use standard SQLite syntax.

        3. Ensure the Executive Summary reflects the totals from the full dataset, not just the displayed rows.
        CRITICAL OUTPUT RULES:
        1. ALWAYS AGGREGATE: You must use SQL aggregation (SUM, COUNT, AVG, GROUP BY) to summarize data. 
           NEVER list raw individual transactions or rows unless specifically asked for a small sample.
        2. TABLE LIMIT: Your 'data_table_markdown' MUST NOT exceed 30 rows. 
           If there are more than 30 categories, use 'ORDER BY' to show the top 30 and group the rest into 'Others'.
        3. BE CONCISE: Use bullet points in 'executive_summary'. Do not repeat the data table in the text.

        SQL SYNTAX:
        - Wrap reserved words in double quotes: SELECT SUM(Total) FROM "Order".
        - For 'Sales Volume by Country', your SQL should look like: 
          SELECT BillingCountry, SUM(Total) as TotalSales FROM Invoice GROUP BY BillingCountry ORDER BY TotalSales DESC.
               
        WORKFLOW:
        1. Analyze the schema and user query.
        2. Internal Logic: Generate and execute SQL to get facts.
        3. executive_summary: Write a professional summary of findings. Output as exactly follows:
        ### 1.  Data Retrieval & Process

        - **Source Tables**: [List the specific tables used]

        - **Process**: [1-sentence explanation of the SQL logic, e.g., Joined Invoice with Customer and grouped by Country]



        ### 2. Basic Descriptive Statistics

        - **Volume**: [e.g., Total records analyzed]

        - **Key Metrics**: [e.g., Mean/Max/Min values of the primary numeric column]



        ### 3. Summary of Findings

        - **Key Insights**: [Main answer to the user's query]

        - **Data Quality**: [Note on missing values, duplicates, or format consistency]



        ### 4. Recommendations for Visualizations

        - **Types**: [e.g., Bar Chart, Line Graph]

        - **Reason**: [Why this chart fits the data] 
        
        4. data_table_markdown: Provide the raw data rows in a Markdown table.
        5. visualizations: Recommend 1-3 charts based on the data analysis results.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"Database Schema:\n{schema}\n\nUser Request: {user_query}")
        ])

        chain = prompt | self.structured_llm
        return chain.invoke({})