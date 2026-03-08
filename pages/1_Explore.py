import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

# 1. 页面配置
st.set_page_config(page_title="Explore | SciOracle AI", layout="wide")

# 2. 沉浸式侧边栏 CSS
st.markdown("""
    <style>
    .stApp { background-color: #131314; }
    [data-testid="stSidebar"] { background-color: #1e1f20; border-right: 1px solid #333; }
    .stChatMessage { border-radius: 15px; background-color: #1e1f20; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 3. 初始化连接
@st.cache_resource
def init_all():
    db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return db, model

supabase, ai_model = init_all()

# 4. 状态管理
if 'history' not in st.session_state: st.session_state.history = []
if 'current_id' not in st.session_state: st.session_state.current_id = None

# --- 5. 侧边栏：历史记录与 New Chat ---
with st.sidebar:
    st.markdown("<h2 style='color: #818cf8; font-weight: 800;'>SciOracle</h2>", unsafe_allow_html=True)
    
    if ui.button("➕ New Chat", variant="outline", key="nc", class_name="w-full mb-6"):
        st.session_state.current_id = None
        st.rerun()
    
    st.markdown("### 最近分析记录")
    if not st.session_state.history:
        st.caption("暂无查询历史")
    else:
        for idx, item in enumerate(reversed(st.session_state.history[-10:])):
            if st.button(f"📄 {item['id']}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.current_id = item['id']
                st.rerun()
    
    st.divider()
    if ui.button("🏠 返回门户首页", variant="ghost", key="back_home"):
        st.switch_page("app.py")

# --- 6. 主内容区 ---
if not st.session_state.current_id:
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #fff;'>我可以如何帮您分析科研项目？</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9aa0a6;'>输入 Paper ID 开始调取资助情报</p>", unsafe_allow_html=True)
else:
    curr_id = st.session_state.current_id
    with st.spinner('📡 检索云端图谱...'):
        res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", curr_id).execute()
        res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", curr_id).execute()

    if res_abs.data:
        # 存入历史
        if not any(h['id'] == curr_id for h in st.session_state.history):
            st.session_state.history.append({"id": curr_id})
        
        # 显示数据卡片
        with ui.card(key="main_view"):
            st.markdown(f"#### 📑 论文概要: `{curr_id}`")
            st.write(res_abs.data[0]['abstract'])
            st.divider()
            c1, c2 = st.columns(2)
            with c1: st.write(f"💰 **资助方:** {res_grants.data[0]['funder'] if res_grants.data else '未披露'}")
            with c2: st.write(f"🆔 **项目号:** {res_grants.data[0]['award_id'] if res_grants.data else 'N/A'}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if ui.button("✨ 生成 AI 专家深度报告", variant="default", key="ai_btn", class_name="w-full"):
            with st.spinner("🧠 决策大脑正在合成报告..."):
                resp = ai_model.generate_content(f"分析该摘要的技术突破及未来趋势：{res_abs.data[0]['abstract']}")
                with ui.card(key="ai_res"):
                    st.markdown("### 📋 SciOracle 研报")
                    st.markdown(resp.text)
                    st.balloons()
    else:
        st.error("数据库中未检索到该 ID，请检查输入。")

# --- 7. 底部仿 Gemini 搜索框 ---
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
user_input = st.chat_input("在此处输入 Paper ID (如 W2949117887)...")
if user_input:
    st.session_state.current_id = user_input
    st.rerun()
