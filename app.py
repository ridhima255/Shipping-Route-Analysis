import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
[data-testid="stSidebar"] {
    background: #020617;
}
h1, h2, h3 { color: white; }
</style>
""", unsafe_allow_html=True)

st.title(" Shipping Route Analysis Dashboard")

# LOAD DATA
try:
    df = pd.read_csv('data/data.csv')
except:
    df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# DELAY
threshold = st.sidebar.slider("Delay Threshold", 0, 1500, 1000)
df['Delayed'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > threshold else 'On-Time')

# FILTERS
st.sidebar.header("Filters")

state_filter = st.sidebar.multiselect(
    "State", df['State/Province'].unique(),
    default=df['State/Province'].unique()
)

mode_filter = st.sidebar.multiselect(
    "Ship Mode", df['Ship Mode'].unique(),
    default=df['Ship Mode'].unique()
)

filtered_df = df[
    (df['State/Province'].isin(state_filter)) &
    (df['Ship Mode'].isin(mode_filter))
]

# KPI
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", len(filtered_df))
col2.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(),2))
col3.metric("Max Lead Time", filtered_df['Lead Time'].max())
col4.metric("Delay %", f"{(filtered_df['Delayed']=='Delayed').mean()*100:.1f}%")

# HEATMAP
st.subheader(" US Shipping Efficiency Heatmap")

state_abbrev = {...}  # same as yours

state_map = filtered_df.groupby('State/Province')['Lead Time'].mean().reset_index()
state_map['code'] = state_map['State/Province'].map(state_abbrev)
state_map = state_map.dropna()

fig = px.choropleth(
    state_map,
    locations='code',
    locationmode="USA-states",
    color='Lead Time',
    scope="usa",
    color_continuous_scale="RdYlGn_r"
)

st.plotly_chart(fig, use_container_width=True)

# ROUTE EFFICIENCY
st.subheader(" Route Efficiency Overview")

fig, ax = plt.subplots(figsize=(4,3))
filtered_df.groupby('Ship Mode')['Lead Time'].mean().plot(kind='barh', ax=ax)
plt.tight_layout()
st.pyplot(fig, use_container_width=False)

# LEADERBOARD
st.subheader("Route Leaderboard")

leaderboard = filtered_df.groupby('Ship Mode').agg({
    'Lead Time':'mean',
    'Order ID':'count'
}).reset_index()

leaderboard.columns = ['Ship Mode','Avg Lead Time','Total Orders']
st.dataframe(leaderboard)

# GRAPH GRID
colA, colB = st.columns(2)

with colA:
    st.subheader("Lead Time Distribution")
    fig, ax = plt.subplots(figsize=(4,3))
    sns.histplot(filtered_df['Lead Time'], bins=20, kde=True, ax=ax)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

with colB:
    st.subheader(" Delay Distribution")
    fig, ax = plt.subplots(figsize=(4,3))
    filtered_df['Delayed'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

colC, colD = st.columns(2)

with colC:
    st.subheader(" Orders by State")
    fig, ax = plt.subplots(figsize=(4,3))
    filtered_df['State/Province'].value_counts().head(10).plot(kind='bar', ax=ax)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

with colD:
    st.subheader(" Ship Mode Count")
    fig, ax = plt.subplots(figsize=(4,3))
    filtered_df['Ship Mode'].value_counts().plot(kind='bar', ax=ax)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

# TREND
st.subheader("Orders Over Time")

fig, ax = plt.subplots(figsize=(4,3))
filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).size().plot(ax=ax)
plt.tight_layout()
st.pyplot(fig, use_container_width=False)
