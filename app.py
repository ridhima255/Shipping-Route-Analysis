import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")


#  UI STYLE
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
h1 {color: #2c3e50;}
</style>
""", unsafe_allow_html=True)
st.title("📊 Shipping Analytics Dashboard")
st.markdown("### 🚀 Interactive Delivery Insights")


#  LOAD DATA
df = pd.read_csv('data.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Delayed'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > 7 else 'On-Time')


#  FILTERS
st.sidebar.title("🎛 Filters")
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


#  KPI
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(),2))
col2.metric("Max Lead Time", filtered_df['Lead Time'].max())
col3.metric("Total Orders", len(filtered_df))
col4.metric("Delayed Orders", filtered_df['Delayed'].value_counts().get('Delayed',0))
sns.set_style("whitegrid")


#  TABS 
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "📂 Data"])


#  TAB 1 (MAIN DASHBOARD)
with tab1:

    st.subheader("🚀 Top Routes")
    top_routes = filtered_df.groupby('State/Province')['Lead Time'].mean().nsmallest(10)

    fig, ax = plt.subplots()
    top_routes.plot(kind='barh', ax=ax)
    st.pyplot(fig)

    st.subheader("🐢 Slow Routes")
    slow_routes = filtered_df.groupby('State/Province')['Lead Time'].mean().nlargest(10)

    fig, ax = plt.subplots()
    slow_routes.plot(kind='barh', ax=ax)
    st.pyplot(fig)

    st.subheader("🚚 Ship Mode Performance")
    ship_mode = filtered_df.groupby('Ship Mode')['Lead Time'].mean()

    fig, ax = plt.subplots()
    ship_mode.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    st.subheader("📊 Distribution")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df['Lead Time'], bins=20, ax=ax)
    st.pyplot(fig)

    st.subheader("📦 Boxplot")
    fig, ax = plt.subplots()
    sns.boxplot(x=filtered_df['Lead Time'], ax=ax)
    st.pyplot(fig)

    st.subheader("📍 Orders by State")
    state_count = filtered_df['State/Province'].value_counts().head(10)

    fig, ax = plt.subplots()
    state_count.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    st.subheader("🌍 Region Performance")
    region = filtered_df.groupby('Region')['Lead Time'].mean()

    fig, ax = plt.subplots()
    region.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    st.subheader("🥧 Delay Distribution")
    delay_counts = filtered_df['Delayed'].value_counts()

    fig, ax = plt.subplots()
    ax.pie(delay_counts, labels=delay_counts.index, autopct='%1.1f%%')
    st.pyplot(fig)

    st.subheader("🥧 Ship Mode Distribution")
    ship_count = filtered_df['Ship Mode'].value_counts()

    fig, ax = plt.subplots()
    ax.pie(ship_count, labels=ship_count.index, autopct='%1.1f%%')
    st.pyplot(fig)


#  TAB 2 (TREND + INTERACTIVE)
with tab2:
    st.subheader("📈 Orders Over Time")

    trend = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).size()

    fig, ax = plt.subplots()
    trend.plot(ax=ax)
    st.pyplot(fig)

    st.subheader("📊 Choose Chart Type")

    chart_type = st.selectbox("Select", ["Bar", "Line"])

    data = filtered_df.groupby('Ship Mode')['Lead Time'].mean()

    fig, ax = plt.subplots()

    if chart_type == "Bar":
        data.plot(kind='bar', ax=ax)
    else:
        data.plot(kind='line', ax=ax)

    st.pyplot(fig)

    if st.button("🔍 Show Detailed Analysis"):
        detailed = filtered_df.groupby('State/Province')['Lead Time'].mean().sort_values()

        fig, ax = plt.subplots()
        detailed.plot(kind='barh', ax=ax)
        st.pyplot(fig)


#  TAB 3 (DATA VIEW)
with tab3:

    if st.checkbox("📂 Show Raw Data"):
        st.dataframe(filtered_df)
