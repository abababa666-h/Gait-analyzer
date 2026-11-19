import streamlit as st
import plotly.express as px
from analyzer import get_dashboard_data

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="步态分析系统", 
    layout="wide",               
    initial_sidebar_state="expanded", 
    menu_items={}                
)

st.title("MULTI-IMU 步态参数分析与异常检测系统")
st.markdown("---")

# ================= 2. 侧边栏交互 =================
st.sidebar.header("⚙️ 算法参数设置")
mad_slider = st.sidebar.slider(
    "异常判断阈值 (MAD 倍数)", 
    min_value=1.0, max_value=4.0, value=2.5, step=0.1,
    help="值越小，抓出的异常样本越多。"
)

st.sidebar.markdown("---")
st.sidebar.header("📂 导入外部数据")
# 核心功能：允许用户上传多个 CSV
uploaded_files = st.sidebar.file_uploader(
    "拖拽或点击上传 CSV (可多选)", 
    type=["csv"], 
    accept_multiple_files=True,
    help="默认使用本地已有的数据集。如果您上传新的文件（文件名需包含 events 和 trial），系统将优先分析您上传的数据。"
)

# ================= 3. 获取数据 =================
data = get_dashboard_data(mad_threshold=mad_slider, uploaded_files=uploaded_files)

if data["status"] == "error":
    st.error(f"❌ 数据加载失败！错误原因：{data['message']}")
    if uploaded_files:
        st.info("提示：您上传的文件名中，必须包含 'events' 和 'trial' 关键词，系统才能识别。")
    else:
        st.info("请检查：默认的 CSV 文件是否和代码在同一个文件夹下？")
else:
    st.success("✅ 数据读取成功！")
    
    tab1, tab2, tab3 = st.tabs(["📋 原始数据概览", "📈 步态指标可视化", "🚨 异常 Trial 检测"])
    
    # ================= Tab 1: 数据概览 =================
    with tab1:
        st.subheader("步态事件 (Events) 数据前 20 行")
        st.dataframe(data["events"].head(20), use_container_width=True)
        
        st.subheader("Trial 指标数据前 20 行")
        st.dataframe(data["trial"].head(20), use_container_width=True)
        
    # ================= Tab 2: 可视化 =================
    with tab2:
        step_cols = [c for c in data["trial"].columns if 'step' in c.lower() and 'time' in c.lower()]
        
        if step_cols:
            target_col = step_cols[0]
            
            # 智能寻找步频列
            cadence_cols = [c for c in data["trial"].columns if 'cad' in c.lower()]
            if cadence_cols:
                x_col = cadence_cols[0]
            else:
                x_col = data["trial"].columns[0]

            st.subheader(f"基准指标 ({x_col}) vs 步时 ({target_col}) 关系散点图")
            fig = px.scatter(
                data["trial"], 
                x=x_col, 
                y=target_col, 
                color="是否异常", 
                color_discrete_map={True: "#ef4444", False: "#3b82f6"},
                title="红色点代表系统检测出的异常样本"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("步时均值分布图 (按 Trial 排序)")
            st.bar_chart(data["trial"][[target_col]].dropna())
        else:
            st.warning("在数据中未找到包含 'step' 和 'time' 的列，无法绘图。")

    # ================= Tab 3: 异常检测 =================
    with tab3:
        st.subheader("基于 Layer 2 (MAD) 算法的异常判断")
        st.info(f"当前规则：偏离受试者自身步时中位数超过 {mad_slider} 倍 MAD 的 Trial 判定为异常。")
        
        abnormal_df = data["trial"][data["trial"]['是否异常'] == True]
        
        if not abnormal_df.empty:
            st.error(f"⚠️ 检测到 {len(abnormal_df)} 个异常 Trial！请查看下方表格：")
            st.dataframe(abnormal_df, use_container_width=True)
        else:
            st.success("✅ 良好！在当前阈值下，未发现偏离基线的异常 Trial。")
            
        st.subheader("全部 Trial 异常判定结果")
        st.dataframe(data["trial"], use_container_width=True)
        
        # 下载按钮
        st.markdown("---")
        csv_data = data["trial"].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载完整分析报表 (CSV)",
            data=csv_data,
            file_name="gait_analysis_report.csv",
            mime="text/csv",
            type="primary"
        )
