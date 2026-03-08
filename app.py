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

# --- 2. 初始化连接 ---
@st.cache_resource
def init_connections():
    try:
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        return db, genai.GenerativeModel(target), target
    except:
        return None, None, "Offline"

supabase, model, model_name = init_connections()

# --- 3. 状态管理 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_paper_id' not in st.session_state:
    st.session_state.selected_paper_id = None

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
            ui.metric_card(title="查询速度", content="实时", description="模糊匹配毫秒响应", key="m3")
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        with ui.card(key="explore_card"):
            st.markdown("<div style='text-align: center; padding: 10px;'>", unsafe_allow_html=True)
            ui.element("h3", content="准备好深入了吗？", cls="text-lg mb-4")
            if ui.button("🚀 开启探索", key="start_btn", class_name="w-full"):
                st.session_state.page = 'explore'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# --- 5. 探索工作台 (核心升级区) ---
else:
    with st.sidebar:
        st.markdown("<h2 class='hero-text' style='font-size: 2rem;'>SciOracle</h2>", unsafe_allow_html=True)
        if ui.button("🏠 返回首页", key="back_btn", class_name="w-full"):
            st.session_state.page = 'home'
            st.rerun()
        st.divider()
        
        # 模式选择
        search_mode = st.radio("选择搜索模式", ["关键词搜索", "Paper ID 精确查询"])
        
        if search_mode == "Paper ID 精确查询":
            input_val = st.text_input("🔍 输入 Paper ID", placeholder="W2949117887")
            if input_val: st.session_state.selected_paper_id = input_val
        else:
            keyword = st.text_input("🔑 输入关键词", placeholder="例如: AI, Cancer, Robot")
        
        st.divider()
        st.info(f"🤖 引擎: {model_name}")

    # 主界面显示逻辑
    if search_mode == "关键词搜索" and keyword:
        st.markdown(f"### 🔍 包含关键词 '{keyword}' 的研究成果")
        with st.spinner('正在搜索全量摘要数据库...'):
            # 模糊查询前 10 条结果
            res = supabase.table("mvp_abstracts").select("paper_id, abstract").ilike("abstract", f"%{keyword}%").limit(10).execute()
        
        if res.data:
            for item in res.data:
                with ui.card(key=f"card_{item['paper_id']}"):
                    st.markdown(f"**ID:** `{item['paper_id']}`")
                    # 只显示摘要的前 200 个字
                    st.write(item['abstract'][:200] + "...")
                    if st.button("查看深度 AI 分析", key=f"btn_{item['paper_id']}"):
                        st.session_state.selected_paper_id = item['paper_id']
                        st.rerun()
        else:
            st.warning("未找到匹配的论文，请换个词试试。")

    # 如果选定了某个 Paper ID (无论是通过 ID 输入还是列表点击)
    if st.session_state.selected_paper_id:
        curr_id = st.session_state.selected_paper_id
        st.markdown(f"### 📑 深度情报分析: `{curr_id}`")
        
        with st.spinner('📡 调取详细资助与机构数据...'):
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", curr_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", curr_id).execute()
            res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", curr_id).execute()

        if res_abs.data:
            with ui.card(key="main_res"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    ui.element("h3", content="📖 摘要原文", cls="text-xl font-bold mb-4 text-indigo-400")
                    st.write(res_abs.data[0]['abstract'])
                with col2:
                    ui.element("h3", content="🛡️ 资助背景", cls="text-xl font-bold mb-4 text-indigo-400")
                    ui.metric_card(title="资助机构", content=res_grants.data[0]['funder'] if res_grants.data else "未披露", key="res_f")
                    ui.metric_card(title="项目号", content=res_grants.data[0]['award_id'] if res_grants.data else "N/A", key="res_a")

            if ui.button("✨ 启动 AI 专家分析报告", key="run_ai", class_name="w-full"):
                with st.spinner("🧠 SciOracle AI 正在合成情报报告..."):
                    prompt = f"分析该摘要的技术突破点、潜在价值及未来趋势：{res_abs.data[0]['abstract']}"
                    response = model.generate_content(prompt)
                    with ui.card(key="ai_report"):
                        ui.element("h2", content="📋 SciOracle AI 专家研报", cls="text-2xl font-bold mb-4 text-rose-400")
                        st.markdown(response.text)
                        st.balloons()
        
        # 增加一个清除选择的按钮
        if st.button("❌ 关闭分析，返回搜索列表"):
            st.session_state.selected_paper_id = None
            st.rerun()

    elif not keyword and search_mode == "关键词搜索":
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        ui.element("h2", content="请输入关键词开始探索", cls="text-center text-gray-400 text-3xl")
