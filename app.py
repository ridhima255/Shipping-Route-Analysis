import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"

st.set_page_config(layout="wide")

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f3e8ff, #ffe4e6);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b, #312e81);
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.block-container {
    padding-top: 1rem;
}

h1 {
    color: #4c1d95 !important;
    text-align: center;
    font-size: 52px !important;
    font-weight: 800 !important;
}

h2 {
    color: #5b21b6 !important;
    font-size: 40px !important;
    font-weight: 700 !important;
}

h3 {
    color: #6d28d9 !important;
    font-size: 30px !important;
    font-weight: 700 !important;
}

p, label, div {
    color: #312e81;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.7);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.15);
}

.stPlotlyChart {
    background: white;
    padding: 10px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.12);
}

</style>
""", unsafe_allow_html=True)

st.title("Shipping Route Analysis Dashboard")

df = pd.read_csv("data.csv")

df['Lead Time'] = df['Days for shipping (real)']

threshold = st.sidebar.slider("Delay Threshold", 1, 10, 3)

df['Status'] = df['Lead Time'].apply(
    lambda x: 'Delayed' if x > threshold else 'On-Time'
)

state = st.sidebar.multiselect(
    "Select State",
    df['Customer State'].unique(),
    default=df['Customer State'].unique()
)

mode = st.sidebar.multiselect(
    "Select Shipping Mode",
    df['Shipping Mode'].unique(),
    default=df['Shipping Mode'].unique()
)

df = df[
    (df['Customer State'].isin(state)) &
    (df['Shipping Mode'].isin(mode))
]

st.markdown("## Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Lead Time", round(df['Lead Time'].mean(), 2))
col2.metric("Total Orders", len(df))
col3.metric("Total Routes", df['Customer State'].nunique())
col4.metric("Max Lead Time", df['Lead Time'].max())

st.markdown("---")

st.subheader("Lead Time Distribution")

fig = px.histogram(
    df,
    x='Lead Time',
    nbins=20,
    color='Status',
    color_discrete_sequence=['#8b5cf6', '#ec4899']
)

st.plotly_chart(fig, use_container_width=True)

colA, colB = st.columns(2)

with colA:

    st.subheader("Shipping Mode Comparison")

    fig = px.box(
        df,
        x='Shipping Mode',
        y='Lead Time',
        color='Shipping Mode'
    )

    st.plotly_chart(fig, use_container_width=True)

with colB:

    st.subheader("Orders by Shipping Mode")

    mode_count = df['Shipping Mode'].value_counts().reset_index()
    mode_count.columns = ['Shipping Mode', 'Orders']

    fig = px.bar(
        mode_count,
        x='Shipping Mode',
        y='Orders',
        color='Orders',
        color_continuous_scale='purples'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Regional Delay Analysis")

region_delay = df.groupby('Customer State')['Lead Time'].mean().reset_index()

fig = px.bar(
    region_delay.sort_values('Lead Time', ascending=False).head(10),
    x='Customer State',
    y='Lead Time',
    color='Lead Time',
    color_continuous_scale='RdPu'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

colC, colD = st.columns(2)

with colC:

    st.subheader("Top Performing States")

    top_routes = df.groupby(
        'Customer State'
    )['Lead Time'].mean().nsmallest(5)

    st.dataframe(top_routes)

with colD:

    st.subheader("Worst Performing States")

    worst_routes = df.groupby(
        'Customer State'
    )['Lead Time'].mean().nlargest(5)

    st.dataframe(worst_routes)

st.markdown("---")

st.subheader("Shipping Mode Leaderboard")

leader = df.groupby('Shipping Mode').agg({
    'Lead Time':'mean',
    'Sales':'sum'
}).reset_index()

leader.columns = ['Shipping Mode', 'Avg Lead Time', 'Total Sales']

st.dataframe(
    leader.sort_values('Avg Lead Time')
)

st.markdown("---")

st.subheader("Sales vs Lead Time Insight")

fig = px.scatter(
    df,
    x='Lead Time',
    y='Sales',
    color='Shipping Mode',
    size='Sales'
)

st.plotly_chart(fig, use_container_width=True)

highest_mode = df.groupby(
    'Shipping Mode'
)['Lead Time'].mean().idxmax()

st.info(f"Highest average lead time observed in: {highest_mode}")

if st.checkbox("Show Only Delayed Orders"):
    st.dataframe(df[df['Status'] == 'Delayed'])