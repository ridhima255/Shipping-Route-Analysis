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
df['Delayed'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > 7 else 'On-Time')


# SIDEBAR FILTERS
st.sidebar.header("🔍 Filters")
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
col1.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(),2))
col2.metric("Total Orders", len(filtered_df))
col3.metric("Max Lead Time", filtered_df['Lead Time'].max())
col4.metric("Delay %", f"{(filtered_df['Delayed']=='Delayed').mean()*100:.1f}%")


# ROUTE EFFICIENCY

st.subheader(" Route Efficiency Overview")
route_eff = filtered_df.groupby('Ship Mode')['Lead Time'].mean()
fig, ax = plt.subplots()
route_eff.plot(kind='barh', ax=ax)
st.pyplot(fig)


# LEADERBOARD
st.subheader(" Route Leaderboard")
leaderboard = filtered_df.groupby('Ship Mode').agg({
    'Lead Time':'mean',
    'Order ID':'count'
}).reset_index()
leaderboard.columns = ['Ship Mode','Avg Lead Time','Total Orders']
st.dataframe(leaderboard)


# US HEATMAP

st.subheader("🌍 Geographic Shipping Heatmap")
state_map = filtered_df.groupby('State/Province')['Lead Time'].mean().reset_index()
fig = px.choropleth(
    state_map,
    locations='State/Province',
    locationmode="USA-states",
    color='Lead Time',
    scope="usa",
    color_continuous_scale="RdYlGn_r"
)
st.plotly_chart(fig, use_container_width=True)


#  MULTIPLE GRAPHS 
# 1
st.subheader("Lead Time Distribution")
fig, ax = plt.subplots()
sns.histplot(filtered_df['Lead Time'], bins=20, ax=ax)
st.pyplot(fig)

# 2
st.subheader("Orders by State")
fig, ax = plt.subplots()
filtered_df['State/Province'].value_counts().head(10).plot(kind='bar', ax=ax)
st.pyplot(fig)

# 3
st.subheader(" Region Performance")
fig, ax = plt.subplots()
filtered_df.groupby('Region')['Lead Time'].mean().plot(kind='bar', ax=ax)
st.pyplot(fig)

# 4
st.subheader(" Delay Distribution")
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
st.subheader(" Lead Time by Ship Mode")
fig, ax = plt.subplots()
sns.boxplot(data=filtered_df, x='Ship Mode', y='Lead Time', ax=ax)
st.pyplot(fig)

# 8
st.subheader("Lead Time by Region")
fig, ax = plt.subplots()
sns.boxplot(data=filtered_df, x='Region', y='Lead Time', ax=ax)
st.pyplot(fig)

# 9
st.subheader(" Orders by Region")
fig, ax = plt.subplots()
filtered_df['Region'].value_counts().plot(kind='bar', ax=ax)
st.pyplot(fig)

# 10
st.subheader(" Avg Lead Time by State")
fig, ax = plt.subplots()
filtered_df.groupby('State/Province')['Lead Time'].mean().head(10).plot(kind='bar', ax=ax)
st.pyplot(fig)

# 11
st.subheader("Ship Mode vs Delay")
fig, ax = plt.subplots()
pd.crosstab(filtered_df['Ship Mode'], filtered_df['Delayed']).plot(kind='bar', ax=ax)
st.pyplot(fig)

# 12
st.subheader(" Orders by Customer")
fig, ax = plt.subplots()
filtered_df['Customer ID'].value_counts().head(10).plot(kind='bar', ax=ax)
st.pyplot(fig)

# 13
st.subheader("Lead Time Trend")
fig, ax = plt.subplots()
filtered_df.sort_values('Order Date').groupby('Order Date')['Lead Time'].mean().plot(ax=ax)
st.pyplot(fig)

# 14
st.subheader(" Region vs Delay")
fig, ax = plt.subplots()
pd.crosstab(filtered_df['Region'], filtered_df['Delayed']).plot(kind='bar', ax=ax)
st.pyplot(fig)

# 15
st.subheader("Ship Mode vs Orders")
fig, ax = plt.subplots()
filtered_df.groupby('Ship Mode').size().plot(kind='bar', ax=ax)
st.pyplot(fig)
