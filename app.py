import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
h1,h2,h3 { color:white; }
</style>
""", unsafe_allow_html=True)

st.title("Shipping Route Analysis Dashboard")

df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Actual Days'] = (df['Ship Date'] - df['Order Date']).dt.days

threshold = st.sidebar.slider("Delay Threshold (Days)", 1, 20, 7)

df['Delay Gap'] = df['Actual Days'] - threshold

df['Status'] = df['Actual Days'].apply(
    lambda x: 'Delayed' if x > threshold else ('Early' if x < threshold else 'On-Time')
)

state = st.sidebar.multiselect("State", df['State/Province'].unique(), default=df['State/Province'].unique())
mode = st.sidebar.multiselect("Ship Mode", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())

df = df[df['State/Province'].isin(state) & df['Ship Mode'].isin(mode)]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Orders", len(df))
col2.metric("On-Time %", f"{(df['Status']=='On-Time').mean()*100:.1f}%")
col3.metric("Delay %", f"{(df['Status']=='Delayed').mean()*100:.1f}%")
col4.metric("Avg Delay", round(df['Delay Gap'].mean(), 2))

st.markdown("---")

st.subheader("Orders Trend")

trend = df.groupby(df['Order Date'].dt.to_period('M')).size().reset_index(name='Orders')
trend['Order Date'] = trend['Order Date'].astype(str)

fig = px.line(trend, x='Order Date', y='Orders', markers=True)
st.plotly_chart(fig, use_container_width=True)

colA, colB = st.columns(2)

with colA:
    st.subheader("Delay Distribution")
    fig = px.histogram(df, x='Delay Gap', nbins=30)
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("Delivery Status")
    fig = px.pie(df, names='Status')
    st.plotly_chart(fig, use_container_width=True)

colC, colD = st.columns(2)

with colC:
    st.subheader("Mode Efficiency")
    mode_perf = df.groupby('Ship Mode')['Delay Gap'].mean().reset_index()
    fig = px.bar(mode_perf, x='Ship Mode', y='Delay Gap', color='Delay Gap')
    st.plotly_chart(fig, use_container_width=True)

with colD:
    st.subheader("Orders by Mode")
    count_df = df['Ship Mode'].value_counts().reset_index()
    count_df.columns = ['Ship Mode', 'Count']
    fig = px.bar(count_df, x='Ship Mode', y='Count')
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Geographic Heatmap")

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

geo = df.groupby('State/Province')['Delay Gap'].mean().reset_index()
geo['code'] = geo['State/Province'].map(state_abbrev)
geo = geo.dropna()

fig = px.choropleth(geo, locations='code', locationmode="USA-states",
                    color='Delay Gap', scope="usa",
                    color_continuous_scale="RdYlGn_r")

st.plotly_chart(fig, use_container_width=True)

colE, colF = st.columns(2)

with colE:
    st.subheader("Region Risk")
    risk = df.groupby('Region')['Status'].apply(lambda x: (x=='Delayed').mean()).reset_index(name='Risk')
    fig = px.bar(risk, x='Region', y='Risk', color='Risk')
    st.plotly_chart(fig, use_container_width=True)

with colF:
    st.subheader("Delay by Mode")
    risk_mode = df.groupby('Ship Mode')['Status'].apply(lambda x: (x=='Delayed').mean()).reset_index(name='Risk')
    fig = px.bar(risk_mode, x='Ship Mode', y='Risk', color='Risk')
    st.plotly_chart(fig, use_container_width=True)

colG, colH = st.columns(2)

with colG:
    st.subheader("Best States")
    st.dataframe(df.groupby('State/Province')['Delay Gap'].mean().nsmallest(5))

with colH:
    st.subheader("Worst States")
    st.dataframe(df.groupby('State/Province')['Delay Gap'].mean().nlargest(5))
