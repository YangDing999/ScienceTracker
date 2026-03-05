import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. 页面配置 (快捷 UI 设计) ---
st.set_page_config(
    page_title="DocTrack AI Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式（让界面看起来更像专业的情报系统）
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    .report-card { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库连接 (从 Streamlit Secrets 读取，更安全) ---
# 在部署网站时，我们会把这些填在 Streamlit 管理后台，而不是代码里
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 3. UI 布局 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.title("控制面板")
    st.info("从云端实时调取科研情报")
    test_paper_id = st.text_input("🔍 输入 Paper ID (如: W2949117887)", "")
    st.divider()
    st.caption("Powered by Gemini 1.5 & Supabase")

# 主界面
st.markdown("# 🚀 全球科研资助与人才情报系统")
st.markdown("---")

if test_paper_id:
    with st.spinner('正在从 Supabase 提取深度数据...'):
        # 调取数据
        res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", test_paper_id).execute()
        res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", test_paper_id).execute()
        res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", test_paper_id).execute()

    if res_abs.data:
        # 使用列布局展示情报
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📝 核心摘要")
            st.info(res_abs.data[0]['abstract'])
            
        with c2:
            st.subheader("📊 情报画像")
            st.write("🏛️ **关联机构 ID:**", res_affil.data[0]['institution_id'] if res_affil.data else "未知")
            st.write("💰 **资助方:**", res_grants.data[0]['funder'] if res_grants.data else "未披露")
            st.write("🆔 **项目号:**", res_grants.data[0]['award_id'] if res_grants.data else "N/A")

        st.divider()
        # AI 按钮逻辑
        if st.button("✨ 生成 AI 专家级趋势分析报告"):
            st.success("正在调用 Gemini API 分析资助趋势与技术突破口...")
            # 稍后在这里插入 Gemini 函数
    else:
        st.error("未在云端数据库中找到该 Paper ID，请检查输入。")
else:
    st.write("👋 请在左侧输入 Paper ID 以开始分析。")
