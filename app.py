import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f3e8ff, #ffe4e6);
}
h1,h2,h3 { color:#4c1d95; }
</style>
""", unsafe_allow_html=True)

st.title("Logistics Intelligence Dashboard")

df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

threshold = st.sidebar.slider("Delay Threshold", 1, 2000, 1000)

df['Status'] = df['Lead Time'].apply(lambda x: 'Delayed' if x > threshold else 'On-Time')

state = st.sidebar.multiselect("State", df['State/Province'].unique(), default=df['State/Province'].unique())
mode = st.sidebar.multiselect("Ship Mode", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())

df = df[df['State/Province'].isin(state) & df['Ship Mode'].isin(mode)]

st.markdown("### Key Metrics")

col1,col2,col3,col4 = st.columns(4)

col1.metric("Avg Lead Time", round(df['Lead Time'].mean(),2))
col2.metric("Total Orders", len(df))
col3.metric("Total Routes", df['State/Province'].nunique())
col4.metric("Max Delay", df['Lead Time'].max())

st.markdown("---")

st.subheader("Lead Time Distribution")
fig = px.histogram(df, x='Lead Time', nbins=30, color='Status')
st.plotly_chart(fig, use_container_width=True)

colA,colB = st.columns(2)

with colA:
    st.subheader("Shipping Mode Comparison")
    fig = px.box(df, x='Ship Mode', y='Lead Time', color='Ship Mode')
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("Orders by Mode")
    mode_count = df['Ship Mode'].value_counts().reset_index()
    mode_count.columns = ['Ship Mode','Orders']
    fig = px.bar(mode_count, x='Ship Mode', y='Orders', color='Orders')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Orders Over Time")

trend = df.groupby(df['Order Date'].dt.to_period('M')).size().reset_index(name='Orders')
trend['Order Date'] = trend['Order Date'].astype(str)

fig = px.line(trend, x='Order Date', y='Orders', markers=True)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Geographic Efficiency")

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

geo = df.groupby('State/Province')['Lead Time'].mean().reset_index()
geo['code'] = geo['State/Province'].map(state_abbrev)

fig = px.choropleth(geo, locations='code', locationmode="USA-states",
                    color='Lead Time', scope="usa",
                    color_continuous_scale="RdYlGn_r")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

colC,colD = st.columns(2)

with colC:
    st.subheader("Top Routes")
    st.dataframe(df.groupby('State/Province')['Lead Time'].mean().nsmallest(5))

with colD:
    st.subheader("Worst Routes")
    st.dataframe(df.groupby('State/Province')['Lead Time'].mean().nlargest(5))

st.markdown("---")

st.subheader("Leaderboard")

leader = df.groupby('Ship Mode').agg({
    'Lead Time':'mean',
    'Order Date':'count'
}).reset_index()

leader.columns = ['Ship Mode','Avg Lead Time','Orders']

st.dataframe(leader.sort_values('Avg Lead Time'))
fig = px.box(df, x='Ship Mode', y='Actual Days')
st.plotly_chart(fig, use_container_width=True)
st.subheader("Correlation Insight")
st.write("Higher lead time observed in:", df.groupby('Ship Mode')['Actual Days'].mean().idxmax())
if st.checkbox("Show Only Delayed Orders"):
    st.dataframe(df[df['Status']=='Delayed'])
