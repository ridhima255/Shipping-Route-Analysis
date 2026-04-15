import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("📊 Shipping Route Analysis Dashboard")

# Load data
df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# =======================
# 🔥 SIDEBAR FILTERS
# =======================
st.sidebar.header("Filters")

selected_state = st.sidebar.multiselect(
    "Select State",
    df['State/Province'].unique(),
    default=df['State/Province'].unique()
)

selected_mode = st.sidebar.multiselect(
    "Select Ship Mode",
    df['Ship Mode'].unique(),
    default=df['Ship Mode'].unique()
)

filtered_df = df[
    (df['State/Province'].isin(selected_state)) &
    (df['Ship Mode'].isin(selected_mode))
]

# =======================
# 🔥 KPI SECTION
# =======================
col1, col2, col3 = st.columns(3)

col1.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(), 2))
col2.metric("Total Orders", len(filtered_df))
col3.metric("Max Lead Time", filtered_df['Lead Time'].max())

# =======================
# 🔥 TOP ROUTES
# =======================
route_analysis = filtered_df.groupby(['State/Province']).agg({
    'Lead Time': 'mean'
}).reset_index()

top_routes = route_analysis.nsmallest(10, 'Lead Time')

col4, col5 = st.columns(2)

with col4:
    st.subheader("🚀 Top Fastest Routes")
    fig1, ax1 = plt.subplots()
    sns.barplot(data=top_routes, x='Lead Time', y='State/Province', ax=ax1)
    st.pyplot(fig1)

# =======================
# 🔥 SHIP MODE ANALYSIS
# =======================
with col5:
    st.subheader("🚚 Shipping Mode Performance")
    ship_mode = filtered_df.groupby('Ship Mode')['Lead Time'].mean().reset_index()
    fig2, ax2 = plt.subplots()
    sns.barplot(data=ship_mode, x='Ship Mode', y='Lead Time', ax=ax2)
    st.pyplot(fig2)

# =======================
# 🔥 DISTRIBUTION
# =======================
st.subheader("📊 Lead Time Distribution")
fig3, ax3 = plt.subplots()
sns.histplot(filtered_df['Lead Time'], bins=20, ax=ax3)
st.pyplot(fig3)