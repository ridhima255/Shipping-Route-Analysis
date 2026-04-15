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


st.subheader("🗺Geographic Shipping Map")

state_coords = {
    "Texas": (31.9686, -99.9018),
    "California": (36.7783, -119.4179),
    "New York": (43.0000, -75.0000),
    "Florida": (27.6648, -81.5158),
    "Illinois": (40.0000, -89.0000),
    "Pennsylvania": (41.2033, -77.1945),
    "Ohio": (40.4173, -82.9071),
    "Georgia": (32.1656, -82.9001),
    "North Carolina": (35.7822, -80.7935),
    "Michigan": (44.3148, -85.6024)
}

geo_df = filtered_df.groupby('State/Province').size().reset_index(name='Orders')

# Map lat-long
geo_df['latitude'] = geo_df['State/Province'].map(lambda x: state_coords.get(x, (37.0902, -95.7129))[0])
geo_df['longitude'] = geo_df['State/Province'].map(lambda x: state_coords.get(x, (37.0902, -95.7129))[1])

st.map(geo_df)


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
