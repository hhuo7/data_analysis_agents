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
from xhtml2pdf import pisa
from dotenv import load_dotenv

# Internal imports
import manager
from agents.workflow import create_bi_workflow

# 1. INITIAL SETUP
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("API Key missing. Please check your .env file.")
    st.stop()

manager.init_mgmt_db()
st.set_page_config(page_title="Data Analysis Platform", layout="wide")

# 2. DYNAMIC PARAMETER MAPPING (Style Config)
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

# 3. PDF GENERATION 
def create_styled_pdf(analysis_report, plot_buffers):
    images_html = ""
    for buf in plot_buffers:
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        images_html += f'<div class="chart"><img src="data:image/png;base64,{img_b64}" /></div>'

    summary_html = markdown2.markdown(analysis_report.executive_summary)
    table_html = markdown2.markdown(analysis_report.data_table_markdown, extras=["tables"])

    html_template = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 1.5cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; }}
            h1 {{ text-align: center; color: #1a4e8a; border-bottom: 2px solid #1a4e8a; padding-bottom: 10px; }}
            h2 {{ color: #2c3e50; margin-top: 30px; border-left: 5px solid #1a4e8a; padding-left: 10px; background-color: #f8f9fa; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 9px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #1a4e8a; color: white; font-weight: bold; }}
            .chart {{ text-align: center; margin-top: 25px; page-break-inside: avoid; }}
            .chart img {{ width: 100%; max-width: 500px; border: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <h1>Data Analysis Report</h1>
        <h2>1. Executive Summary</h2>
        <div>{summary_html}</div>
        <h2>2. Data Insights (Top Records)</h2>
        <div class="table-container">{table_html}</div>
        <pdf:nextpage />
        <h2>3. Visual Analytics</h2>
        {images_html}
    </body>
    </html>
    """
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_template), dest=pdf_buffer)
    return pdf_buffer.getvalue()

# 4. SIDEBAR & ACCESS CONTROL
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

# 5. MAIN UI TABS
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

        # 6. DISPLAY RESULTS
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
                # Clear Plot State
                plt.close("all")

                # Fetch Config for Mapping
                cfg = STYLE_CONFIG[selected_theme]

                # Build Style Preamble (Forces the Theme)
                style_preamble = f"""import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
plt.style.use('{cfg['plt_style']}')
sns.set_palette('{cfg['sns_palette']}')
sns.set_context('{cfg['context']}')
{cfg['extra_code']}"""

                # Prepare Execution Environment
                exec_env = {
                    "plt": plt,
                    "sns": sns,
                    "pd": pd,
                    "px": px,
                    "io": io,
                    "np": __import__("numpy"),
                }

                # Clean AI Code and Inject Style
                raw_ai_code = (
                    res["viz_code"]
                    .replace("```python", "")
                    .replace("```", "")
                    .strip()
                )

                # Remove AI's own style calls to prevent override
                cleaned_ai_code = re.sub(r"plt\.style\.use$.*$", "", raw_ai_code)

                # Remove plt.show() calls as they cause warnings in non-interactive backend
                cleaned_ai_code = re.sub(r"plt\.show\(\)", "", cleaned_ai_code)

                # Remove percentage sizes that cause warnings
                cleaned_ai_code = re.sub(r"'(\d+)%'", r'\1', cleaned_ai_code)
                cleaned_ai_code = re.sub(r'"(\d+)%', r'\1', cleaned_ai_code)

                # Replace deprecated applymap with map
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

                # Execute Visualizer Code
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

                # Capture Matplotlib Figures for PDF export and display
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

            # 7. DOWNLOAD SECTION
            if "pdf_bufs" in st.session_state and st.session_state["pdf_bufs"]:
                pdf_data = create_styled_pdf(report, st.session_state["pdf_bufs"])
                st.download_button(
                    label="📥 Download Full PDF Report",
                    data=pdf_data,
                    file_name=f"DA_Report_{db_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

# 8. ADMIN TAB
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