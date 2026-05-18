import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"

st.set_page_config(
    page_title="Shipping Route Analysis Dashboard",
    layout="wide"
)

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: #f3f4f6;
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
    color: #111827 !important;
    font-size: 48px !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #111827 !important;
    font-weight: 700 !important;
}

label {
    color: white !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

[data-testid="metric-container"] {
    background: white !important;
    border-left: 6px solid #7c3aed;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.12);
}

[data-testid="metric-container"] * {
    color: #111827 !important;
}

.stPlotlyChart {
    background: white;
    padding: 10px;
    border-radius: 16px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

st.title("Logistics Performance Insights")

df = pd.read_csv("data.csv")

df['Lead Time'] = df['Days for shipping (real)']

df['Delay Gap'] = (
    df['Days for shipping (real)'] -
    df['Days for shipment (scheduled)']
)

df['Status'] = df['Delay Gap'].apply(
    lambda x: 'Delayed' if x > 0 else 'On-Time'
)

# SIDEBAR FILTERS

state = st.sidebar.multiselect(
    "Customer State",
    sorted(df['Customer State'].dropna().unique()),
    default=sorted(df['Customer State'].dropna().unique())
)

mode = st.sidebar.multiselect(
    "Shipping Mode",
    sorted(df['Shipping Mode'].dropna().unique()),
    default=sorted(df['Shipping Mode'].dropna().unique())
)

segment = st.sidebar.multiselect(
    "Customer Segment",
    sorted(df['Customer Segment'].dropna().unique()),
    default=sorted(df['Customer Segment'].dropna().unique())
)

market = st.sidebar.multiselect(
    "Market",
    sorted(df['Market'].dropna().unique()),
    default=sorted(df['Market'].dropna().unique())
)

df = df[
    (df['Customer State'].isin(state)) &
    (df['Shipping Mode'].isin(mode)) &
    (df['Customer Segment'].isin(segment)) &
    (df['Market'].isin(market))
]

# KPI CARDS

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "On-Time Delivery %",
        f"{round((df['Status']=='On-Time').mean()*100,2)}%"
    )

with k2:
    st.metric(
        "Avg Delivery Delay",
        f"{round(df['Delay Gap'].mean(),2)} Days"
    )

with k3:
    st.metric(
        "Late Delivery Risk",
        f"{round(df['Late_delivery_risk'].mean()*100,2)}%"
    )

with k4:
    st.metric(
        "Total Orders",
        len(df)
    )

st.markdown("---")

# ROW 1

c1, c2 = st.columns(2)

with c1:

    st.subheader("Lead Time Distribution")

    fig1 = px.histogram(
        df,
        x='Lead Time',
        color='Status',
        nbins=30,
        color_discrete_sequence=['#43a047', '#ef5350']
    )

    fig1.update_layout(height=350)

    st.plotly_chart(fig1, use_container_width=True)

with c2:

    st.subheader("Shipping Mode Efficiency")

    fig2 = px.box(
        df,
        x='Shipping Mode',
        y='Delay Gap',
        color='Shipping Mode'
    )

    fig2.update_layout(height=350)

    st.plotly_chart(fig2, use_container_width=True)

# ROW 2

c3, c4 = st.columns(2)

with c3:

    st.subheader("Regional Delay Analysis")

    region_delay = df.groupby(
        'Order Region'
    )['Delay Gap'].mean().reset_index()

    fig3 = px.bar(
        region_delay,
        x='Order Region',
        y='Delay Gap',
        color='Delay Gap',
        color_continuous_scale='RdYlGn_r'
    )

    fig3.update_layout(height=350)

    st.plotly_chart(fig3, use_container_width=True)

with c4:

    st.subheader("Customer Segment Impact")

    segment_delay = df.groupby(
        'Customer Segment'
    )['Delay Gap'].mean().reset_index()

    fig4 = px.bar(
        segment_delay,
        x='Customer Segment',
        y='Delay Gap',
        color='Delay Gap',
        color_continuous_scale='Sunset'
    )

    fig4.update_layout(height=350)

    st.plotly_chart(fig4, use_container_width=True)

# ROW 3

c5, c6 = st.columns(2)

with c5:

    st.subheader("Delivery Risk Bubble Map")

    geo = df.groupby(
        'Order State'
    ).agg({
        'Delay Gap':'mean',
        'Sales':'sum'
    }).reset_index()

    fig5 = px.scatter(
        geo,
        x='Order State',
        y='Delay Gap',
        size='Sales',
        color='Delay Gap',
        hover_name='Order State',
        color_continuous_scale='RdPu',
        size_max=40
    )

    fig5.update_layout(height=350)

    st.plotly_chart(fig5, use_container_width=True)

with c6:

    st.subheader("Sales vs Delivery Delay")

    fig6 = px.scatter(
        df,
        x='Delay Gap',
        y='Sales',
        color='Shipping Mode',
        size='Sales',
        hover_data=['Product Name']
    )

    fig6.update_layout(height=350)

    st.plotly_chart(fig6, use_container_width=True)

# ROW 4

c7, c8 = st.columns(2)

with c7:

    st.subheader("Top Performing States")

    top_routes = df.groupby(
        'Order State'
    )['Delay Gap'].mean().nsmallest(5)

    st.dataframe(top_routes)

with c8:

    st.subheader("Worst Performing States")

    worst_routes = df.groupby(
        'Order State'
    )['Delay Gap'].mean().nlargest(5)

    st.dataframe(worst_routes)

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

st.success(
    f"Highest average delay observed in: {highest_mode}"
)

if st.checkbox("Show Only Delayed Orders"):
    st.dataframe(
        df[df['Status'] == 'Delayed']
    )
