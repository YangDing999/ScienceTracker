import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

# --- 1. 页面配置与高级 Gemini 风格 CSS ---
st.set_page_config(page_title="SciOracle AI", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    /* Gemini 风格的深色背景 */
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    
    /* 侧边栏样式定制 */
    [data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #333;
    }
    
    /* 历史记录按钮样式 */
    .history-item {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        cursor: pointer;
        transition: background 0.3s;
        border: 1px solid transparent;
    }
    .history-item:hover {
        background-color: #333537;
    }
    
    /* 模拟 Gemini 的底部输入框布局 */
    .fixed-bottom {
        position: fixed;
        bottom: 30px;
        left: 20%;
        right: 20%;
        z-index: 1000;
    }
    
    /* 隐藏原生的装饰 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
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

# --- 3. 状态管理 (New Chat & History) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'history' not in st.session_state:
    st.session_state.history = []  # 存储格式：[{"id": "W123", "title": "摘要片段..."}, ...]
if 'current_id' not in st.session_state:
    st.session_state.current_id = None

# 侧边栏：Gemini 风格导航
if st.session_state.page == 'explore':
    with st.sidebar:
        st.markdown("<h2 style='color: #818cf8; font-size: 1.5rem;'>SciOracle AI</h2>", unsafe_allow_html=True)
        
        # New Chat 按钮
        if ui.button("➕ New Analysis", variant="outline", key="new_chat", class_name="w-full mb-6"):
            st.session_state.current_id = None
            st.rerun()
        
        st.markdown("### 最近记录")
        # 渲染历史记录
        if not st.session_state.history:
            st.caption("暂无查询历史")
        else:
            for idx, item in enumerate(reversed(st.session_state.history[-10:])): # 只显示最近10条
                if st.button(f"📄 {item['id']}\n{item['title'][:15]}...", key=f"hist_{idx}", use_container_width=True):
                    st.session_state.current_id = item['id']
                    st.rerun()
        
        st.divider()
        if st.button("🏠 返回首页门户", variant="ghost", key="back_home"):
            st.session_state.page = 'home'
            st.rerun()

# --- 4. 首页逻辑 (Landing Page) ---
if st.session_state.page == 'home':
    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 5rem; font-weight: 800; background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>SciOracle</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #9aa0a6;'>您的专业级科研资助与情报助理</p>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        if ui.button("🚀 开启对话探索", variant="default", key="go_explore", class_name="w-full py-6"):
            st.session_state.page = 'explore'
            st.rerun()

# --- 5. 探索工作台 (Gemini 风格) ---
elif st.session_state.page == 'explore':
    # 主内容区域
    if not st.session_state.current_id:
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #e3e3e3;'>今天想分析哪篇论文？</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>输入 Paper ID 调取深度情报，或在左侧查看历史记录。</p>", unsafe_allow_html=True)
    else:
        # 显示具体详情
        curr_id = st.session_state.current_id
        with st.spinner('📡 检索云端数据...'):
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", curr_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", curr_id).execute()

        if res_abs.data:
            # 记录到历史（如果不在历史中）
            if not any(h['id'] == curr_id for h in st.session_state.history):
                st.session_state.history.append({"id": curr_id, "title": res_abs.data[0]['abstract'][:30]})
            
            # 模仿 AI 回复的卡片布局
            with ui.card(key="res_main"):
                st.markdown(f"#### 📑 论文概要: `{curr_id}`")
                st.write(res_abs.data[0]['abstract'])
                
                c1, c2 = st.columns(2)
                with c1:
                    ui.metric_card(title="资助机构", content=res_grants.data[0]['funder'] if res_grants.data else "N/A", key="f1")
                with c2:
                    ui.metric_card(title="项目号", content=res_grants.data[0]['award_id'] if res_grants.data else "N/A", key="a1")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # AI 分析部分
            if ui.button("✨ 生成 AI 专家深度报告", variant="default", key="ai_btn"):
                with st.spinner("🧠 决策大脑正在合成报告..."):
                    prompt = f"分析该摘要的技术突破、资助价值及未来3年趋势：{res_abs.data[0]['abstract']}"
                    response = model.generate_content(prompt)
                    with ui.card(key="ai_res"):
                        st.markdown("### 📋 SciOracle 专家研报")
                        st.markdown(response.text)
                        st.balloons()
        else:
            st.error("未找到数据，请检查 ID 格式。")

    # 底部固定输入框区域 (仿 Gemini)
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    with st.container():
        # 这里使用 columns 实现居中输入框
        _, input_col, _ = st.columns([1, 2, 1])
        with input_col:
            query_id = st.text_input("", placeholder="输入 Paper ID (例如: W2949117887)", key="bottom_input", label_visibility="collapsed")
            if query_id:
                st.session_state.current_id = query_id
                st.rerun()
