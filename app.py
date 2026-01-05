import streamlit as st
import os
import io
import base64
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import markdown2
from fpdf import FPDF
from dotenv import load_dotenv

import manager
from agents.workflow import create_bi_workflow

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("API Key missing. Please check your .env file.")
    st.stop()

manager.init_mgmt_db()
st.set_page_config(page_title="Data Analysis Platform", layout="wide")


STYLE_CONFIG = {
    "Professional Business": {
        "plt_style": "seaborn-v0_8-muted",
        "sns_palette": "Blues_d",
        "context": "notebook",
        "extra_code": "plt.rcParams['axes.spines.top'] = False; plt.rcParams['axes.spines.right'] = False;"
    },
    "High-Contrast Dark": {
        "plt_style": "dark_background",
        "sns_palette": "magma",
        "context": "talk",
        "extra_code": "plt.rcParams['grid.color'] = '#444444'; plt.rcParams['axes.facecolor'] = '#121212';"
    },
    "Scientific Report": {
        "plt_style": "ggplot",
        "sns_palette": "Greys_r",
        "context": "paper",
        "extra_code": "plt.rcParams['font.serif'] = ['Times New Roman']; plt.grid(True, linestyle='--')"
    },
    "Vibrant & Bold": {
        "plt_style": "bmh",
        "sns_palette": "husl",
        "context": "poster",
        "extra_code": "plt.rcParams['axes.labelweight'] = 'bold';"
    }
}


def create_styled_pdf(analysis_report, plot_buffers):
    """
    Generates a professional PDF report using fpdf2.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_text_color(26, 78, 138)  # Professional Blue
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 20, "Data Analysis Report", ln=True, align="C")
    
    pdf.set_draw_color(26, 78, 138)
    pdf.set_line_width(0.5)
    pdf.line(10, 35, 200, 35)
    pdf.ln(10)
    
    pdf.set_text_color(44, 62, 80)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(51, 51, 51)
    summary_html = markdown2.markdown(analysis_report.executive_summary)
    pdf.write_html(summary_html)
    pdf.ln(10)
    
    pdf.set_text_color(44, 62, 80)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "2. Data Insights (Top Records)", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 9)
    table_html = markdown2.markdown(analysis_report.data_table_markdown, extras=["tables"])
  
    pdf.write_html(table_html)
    
    if plot_buffers:
        pdf.add_page()
        pdf.set_text_color(44, 62, 80)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "3. Visual Analytics", ln=True)
        pdf.ln(5)
        
        for buf in plot_buffers:
            buf.seek(0)

            pdf.image(buf, w=pdf.epw)
            pdf.ln(10)
            
    return bytes(pdf.output())


with st.sidebar:
    st.title("🛡️ Access Control")
    user_role = st.selectbox("Current User Session", manager.get_all_users())
    allowed_dbs = manager.get_allowed_databases(user_role)

    st.divider()
    with st.expander("➕ Register New Database"):
        up_file = st.file_uploader("Upload SQLite File", type=["sqlite", "db"])
        up_name = st.text_input("Database Nickname (e.g., Sales_2024)")
        if st.button("Upload and Register"):
            if up_file and up_name:
                if not os.path.exists("data"):
                    os.makedirs("data")
                path = f"data/{up_file.name}"
                with open(path, "wb") as f:
                    f.write(up_file.getbuffer())
                manager.add_database_to_mgmt(up_name, path, user_role)
                st.success(f"Registered {up_name} successfully!")
                st.rerun()
            else:
                if not up_file:
                    st.error("Please upload a SQLite file.")
                if not up_name:
                    st.error("Please enter a database nickname.")


tab_main, tab_admin = st.tabs(["📊 Analysis Dashboard", "🛠️ System Administration"])

with tab_main:
    if not allowed_dbs:
        st.warning("No databases assigned to your profile. Contact your administrator.")
    else:
        db_name = st.selectbox("Select Target Database", list(allowed_dbs.keys()))
        db_path = allowed_dbs[db_name]
        query = st.text_area(
            "What would you like to analyze?",
            placeholder="e.g., Show total sales volume by country. Please be specific in your request."
        )

        selected_theme = st.selectbox("Report Visual Theme", list(STYLE_CONFIG.keys()))

        if st.button("🚀 Execute Workflow", use_container_width=True) and query:
            with st.spinner(f"AI Agents are analyzing {db_name}..."):
                bi_app = create_bi_workflow()
                res = bi_app.invoke(
                    {
                        "user_query": query,
                        "db_uri": db_path,
                        "user_role": user_role,
                        "errors": [],
                    }
                )

                if res.get("errors"):
                    st.error(f"Workflow Error: {res['errors']}")
                else:
                    st.session_state["workflow_result"] = res

        
        if "workflow_result" in st.session_state:
            res = st.session_state["workflow_result"]
            report = res["analysis_report"]

            st.divider()
            st.subheader("📝 Executive Summary")
            st.info(report.executive_summary)

            with st.expander("📂 View Source Data Table"):
                st.markdown(report.data_table_markdown)

            st.subheader("📈 Visualizations")
            all_bufs = []

            try:
                
                plt.close("all")                
                cfg = STYLE_CONFIG[selected_theme]                
                style_preamble = f"""import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
plt.style.use('{cfg['plt_style']}')
sns.set_palette('{cfg['sns_palette']}')
sns.set_context('{cfg['context']}')
{cfg['extra_code']}"""

                
                exec_env = {
                    "plt": plt,
                    "sns": sns,
                    "pd": pd,
                    "px": px,
                    "io": io,
                    "np": __import__("numpy"),
                }


                raw_ai_code = (
                    res["viz_code"]
                    .replace("```python", "")
                    .replace("```", "")
                    .strip()
                )

               
                cleaned_ai_code = re.sub(r"plt\.style\.use$.*$", "", raw_ai_code)
             
                cleaned_ai_code = re.sub(r"plt\.show\(\)", "", cleaned_ai_code)

                cleaned_ai_code = re.sub(r"'(\d+)%'", r'\1', cleaned_ai_code)
                cleaned_ai_code = re.sub(r'"(\d+)%', r'\1', cleaned_ai_code)

                cleaned_ai_code = cleaned_ai_code.replace('.applymap(', '.map(')

                # Remove obvious invalid context-manager usage lines
                cleaned_ai_code = "\n".join(
                    [
                        line
                        for line in cleaned_ai_code.split("\n")
                        if not line.strip().startswith("with plt")
                        and not line.strip().startswith("with sns")
                        and not line.strip().startswith("with px")
                    ]
                )

                final_exec_code = style_preamble + "\n" + cleaned_ai_code

               
                try:
                    exec(final_exec_code, exec_env)
                except (TypeError, ValueError, IndentationError) as e:
                    if (
                        "'module' object does not support the context manager protocol" in str(e)
                        or "cannot convert float NaN to integer" in str(e)
                        or "unexpected indent" in str(e)
                        or "could not convert string to float" in str(e)
                    ):
                        st.info(
                            "Visualization could not be generated due to code issues. "
                            "Showing analysis results only."
                        )
                    else:
                        raise

             
                fig_nums = plt.get_fignums()
                if fig_nums:
                    cols = st.columns(len(fig_nums)) if len(fig_nums) > 1 else None

                    for i, num in enumerate(fig_nums):
                        fig = plt.figure(num)
                        if fig.get_axes():
                            if cols:
                                cols[i % len(cols)].pyplot(fig)
                            else:
                                st.pyplot(fig)

                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                            all_bufs.append(buf)

                    st.session_state["pdf_bufs"] = all_bufs
                else:
                    st.info("The AI generated a textual insight or non-Matplotlib visualization.")

                with st.expander("🛠️ View Internal Analysis Logic"):
                    st.code(final_exec_code, language="python")

            except Exception as e:
                st.error(f"Visualization Execution Error: {e}")

          
            if "pdf_bufs" in st.session_state and st.session_state["pdf_bufs"]:
                pdf_data = create_styled_pdf(report, st.session_state["pdf_bufs"])
                st.download_button(
                    label="📥 Download Full PDF Report",
                    data=pdf_data,
                    file_name=f"DA_Report_{db_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )


with tab_admin:
    if user_role == "admin":
        st.subheader("User Permissions Management")
        all_users = manager.get_all_users()
        target = st.selectbox("Select User to Edit", [u for u in all_users if u != "admin"])

        available_dbs = manager.get_all_databases_metadata()
        current_perms = list(manager.get_allowed_databases(target).keys())

        new_perms = st.multiselect(
            "Assign Database Access", options=available_dbs, default=current_perms
        )

        if st.button("Update Permissions"):
            manager.update_user_permissions(target, new_perms)
            st.success(f"Permissions for {target} updated successfully.")
    else:
        st.error("Access Denied: Administrative privileges required.")