import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 强制 matplotlib 使用英文字体（解决云端乱码）
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="HR离职风险分析看板", layout="wide")
st.title("HR 员工离职风险分析看板")

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

df['风险分'] = (
    (df['Age'] < 30) * 0.3 +
    (df['MonthlyIncome'] < 3000) * 0.3 +
    (df['YearsAtCompany'] < 1) * 0.2 +
    (df['BusinessTravel'] == 'Travel_Frequently') * 0.2
) * 100

st.sidebar.header("筛选条件")
age_options = ['全部'] + sorted(df['年龄分组'].dropna().unique().tolist())
selected_age = st.sidebar.selectbox("选择年龄段", age_options)
job_options = ['全部'] + sorted(df['JobRole'].unique().tolist())
selected_job = st.sidebar.selectbox("选择岗位", job_options)

filtered_df = df.copy()
if selected_age != '全部':
    filtered_df = filtered_df[filtered_df['年龄分组'] == selected_age]
if selected_job != '全部':
    filtered_df = filtered_df[filtered_df['JobRole'] == selected_job]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总人数", len(filtered_df))
with col2:
    attrition_count = (filtered_df['Attrition'] == 'Yes').sum()
    st.metric("离职人数", attrition_count)
with col3:
    attrition_rate = attrition_count / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    st.metric("离职率", f"{attrition_rate:.1f}%")
with col4:
    avg_age = filtered_df['Age'].mean()
    st.metric("平均年龄", f"{avg_age:.1f}岁")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Attrition Rate by Age Group")
    age_attrition = filtered_df.groupby('年龄分组', observed=True)['Attrition'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    )
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    bars = ax1.bar(age_attrition.index, age_attrition.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax1.set_ylabel('Attrition Rate (%)')
    ax1.set_ylim(0, max(age_attrition.values) * 1.2 if len(age_attrition) > 0 else 50)
    for bar, val in zip(bars, age_attrition.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%', ha='center', va='bottom')
    st.pyplot(fig1)

with col2:
    st.subheader("Attrition Rate by Income Group")
    income_attrition = filtered_df.groupby('收入分组', observed=True)['Attrition'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    )
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars = ax2.bar(income_attrition.index, income_attrition.values, color=['#FF6B6B', '#FECA57', '#48DBFB', '#0ABDE3'])
    ax2.set_ylabel('Attrition Rate (%)')
    ax2.set_ylim(0, max(income_attrition.values) * 1.2 if len(income_attrition) > 0 else 50)
    for bar, val in zip(bars, income_attrition.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%', ha='center', va='bottom')
    st.pyplot(fig2)

st.divider()

st.subheader("Attrition Rate by Job Role")
job_attrition = filtered_df.groupby('JobRole')['Attrition'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
).sort_values(ascending=False)

fig3, ax3 = plt.subplots(figsize=(10, 5))
colors = ['#FF6B6B' if i < 3 else '#4ECDC4' for i in range(len(job_attrition))]
bars = ax3.barh(job_attrition.index, job_attrition.values, color=colors)
ax3.set_xlabel('Attrition Rate (%)')
for bar, val in zip(bars, job_attrition.values):
    ax3.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', va='center')
st.pyplot(fig3)

st.divider()

st.subheader("高风险员工 Top 10")
risk_df = filtered_df.nlargest(10, '风险分')[['Age', 'JobRole', 'MonthlyIncome', 'YearsAtCompany', 'BusinessTravel', '风险分']]
st.dataframe(risk_df.style.format({'风险分': '{:.0f}分'}), use_container_width=True)

st.caption("数据来源：IBM HR Analytics Employee Attrition Dataset | 看板工具：Streamlit")
