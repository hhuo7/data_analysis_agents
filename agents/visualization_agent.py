from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class VisualizationAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)

    def generate_viz_code(self, analysis_report, user_chart_preference="Auto", user_hint=""):
        """
        Generates executable Python code for visualizations based on the Analysis Agent's output.
        
        Args:
            analysis_report: The AnalysisResponse object from the previous step.
            user_chart_preference: Specific chart type selected in UI (e.g., 'Bar Chart').
            user_hint: Extra styling or focus instructions from the user.
        """
        
        system_prompt = """
        You are an expert Data Visualization Agent. Your task is to write high-quality Python code 
        using Matplotlib, Seaborn, or Plotly to visualize analyzed data.

        ### COMPANY STYLE GUIDELINES:
        1. Aesthetics: Use a clean, minimalist professional look (e.g., white background, no unnecessary borders).
        2. Color Palette: Use professional "Corporate" colors (e.g., Deep Blues, Slate Greys, muted Greens).
        3. Clarity: Every chart MUST have a clear Title, X/Y Axis Labels, and a Legend if multiple series exist.
        4. Resolution: Set 'dpi=120' for Matplotlib figures.
        5. Size: Set figure size to (8, 5) or smaller for better fit in the interface.
        6. Multiple Charts: If the analysis suggests multiple charts, generate code for all of them using subplots or separate figures, and display each with st.pyplot(plt) or st.plotly_chart(fig).

        ### TECHNICAL CONSTRAINTS:
        - Input Data: Use the provided 'data_table_markdown' to create a pandas DataFrame within the code.
        - Execution: Your output must be ONLY a block of Python code inside ```python ``` markers.
        - Streamlit Integration: Use 'st.pyplot(plt)' or 'st.plotly_chart(fig)' to render the charts.
        - CRITICAL: Never use 'with plt' or 'with sns'. Modules are not context managers.
        - Use standard plotting calls like 'plt.figure()' and 'plt.plot()'.
        - Do not use 'with plt.subplots()' unless you assign it to variables like 'fig, ax = plt.subplots()'.
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
        
        User Preferences:
        - Desired Chart Type: {user_chart_preference}
        - Visual Hints: {user_hint}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])

        chain = prompt | self.llm
        
        response = chain.invoke({})
        return response.content