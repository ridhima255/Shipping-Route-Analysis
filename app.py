import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("Dataset Column Checker")

df = pd.read_csv("data.csv")import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_dark"

st.set_page_config(
    page_title="Shipping Route Analysis Dashboard",
    layout="wide"
)

st.markdown("""
<style>

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] p {
    color: white !important;
    font-weight: 700 !important;
}

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
    font-size: 36px !important;
    font-weight: 700 !important;
}

h3 {
    color: #6d28d9 !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

p {
    color: #312e81;
}

label {
    color: white !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.75);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.15);
}

[data-testid="metric-container"] label {
    color: #4c1d95 !important;
    font-weight: 700 !important;
}

[data-testid="metric-container"] div {
    color: #4c1d95 !important;
}

.stPlotlyChart {
    background: rgba(255,255,255,0.06);
    padding: 12px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.12);
}

</style>
""", unsafe_allow_html=True)

st.title("Shipping Route Analysis Dashboard")

df = pd.read_csv("data.csv")

df['Lead Time'] = df['Days for shipping (real)']

df['Delay Gap'] = (
    df['Days for shipping (real)'] -
    df['Days for shipment (scheduled)']
)

df['Status'] = df['Delay Gap'].apply(
    lambda x: 'Delayed' if x > 0 else 'On-Time'
)

state = st.sidebar.multiselect(
    "Select Customer State",
    sorted(df['Customer State'].dropna().unique()),
    default=sorted(df['Customer State'].dropna().unique())
)

mode = st.sidebar.multiselect(
    "Select Shipping Mode",
    sorted(df['Shipping Mode'].dropna().unique()),
    default=sorted(df['Shipping Mode'].dropna().unique())
)

segment = st.sidebar.multiselect(
    "Select Customer Segment",
    sorted(df['Customer Segment'].dropna().unique()),
    default=sorted(df['Customer Segment'].dropna().unique())
)

market = st.sidebar.multiselect(
    "Select Market",
    sorted(df['Market'].dropna().unique()),
    default=sorted(df['Market'].dropna().unique())
)

df = df[
    (df['Customer State'].isin(state)) &
    (df['Shipping Mode'].isin(mode)) &
    (df['Customer Segment'].isin(segment)) &
    (df['Market'].isin(market))
]

st.markdown("## Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "On-Time Delivery %",
    f"{round((df['Status']=='On-Time').mean()*100,2)}%"
)

col2.metric(
    "Average Delivery Delay",
    f"{round(df['Delay Gap'].mean(),2)} Days"
)

col3.metric(
    "Late Delivery Risk Ratio",
    f"{round(df['Late_delivery_risk'].mean()*100,2)}%"
)

col4.metric(
    "Total Orders",
    len(df)
)

st.markdown("---")

st.subheader("Lead Time Distribution")

fig = px.histogram(
    df,
    x='Lead Time',
    nbins=30,
    color='Status',
    color_discrete_sequence=['#8b5cf6', '#ec4899']
)

st.plotly_chart(fig, use_container_width=True)

colA, colB = st.columns(2)

with colA:

    st.subheader("Shipping Mode Efficiency")

    fig = px.box(
        df,
        x='Shipping Mode',
        y='Delay Gap',
        color='Shipping Mode'
    )

    st.plotly_chart(fig, use_container_width=True)

with colB:

    st.subheader("Late Delivery Risk Distribution")

    fig = px.pie(
        df,
        names='Late_delivery_risk',
        color_discrete_sequence=['#8b5cf6','#ec4899']
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Regional Delay Analysis")

region_delay = df.groupby(
    'Order Region'
)['Delay Gap'].mean().reset_index()

fig = px.bar(
    region_delay.sort_values(
        'Delay Gap',
        ascending=False
    ),
    x='Order Region',
    y='Delay Gap',
    color='Delay Gap',
    color_continuous_scale='RdPu'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Geographic Efficiency Map")

geo = df.groupby(
    ['Order State','Latitude','Longitude']
)['Delay Gap'].mean().reset_index()

fig = px.scatter_geo(
    geo,
    lat='Latitude',
    lon='Longitude',
    color='Delay Gap',
    hover_name='Order State',
    size='Delay Gap',
    color_continuous_scale='RdPu',
    scope='world'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

colC, colD = st.columns(2)

with colC:

    st.subheader("Top Performing States")

    top_routes = df.groupby(
        'Order State'
    )['Delay Gap'].mean().nsmallest(5)

    st.dataframe(top_routes)

with colD:

    st.subheader("Worst Performing States")

    worst_routes = df.groupby(
        'Order State'
    )['Delay Gap'].mean().nlargest(5)

    st.dataframe(worst_routes)

st.markdown("---")

st.subheader("Market Wise Logistics Efficiency")

market_delay = df.groupby(
    'Market'
)['Delay Gap'].mean().reset_index()

fig = px.bar(
    market_delay.sort_values(
        'Delay Gap',
        ascending=False
    ),
    x='Market',
    y='Delay Gap',
    color='Delay Gap',
    color_continuous_scale='Sunset'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Sales vs Delivery Delay")

fig = px.scatter(
    df,
    x='Delay Gap',
    y='Sales',
    color='Shipping Mode',
    size='Sales',
    hover_data=['Product Name']
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Customer Segment Impact")

segment_delay = df.groupby(
    'Customer Segment'
)['Delay Gap'].mean().reset_index()

fig = px.bar(
    segment_delay,
    x='Customer Segment',
    y='Delay Gap',
    color='Delay Gap',
    color_continuous_scale='Purp'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Shipping Mode Leaderboard")

leader = df.groupby('Shipping Mode').agg({
    'Delay Gap':'mean',
    'Sales':'sum',
    'Order Customer Id':'count'
}).reset_index()

leader.columns = [
    'Shipping Mode',
    'Average Delay',
    'Total Sales',
    'Total Orders'
]

st.dataframe(
    leader.sort_values('Average Delay')
)

highest_mode = df.groupby(
    'Shipping Mode'
)['Delay Gap'].mean().idxmax()

st.info(
    f"Highest average delay observed in: {highest_mode}"
)

if st.checkbox("Show Only Delayed Orders"):
    st.dataframe(
        df[df['Status'] == 'Delayed']
    )

st.write(df.columns)
