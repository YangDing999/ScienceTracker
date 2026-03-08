import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

st.set_page_config(page_title="Explore | SciOracle AI", layout="wide")

# 自定义侧边栏和对话样式
st.markdown("""
    <style>
    .stApp { background-color: #131314; }
    [data-testid="stSidebar"] { background-color: #1e1f20; }
    </style>
    """, unsafe_allow_html=True)

# 初始化连接 (跨文件共享时建议加上缓存)
@st.cache_resource
def init_connections():
    db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return db, model

supabase, ai_model = init_connections()

# 初始化历史记录 (Session State 在页面间是共享的)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_id' not in st.session_state:
    st.session_state.current_id = None

# --- 侧边栏：历史记录与 New Chat ---
with st.sidebar:
    st.markdown("<h2 style='color: #818cf8;'>SciOracle</h2>", unsafe_allow_html=True)
    if ui.button("➕ New Chat", variant="outline", key="nc", class_name="w-full mb-4"):
        st.session_state.current_id = None
        st.rerun()
    
    st.markdown("### 最近分析")
    for idx, item in enumerate(reversed(st.session_state.history[-8:])):
        if st.button(f"📄 {item['id']}", key=f"h_{idx}", use_container_width=True):
            st.session_state.current_id = item['id']
            st.rerun()

# --- 主界面 ---
if not st.session_state.current_id:
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>我可以如何帮您？</h2>", unsafe_allow_html=True)
else:
    curr_id = st.session_state.current_id
    res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", curr_id).execute()
    
    if res_abs.data:
        # 添加到历史
        if not any(h['id'] == curr_id for h in st.session_state.history):
            st.session_state.history.append({"id": curr_id})
            
        with ui.card(key="info"):
            st.markdown(f"#### 正在分析: `{curr_id}`")
            st.write(res_abs.data[0]['abstract'])
            
        if ui.button("✨ 生成 AI 研报", variant="default", key="gen"):
            with st.spinner("AI 思考中..."):
                resp = ai_model.generate_content(f"分析摘要：{res_abs.data[0]['abstract']}")
                st.markdown(resp.text)

# 底部输入框
user_input = st.chat_input("输入 Paper ID...")
if user_input:
    st.session_state.current_id = user_input
    st.rerun()
