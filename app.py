import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# ========== 页面配置 ==========
st.set_page_config(
    page_title="HR离职风险分析看板",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 自定义CSS样式 ==========
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        padding: 1rem 0 0.5rem 0;
        border-bottom: 4px solid #2563EB;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 0.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(37,99,235,0.12);
    }
    .metric-card .label {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .metric-card .delta {
        font-size: 0.8rem;
        color: #28a745;
    }
    .custom-divider {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(to right, #2563EB, #f8f9fa);
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 1.5rem 0 0.3rem 0;
        padding-left: 0.8rem;
        border-left: 4px solid #2563EB;
    }
    .section-desc {
        font-size: 0.95rem;
        color: #6c757d;
        margin: 0 0 1rem 0.8rem;
        padding: 0.5rem 1rem;
        background: #f8f9fa;
        border-radius: 6px;
        border-left: 3px solid #2563EB;
    }
    .conclusion-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #1e3a8a 100%);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1rem 0 0.5rem 0;
        color: white;
        box-shadow: 0 4px 20px rgba(37,99,235,0.2);
    }
    .conclusion-card .title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: #60A5FA;
    }
    .conclusion-card .item {
        font-size: 0.95rem;
        padding: 0.3rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .conclusion-card .item:last-child {
        border-bottom: none;
    }
    .conclusion-card .highlight {
        color: #FCD34D;
        font-weight: 600;
    }
    .footer {
        margin-top: 2.5rem;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 2px solid #e9ecef;
        text-align: center;
        color: #adb5bd;
        font-size: 0.8rem;
    }
    .footer .version {
        background: #e9ecef;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        display: inline-block;
        margin: 0 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<div class="main-title">员工离职风险分析看板</div>', unsafe_allow_html=True)

# ========== 加载数据 ==========
@st.cache_data
def load_data():
    df = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")
    bins = [18, 30, 40, 50, 70]
    labels = ['18-30岁', '30-40岁', '40-50岁', '50岁以上']
    df['年龄分组'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    bins_income = [0, 3000, 6000, 10000, 20000]
    labels_income = ['低收入', '中低收入', '中高收入', '高收入']
    df['收入分组'] = pd.cut(df['MonthlyIncome'], bins=bins_income, labels=labels_income, right=False)
    return df

df = load_data()

# ========== 设置中文字体 ==========
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("### 筛选条件")
    st.markdown("---")
    
    age_options = ['全部'] + sorted(df['年龄分组'].dropna().unique().tolist())
    selected_age = st.selectbox("年龄段", age_options)
    
    job_options = ['全部'] + sorted(df['JobRole'].unique().tolist())
    selected_job = st.selectbox("岗位", job_options)
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ========== 数据筛选 ==========
filtered_df = df.copy()
if selected_age != '全部':
    filtered_df = filtered_df[filtered_df['年龄分组'] == selected_age]
if selected_job != '全部':
    filtered_df = filtered_df[filtered_df['JobRole'] == selected_job]

# ========== KPI 卡片 ==========
total = len(filtered_df)
attrition_count = (filtered_df['Attrition'] == 'Yes').sum()
attrition_rate = attrition_count / total * 100 if total > 0 else 0
avg_age = filtered_df['Age'].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">总人数</div>
        <div class="value">{total}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">离职人数</div>
        <div class="value" style="color:#EF4444;">{attrition_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">离职率</div>
        <div class="value" style="color:#EF4444;">{attrition_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">平均年龄</div>
        <div class="value">{avg_age:.1f}岁</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ============================================================
# 分析结论总结（3条核心结论）
# ============================================================
age_attrition_all = df.groupby('年龄分组', observed=True)['Attrition'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
)
youngest_age = age_attrition_all.idxmax() if len(age_attrition_all) > 0 else ""
youngest_rate = age_attrition_all.max() if len(age_attrition_all) > 0 else 0

job_attrition_all = df.groupby('JobRole')['Attrition'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
).sort_values(ascending=False)
top_job = job_attrition_all.index[0] if len(job_attrition_all) > 0 else ""
top_job_rate = job_attrition_all.values[0] if len(job_attrition_all) > 0 else 0

st.markdown(f"""
<div class="conclusion-card">
    <div class="title">核心分析结论</div>
    <div class="item"> 整体离职率 <span class="highlight">{attrition_rate:.1f}%</span>，其中 <span class="highlight">{youngest_age}</span> 离职率最高（{youngest_rate:.1f}%）</div>
    <div class="item"> 离职风险最高的人群画像：<span class="highlight">18-30岁 + 低收入 + 销售代表 + 入职1年以内</span></div>
    <div class="item"> 建议重点关注 <span class="highlight">{top_job}</span> 岗位（离职率 {top_job_rate:.1f}%），优化薪酬体系和晋升路径</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ============================================================
# 图表1：各年龄段离职率
# ============================================================
st.markdown('<div class="section-title">各年龄段离职率</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">不同年龄段的离职率差异明显，帮助HR识别哪些年龄段的员工更容易流失。</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    age_attrition = filtered_df.groupby('年龄分组', observed=True)['Attrition'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    )
    
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    bars = ax1.bar(age_attrition.index, age_attrition.values, 
                   color=['#2563EB', '#60A5FA', '#93C5FD', '#BFDBFE'])
    ax1.set_ylabel('离职率 (%)', fontsize=11)
    ax1.set_ylim(0, max(age_attrition.values) * 1.2 if len(age_attrition) > 0 else 50)
    ax1.tick_params(axis='x', rotation=0, labelsize=10)
    for bar, val in zip(bars, age_attrition.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    st.pyplot(fig1)

with col2:
    st.write("详细数据")
    st.dataframe(age_attrition.reset_index().rename(
        columns={'index': '年龄段', 'Attrition': '离职率 (%)'}
    ), hide_index=True, use_container_width=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ============================================================
# 图表2：各收入段离职率
# ============================================================
st.markdown('<div class="section-title">各收入段离职率</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">分析不同收入水平的员工离职情况，判断薪酬水平对员工留存的影响。</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    income_attrition = filtered_df.groupby('收入分组', observed=True)['Attrition'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    )
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars = ax2.bar(income_attrition.index, income_attrition.values,
                   color=['#EF4444', '#F59E0B', '#60A5FA', '#2563EB'])
    ax2.set_ylabel('离职率 (%)', fontsize=11)
    ax2.set_ylim(0, max(income_attrition.values) * 1.2 if len(income_attrition) > 0 else 50)
    ax2.tick_params(axis='x', rotation=0, labelsize=10)
    for bar, val in zip(bars, income_attrition.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    st.pyplot(fig2)

with col2:
    st.write("详细数据")
    st.dataframe(income_attrition.reset_index().rename(
        columns={'index': '收入段', 'Attrition': '离职率 (%)'}
    ), hide_index=True, use_container_width=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ============================================================
# 图表3：各岗位离职率排名
# ============================================================
st.markdown('<div class="section-title">各岗位离职率排名</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">不同岗位的离职率差异显著，帮助HR精准定位流失最严重的岗位，制定针对性改善措施。</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    job_attrition = filtered_df.groupby('JobRole')['Attrition'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).sort_values(ascending=False)
    
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    colors = ['#EF4444' if i < 3 else '#60A5FA' for i in range(len(job_attrition))]
    bars = ax3.barh(job_attrition.index, job_attrition.values, color=colors)
    ax3.set_xlabel('离职率 (%)', fontsize=11)
    ax3.tick_params(axis='y', labelsize=9)
    for bar, val in zip(bars, job_attrition.values):
        ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')
    st.pyplot(fig3)

with col2:
    st.write("详细数据")
    st.dataframe(job_attrition.reset_index().rename(
        columns={'index': '岗位', 'Attrition': '离职率 (%)'}
    ).head(10), hide_index=True, use_container_width=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ============================================================
# 底部大表格（恢复完整数据）
# ============================================================
st.markdown('<div class="section-title">完整数据预览</div>', unsafe_allow_html=True)
st.dataframe(
    filtered_df[['Age', 'Attrition', 'JobRole', 'MonthlyIncome', 'YearsAtCompany', 
                 'BusinessTravel', 'Department', 'JobSatisfaction', 'EnvironmentSatisfaction']].head(100),
    use_container_width=True,
    hide_index=True
)

# ============================================================
# 底部信息
# ============================================================
st.markdown("""
<div class="footer">
    <span class="badge">版本 v2.0</span>
    <span class="badge">数据来源: IBM HR Analytics</span>
    <span class="badge">最后更新: 2026-07-30</span>
    <br><br>
    工具: Streamlit | 员工离职风险分析看板
</div>
""", unsafe_allow_html=True)
