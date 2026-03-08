import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

# --- 1. 页面基础配置与高级 CSS 注入 ---
st.set_page_config(page_title="SciOracle AI | 全球科研智能枢纽", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    /* 全局背景：深邃渐变 */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #1e1b4b 0%, #020617 100%);
        color: #f8fafc;
    }
    
    /* 隐藏原生装饰 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 霓虹渐变文字 */
    .hero-text {
        background: linear-gradient(90deg, #818cf8, #c084fc, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* 玻璃感容器 */
    .glass-panel {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化连接 (缓存处理) ---
@st.cache_resource
def init_connections():
    try:
        # Supabase 连接
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        # Gemini 配置
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 自动探测可用模型
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
        return db, genai.GenerativeModel(target), target
    except Exception as e:
        return None, None, f"Error: {str(e)}"

supabase, model, model_name = init_connections()

# --- 3. 页面状态管理 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 4. 首页设计 (Landing Page) ---
if st.session_state.page == 'home':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    
    # 标题区
    st.markdown("<h1 style='text-align: center; font-size: 5.5rem;' class='hero-text'>SciOracle AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #94a3b8; margin-bottom: 60px;'>解码全球科研资助逻辑，预见下一个技术奇点。</p>", unsafe_allow_html=True)
    
    # 核心指标展示 (Shadcn UI)
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
    
    # 显著的探索入口
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        with ui.card(key="explore_card"):
            st.markdown("<div style='text-align: center; padding: 10px;'>", unsafe_allow_html=True)
            ui.element("h3", content="准备好深入了吗？", cls="text-lg mb-4")
            if ui.button("🚀 开启数据探索", variant="default", key="start_btn", class_name="w-full"):
                st.session_state.page = 'explore'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# --- 5. 探索工作台 (Workspace) ---
else:
    # 侧边栏：极简专业感
    with st.sidebar:
        st.markdown("<h2 class='hero-text' style='font-size: 2rem;'>SciOracle</h2>", unsafe_allow_html=True)
        if ui.button("🏠 返回首页门户", variant="outline", key="back_btn", class_name="w-full"):
            st.session_state.page = 'home'
            st.rerun()
        st.divider()
        search_id = st.text_input("🔍 输入 Paper ID", placeholder="W2949117887")
        st.divider()
        # 修正后的 ui.alert 参数
        ui.alert(icon="terminal", title="系统状态", description=f"已连接引擎: {model_name}", variant="default", key="status_info")

    # 主界面布局
    if not search_id:
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        ui.element("h2", content="请在左侧侧边栏输入 Paper ID", cls="text-center text-gray-400 text-3xl")
        st.markdown("<p style='text-align: center; color: #64748b;'>SciOracle 将实时穿透云端数据库并生成 AI 分析报告</p>", unsafe_allow_html=True)
    else:
        with st.spinner('📡 正在解析全球科研图谱...'):
            # 数据获取逻辑
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", search_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", search_id).execute()
            res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", search_id).execute()

        if res_abs.data:
            # 结果展示区：采用 Shadcn 卡片包裹
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
            
            # AI 报告区
            if ui.button("✨ 启动 AI 深度决策分析", variant="default", key="run_ai", class_name="w-full"):
                with st.spinner("🧠 SciOracle AI 正在合成情报报告..."):
                    try:
                        prompt = f"请以科学战略顾问的身份，分析以下研究的技术独特性、潜在经济价值及未来 3-5 年的资助趋势：{res_abs.data[0]['abstract']}"
                        response = model.generate_content(prompt)
                        
                        with ui.card(key="ai_report_card"):
                            ui.element("h2", content="📋 SciOracle AI 专家研报", cls="text-2xl font-bold mb-4 text-rose-400")
                            st.markdown(response.text)
                            st.balloons()
                    except Exception as e:
                        st.error(f"AI 分析失败: {str(e)}")
        else:
            # 修正后的错误提示参数
            ui.alert(icon="alert-triangle", title="查询无结果", description="云端数据库中未检索到该 Paper ID，请确认 ID 是否正确或已录入。", variant="destructive", key="query_fail")
