import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# =======================
# 🎨 UI
# =======================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
h1,h2,h3 { color:white; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Logistics Delivery Performance Dashboard")
st.markdown("### 📌 Diagnostic Analytics for Shipping Efficiency & Delay Risk")

# =======================
# LOAD DATA
# =======================
try:
    df = pd.read_csv('data/data.csv')
except:
    df = pd.read_csv('data.csv')

# =======================
# DATA PREP
# =======================
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

df['Actual Days'] = (df['Ship Date'] - df['Order Date']).dt.days

if 'Days for shipment (scheduled)' in df.columns:
    df['Scheduled Days'] = df['Days for shipment (scheduled)']
else:
    df['Scheduled Days'] = df['Actual Days'] - 2

df['Delay Gap'] = df['Actual Days'] - df['Scheduled Days']

def classify(x):
    if x > 0:
        return 'Delayed'
    elif x < 0:
        return 'Early'
    else:
        return 'On-Time'

df['Delivery Status'] = df['Delay Gap'].apply(classify)

# =======================
# SIDEBAR
# =======================
st.sidebar.header("🎯 Filters")

state_filter = st.sidebar.multiselect("State", df['State/Province'].unique(), default=df['State/Province'].unique())
mode_filter = st.sidebar.multiselect("Ship Mode", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())

filtered_df = df[
    (df['State/Province'].isin(state_filter)) &
    (df['Ship Mode'].isin(mode_filter))
]

# =======================
# KPI
# =======================
on_time_rate = (filtered_df['Delivery Status']=='On-Time').mean()*100 if not filtered_df.empty else 0
delay_rate = (filtered_df['Delivery Status']=='Delayed').mean()*100 if not filtered_df.empty else 0
avg_delay = filtered_df['Delay Gap'].mean() if not filtered_df.empty else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("On-Time Delivery %", f"{on_time_rate:.1f}%")
col2.metric("Late Delivery Risk %", f"{delay_rate:.1f}%")
col3.metric("Avg Delay (Days)", round(avg_delay,2))
col4.metric("Total Orders", len(filtered_df))

st.markdown("---")

# =======================
# DELIVERY PERFORMANCE
# =======================
st.subheader("📊 Delivery Performance Overview")

if not filtered_df.empty:
    fig = px.pie(filtered_df, names='Delivery Status')
    st.plotly_chart(fig, use_container_width=True)

# =======================
# DELAY GAP
# =======================
st.subheader("📉 Delay Gap Distribution")

if not filtered_df.empty:
    fig = px.histogram(filtered_df, x='Delay Gap', nbins=30)
    st.plotly_chart(fig, use_container_width=True)

# =======================
# SHIPPING MODE
# =======================
st.subheader("🚀 Shipping Mode Efficiency")

if not filtered_df.empty:
    mode_perf = filtered_df.groupby('Ship Mode')['Delay Gap'].mean().reset_index()
    fig = px.bar(mode_perf, x='Ship Mode', y='Delay Gap', color='Delay Gap')
    st.plotly_chart(fig, use_container_width=True)

# =======================
# 🌍 GEOGRAPHICAL HEATMAP (IMPORTANT 🔥)
# =======================
st.subheader("🌍 Geographic Delay Heatmap")

state_abbrev = {
'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV',
'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY',
'North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT',
'Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV',
'Wisconsin':'WI','Wyoming':'WY'
}

if not filtered_df.empty:
    state_map = filtered_df.groupby('State/Province')['Delay Gap'].mean().reset_index()
    state_map['code'] = state_map['State/Province'].map(state_abbrev)
    state_map = state_map.dropna()

    fig = px.choropleth(
        state_map,
        locations='code',
        locationmode="USA-states",
        color='Delay Gap',
        scope="usa",
        color_continuous_scale="RdYlGn_r"
    )

    st.plotly_chart(fig, use_container_width=True)

# =======================
# REGIONAL RISK
# =======================
st.subheader("🌍 Regional Delay Risk")

if not filtered_df.empty:
    region_risk = filtered_df.groupby('Region')['Delivery Status']\
        .apply(lambda x: (x=='Delayed').mean())\
        .reset_index(name='Delay Risk')

    fig = px.bar(region_risk, x='Region', y='Delay Risk', color='Delay Risk')
    st.plotly_chart(fig, use_container_width=True)

# =======================
# DIAGNOSTICS
# =======================
st.subheader("🧠 Delay Diagnostics")

if not filtered_df.empty:
    worst_mode = filtered_df.groupby('Ship Mode')['Delay Gap'].mean().idxmax()
    worst_region = filtered_df.groupby('Region')['Delay Gap'].mean().idxmax()

    st.error(f"🚨 Highest delays in {worst_mode}")
    st.warning(f"⚠️ High-risk region: {worst_region}")

# =======================
# TREND
# =======================
st.subheader("📈 Trend Analysis")

if not filtered_df.empty:
    trend = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).size().reset_index(name='Orders')
    trend['Order Date'] = trend['Order Date'].astype(str)

    fig = px.line(trend, x='Order Date', y='Orders', markers=True)
    st.plotly_chart(fig, use_container_width=True)
