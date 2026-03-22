import streamlit as st
import pandas as pd
import plotly.express as px

# .venv\Scripts\Activate.ps1

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="eSign Dashboard", layout="wide")

# -----------------------------
# CUSTOM UI (DARK + COLORFUL)
# -----------------------------
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: white;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.markdown("""
# 📊 eSign Business Report Dashboard
### 🎯 Objective:
Analyze transaction performance, failure points, and user activity.
---
""")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("hi.csv")

# -----------------------------
# DATA CLEANING
# -----------------------------
df['TXN Time'] = pd.to_datetime(df['TXN Time'], errors='coerce')
df['Date'] = df['TXN Time'].dt.date
df['Status'] = df['Status'].str.upper().str.strip()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

app_filter = st.sidebar.multiselect(
    "📱 Application",
    df['Application Name'].dropna().unique(),
    default=df['Application Name'].dropna().unique()
)

status_filter = st.sidebar.multiselect(
    "📊 Status",
    df['Status'].dropna().unique(),
    default=df['Status'].dropna().unique()
)

df = df[
    (df['Application Name'].isin(app_filter)) &
    (df['Status'].isin(status_filter))
]

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Total", len(df))
col2.metric("✅ Success", len(df[df['Status'] == "SUCCESS"]))
col3.metric("❌ Failed", len(df[df['Status'] == "FAILED"]))
col4.metric("⏳ Pending", len(df[df['Status'] == "PENDING"]))

st.markdown("---")

# -----------------------------
# Q1: DAY-WISE STATUS
# -----------------------------
st.markdown("## 📊 Q1. Day-wise Transaction Status Comparison")
st.markdown("👉 Compare SUCCESS, FAILED, PENDING transactions for each day")

status_trend = df.groupby(['Date', 'Status']).size().reset_index(name='Count')

fig1 = px.bar(
    status_trend,
    x="Date",
    y="Count",
    color="Status",
    barmode="group",
    color_discrete_map={
        "SUCCESS": "green",
        "FAILED": "red",
        "PENDING": "orange"
    }
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Q2: FAILURE BY STAGE
# -----------------------------
st.markdown("## ❌ Q2. Stage Responsible for Most Failures")
st.markdown("👉 Identify which stage causes maximum failures")

failed_df = df[df['Status'] == 'FAILED']
stage_fail = failed_df['Stage'].value_counts().reset_index()
stage_fail.columns = ['Stage', 'Count']

fig2 = px.bar(
    stage_fail,
    x="Stage",
    y="Count",
    color="Count",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Q3a: MOST TRANSACTIONS BY APP
# -----------------------------
st.markdown("## 📱 Q3a. Application with Most Transactions")

app_txn = df['Application Name'].value_counts().reset_index()
app_txn.columns = ['Application Name', 'Count']

fig3 = px.pie(
    app_txn,
    names="Application Name",
    values="Count",
    hole=0.4
)

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Q3b: SUCCESS VS FAILURE
# -----------------------------
st.markdown("## 📊 Q3b. Application-wise Success vs Failure")

app_status = df.groupby(['Application Name', 'Status']).size().reset_index(name='Count')

fig4 = px.bar(
    app_status,
    x="Application Name",
    y="Count",
    color="Status",
    barmode="group",
    color_discrete_map={
        "SUCCESS": "green",
        "FAILED": "red"
    }
)

st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# Q4: TOP PERSON
# -----------------------------
st.markdown("## 👤 Q4. Person with Most Successful Transactions")

success_df = df[df['Status'] == 'SUCCESS']
top_person = success_df['Person'].value_counts().reset_index()
top_person.columns = ['Person', 'Count']

fig5 = px.bar(
    top_person,
    x="Person",
    y="Count",
    color="Count",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig5, use_container_width=True)


# -----------------------------
# Q5: ADVANCED TIME ANALYSIS
# -----------------------------
st.markdown("## ⏰ Q5. Transaction Time vs Application & Status Analysis")
st.markdown("### 🎯 Identify peak failure hours and application-level patterns")

# Extract Hour
df['Hour'] = df['TXN Time'].dt.hour

# -----------------------------
# 1. HOURLY STATUS TREND
# -----------------------------
st.markdown("### 📊 Hourly Transaction Status Trend")

hourly_status = df.groupby(['Hour', 'Status']).size().reset_index(name='Count')

fig6 = px.line(
    hourly_status,
    x="Hour",
    y="Count",
    color="Status",
    markers=True,
    color_discrete_map={
        "SUCCESS": "green",
        "FAILED": "red",
        "PENDING": "orange"
    }
)

st.plotly_chart(fig6, use_container_width=True)

# -----------------------------
# 2. FAILURE HEATMAP (BEST PART 🔥)
# -----------------------------
st.markdown("### 🔥 Failure Heatmap (Hour vs Application)")

failed_df = df[df['Status'] == 'FAILED']

heatmap_data = failed_df.groupby(['Hour', 'Application Name']).size().reset_index(name='Failures')

fig7 = px.density_heatmap(
    heatmap_data,
    x="Hour",
    y="Application Name",
    z="Failures",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig7, use_container_width=True)

# -----------------------------
# 3. PEAK FAILURE HOUR
# -----------------------------
fail_hour = failed_df['Hour'].value_counts().reset_index()
fail_hour.columns = ['Hour', 'Failures']

peak_hour = fail_hour.sort_values(by='Failures', ascending=False).iloc[0]

st.error(f"🚨 Peak Failure Time: {peak_hour['Hour']}:00 - {peak_hour['Hour']+1}:00")

# -----------------------------
# 4. AUTO BUSINESS INSIGHTS 🔥
# -----------------------------
top_app = failed_df['Application Name'].value_counts().idxmax()
top_app_fail = failed_df['Application Name'].value_counts().max()

st.info(f"""
📌 **Key Insights:**

- ⏰ Highest failures occur at **{peak_hour['Hour']}:00 - {peak_hour['Hour']+1}:00**
- 📱 Application with most failures: **{top_app} ({top_app_fail} failures)**
- ⚠️ Possible reasons:
  - High traffic during peak hours
  - Server/API performance issues
  - Load imbalance

👉 Recommendation:
Monitor system performance during peak hours and optimize high-failure applications.
""")


# -----------------------------
# RAW DATA
# -----------------------------
st.markdown("## 📄 Raw Data")
st.dataframe(df)