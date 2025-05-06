import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(layout="wide", page_title="汽車銷售進階圖解報告 2")
st.title("🚗 汽車銷售進階圖解式分析報告 2")
st.markdown("""
- **設計: Aries Yeh V1.0**
""")
st.markdown(
    '<a href="https://auto-sales2-cb6fevkyg2ou5t9fd53sov.streamlit.app/" style="font-size:32px;">請點擊這裡👉🏻演示線上🚗 汽車銷售進階圖解式分析報告 2</a>',
    unsafe_allow_html=True
)

st.markdown("""
互動式儀表板協助洞察汽車銷售趨勢、產品表現、顧客行為、市場分布與行銷效果，作為商業決策的依據。
---
""")

# 資料載入與預處理
@st.cache_data
def load_data():
    df = pd.read_csv("Auto Sales data.csv")
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], dayfirst=True)
    df['YEAR'] = df['ORDERDATE'].dt.year
    df['MONTH'] = df['ORDERDATE'].dt.to_period('M')
    return df

df = load_data()

st.markdown("---")
st.subheader("1️⃣ 客戶生命週期分群圖")
st.caption("➤ 視覺化活躍、流失與潛力客戶（氣泡圖）")

latest_orders = df.groupby("CUSTOMERNAME")['ORDERDATE'].max().reset_index()
latest_orders['DAYS_SINCE_LASTORDER'] = (df['ORDERDATE'].max() - latest_orders['ORDERDATE']).dt.days
sales_sum = df.groupby("CUSTOMERNAME")['SALES'].sum().reset_index()
merged = pd.merge(latest_orders, sales_sum, on="CUSTOMERNAME")

fig1 = px.scatter(merged, x="DAYS_SINCE_LASTORDER", y="SALES", size="SALES", color="SALES",
                  hover_name="CUSTOMERNAME", title="客戶活躍程度與貢獻氣泡圖",
                  labels={"DAYS_SINCE_LASTORDER": "距上次訂單天數", "SALES": "總銷售金額"})
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("2️⃣ 銷售熱力地圖（國家 × 產品線）")
st.caption("➤ 比較不同國家對產品線的偏好（熱力交叉表）")

pivot = df.pivot_table(values='SALES', index='COUNTRY', columns='PRODUCTLINE', aggfunc='sum', fill_value=0)
fig2 = px.imshow(pivot, text_auto=True, color_continuous_scale='Blues', aspect="auto",
                 title="不同國家對產品線的銷售熱度")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("3️⃣ 單價 vs 數量利潤圖")
st.caption("➤ 利用分散圖顯示每筆交易的單價與數量，氣泡代表營收")

fig3 = px.scatter(df, x='PRICEEACH', y='QUANTITYORDERED', size='SALES', color='PRODUCTLINE',
                  title="單價與數量的利潤分布圖",
                  labels={'PRICEEACH': '單價', 'QUANTITYORDERED': '數量'})
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("4️⃣ 回購週期雷達圖（依產品線）")
st.caption("➤ 顯示每個產品線的平均回購週期")

repurchase = df.groupby(['CUSTOMERNAME', 'PRODUCTLINE'])['ORDERDATE'].agg(['min', 'max', 'count']).reset_index()
repurchase['DAYS_BETWEEN'] = (repurchase['max'] - repurchase['min']).dt.days / repurchase['count'].clip(lower=1)
radar_data = repurchase.groupby('PRODUCTLINE')['DAYS_BETWEEN'].mean().reset_index()

fig4 = go.Figure()
fig4.add_trace(go.Scatterpolar(
    r=radar_data['DAYS_BETWEEN'],
    theta=radar_data['PRODUCTLINE'],
    fill='toself',
    name='平均回購週期 (天)'
))
fig4.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False,
                   title="各產品線平均回購週期雷達圖")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("5️⃣ 國家 → 產品線流向圖")
st.caption("➤ 視覺化各國家顧客對應的產品線偏好（Sankey圖）")

from plotly.graph_objects import Sankey
sankey_data = df.groupby(['COUNTRY', 'PRODUCTLINE'])['SALES'].sum().reset_index()
countries = sankey_data['COUNTRY'].unique().tolist()
products = sankey_data['PRODUCTLINE'].unique().tolist()
labels = countries + products
source = sankey_data['COUNTRY'].apply(lambda x: countries.index(x)).tolist()
target = sankey_data['PRODUCTLINE'].apply(lambda x: len(countries) + products.index(x)).tolist()
values = sankey_data['SALES'].tolist()

fig5 = go.Figure(data=[go.Sankey(
    node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels),
    link=dict(source=source, target=target, value=values)
)])
fig5.update_layout(title_text="國家 → 產品線 銷售流向圖", font_size=10)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.subheader("6️⃣ Deal Size 潛力矩陣圖")
st.caption("➤ 以客戶數與平均交易額為軸，劃分出策略象限")

deal_data = df.groupby(['CUSTOMERNAME', 'DEALSIZE'])['SALES'].sum().reset_index()
deal_summary = deal_data.groupby('DEALSIZE').agg({'CUSTOMERNAME': 'nunique', 'SALES': 'mean'}).reset_index()
fig6 = px.scatter(deal_summary, x='CUSTOMERNAME', y='SALES', text='DEALSIZE',
                  title="交易規模潛力象限圖",
                  labels={'CUSTOMERNAME': '客戶數', 'SALES': '平均交易額'}, size=[30]*len(deal_summary))
fig6.update_traces(textposition='top center')
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.info("報告完畢。可根據業務策略需求進一步延伸分析面向，如客戶留存率、產品升級率、促銷反應等。")
