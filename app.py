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

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

threshold = st.sidebar.slider("Delay Threshold", 1, 2000, 1000)

df['Status'] = df['Lead Time'].apply(
    lambda x: 'Delayed' if x > threshold else 'On-Time'
)

state = st.sidebar.multiselect(
    "Select State",
    df['State/Province'].unique(),
    default=df['State/Province'].unique()
)

mode = st.sidebar.multiselect(
    "Select Ship Mode",
    df['Ship Mode'].unique(),
    default=df['Ship Mode'].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

df = df[
    (df['State/Province'].isin(state)) &
    (df['Ship Mode'].isin(mode)) &
    (df['Order Date'] >= start_date) &
    (df['Order Date'] <= end_date)
]

st.markdown("## Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Lead Time", round(df['Lead Time'].mean(),2))
col2.metric("Total Orders", len(df))
col3.metric("Total Routes", df['State/Province'].nunique())
col4.metric("Max Lead Time", df['Lead Time'].max())

st.markdown("---")

st.subheader("Lead Time Distribution")

fig = px.histogram(
    df,
    x='Lead Time',
    nbins=30,
    color='Status',
    color_discrete_sequence=['#8b5cf6','#ec4899']
)

st.plotly_chart(fig, use_container_width=True)

colA, colB = st.columns(2)

with colA:

    st.subheader("Shipping Mode Comparison")

    fig = px.box(
        df,
        x='Ship Mode',
        y='Lead Time',
        color='Ship Mode'
    )

    st.plotly_chart(fig, use_container_width=True)

with colB:

    st.subheader("Orders by Mode")

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

st.subheader("Geographic Efficiency")

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

geo = df.groupby('State/Province')['Lead Time'].mean().reset_index()

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

    st.subheader("Top Routes")

    top_routes = df.groupby(
        'State/Province'
    )['Lead Time'].mean().nsmallest(5)

    st.dataframe(top_routes)

with colD:

    st.subheader("Worst Routes")

    worst_routes = df.groupby(
        'State/Province'
    )['Lead Time'].mean().nlargest(5)

    st.dataframe(worst_routes)

st.markdown("---")

st.subheader("Leaderboard")

leader = df.groupby('Ship Mode').agg({
    'Lead Time':'mean',
    'Order Date':'count'
}).reset_index()

leader.columns = ['Ship Mode', 'Avg Lead Time', 'Orders']

st.dataframe(
    leader.sort_values('Avg Lead Time')
)

st.markdown("---")

st.subheader("Delay Insights")

fig = px.scatter(
    df,
    x='Lead Time',
    y='Order Date',
    color='Ship Mode',
    size='Lead Time'
)

st.plotly_chart(fig, use_container_width=True)

highest_mode = df.groupby(
    'Ship Mode'
)['Lead Time'].mean().idxmax()

st.info(f"Highest average lead time observed in: {highest_mode}")

if st.checkbox("Show Only Delayed Orders"):
    st.dataframe(df[df['Status'] == 'Delayed'])