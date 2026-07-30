import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="招聘人才分析看板", layout="wide")
st.title("招聘人才适配性分析看板")

@st.cache_data
def load_data():
    df = pd.read_csv("data/talent_recruitment_job_matching_dataset.csv")
    df['薪资差距'] = df['Expected_Salary_CNY_K'] - df['Current_Salary_CNY_K']
    df['薪资涨幅'] = (df['薪资差距'] / df['Current_Salary_CNY_K'] * 100).round(1)
    return df

df = load_data()

st.sidebar.header("筛选条件")
target_options = ['全部'] + sorted(df['Target_Category'].unique().tolist())
selected_target = st.sidebar.selectbox("适配性分类", target_options)

city_options = ['全部'] + sorted(df['Location'].unique().tolist())
selected_city = st.sidebar.selectbox("城市", city_options)

edu_options = ['全部'] + sorted(df['Highest_Degree'].unique().tolist())
selected_edu = st.sidebar.selectbox("学历", edu_options)

min_salary = int(df['Current_Salary_CNY_K'].min())
max_salary = int(df['Current_Salary_CNY_K'].max())
salary_range = st.sidebar.slider("当前薪资范围 (K)", min_salary, max_salary, (min_salary, max_salary))

filtered_df = df.copy()
if selected_target != '全部':
    filtered_df = filtered_df[filtered_df['Target_Category'] == selected_target]
if selected_city != '全部':
    filtered_df = filtered_df[filtered_df['Location'] == selected_city]
if selected_edu != '全部':
    filtered_df = filtered_df[filtered_df['Highest_Degree'] == selected_edu]
filtered_df = filtered_df[(filtered_df['Current_Salary_CNY_K'] >= salary_range[0]) & 
                           (filtered_df['Current_Salary_CNY_K'] <= salary_range[1])]

col1, col2, col3, col4, col5 = st.columns(5)
total = len(filtered_df)
high_count = (filtered_df['Target_Category'] == 'Highly Suitable').sum()
high_pct = high_count / total * 100 if total > 0 else 0
avg_salary = filtered_df['Current_Salary_CNY_K'].mean()
avg_exp = filtered_df['Experience_Years'].mean()

with col1:
    st.metric("总候选人数", f"{total:,}")
with col2:
    st.metric("高适配人数", high_count)
with col3:
    st.metric("高适配占比", f"{high_pct:.1f}%")
with col4:
    st.metric("平均薪资", f"{avg_salary:.1f}K")
with col5:
    st.metric("平均经验", f"{avg_exp:.1f}年")

st.divider()

# ========== 图表1：适配性分类分布（饼图） ==========
st.subheader("适配性分类分布")
col1, col2 = st.columns([2, 1])

with col1:
    target_dist = filtered_df['Target_Category'].value_counts().reset_index()
    target_dist.columns = ['适配性分类', '人数']
    fig1 = px.pie(target_dist, values='人数', names='适配性分类', 
                   color='适配性分类',
                   color_discrete_map={'Highly Suitable': '#4ECDC4', 
                                       'Less Suitable': '#FF6B6B', 
                                       'Moderately Suitable': '#FECA57'},
                   title='适配性分类分布')
    fig1.update_traces(textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.write("详细数据")
    st.dataframe(target_dist, hide_index=True, use_container_width=True)

st.divider()

# ========== 图表2：各城市候选人分布 ==========
st.subheader("各城市候选人分布 (Top 10)")
col1, col2 = st.columns([2, 1])

with col1:
    city_dist = filtered_df['Location'].value_counts().head(10).reset_index()
    city_dist.columns = ['城市', '人数']
    fig2 = px.bar(city_dist, y='城市', x='人数', orientation='h',
                   color='人数', color_continuous_scale='Blues',
                   title='各城市候选人分布')
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.write("详细数据")
    st.dataframe(city_dist, hide_index=True, use_container_width=True)

st.divider()

# ========== 图表3：各适配性人群平均薪资 ==========
st.subheader("各适配性人群平均薪资")
col1, col2 = st.columns([2, 1])

with col1:
    salary_by_target = filtered_df.groupby('Target_Category')['Current_Salary_CNY_K'].mean().reset_index()
    salary_by_target.columns = ['适配性分类', '平均薪资']
    fig3 = px.bar(salary_by_target, x='适配性分类', y='平均薪资',
                   color='适配性分类',
                   color_discrete_map={'Highly Suitable': '#4ECDC4', 
                                       'Less Suitable': '#FF6B6B', 
                                       'Moderately Suitable': '#FECA57'},
                   title='各适配性人群平均薪资',
                   text='平均薪资')
    fig3.update_traces(texttemplate='%{text:.1f}K', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.write("详细数据")
    st.dataframe(salary_by_target, hide_index=True, use_container_width=True)

st.divider()

# ========== 图表4：薪资分布箱线图 ==========
st.subheader("各适配性人群薪资分布")
col1, col2 = st.columns([2, 1])

with col1:
    fig4 = px.box(filtered_df, x='Target_Category', y='Current_Salary_CNY_K',
                   color='Target_Category',
                   color_discrete_map={'Highly Suitable': '#4ECDC4', 
                                       'Less Suitable': '#FF6B6B', 
                                       'Moderately Suitable': '#FECA57'},
                   title='各适配性人群薪资分布',
                   labels={'Target_Category': '适配性分类', 'Current_Salary_CNY_K': '薪资 (K)'})
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.write("薪资统计")
    salary_stats = filtered_df.groupby('Target_Category')['Current_Salary_CNY_K'].describe()
    st.dataframe(salary_stats, use_container_width=True)

st.divider()

# ========== 图表5：高适配人群学历分布 ==========
st.subheader("高适配人群学历分布")
col1, col2 = st.columns([2, 1])

high_df = filtered_df[filtered_df['Target_Category'] == 'Highly Suitable']

with col1:
    if len(high_df) > 0:
        edu_dist = high_df['Highest_Degree'].value_counts().head(8).reset_index()
        edu_dist.columns = ['学历', '人数']
        fig5 = px.bar(edu_dist, y='学历', x='人数', orientation='h',
                       color='人数', color_continuous_scale='Greens',
                       title='高适配人群学历分布')
        fig5.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("当前筛选条件下无高适配候选人")

with col2:
    st.write("详细数据")
    if len(high_df) > 0:
        st.dataframe(edu_dist, hide_index=True, use_container_width=True)
    else:
        st.info("无数据")

st.divider()

# ========== 图表6：高适配人群岗位分布 ==========
st.subheader("高适配人群岗位分布 (Top 10)")
col1, col2 = st.columns([2, 1])

with col1:
    if len(high_df) > 0:
        role_dist = high_df['Current_Role'].value_counts().head(10).reset_index()
        role_dist.columns = ['岗位', '人数']
        fig6 = px.bar(role_dist, y='岗位', x='人数', orientation='h',
                       color='人数', color_continuous_scale='Reds',
                       title='高适配人群岗位分布')
        fig6.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("当前筛选条件下无高适配候选人")

with col2:
    st.write("详细数据")
    if len(high_df) > 0:
        st.dataframe(role_dist, hide_index=True, use_container_width=True)
    else:
        st.info("无数据")

st.divider()

# ========== 图表7：招聘官评级分布 ==========
st.subheader("招聘官评级分布")
col1, col2 = st.columns([2, 1])

with col1:
    rating_dist = filtered_df['Recruiter_Rating'].value_counts().sort_index().reset_index()
    rating_dist.columns = ['招聘官评级', '人数']
    fig7 = px.bar(rating_dist, x='招聘官评级', y='人数',
                   color='人数', color_continuous_scale='Purples',
                   title='招聘官评级分布',
                   text='人数')
    fig7.update_traces(textposition='outside')
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    st.write("详细数据")
    st.dataframe(rating_dist, hide_index=True, use_container_width=True)

st.divider()

# ========== 图表8：各评级下的高适配占比 ==========
st.subheader("各评级下的高适配占比")
col1, col2 = st.columns([2, 1])

with col1:
    rating_high = filtered_df.groupby('Recruiter_Rating').apply(
        lambda x: (x['Target_Category'] == 'Highly Suitable').mean() * 100
    ).reset_index()
    rating_high.columns = ['招聘官评级', '高适配占比']
    fig8 = px.bar(rating_high, x='招聘官评级', y='高适配占比',
                   color='高适配占比', color_continuous_scale='Oranges',
                   title='各评级下的高适配占比',
                   text='高适配占比')
    fig8.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig8, use_container_width=True)

with col2:
    st.write("详细数据")
    st.dataframe(rating_high, hide_index=True, use_container_width=True)

st.divider()

# ========== 数据表格 ==========
st.subheader("全部候选人数据预览")
st.dataframe(filtered_df[['Candidate_ID', 'Gender', 'Age', 'Location', 'Highest_Degree', 
                          'Current_Role', 'Current_Salary_CNY_K', 'Expected_Salary_CNY_K',
                          'Target_Category', 'Recruiter_Rating']].head(100), 
             use_container_width=True)

st.caption("数据来源: Talent Recruitment Dataset | 工具: Streamlit")