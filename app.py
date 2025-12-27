import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from dotenv import load_dotenv

import manager, agent_logic, viz_logic

# 1. 初始化与配置
load_dotenv()
manager.init_mgmt_db()

# --- [PDF 导出引擎：适配 fpdf2 最新版本] ---
def create_pdf(analysis_text, plot_buf):
    # 初始化 PDF (默认 A4, mm)
    pdf = FPDF()
    pdf.add_page()
    
    # 标题：使用 helvetica 替代已弃用的 arial 映射
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Business Intelligence Report", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    # 章节 1: 分析结果
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, "1. Analysis Results", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("helvetica", size=11)
    # 处理文本编码
    clean_text = analysis_text.replace("**", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text, 
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # 章节 2: 视觉图表
    if plot_buf:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, "2. Visual Representation", 
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        plot_buf.seek(0)
        # 居中放置图片 (A4 宽 210mm, 边距 15mm, 图片宽 180mm)
        pdf.image(plot_buf, x=15, w=180)
    
    # 现代 fpdf2 output() 默认返回字节流
    return pdf.output()

# --- Streamlit 页面配置 ---
st.set_page_config(page_title="Dual-Agent BI Platform", layout="wide")

# 自定义 CSS 样式
st.markdown("""
    <style>
    .report-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 25px;
        border: 1px solid #e9ecef;
        margin-bottom: 25px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.title("🛡️ Secure Access")
    user_role = st.selectbox("Login As", manager.get_all_users())
    
    # 获取当前用户有权访问的数据库 (Restriction Logic)
    allowed_dbs = manager.get_allowed_databases(user_role)
    
    st.divider()
    with st.expander("➕ Upload New Database"):
        up_file = st.file_uploader("Upload .sqlite", type=["sqlite", "db"])
        up_name = st.text_input("DB Nickname")
        if st.button("Integrate DB"):
            if up_file and up_name:
                if not os.path.exists("data"): os.makedirs("data")
                path = f"data/{up_file.name}"
                with open(path, "wb") as f: f.write(up_file.getbuffer())
                manager.add_database_to_mgmt(up_name, path, user_role)
                st.success("Integrated!")
                st.rerun()

tab_main, tab_admin = st.tabs(["📊 智能看板", "🛠️ 权限管理"])

with tab_main:
    # 居中布局控制
    _, main_col, _ = st.columns([1, 6, 1])
    
    with main_col:
        st.subheader("💡 提问中心")
        selected_db_name = st.selectbox("选择目标数据库", list(allowed_dbs.keys()))
        user_query = st.text_input("描述你想分析的数据内容:", placeholder="例如：展示 orderdetail 表中的销售分析")
        
        st.divider()

        # --- STEP 1: Analysis Agent (垂直堆叠第一层) ---
        st.markdown("### 📋 Step 1: Data Analysis Agent")
        run_analysis = st.button("🚀 开始深度分析", width=True)
        
        if run_analysis and user_query:
            with st.spinner("Analysis Agent 正在分析数据..."):
                report_content = agent_logic.run_analysis(allowed_dbs[selected_db_name], "General", user_query)
                st.session_state['report'] = report_content
                # 重置图表缓存，确保分析更新后图表也需要重新生成
                if 'plot_buf' in st.session_state:
                    del st.session_state['plot_buf']

        if 'report' in st.session_state:
            st.markdown(f'<div class="report-card">{st.session_state["report"]}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True) # 替代已弃用的 ln()

        # --- STEP 2: Visualization Agent (垂直堆叠第二层) ---
        st.markdown("### 🎨 Step 2: Visualization Agent")
        with st.expander("🛠️ 图表配置选项", expanded=True):
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                chart_type = st.selectbox("强制指定类型:", ["Auto (智能推荐)", "Bar Chart", "Line Chart", "Pie Chart", "Histogram", "Heat Map", "Scatter Plot"])
            with v_col2:
                viz_hint = st.text_input("视觉增强建议:", placeholder="例如：使用深蓝色调")
            
            run_viz = st.button("🖌️ 生成可视化图表", use_container_width=True)

        # 图表渲染逻辑
        if run_viz:
            if 'report' not in st.session_state:
                st.warning("⚠️ 请先执行『Step 1』分析数据。")
            else:
                with st.spinner("Visualization Agent 正在绘图..."):
                    # 获取 AI 代码
                    viz_code = viz_logic.generate_visualization(st.session_state['report'], chart_type, viz_hint)
                    try:
                        # 清理全局状态
                        plt.close('all')
                        # 执行环境注入
                        exec_env = {"plt": plt, "sns": sns, "pd": pd, "st": st, "px": px, "io": io}
                        
                        # 1. 执行 AI 代码渲染到界面 (AI 代码应包含 st.pyplot)
                        exec(viz_code, exec_env)
                        
                        # 2. 静默捕获当前图表用于 PDF 导出
                        if plt.get_fignums():
                            fig = plt.gcf()
                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", bbox_inches='tight', dpi=120)
                            st.session_state['plot_buf'] = buf
                            
                    except Exception as e:
                        st.error("📊 图表生成失败，请尝试简化描述或更换图表类型。")
                        if 'plot_buf' in st.session_state:
                            del st.session_state['plot_buf']

        elif 'plot_buf' in st.session_state:
            # 状态保持：在页面因其他交互刷新时，从缓存显示图表
            st.image(st.session_state['plot_buf'], use_container_width=True)

        # --- 底部导出区 ---
        if 'report' in st.session_state:
            st.divider()
            st.subheader("🏁 报告导出")
            # 调用现代化的 PDF 生成器
            final_pdf = create_pdf(st.session_state['report'], st.session_state.get('plot_buf'))
            
            st.download_button(
                label="✨ 导出完整 PDF 商业报告", 
                data=bytes(final_pdf), 
                file_name="Business_Report.pdf", 
                mime="application/pdf",
                use_container_width=True
            )


# --- Tab 2: 用户限制 (仅管理员) ---
with tab_admin:
    st.header("🔑 用户权限配置中心")
    if user_role == "admin":
        st.info("作为管理员，您可以控制每个用户对数据库的访问权限。")
        
        # 1. 选择要配置的用户
        target_user = st.selectbox("选择目标用户进行权限限制:", [u for u in manager.get_all_users() if u != 'admin'])
        
        # 2. 获取系统中所有的数据库
        all_dbs = manager.get_all_databases_metadata()
        
        # 3. 获取该用户当前已有的权限
        current_allowed = list(manager.get_allowed_databases(target_user).keys())
        
        # 4. 权限勾选
        st.subheader(f"为用户 '{target_user}' 分配数据库")
        new_perms = st.multiselect("勾选允许访问的数据库:", options=all_dbs, default=current_allowed)
        
        if st.button("💾 保存权限设置", use_container_width=True):
            manager.update_user_permissions(target_user, new_perms)
            st.success(f"权限已更新！用户 '{target_user}' 现在可以访问: {', '.join(new_perms) if new_perms else '无'}")
            
    else:
        st.error("⚠️ 只有 'admin' 角色可以访问此面板。请在侧边栏切换身份。")