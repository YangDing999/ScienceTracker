import streamlit as st
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai
import streamlit_shadcn_ui as ui

# --- 1. 页面配置与主题注入 ---
st.set_page_config(page_title="SciOracle AI | 科技情报枢纽", page_icon="🔮", layout="wide")

# 注入自定义 CSS：深色背景 + 霓虹渐变 + 玻璃拟态
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 30%, #1e1b4b 0%, #020617 100%);
        color: #f8fafc;
    }
    /* 隐藏原生 Streamlit 装饰 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 标题动效 */
    .hero-text {
        background: linear-gradient(to right, #818cf8, #c084fc, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.05em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化连接 (缓存处理) ---
@st.cache_resource
def init_connections():
    try:
        db = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 探测可用模型
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        return db, genai.GenerativeModel(target), target
    except:
        return None, None, "Offline"

supabase, model, model_name = init_connections()

# --- 3. 状态管理 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 4. 首页设计 (Landing Page) ---
if st.session_state.page == 'home':
    # 顶部留白
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    
    # 主标题区
    st.markdown("<h1 style='text-align: center; font-size: 5rem;' class='hero-text'>SciOracle AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #94a3b8; margin-bottom: 50px;'>下一代科研资助情报分析引擎，穿透学术迷雾。</p>", unsafe_allow_html=True)
    
    # 使用 Shadcn UI 的 Metric Cards 展示实力
    _, m_col, _ = st.columns([1, 6, 1])
    with m_col:
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(title="情报覆盖", content="2.5B+", description="全球论文与资助关联数据", key="m1")
        with cols[1]:
            ui.metric_card(title="分析引擎", content="Gemini 1.5", description="深度语义与逻辑推理", key="m2")
        with cols[2]:
            ui.metric_card(title="查询延迟", content="< 500ms", description="分布式云端数据库响应", key="m3")
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    # 显著的探索入口
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        with ui.card(key="explore_entry"):
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.write("准备好深入数据了吗？")
            if ui.button("🚀 开启探索", variant="default", key="go_btn", class_name="w-full"):
                st.session_state.page = 'explore'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 底部装饰性图标
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    ui.badges(badge_list=[("权威数据源", "outline"), ("AI 驱动", "destructive"), ("实时更新", "secondary")], class_name="flex justify-center gap-4")

# --- 5. 探索工作台 (Workspace) ---
else:
    # 侧边栏导航
    with st.sidebar:
        st.markdown("<h2 class='hero-text'>SciOracle</h2>", unsafe_allow_html=True)
        if ui.button("🏠 返回门户首页", variant="outline", key="back_home", class_name="w-full"):
            st.session_state.page = 'home'
            st.rerun()
        st.divider()
        search_id = st.text_input("🔍 输入 Paper ID (OpenAlex)", placeholder="W2949117887")
        st.divider()
        ui.alert(title="引擎状态", content=f"已连接: {model_name}", variant="default")

    # 主操作区
    if not search_id:
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        ui.element("h2", content="等待指令", cls="text-center text-gray-500 text-3xl")
        st.markdown("<p style='text-align: center;'>请在左侧侧边栏输入需要分析的 Paper ID。</p>", unsafe_allow_html=True)
    else:
        with st.spinner('📡 正在从云端调取多维度数据...'):
            # 数据抓取逻辑
            res_abs = supabase.table("mvp_abstracts").select("abstract").eq("paper_id", search_id).execute()
            res_grants = supabase.table("mvp_grants").select("funder, award_id").eq("paper_id", search_id).execute()
            res_affil = supabase.table("mvp_authorships").select("institution_id").eq("paper_id", search_id).execute()

        if res_abs.data:
            # 采用 Shadcn Card 包裹结果
            with ui.card(key="result_card"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    ui.element("h3", content="📝 核心摘要", cls="text-xl font-bold mb-2")
                    st.write(res_abs.data[0]['abstract'])
                with c2:
                    ui.element("h3", content="📊 关键指标", cls="text-xl font-bold mb-2")
                    ui.metric_card(title="资助方", content=res_grants.data[0]['funder'] if res_grants.data else "N/A", key="funder_card")
                    ui.metric_card(title="项目 ID", content=res_grants.data[0]['award_id'] if res_grants.data else "N/A", key="award_card")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # AI 按钮：放在显著位置
            if ui.button("✨ 生成 AI 专家趋势报告", variant="default", key="ai_run"):
                with st.spinner("🧠 决策大脑正在合成情报..."):
                    prompt = f"以专家视角分析该研究的技术突破点、资助价值及未来3年技术路径：{res_abs.data[0]['abstract']}"
                    response = model.generate_content(prompt)
                    with ui.card(key="ai_report"):
                        ui.element("h2", content="📋 SciOracle AI 专家研报", cls="text-2xl font-bold text-purple-400 mb-4")
                        st.markdown(response.text)
                        st.balloons()
        else:
            ui.alert(title="查询失败", content="数据库中未检索到该 ID，请检查输入或联系管理员。", variant="destructive")
