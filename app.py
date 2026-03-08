import streamlit as st
import streamlit_shadcn_ui as ui

# 1. 页面配置
st.set_page_config(page_title="SciOracle AI | Home", page_icon="🔮", layout="wide")

# 2. 注入背景样式
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    header {visibility: hidden;}
    .hero-gradient {
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 5.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 英雄展位区
st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;' class='hero-gradient'>SciOracle AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #9aa0a6; margin-bottom: 50px;'>穿透科研迷雾，预见资助逻辑</p>", unsafe_allow_html=True)

# 4. 核心功能展示卡片
_, m_col, _ = st.columns([1, 6, 1])
with m_col:
    c1, c2, c3 = st.columns(3)
    with c1:
        ui.metric_card(title="情报规模", content="2.5B+", description="论文与资助多维关联")
    with c2:
        ui.metric_card(title="核心大脑", content="Gemini 1.5", description="Google 最强逻辑引擎")
    with c3:
        ui.metric_card(title="查询时效", content="Real-time", description="毫秒级云端动态索引")

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

# 5. 标准官方导航逻辑
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    
    if st.button("🚀 开启数据探索之旅", use_container_width=True, type="primary"):
        # 官方标准写法，不要加任何诊断代码
        st.switch_page("pages/1_Explore.py")
                
    st.markdown("</div>", unsafe_allow_html=True)
