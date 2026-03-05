import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="SciOracle AI - Global Research Intelligence",
    page_icon="🔮",
    layout="wide"
)

# 自定义 UI 样式
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #6D28D9; color: white; font-weight: bold; }
    .report-box { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; line-height: 1.6; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库与 AI 连接 (从 Secrets 读取) ---
@st.cache_resource
def init_connections():
    try:
        # Supabase 连接
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        db: Client = create_client(supabase_url, supabase_key)
        
        # Gemini 配置
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 使用最标准的模型名称，SDK 会自动处理路径
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
        
        return db, ai_model
    except Exception as e:
        st.error(f"⚠️ 初始化失败，请检查 Secrets 配置: {e}")
        return None, None

supabase, model = init_connections()

# --- 3. UI 侧边栏 ---
with st.sidebar:
    st.markdown("# 🔮 SciOracle AI")
    st.markdown("---")
    # 默认提供一个测试 ID，方便用户点击
    test_paper_id = st.text_input("🔍 输入 Paper ID", placeholder="例如: W2949117887")
    st.divider()
    st.info("💡 提示：SciOracle 正在通过云端数据库实时检索全球科研数据。")

# --- 4. 主界面逻辑 ---
st.markdown("# 🔮 SciOracle AI: 全球科研情报决策系统")
st.markdown("> **基于深度学术数据与 Gemini 1.5 强力驱动**")

if test_paper_id:
    with st.spinner('📡 正在调取云端数据...'):
        # 调取各表数据
        res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", test_paper_id).execute()
        res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", test_paper_id).execute()
        res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", test_paper_id).execute()

    if res_abs.data:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📑 核心摘要预览")
            st.markdown(f'<div class="report-box">{res_abs.data[0]["abstract"]}</div>', unsafe_allow_html=True)
            
        with c2:
            st.subheader("📊 结构化情报")
            st.write("🏛️ **研究机构 ID:**", res_affil.data[0]['institution_id'] if res_affil.data else "未知")
            st.write("💰 **核心资助方:**", res_grants.data[0]['funder'] if res_grants.data else "未披露")
            st.write("🆔 **资助项目号:**", res_grants.data[0]['award_id'] if res_grants.data else "N/A")

        st.divider()
        
        # --- AI 报告生成功能 ---
        if st.button("✨ 立即生成 AI 专家级趋势分析报告"):
            if not model:
                st.error("AI 模型未就绪，请检查 API Key。")
            else:
                with st.spinner("🧠 SciOracle AI 正在分析技术趋势并生成研报..."):
                    try:
                        # 构造严谨的 Prompt
                        prompt = f"""
                        作为科学计量学专家，请分析以下摘要：
                        {res_abs.data[0]['abstract']}
                        
                        请用中文提供：
                        1. 技术突破点分析
                        2. 资助价值评估
                        3. 未来 3 年技术演进预测
                        """
                        
                        # 调用生成
                        response = model.generate_content(prompt)
                        
                        if response.text:
                            st.subheader("📋 SciOracle 专家研报")
                            st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.warning("AI 返回了空内容，请重试。")
                            
                    except Exception as e:
                        # 如果还是报错，这里会打印出更详细的日志信息
                        st.error(f"AI 生成报告时出错: {str(e)}")
                        st.info("调试建议：检查 Streamlit 管理后台的 Secrets 中 GEMINI_API_KEY 是否填错。")
    else:
        st.warning("🔍 云端数据库中暂无该 ID 的记录。")
else:
    st.write("👋 欢迎。请在左侧输入框输入 Paper ID 开始情报分析。")
