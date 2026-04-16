import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

# =======================
# 🎨 UI
# =======================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
[data-testid="stSidebar"] {
    background: #020617;
}
h1,h2,h3 { color:white; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Shipping Route Analysis Dashboard")

st.markdown("### 📌 Analyze delays, efficiency & logistics performance")

# =======================
# LOAD DATA
# =======================
try:
    df = pd.read_csv('data/data.csv')
except:
    df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# =======================
# SIDEBAR
# =======================
st.sidebar.header("🎯 Filters")

threshold = st.sidebar.slider("Delay Threshold", 0, 1500, 1000)

df['Delayed'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > threshold else 'On-Time')

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

# =======================
# KPI
# =======================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Orders", len(filtered_df))
col2.metric("Avg Lead Time", round(filtered_df['Lead Time'].mean(),2) if not filtered_df.empty else 0)
col3.metric("Max Lead Time", filtered_df['Lead Time'].max() if not filtered_df.empty else 0)
col4.metric("Delay %", f"{(filtered_df['Delayed']=='Delayed').mean()*100:.1f}%" if not filtered_df.empty else "0%")

# =======================
# SECTION 1
# =======================
st.subheader("🚀 Shipping Mode Performance")

colA, colB = st.columns(2)

with colA:
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(4,3))
        filtered_df.groupby('Ship Mode')['Lead Time'].mean().plot(kind='barh', ax=ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

with colB:
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(4,3))
        filtered_df['Ship Mode'].value_counts().plot(kind='bar', ax=ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

# =======================
# HEATMAP
# =======================
st.subheader("🌍 Geographic Performance")

state_abbrev = {
'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV',
'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY',
'North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT',
'Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV',
'Wisconsin':'WI','Wyoming':'WY'
}

if not filtered_df.empty:
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

# =======================
# SECTION 2
# =======================
colC, colD = st.columns(2)

with colC:
    st.subheader("📊 Lead Time Distribution")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(4,3))
        sns.histplot(filtered_df['Lead Time'], bins=20, kde=True, ax=ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

with colD:
    st.subheader("🥧 Delay Distribution")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(4,3))
        filtered_df['Delayed'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

# =======================
# SECTION 3
# =======================
colE, colF = st.columns(2)

with colE:
    st.subheader("📍 Orders by State")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(4,3))
        filtered_df['State/Province'].value_counts().head(10).plot(kind='bar', ax=ax)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

with colF:
    st.subheader("🌍 Region Performance")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(4,3))
        filtered_df.groupby('Region')['Lead Time'].mean().plot(kind='bar', ax=ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=False)

# =======================
# TREND FIXED
# =======================
st.subheader("📈 Trend Analysis")

if not filtered_df.empty:
    fig, ax = plt.subplots(figsize=(5,3))

    trend = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).size()
    trend.index = trend.index.to_timestamp()

    ax.plot(trend.index, trend.values, marker='o', linewidth=2)

    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#0f172a')

    ax.tick_params(colors='white')
    ax.spines[:].set_color('white')

    ax.set_xlabel("Month", color='white')
    ax.set_ylabel("Orders", color='white')

    ax.xaxis.set_major_locator(plt.MaxNLocator(6))
    plt.xticks(rotation=30)

    st.pyplot(fig, use_container_width=False)

# =======================
# BEST / WORST
# =======================
st.subheader("📌 Best vs Worst")

if not filtered_df.empty:
    best = filtered_df.groupby('State/Province')['Lead Time'].mean().nsmallest(5)
    worst = filtered_df.groupby('State/Province')['Lead Time'].mean().nlargest(5)

    col1, col2 = st.columns(2)

    with col1:
        st.write("🔥 Fastest")
        st.dataframe(best)

    with col2:
        st.write("⚠️ Slowest")
        st.dataframe(worst)

# =======================
# INSIGHTS
# =======================
st.subheader("🧠 Insights")

if not filtered_df.empty:
    if filtered_df['Lead Time'].mean() > 1200:
        st.error("🚨 High delivery time")
    else:
        st.success("✅ Performance stable")

# =======================
# DATA PANEL
# =======================
st.subheader("📊 Data Panel")

if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

search = st.text_input("🔍 Search State")

if search:
    st.write(filtered_df[filtered_df['State/Province'].str.contains(search, case=False)])
