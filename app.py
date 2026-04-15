import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Shipping Route Analysis Dashboard")


# LOAD DATA
df = pd.read_csv('data.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
threshold = st.sidebar.slider("Delay Threshold", 0, 1500, 1000)
df['Delayed'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > threshold else 'On-Time')

# SIDEBAR FILTERS
st.sidebar.header("Filters")
selected_state = st.sidebar.multiselect(
    "State", df['State/Province'].unique(),
    default=df['State/Province'].unique()
)
selected_mode = st.sidebar.multiselect(
    "Ship Mode", df['Ship Mode'].unique(),
    default=df['Ship Mode'].unique()
)
filtered_df = df[
    (df['State/Province'].isin(selected_state)) &
    (df['Ship Mode'].isin(selected_mode))
]

# KPI SECTION
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", len(filtered_df))
col2.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(),2))
col3.metric("Max Lead Time", filtered_df['Lead Time'].max())
col4.metric("Delay %", f"{(filtered_df['Delayed']=='Delayed').mean()*100:.1f}%")

# ROUTE EFFICIENCY
st.subheader(" Route Efficiency Overview")
fig, ax = plt.subplots()
filtered_df.groupby('Ship Mode')['Lead Time'].mean().plot(kind='barh', ax=ax)
plt.grid()
st.pyplot(fig)


# LEADERBOARD
st.subheader(" Route Leaderboard")
leaderboard = filtered_df.groupby('Ship Mode').agg({
    'Lead Time':'mean',
    'Order ID':'count'
}).reset_index()
leaderboard.columns = ['Ship Mode','Avg Lead Time','Total Orders']
st.dataframe(leaderboard)

#  FIXED HEATMAP
st.subheader(" Geographic Shipping Heatmap")
state_abbrev = {
    "Texas":"TX","California":"CA","New York":"NY","Florida":"FL",
    "Illinois":"IL","Pennsylvania":"PA","Ohio":"OH","Georgia":"GA",
    "North Carolina":"NC","Michigan":"MI"
}
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

# GRAPHS
# 1
st.subheader("Lead Time Distribution")
fig, ax = plt.subplots()
sns.histplot(filtered_df['Lead Time'], bins=20, kde=True, ax=ax)
st.pyplot(fig)

# 2
st.subheader("Orders by State")
fig, ax = plt.subplots()
filtered_df['State/Province'].value_counts().head(10).plot(kind='bar', ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

# 3
st.subheader("Region Performance")
fig, ax = plt.subplots()
filtered_df.groupby('Region')['Lead Time'].mean().plot(kind='bar', ax=ax)
st.pyplot(fig)

# 4
st.subheader("Delay Distribution")
fig, ax = plt.subplots()
filtered_df['Delayed'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
st.pyplot(fig)

# 5
st.subheader("Ship Mode Count")
fig, ax = plt.subplots()
filtered_df['Ship Mode'].value_counts().plot(kind='bar', ax=ax)
st.pyplot(fig)

# 6
st.subheader("Orders Over Time")
fig, ax = plt.subplots()
filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).size().plot(ax=ax)
st.pyplot(fig)

# 7
st.subheader("Lead Time by Ship Mode")
fig, ax = plt.subplots()
sns.boxplot(data=filtered_df, x='Ship Mode', y='Lead Time', ax=ax)
st.pyplot(fig)

# 8
st.subheader("Lead Time Trend (Smooth)")
trend = filtered_df.sort_values('Order Date')
trend = trend.groupby('Order Date')['Lead Time'].mean()
fig, ax = plt.subplots()
trend.plot(ax=ax)
plt.grid()
st.pyplot(fig)
