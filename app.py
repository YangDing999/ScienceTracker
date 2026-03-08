import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

# --- 1. 页面配置与高级 CSS ---
st.set_page_config(page_title="SciOracle AI | 全球科研智能枢纽", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 10% 20%, #1e1b4b 0%, #020617 100%);
        color: #f8fafc;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .hero-text {
        background: linear-gradient(90deg, #818cf8, #c084fc, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化连接 (带异常处理) ---
@st.cache_resource
def init_connections():
    try:
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        return db, genai.GenerativeModel(target), target
    except Exception as e:
        return None, None, "Offline"

supabase, model, model_name = init_connections()

# --- 3. 状态管理 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 4. 首页逻辑 ---
if st.session_state.page == 'home':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 5.5rem;' class='hero-text'>SciOracle AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #94a3b8; margin-bottom: 60px;'>解码全球科研资助逻辑，预见下一个技术奇点。</p>", unsafe_allow_html=True)
    
    _, m_col, _ = st.columns([1, 6, 1])
    with m_col:
        c1, c2, c3 = st.columns(3)
        with c1:
            ui.metric_card(title="数据规模", content="2.5B+", description="论文与资助节点关联", key="m1")
        with c2:
            ui.metric_card(title="分析引擎", content="Gemini 1.5", description="多模态逻辑推理能力", key="m2")
        with c3:
            ui.metric_card(title="处理速度", content="实时", description="毫秒级云端响应", key="m3")
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        with ui.card(key="explore_card"):
            st.markdown("<div style='text-align: center; padding: 10px;'>", unsafe_allow_html=True)
            ui.element("h3", content="准备好深入了吗？", cls="text-lg mb-4")
            if ui.button("🚀 开启数据探索", key="start_btn", class_name="w-full"):
                st.session_state.page = 'explore'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# --- 5. 探索工作台 ---
else:
    with st.sidebar:
        st.markdown("<h2 class='hero-text' style='font-size: 2rem;'>SciOracle</h2>", unsafe_allow_html=True)
        if ui.button("🏠 返回首页门户", key="back_btn", class_name="w-full"):
            st.session_state.page = 'home'
            st.rerun()
        st.divider()
        search_id = st.text_input("🔍 输入 Paper ID", placeholder="W2949117887")
        st.divider()
        
        # --- 这里的报错修复了：移除不确定的参数 ---
        try:
            ui.alert(title="系统状态", description=f"已连接引擎: {model_name}", key="status_info")
        except:
            st.info(f"🤖 引擎已连接: {model_name}")

    if not search_id:
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        ui.element("h2", content="请在左侧侧边栏输入 Paper ID", cls="text-center text-gray-400 text-3xl")
    else:
        with st.spinner('📡 正在解析全球科研图谱...'):
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", search_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", search_id).execute()
            res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", search_id).execute()

        if res_abs.data:
            with ui.card(key="main_res"):
                col_info, col_metrics = st.columns([2, 1])
                with col_info:
                    ui.element("h3", content="📖 论文核心摘要", cls="text-xl font-bold mb-4 text-indigo-400")
                    st.write(res_abs.data[0]['abstract'])
                with col_metrics:
                    ui.element("h3", content="🛡️ 资助背景", cls="text-xl font-bold mb-4 text-indigo-400")
                    ui.metric_card(title="资助机构", content=res_grants.data[0]['funder'] if res_grants.data else "未披露", key="res_funder")
                    ui.metric_card(title="项目号", content=res_grants.data[0]['award_id'] if res_grants.data else "N/A", key="res_award")

            st.markdown("<br>", unsafe_allow_html=True)
            
            if ui.button("✨ 启动 AI 深度决策分析", key="run_ai", class_name="w-full"):
                with st.spinner("🧠 SciOracle AI 正在合成情报报告..."):
                    try:
                        prompt = f"请以科学战略顾问的身份，分析以下研究的技术独特性、潜在价值及未来趋势：{res_abs.data[0]['abstract']}"
                        response = model.generate_content(prompt)
                        with ui.card(key="ai_report_card"):
                            ui.element("h2", content="📋 SciOracle AI 专家研报", cls="text-2xl font-bold mb-4 text-rose-400")
                            st.markdown(response.text)
                            st.balloons()
                    except Exception as e:
                        st.error(f"AI 分析失败: {str(e)}")
        else:
            try:
                ui.alert(title="查询无结果", description="云端数据库中未检索到该 ID。", variant="destructive", key="query_fail")
            except:
                st.error("❌ 查询无结果：数据库中未检索到该 Paper ID。")
