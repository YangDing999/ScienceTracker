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

# 5. 【智能导航逻辑】：自动寻找 Explore 页面
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    
    if st.button("🚀 开启数据探索之旅", use_container_width=True, type="primary"):
        # 获取当前 Streamlit 识别到的所有页面
        from streamlit.source_util import get_pages
        # 这里的 "app.py" 必须和你当前的文件名一致
        pages = get_pages("app.py")
        
        # 在识别到的页面中寻找包含 "Explore" 的路径
        target_page_path = None
        for page_info in pages.values():
            if "Explore" in page_info['page_name'] or "Explore" in page_info['relative_path']:
                target_page_path = page_info['relative_path']
                break
        
        if target_page_path:
            # 找到路径后，直接用系统提供的路径跳转
            st.switch_page(target_page_path)
        else:
            # 如果系统还没索引到，给出明确提示
            st.error("🚨 导航系统未检测到 Explore 页面。")
            st.info("💡 解决办法：请去 Streamlit Cloud 管理后台点击 'Reboot App'。")
            # 调试用：列出系统看到的页面（发布后可删掉）
            # st.write("系统检测到的页面清单：", [p['page_name'] for p in pages.values()])
            
    st.markdown("</div>", unsafe_allow_html=True)
