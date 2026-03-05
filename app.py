import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="SciOracle AI", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    .report-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; color: #1e293b; }
    .stButton>button { background-color: #6D28D9; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库与 AI 自动探测连接 ---
@st.cache_resource
def init_connections():
    try:
        # Supabase
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        
        # Gemini 自动探测逻辑
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # 寻找可用的模型
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 优先级排序：1.5-flash > 1.5-pro > 1.0-pro
        selected_model = None
        for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if target in available_models:
                selected_model = target
                break
        
        if not selected_model and available_models:
            selected_model = available_models[0]
            
        return db, genai.GenerativeModel(selected_model) if selected_model else None, selected_model
    except Exception as e:
        st.error(f"连接失败: {e}")
        return None, None, None

supabase, model, model_name = init_connections()

# --- 3. UI 布局 ---
with st.sidebar:
    st.markdown("# 🔮 SciOracle AI")
    if model_name:
        st.success(f"在线引擎: {model_name}")
    else:
        st.error("未找到可用 AI 模型")
    test_paper_id = st.text_input("🔍 输入 Paper ID", placeholder="W2949117887")

st.markdown("# 🔮 SciOracle AI: 全球科研情报系统")

if test_paper_id:
    with st.spinner('📡 检索云端数据...'):
        res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", test_paper_id).execute()
        res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", test_paper_id).execute()
        res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", test_paper_id).execute()

    if res_abs.data:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📑 核心摘要")
            st.markdown(f'<div class="report-box">{res_abs.data[0]["abstract"]}</div>', unsafe_allow_html=True)
        with c2:
            st.subheader("📊 结构化情报")
            st.write("🏛️ **机构 ID:**", res_affil.data[0]['institution_id'] if res_affil.data else "未知")
            st.write("💰 **资助方:**", res_grants.data[0]['funder'] if res_grants.data else "未披露")

        st.divider()
        
        if st.button("✨ 生成 AI 专家级趋势分析报告"):
            if model:
                with st.spinner("🧠 正在利用分布式 AI 生成深度研报..."):
                    try:
                        prompt = f"作为科学专家，分析以下摘要的技术突破、资助价值和未来3年预测：{res_abs.data[0]['abstract']}"
                        response = model.generate_content(prompt)
                        st.subheader("📋 SciOracle 专家研报")
                        st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                        st.balloons()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
            else:
                st.error("AI 引擎未就绪")
    else:
        st.warning("🔍 数据库中暂无该 ID。")
