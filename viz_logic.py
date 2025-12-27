import os
from langchain_openai import ChatOpenAI

COMPANY_STYLE = """
- Palette: ['#1E3A8A', '#64748B', '#F59E0B', '#10B981', '#EF4444']
- Style: 'seaborn-v0_8-whitegrid'
- Rules: Always include 'st.pyplot(plt.gcf())'. Ensure labels and titles are clear.
"""

VIZ_SYSTEM_PROMPT = f"""
You are a Data Visualization Expert. 
Input: 1. A Data Analysis Report. 2. A preferred Chart Type. 3. Specific Viz Instructions.

### Task:
1. If 'Chart Type' is not 'Auto', force use of that type.
2. If 'Chart Type' is 'Auto', analyze the data and pick the best format (Bar, Line, Pie, etc.).
3. Apply branding: {COMPANY_STYLE}
4. Output ONLY raw Python code using Matplotlib/Seaborn.

The code must end with st.pyplot(plt.gcf()) to display the chart.
If the data is insufficient for the requested chart type, fall back to a simple Bar Chart instead of failing.
"""

def generate_visualization(analysis_report, chart_type, custom_viz_request):
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
    ANALYSIS REPORT: {analysis_report}
    PREFERRED CHART TYPE: {chart_type}
    CUSTOM VIZ INSTRUCTIONS: {custom_viz_request}
    
    Generate the code.
    """
    
    response = llm.invoke([("system", VIZ_SYSTEM_PROMPT), ("user", prompt)])
    return response.content.replace("```python", "").replace("```", "").strip()