import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="SciOracle AI | 全球科研智能枢纽", page_icon="🔮", layout="wide")

# --- 2. 注入高级 AI 感 CSS ---
st.markdown("""
    <style>
    /* 全局背景：深邃星空渐变 */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }
    
    /* 渐变标题文字 */
    .hero-title {
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem; font-weight: 800; text-align: center; margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        color: #94a3b8; text-align: center; font-size: 1.5rem; margin-bottom: 3rem;
    }

    /* 玻璃拟态卡片 */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem; border-radius: 1.5rem; text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-10px);
        border-color: #6366f1;
        background: rgba(30, 41, 59, 0.6);
    }

    /* 隐藏原有的 Streamlit 元素以增强沉浸感 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化连接 (保持不变) ---
@st.cache_resource
def init_connections():
    try:
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 寻找可用模型
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
        return db, genai.GenerativeModel(target_model), target_model
    except:
        return None, None, "Disconnected"

supabase, model, model_name = init_connections()

# --- 4. 状态管理：控制显示首页还是探索页 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to_explore():
    st.session_state.page = 'explore'

def go_to_home():
    st.session_state.page = 'home'

# --- 5. 首页逻辑 (Landing Page) ---
if st.session_state.page == 'home':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>SciOracle AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>解码全球科研资助逻辑，洞察下一个科技引爆点</p>", unsafe_allow_html=True)
    
    # 显著的探索按钮
    col_btn, _ = st.columns([1, 10]) # 居中对齐的小技巧
    with st.container():
        _, center_col, _ = st.columns([2, 2, 2])
        with center_col:
            if st.button("🚀 开启数据探索之旅", use_container_width=True, type="primary"):
                go_to_explore()
                st.rerun()

    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

    # 功能卡片展示
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class='glass-card'><h3>🔍 智能检索</h3><p>覆盖 2.5 亿篇论文，秒级定位核心文献与项目编号。</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='glass-card'><h3>🧠 AI 研报</h3><p>基于 Gemini 1.5 Pro，自动生成专家级技术趋势分析。</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class='glass-card'><h3>📊 资助图谱</h3><p>穿透资助方与机构关系，揭示科研经费流动真相。</p></div>""", unsafe_allow_html=True)

# --- 6. 探索页逻辑 (App Workspace) ---
else:
    with st.sidebar:
        st.markdown("## 🔮 SciOracle Workspace")
        if st.button("🏠 返回首页"):
            go_to_home()
            st.rerun()
        st.divider()
        st.write(f"🟢 引擎已就绪: {model_name}")
        search_id = st.text_input("输入 Paper ID 开始解析", placeholder="例如: W2949117887")
        st.divider()
        st.caption("© 2026 SciOracle AI. All rights reserved.")

    st.markdown("### 🔍 实时科研情报调取")
    
    if search_id:
        with st.spinner('📡 正在穿透云端数据库...'):
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", search_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", search_id).execute()
            res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", search_id).execute()

        if res_abs.data:
            col_main, col_side = st.columns([2, 1])
            with col_main:
                st.markdown("#### 📄 论文摘要")
                st.info(res_abs.data[0]['abstract'])
                
                if st.button("✨ 生成 AI 深度情报报告", type="primary"):
                    with st.spinner("AI 正在深度思考中..."):
                        prompt = f"分析该摘要的技术突破、资助逻辑和未来3年趋势：{res_abs.data[0]['abstract']}"
                        response = model.generate_content(prompt)
                        st.markdown("#### 📋 AI 专家研报")
                        st.success(response.text)
                        st.balloons()
            
            with col_side:
                st.markdown("#### 📌 结构化画像")
                st.metric("核心资助方", res_grants.data[0]['funder'] if res_grants.data else "未披露")
                st.metric("机构关联", res_affil.data[0]['institution_id'] if res_affil.data else "未知")
                st.write(f"项目编号: `{res_grants.data[0]['award_id'] if res_grants.data else 'N/A'}`")
        else:
            st.error("未找到数据。请检查 ID 是否正确。")
    else:
        st.markdown("""
        <div style='background: rgba(99, 102, 241, 0.1); padding: 50px; border-radius: 20px; text-align: center; border: 1px dashed #6366f1;'>
            <h2 style='color: #6366f1;'>等待指令中...</h2>
            <p>请在左侧侧边栏输入 Paper ID 以激活 AI 分析模块</p>
        </div>
        """, unsafe_allow_html=True)
