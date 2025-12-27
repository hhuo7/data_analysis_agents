import streamlit as st
import pandas as pd
from fpdf import FPDF
from dotenv import load_dotenv
import manager, agent_logic

load_dotenv()
manager.init_mgmt_db()

st.set_page_config(page_title="Data Analysis Agent", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("🛡️ Secure Access")
    user_role = st.selectbox("Login As", manager.get_all_users())
    
    with st.expander("➕ Upload New Database"):
        up_file = st.file_uploader("Upload .sqlite", type=["sqlite", "db"])
        up_name = st.text_input("DB Nickname")
        if st.button("Integrate DB"):
            if up_file and up_name:
                path = f"data/{up_file.name}"
                with open(path, "wb") as f: f.write(up_file.getbuffer())
                manager.add_database_to_mgmt(up_name, path, user_role)
                st.success("Done!")
                st.rerun()

# --- Main UI ---
tab_analysis, tab_admin = st.tabs(["🔍 Analysis", "⚙️ Management"])

with tab_analysis:
    dbs = manager.get_allowed_databases(user_role)
    selected_db = st.selectbox("Select Database", list(dbs.keys()))
    
    col1, col2 = st.columns([1, 2])
    with col1:
        a_type = st.selectbox("Type", ["General Query", "EDA", "Sales Trends"])
        u_prompt = st.text_area("Question", placeholder="How many customers are in London?")
        run = st.button("Run AI Analysis")

    with col2:
        if run and selected_db:
            with st.spinner("Analyzing..."):
                res = agent_logic.run_analysis(dbs[selected_db], a_type, u_prompt)
                st.session_state['last_result'] = res
                st.markdown(res)

    if 'last_result' in st.session_state:
        st.divider()
        c1, c2, c3 = st.columns(3)
        res_text = st.session_state['last_result']
        c1.download_button("Export Markdown", res_text, "report.md")
        # CSV and PDF logic...
        if "|" in res_text:
            try:
                # Basic MD Table to CSV
                rows = [l for l in res_text.split("\n") if "|" in l and "---" not in l]
                df = pd.DataFrame([r.strip("|").split("|") for r in rows])
                c2.download_button("Export CSV", df.to_csv(index=False), "data.csv")
            except: pass
        
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, res_text.encode('latin-1', 'replace').decode('latin-1'))
        c3.download_button("Export PDF", bytes(pdf.output()), "report.pdf")

with tab_admin:
    if user_role != "admin":
        st.error("Admin Only")
    else:
        target = st.selectbox("Target User", manager.get_all_users())
        all_dbs = manager.get_all_databases_metadata()
        current_perms = list(manager.get_allowed_databases(target).keys())
        new_perms = st.multiselect("Assign DBs", all_dbs, default=current_perms)
        if st.button("Save Permissions"):
            manager.update_user_permissions(target, new_perms)
            st.success("Updated")