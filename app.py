import streamlit as st
import os
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT VARIABLES AT THE VERY TOP
load_dotenv()

# 2. VERIFY KEY (Optional Debugging)
if not os.getenv("OPENAI_API_KEY"):
    st.error("API Key not found. Please check your .env file in the project root.")
    st.stop()

# 3. IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import manager
from agents.workflow import create_bi_workflow

# 4. INITIALIZATION
manager.init_mgmt_db()
st.set_page_config(page_title="Autonomous BI Platform", layout="wide")

# 5. PDF REPORT ENGINE
def create_pdf(analysis_report, plot_buf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Business Intelligence Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, "1. Analysis Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("helvetica", size=11)
    clean_text = analysis_report.executive_summary.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    if plot_buf:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, "2. Visual Representation", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        plot_buf.seek(0)
        pdf.image(plot_buf, x=15, w=180)
        
    return pdf.output()

# 6. SIDEBAR & ACCESS CONTROL
with st.sidebar:
    st.title("🛡️ Access Control")
    user_role = st.selectbox("Login As", manager.get_all_users())
    allowed_dbs = manager.get_allowed_databases(user_role)
    
    st.divider()
    with st.expander("➕ Upload Database"):
        up_file = st.file_uploader("Upload .sqlite", type=["sqlite", "db"])
        up_name = st.text_input("DB Nickname")
        if st.button("Register Database"):
            if up_file and up_name:
                if not os.path.exists("data"): os.makedirs("data")
                path = f"data/{up_file.name}"
                with open(path, "wb") as f: f.write(up_file.getbuffer())
                manager.add_database_to_mgmt(up_name, path, user_role)
                st.success("Database Integrated!")
                st.rerun()

# 7. MAIN INTERFACE
tab_main, tab_admin = st.tabs(["📊 Intelligent Dashboard", "🛠️ Admin Panel"])

with tab_main:
    if not allowed_dbs:
        st.warning("No databases assigned to your account.")
    else:
        db_name = st.selectbox("Select Target Database", list(allowed_dbs.keys()))
        db_path = allowed_dbs[db_name]
        
        st.divider()
        st.markdown("### Agent Analysis")
        
        query = st.text_input("Enter Analysis Query", placeholder="e.g., Analyze the monthly sales growth...")
        
        col_c1, col_c2 = st.columns(2)
        pref = col_c1.selectbox("Preferred Chart", ["Auto", "Bar", "Line", "Pie", "Scatter"])
        hint = col_c2.text_input("Style Hints", placeholder="e.g., use dark blue theme")

        if st.button("🚀 Run Workflow", use_container_width=True) and query:
            with st.spinner("Agents are collaborating on your data..."):
                # LAZY INITIALIZATION OF WORKFLOW
                bi_app = create_bi_workflow()
                
                state = {
                    "user_query": query,
                    "db_uri": db_path,
                    "user_role": user_role,
                    "chart_preference": pref,
                    "viz_hint": hint,
                    "errors": []
                }
                
                result = bi_app.invoke(state)
                
                if result.get("errors"):
                    st.error(f"Workflow Error: {result['errors']}")
                else:
                    st.session_state['workflow_result'] = result

        # DISPLAY RESULTS
        if 'workflow_result' in st.session_state:
            res = st.session_state['workflow_result']
            report = res['analysis_report']
            
            st.markdown("#### 📋 Report Summary")
            st.info(report.executive_summary)
            
            with st.expander("View Raw Data Table"):
                st.markdown(report.data_table_markdown)
            
            st.markdown("#### 🎨 Generated Visuals")
            try:
                plt.close('all')
                exec_env = {"plt": plt, "sns": sns, "pd": pd, "st": st, "px": px, "io": io}
                
                # Execute AI-generated visualization code
                clean_code = res['viz_code'].replace("```python", "").replace("```", "")
                exec(clean_code, exec_env)

                # Display all figures
                fig_nums = plt.get_fignums()
                if fig_nums:
                    cols = st.columns(len(fig_nums)) if len(fig_nums) > 1 else [st]
                    for i, fig_num in enumerate(fig_nums):
                        plt.figure(fig_num)
                        with cols[i % len(cols)]:
                            st.pyplot(plt.gcf())
                    
                    # Save the last figure for PDF
                    buf = io.BytesIO()
                    plt.gcf().savefig(buf, format="png", bbox_inches='tight', dpi=120)
                    st.session_state['last_plot_buf'] = buf
                else:
                    st.warning("No visualizations were generated.")
            except Exception as e:
                st.error(f"Visualization Execution Error: {e}")
            
            if 'last_plot_buf' in st.session_state:
                pdf_data = create_pdf(report, st.session_state['last_plot_buf'])
                st.download_button(
                    label="✨ Download Business Report (PDF)",
                    data=bytes(pdf_data),
                    file_name="Business_Insight_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# 8. ADMIN INTERFACE
with tab_admin:
    if user_role == "admin":
        st.header("🔑 User Permission Management")
        target_user = st.selectbox("Select Target User", [u for u in manager.get_all_users() if u != 'admin'])
        all_dbs_meta = manager.get_all_databases_metadata()
        
        current_perms = list(manager.get_allowed_databases(target_user).keys())
        new_perms = st.multiselect("Grant Access To", options=all_dbs_meta, default=current_perms)
        
        if st.button("Save Permissions", use_container_width=True):
            manager.update_user_permissions(target_user, new_perms)
            st.success(f"Permissions updated for {target_user}")
    else:
        st.error("Access Denied: Admin privileges required.")