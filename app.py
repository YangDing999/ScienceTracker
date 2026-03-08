import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

# --- 1. 页面配置与全景 CSS ---
st.set_page_config(page_title="SciOracle AI", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    /* Gemini 核心深色调 */
    .stApp { background-color: #131314; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20; border-right: 1px solid #333; }
    
    /* 隐藏顶部白条和原生装饰 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 渐变标题 */
    .gemini-gradient {
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* 玻璃感卡片 */
    .stChatMessage { border-radius: 15px; background-color: #1e1f20; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心初始化 (带缓存) ---
@st.cache_resource
def init_all():
    try:
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return db, model
    except:
        return None, None

supabase, ai_model = init_all()

# --- 3. 状态管理 (取代多页面跳转) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home' # 初始页为首页
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_id' not in st.session_state:
    st.session_state.current_id = None

# --- 4. 侧边栏：仅在“探索页”显示内容 ---
if st.session_state.page == 'explore':
    with st.sidebar:
        st.markdown("<h2 class='gemini-gradient' style='font-size: 1.8rem;'>SciOracle AI</h2>", unsafe_allow_html=True)
        
        # New Chat 按钮
        if ui.button("➕ New Analysis", variant="outline", key="nc_btn", class_name="w-full mb-6"):
            st.session_state.current_id = None
            st.rerun()
        
        st.markdown("### 最近分析")
        if not st.session_state.history:
            st.caption("暂无查询历史")
        else:
            for idx, item in enumerate(reversed(st.session_state.history[-8:])):
                if st.button(f"📄 {item['id']}", key=f"hist_{idx}", use_container_width=True):
                    st.session_state.current_id = item['id']
                    st.rerun()
        
        st.divider()
        if ui.button("🏠 返回门户首页", variant="ghost", key="to_home"):
            st.session_state.page = 'home'
            st.rerun()

# --- 5. 视图逻辑：首页 (Home View) ---
if st.session_state.page == 'home':
    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 5.5rem;' class='gemini-gradient'>SciOracle AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #9aa0a6; margin-bottom: 50px;'>穿透科研迷雾，预见资助逻辑</p>", unsafe_allow_html=True)
    
    _, m_col, _ = st.columns([1, 6, 1])
    with m_col:
        c1, c2, c3 = st.columns(3)
        with c1: ui.metric_card(title="情报规模", content="2.5B+", description="论文与资助多维关联")
        with c2: ui.metric_card(title="核心大脑", content="Gemini 1.5", description="Google 最强推理引擎")
        with c3: ui.metric_card(title="查询时效", content="Real-time", description="毫秒级云端动态索引")
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        if ui.button("🚀 开启数据探索之旅", variant="default", key="start_exp", class_name="w-full py-6"):
            st.session_state.page = 'explore'
            st.rerun()

# --- 6. 视图逻辑：探索页 (Explore View) ---
elif st.session_state.page == 'explore':
    # A. 欢迎界面 (未选择 ID 时)
    if not st.session_state.current_id:
        st.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #fff;'>我可以如何帮您分析科研项目？</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>输入 Paper ID 调取全球资助图谱与 AI 深度研报</p>", unsafe_allow_html=True)
    
    # B. 分析详情界面 (已输入 ID 时)
    else:
        curr_id = st.session_state.current_id
        with st.spinner('📡 检索云端图谱...'):
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", curr_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", curr_id).execute()

        if res_abs.data:
            # 存入历史记录
            if not any(h['id'] == curr_id for h in st.session_state.history):
                st.session_state.history.append({"id": curr_id})
            
            with ui.card(key="main_res"):
                st.markdown(f"#### 📑 正在分析: `{curr_id}`")
                st.write(res_abs.data[0]['abstract'])
                st.divider()
                st.write(f"💰 **资助方:** {res_grants.data[0]['funder'] if res_grants.data else '未披露'}")
                st.write(f"🆔 **项目 ID:** {res_grants.data[0]['award_id'] if res_grants.data else 'N/A'}")

            st.markdown("<br>", unsafe_allow_html=True)
            
            if ui.button("✨ 生成 AI 专家深度报告", variant="default", key="ai_gen", class_name="w-full"):
                with st.spinner("🧠 决策大脑正在合成报告..."):
                    prompt = f"分析该摘要的技术突破及未来趋势：{res_abs.data[0]['abstract']}"
                    response = ai_model.generate_content(prompt)
                    with ui.card(key="ai_output"):
                        st.markdown("### 📋 SciOracle 研报")
                        st.markdown(response.text)
                        st.balloons()
        else:
            ui.alert(title="查询失败", description=f"数据库中未找到 ID: {curr_id}", variant="destructive", key="err_alert")

    # C. 底部固定聊天框 (Gemini 核心体验)
    # 使用占位符把内容顶上去，确保输入框在底部有呼吸感
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    user_input = st.chat_input("在此处输入 Paper ID (如 W2949117887)...")
    if user_input:
        st.session_state.current_id = user_input
        st.rerun()
