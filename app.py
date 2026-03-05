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
    .report-box { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库与 AI 连接 (从 Secrets 读取) ---
try:
    # Supabase 连接
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    
    # Gemini 配置
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"配置读取失败，请检查 Secrets。错误详情: {e}")

# --- 3. UI 侧边栏 ---
with st.sidebar:
    st.markdown("# 🔮 SciOracle AI")
    st.markdown("---")
    test_paper_id = st.text_input("🔍 输入 Paper ID (如: W2949117887)", "")
    st.divider()
    st.info("💡 提示：输入 ID 后，点击右侧生成的按钮，即可启动 AI 情报分析。")

# --- 4. 主界面逻辑 ---
st.markdown("# 🔮 SciOracle AI: 全球科研情报决策系统")
st.markdown("> **基于 OpenAlex 实时数据与 Gemini 1.5 强力驱动**")

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
        if st.button("✨ 立即生成 AI 深度专家研报"):
            with st.spinner("🧠 SciOracle AI 正在分析技术趋势..."):
                try:
                    # 构造 Prompt
                    prompt = f"""
                    你是一位全球顶尖的科学计量学专家和科研资助顾问。请基于以下论文摘要进行深度分析：
                    
                    摘要内容：{res_abs.data[0]['abstract']}
                    
                    请生成一份 500 字左右的专业情报报告，包含以下板块：
                    1. 技术突破点：该研究解决了什么关键科学问题？
                    2. 资助逻辑分析：为什么资助机构愿意投资该领域？
                    3. 未来趋势预测：基于该技术，未来 3-5 年可能的爆发点在哪？
                    4. 对决策者的建议：如果你是资助官，你应该如何布局该领域？
                    
                    请使用专业、简洁、洞察力强的语言。
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.subheader("📋 SciOracle 专家研报")
                    st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                    st.balloons() # 庆祝一下！
                    
                except Exception as e:
                    st.error(f"AI 生成报告时出错: {e}")
    else:
        st.error("❌ 未找到该 Paper ID，请检查数据是否已上传至 Supabase。")
else:
    st.write("👋 欢迎访问 SciOracle。请输入左侧 Paper ID 开启深度情报之旅。")
