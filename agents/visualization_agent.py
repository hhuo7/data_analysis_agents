from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class VisualizationAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)

    def generate_viz_code(self, analysis_report):
        """
        Generates executable Python code for visualizations based on the Analysis Agent's output.
        
        Args:
            analysis_report: The AnalysisResponse object from the previous step.
        """
        
        system_prompt = """
        You are an expert Data Visualization Agent. Your task is to write high-quality Python code 
        using Matplotlib, Seaborn, or Plotly to visualize analyzed data.

        ### TECHNICAL CONSTRAINTS:
        - Input Data: Use the provided 'data_table_markdown' to create a pandas DataFrame within the code.
        - Execution: Your output must be ONLY a block of Python code inside ```python ``` markers.

        - CRITICAL: NEVER use 'with plt' or 'with sns' or any 'with module:'. Modules are NOT context managers and will cause errors. Do NOT use any 'with' statements involving plt or sns. NEVER write 'with plt:' or 'with sns:' - this is INVALID and will fail.
        - Use standard plotting calls like 'plt.figure()' and 'plt.plot()'.
        - Do not use 'with plt.subplots()' unless you assign it to variables like 'fig, ax = plt.subplots()'.
        - NEVER use context managers for matplotlib or seaborn modules.
        - Execution: Your output must be ONLY a block of Python code inside ```python ``` markers.
        
        CRITICAL INSTRUCTIONS:
            1. DATA PARSING: Use `io.StringIO` and `pd.read_table`. 
               To handle Markdown tables correctly, follow this pattern:
               
               import io
               import pandas as pd
               
               data = \"\"\"{{markdown_table}}\"\"\"
               # Remove leading/trailing whitespace from the markdown string
               data = data.strip()
               
               # Read the table, filtering out empty columns caused by leading/trailing pipes
               df = pd.read_table(io.StringIO(data), sep="|", skipinitialspace=True)
               df = df.dropna(axis=1, how='all').iloc[1:] # Drop empty cols and the '---' separator row
               
               # Clean column names and data
               df.columns = [c.strip() for c in df.columns if 'Unnamed' not in c]
               df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
               # Handle missing values
               df = df.fillna(0)

            2. ACCURACY: Do not manually type out data points. Always use the DataFrame created from the source text.
            3. ROBUSTNESS: If a bracket or parenthesis is opened, it MUST be closed.
            4. CLEANUP: Use plt.close('all') before starting a new plot.
            5. For multiple charts: If creating multiple figures, call st.pyplot(plt) after each figure is complete, and use plt.figure() to start a new one.

                
        Generate the Python code now.
        """
        # Contextualizing the prompt with the analysis and user hints
        human_message = f"""
        Analysis Summary: {analysis_report.executive_summary}
        Data Table (Markdown): {analysis_report.data_table_markdown}
        Recommended Visuals: {analysis_report.visualizations}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])

        chain = prompt | self.llm
        
        for attempt in range(3):
            response = chain.invoke({})
            content = response.content
            if 'with plt' not in content and 'with sns' not in content:
                return content
        
        # If all attempts fail, return the last one anyway
        return content