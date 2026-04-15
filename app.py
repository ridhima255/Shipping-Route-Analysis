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


#  DATA EXPLORATION PANEL 
st.markdown("## 📊 Data Exploration Panel")
show_raw = st.checkbox("Show Raw Data")
if show_raw:
    st.dataframe(filtered_df)

# SEARCH
search_state = st.text_input("Search State")
if search_state:
    st.write(
        filtered_df[
            filtered_df['State/Province'].str.contains(search_state, case=False)
        ]
    )

st.subheader("Best & Worst Routes")

top_routes = filtered_df.groupby('State/Province')['Lead Time'].mean().nsmallest(5)
worst_routes = filtered_df.groupby('State/Province')['Lead Time'].mean().nlargest(5)

col1, col2 = st.columns(2)

with col1:
    st.write(" Fastest Routes")
    st.dataframe(top_routes)

with col2:
    st.write(" Slowest Routes")
    st.dataframe(worst_routes)
st.subheader(" Key Insights")

avg = filtered_df['Lead Time'].mean()

if avg > 1200:
    st.warning(" Overall shipping is slow. Optimization needed.")
else:
    st.success("Shipping performance is good.")
delay_rate = (filtered_df['Delayed']=='Delayed').mean()

if delay_rate > 0.7:
    st.error(" High delay rate detected!")
st.subheader(" Best Performing State")
best_state = filtered_df.groupby('State/Province')['Lead Time'].mean().idxmin()
st.success(f" {best_state} has the fastest delivery")
st.subheader("Bottleneck Region")
worst = filtered_df.groupby('Region')['Lead Time'].mean().idxmax()
st.error(f" {worst} region has highest delay")
st.subheader(" Detailed Data View")
st.dataframe(filtered_df.sort_values(by='Lead Time', ascending=False))
st.subheader("🚨 Delay Heat by State")

delay_rate = filtered_df.groupby('State/Province')['Delayed'].apply(lambda x: (x=='Delayed').mean())

fig, ax = plt.subplots(figsize=(4,3))
delay_rate.sort_values().plot(kind='barh', color='red', ax=ax)
st.pyplot(fig, use_container_width=False)
with st.spinner("Analyzing shipping data..."):
    import time
    time.sleep(1)
col1.metric(
    "Avg Lead Time",
    round(filtered_df['Lead Time'].mean(),2),
    delta="↓ Improving"
)
