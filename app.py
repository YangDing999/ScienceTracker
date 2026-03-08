import streamlit as st
import streamlit_shadcn_ui as ui

st.set_page_config(page_title="SciOracle AI", page_icon="🔮", layout="wide")

# 注入全局背景样式
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    header {visibility: hidden;}
    .gemini-gradient {
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 5rem;' class='gemini-gradient'>SciOracle</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #9aa0a6;'>新一代科研资助决策大脑</p>", unsafe_allow_html=True)

_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    # 引导用户去探索页
    st.markdown("<br>", unsafe_allow_html=True)
    st.page_link("pages/1_Explore.py", label="🚀 立即开启探索", icon="✨")

# 首页功能介绍卡片
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
cols = st.columns(3)
with cols[0]:
    ui.metric_card(title="数据源", content="OpenAlex", description="实时同步全球科研数据库")
with cols[1]:
    ui.metric_card(title="AI 核心", content="Gemini 1.5", description="Google 最强多模态逻辑引擎")
with cols[2]:
    ui.metric_card(title="分析维度", content="资助图谱", description="穿透项目号与经费流向")
