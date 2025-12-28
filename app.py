import streamlit as st
import os
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import markdown2
from xhtml2pdf import pisa
from dotenv import load_dotenv

import manager
from agents.workflow import create_bi_workflow

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("API Key missing.")
    st.stop()

manager.init_mgmt_db()
st.set_page_config(page_title="AI BI Platform", layout="wide")

def create_styled_pdf(analysis_report, plot_buffers):
    images_html = ""
    for buf in plot_buffers:
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        images_html += f'<div class="chart"><img src="data:image/png;base64,{img_b64}" /></div>'

    # Convert Markdown to HTML with Table support
    summary_html = markdown2.markdown(analysis_report.executive_summary)
    table_html = markdown2.markdown(analysis_report.data_table_markdown, extras=["tables"])

    html_template = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 1.5cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #333; }}
            h1 {{ text-align: center; color: #1a4e8a; border-bottom: 2px solid #1a4e8a; }}
            h2 {{ color: #2c3e50; margin-top: 20px; border-left: 5px solid #1a4e8a; padding-left: 10px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .chart {{ text-align: center; margin-top: 20px; }}
            .chart img {{ width: 100%; max-width: 550px; }}
        </style>
    </head>
    <body>
        <h1>Business Intelligence Report</h1>
        <h2>1. Executive Summary</h2>
        <div>{summary_html}</div>
        <h2>2. Data Insights</h2>
        <div>{table_html}</div>
        <pdf:nextpage />
        <h2>3. Visual Analytics</h2>
        {images_html}
    </body>
    </html>
    """
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_template), dest=pdf_buffer)
    return pdf_buffer.getvalue()

with st.sidebar:
    st.title("🛡️ Access Control")
    user_role = st.selectbox("Login As", manager.get_all_users())
    allowed_dbs = manager.get_allowed_databases(user_role)
    
    st.divider()
    with st.expander("➕ Upload Database"):
        up_file = st.file_uploader("Upload .sqlite", type=["sqlite", "db"])
        up_name = st.text_input("DB Nickname")
        if st.button("Register"):
            if up_file and up_name:
                if not os.path.exists("data"): os.makedirs("data")
                path = f"data/{up_file.name}"
                with open(path, "wb") as f: f.write(up_file.getbuffer())
                manager.add_database_to_mgmt(up_name, path, user_role)
                st.rerun()

tab_main, tab_admin = st.tabs(["📊 Dashboard", "🛠️ Admin"])

with tab_main:
    if not allowed_dbs:
        st.warning("No databases assigned.")
    else:
        db_name = st.selectbox("Database", list(allowed_dbs.keys()))
        db_path = allowed_dbs[db_name]
        query = st.text_input("Analysis Query")
        
        c1, c2 = st.columns(2)
        pref = c1.selectbox("Chart Type", ["Auto", "Bar", "Line", "Pie", "Scatter"])
        hint = c2.text_input("Style Hint")

        if st.button("🚀 Run Workflow", use_container_width=True) and query:
            with st.spinner("Processing..."):
                bi_app = create_bi_workflow()
                res = bi_app.invoke({
                    "user_query": query, "db_uri": db_path, "user_role": user_role,
                    "chart_preference": pref, "viz_hint": hint, "errors": []
                })
                if res.get("errors"): st.error(res['errors'])
                else: st.session_state['workflow_result'] = res

        if 'workflow_result' in st.session_state:
            res = st.session_state['workflow_result']
            report = res['analysis_report']
            
            st.markdown("### Summary")
            st.info(report.executive_summary)
            
            with st.expander("Data Table"):
                st.markdown(report.data_table_markdown)
            
            all_bufs = []
            try:
                # 1. Clear previous figures to prevent memory leaks and ghost plots
                plt.close('all')
                plt.clf()
                
                # 2. Prepare environment
                exec_env = {
                    "plt": plt, 
                    "sns": sns, 
                    "pd": pd, 
                    "st": st, 
                    "px": px, 
                    "io": io,
                    "np": __import__('numpy') # AI often uses numpy
                }
                
                # 3. Clean and isolate the code
                code = res['viz_code'].replace("```python", "").replace("```", "").strip()
                
                # 4. Execute (No 'with' context here)
                exec(code, exec_env)

                # 5. Capture figures
                fig_nums = plt.get_fignums()
                if fig_nums:
                    cols = st.columns(len(fig_nums)) if len(fig_nums) > 1 else [st]
                    for i, num in enumerate(fig_nums):
                        fig = plt.figure(num)
                        # Ensure the figure actually has content
                        if fig.get_axes():
                            with cols[i % len(cols)]: 
                                st.pyplot(fig)
                            
                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", bbox_inches='tight', dpi=120)
                            all_bufs.append(buf)
                    
                    st.session_state['pdf_bufs'] = all_bufs
                else:
                    # Fallback if AI used Plotly (px) instead of Matplotlib
                    st.info("Check if the agent generated interactive Plotly charts.")
                    
            except Exception as e:
                st.error(f"Visualization Logic Error: {e}")
                st.info("The AI attempted to use an invalid syntax. Try re-running the query.")

            if 'pdf_bufs' in st.session_state:
                pdf_data = create_styled_pdf(report, st.session_state['pdf_bufs'])
                st.download_button("📥 Download PDF Report", pdf_data, "Report.pdf", "application/pdf", use_container_width=True)

with tab_admin:
    if user_role == "admin":
        target = st.selectbox("User", [u for u in manager.get_all_users() if u != 'admin'])
        dbs = manager.get_all_databases_metadata()
        perms = st.multiselect("Access", options=dbs, default=list(manager.get_allowed_databases(target).keys()))
        if st.button("Save"):
            manager.update_user_permissions(target, perms)
            st.success("Updated")
    else:
        st.error("Admin only.")