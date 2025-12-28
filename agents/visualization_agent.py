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
        5. Multiple Charts: If the analysis suggests multiple charts, generate code for all of them using subplots or separate figures.

        ### TECHNICAL CONSTRAINTS:
        - Input Data: Use the provided 'data_table_markdown' to create a pandas DataFrame within the code.
        - Execution: Your output must be ONLY a block of Python code inside ```python ``` markers.
        - Streamlit Integration: Use 'st.pyplot(plt)' or 'st.plotly_chart(fig)' to render the charts.
        """

        # Contextualizing the prompt with the analysis and user hints
        human_message = f"""
        Analysis Summary: {analysis_report.executive_summary}
        Data Table (Markdown): {analysis_report.data_table_markdown}
        Recommended Visuals: {analysis_report.visualizations}
        
        User Preferences:
        - Desired Chart Type: {user_chart_preference}
        - Visual Hints: {user_hint}
        
        Generate the Python code now.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])

        chain = prompt | self.llm
        
        response = chain.invoke({})
        return response.content