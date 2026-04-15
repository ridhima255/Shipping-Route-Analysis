import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Shipping Route Analysis Dashboard")


# LOAD DATA
df = pd.read_csv('data.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Delayed'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > 7 else 'On-Time')


# FILTERS
#
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

#KPI Section
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(),2))
col2.metric("Total Orders", len(filtered_df))
col3.metric("Max Lead Time", filtered_df['Lead Time'].max())
col4.metric("Delayed Orders", filtered_df['Delayed'].value_counts().get('Delayed',0))


# ROUTE EFFICIENCY OVERVIEW 
st.subheader("Route Efficiency Overview")
route_eff = filtered_df.groupby('State/Province')['Lead Time'].mean().sort_values().head(10)
fig, ax = plt.subplots()
route_eff.plot(kind='barh', ax=ax)
st.pyplot(fig)


# GEOGRAPHIC SHIPPING MAP 
st.subheader(" Geographic Shipping Map")
geo_df = filtered_df.groupby('State/Province').size().reset_index(name='Orders')
st.map(geo_df.rename(columns={'State/Province':'location'}))


# LEAD TIME COMPARISON 
st.subheader(" Lead Time Comparison by Ship Mode")
fig, ax = plt.subplots()
sns.boxplot(data=filtered_df, x='Ship Mode', y='Lead Time', ax=ax)
st.pyplot(fig)


#  OTHER VISUALS
st.subheader(" Lead Time Distribution")
fig, ax = plt.subplots()
sns.histplot(filtered_df['Lead Time'], bins=20, ax=ax)
st.pyplot(fig)

st.subheader("Orders by State")
state_count = filtered_df['State/Province'].value_counts().head(10)

fig, ax = plt.subplots()
state_count.plot(kind='bar', ax=ax)
st.pyplot(fig)

st.subheader("Region Performance")
region = filtered_df.groupby('Region')['Lead Time'].mean()

fig, ax = plt.subplots()
region.plot(kind='bar', ax=ax)
st.pyplot(fig)

st.subheader("Delay Distribution")
delay_counts = filtered_df['Delayed'].value_counts()

fig, ax = plt.subplots()
ax.pie(delay_counts, labels=delay_counts.index, autopct='%1.1f%%')
st.pyplot(fig)

st.subheader(" Ship Mode Distribution")
ship_counts = filtered_df['Ship Mode'].value_counts()

fig, ax = plt.subplots()
ax.pie(ship_counts, labels=ship_counts.index, autopct='%1.1f%%')
st.pyplot(fig)


# TREND
st.subheader(" Orders Over Time")
trend = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).size()
fig, ax = plt.subplots()
trend.plot(ax=ax)
st.pyplot(fig)
