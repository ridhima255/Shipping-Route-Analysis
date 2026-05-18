import pandas as pd
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

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

threshold = st.sidebar.slider(
    "Delay Threshold (Days)",
    1,
    1000,
    7
)

df['Status'] = df['Lead Time'].apply(
    lambda x: 'Delayed' if x > threshold else 'On-Time'
)

state = st.sidebar.multiselect(
    "Select State",
    sorted(df['State/Province'].dropna().unique()),
    default=sorted(df['State/Province'].dropna().unique())
)

mode = st.sidebar.multiselect(
    "Select Shipping Mode",
    sorted(df['Ship Mode'].dropna().unique()),
    default=sorted(df['Ship Mode'].dropna().unique())
)

division = st.sidebar.multiselect(
    "Select Division",
    sorted(df['Division'].dropna().unique()),
    default=sorted(df['Division'].dropna().unique())
)

region = st.sidebar.multiselect(
    "Select Region",
    sorted(df['Region'].dropna().unique()),
    default=sorted(df['Region'].dropna().unique())
)

df = df[
    (df['State/Province'].isin(state)) &
    (df['Ship Mode'].isin(mode)) &
    (df['Division'].isin(division)) &
    (df['Region'].isin(region))
]

st.markdown("## Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average Lead Time",
    f"{round(df['Lead Time'].mean(),2)} Days"
)

col2.metric(
    "Total Orders",
    len(df)
)

col3.metric(
    "On-Time Delivery %",
    f"{round((df['Status']=='On-Time').mean()*100,2)}%"
)

col4.metric(
    "Late Delivery Risk %",
    f"{round((df['Status']=='Delayed').mean()*100,2)}%"
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

    st.subheader("Shipping Mode Performance")

    fig = px.box(
        df,
        x='Ship Mode',
        y='Lead Time',
        color='Ship Mode'
    )

    st.plotly_chart(fig, use_container_width=True)

with colB:

    st.subheader("Orders by Shipping Mode")

    mode_count = df['Ship Mode'].value_counts().reset_index()
    mode_count.columns = ['Ship Mode', 'Orders']

    fig = px.bar(
        mode_count,
        x='Ship Mode',
        y='Orders',
        color='Orders',
        color_continuous_scale='purples'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Orders Over Time")

trend = df.groupby(
    df['Order Date'].dt.to_period('M')
).size().reset_index(name='Orders')

trend['Order Date'] = trend['Order Date'].astype(str)

fig = px.line(
    trend,
    x='Order Date',
    y='Orders',
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Regional Delay Analysis")

region_delay = df.groupby(
    'State/Province'
)['Lead Time'].mean().reset_index()

fig = px.bar(
    region_delay.sort_values(
        'Lead Time',
        ascending=False
    ).head(10),
    x='State/Province',
    y='Lead Time',
    color='Lead Time',
    color_continuous_scale='RdPu'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Geographic Efficiency Map")

state_abbrev = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR',
    'California':'CA','Colorado':'CO','Connecticut':'CT',
    'Delaware':'DE','Florida':'FL','Georgia':'GA',
    'Hawaii':'HI','Idaho':'ID','Illinois':'IL',
    'Indiana':'IN','Iowa':'IA','Kansas':'KS',
    'Kentucky':'KY','Louisiana':'LA','Maine':'ME',
    'Maryland':'MD','Massachusetts':'MA','Michigan':'MI',
    'Minnesota':'MN','Mississippi':'MS','Missouri':'MO',
    'Montana':'MT','Nebraska':'NE','Nevada':'NV',
    'New Hampshire':'NH','New Jersey':'NJ',
    'New Mexico':'NM','New York':'NY',
    'North Carolina':'NC','North Dakota':'ND',
    'Ohio':'OH','Oklahoma':'OK','Oregon':'OR',
    'Pennsylvania':'PA','Rhode Island':'RI',
    'South Carolina':'SC','South Dakota':'SD',
    'Tennessee':'TN','Texas':'TX','Utah':'UT',
    'Vermont':'VT','Virginia':'VA',
    'Washington':'WA','West Virginia':'WV',
    'Wisconsin':'WI','Wyoming':'WY'
}

geo = df.groupby(
    'State/Province'
)['Lead Time'].mean().reset_index()

geo['code'] = geo['State/Province'].map(state_abbrev)

geo = geo.dropna()

fig = px.choropleth(
    geo,
    locations='code',
    locationmode="USA-states",
    color='Lead Time',
    scope="usa",
    color_continuous_scale="RdPu"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

colC, colD = st.columns(2)

with colC:

    st.subheader("Top Performing States")

    top_routes = df.groupby(
        'State/Province'
    )['Lead Time'].mean().nsmallest(5)

    st.dataframe(top_routes)

with colD:

    st.subheader("Worst Performing States")

    worst_routes = df.groupby(
        'State/Province'
    )['Lead Time'].mean().nlargest(5)

    st.dataframe(worst_routes)

st.markdown("---")

st.subheader("Division Wise Delay Risk")

division_delay = df.groupby(
    'Division'
)['Lead Time'].mean().reset_index()

fig = px.bar(
    division_delay.sort_values(
        'Lead Time',
        ascending=False
    ),
    x='Division',
    y='Lead Time',
    color='Lead Time',
    color_continuous_scale='Sunset'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Sales vs Lead Time Insight")

fig = px.scatter(
    df,
    x='Lead Time',
    y='Sales',
    color='Ship Mode',
    size='Sales',
    hover_data=['Product Name']
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Shipping Mode Leaderboard")

leader = df.groupby('Ship Mode').agg({
    'Lead Time':'mean',
    'Sales':'sum',
    'Order ID':'count'
}).reset_index()

leader.columns = [
    'Ship Mode',
    'Average Lead Time',
    'Total Sales',
    'Total Orders'
]

st.dataframe(
    leader.sort_values('Average Lead Time')
)

highest_mode = df.groupby(
    'Ship Mode'
)['Lead Time'].mean().idxmax()

st.info(
    f"Highest average lead time observed in: {highest_mode}"
)

if st.checkbox("Show Only Delayed Orders"):
    st.dataframe(
        df[df['Status'] == 'Delayed']
    )
