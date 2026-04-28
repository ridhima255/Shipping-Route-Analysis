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

# LOAD
df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
df['Actual Days'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Scheduled Days'] = df.get('Days for shipment (scheduled)', df['Actual Days'] - 2)
df['Delay Gap'] = df['Actual Days'] - df['Scheduled Days']
df['Status'] = df['Delay Gap'].apply(lambda x: 'Delayed' if x>0 else ('Early' if x<0 else 'On-Time'))
st.sidebar.header("Filters")
state = st.sidebar.multiselect("State", df['State/Province'].unique(), default=df['State/Province'].unique())
mode = st.sidebar.multiselect("Ship Mode", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())
df = df[df['State/Province'].isin(state) & df['Ship Mode'].isin(mode)]
col1,col2,col3,col4 = st.columns(4)
col1.metric("Orders", len(df))
col2.metric("On-Time %", f"{(df['Status']=='On-Time').mean()*100:.1f}%")
col3.metric("Delay %", f"{(df['Status']=='Delayed').mean()*100:.1f}%")
col4.metric("Avg Delay", round(df['Delay Gap'].mean(),2))

st.markdown("---")
st.subheader("Orders Trend")

trend = df.groupby(df['Order Date'].dt.to_period('M')).size().reset_index(name='Orders')
trend['Order Date'] = trend['Order Date'].astype(str)

fig = px.line(trend, x='Order Date', y='Orders', markers=True, color_discrete_sequence=['cyan'])
st.plotly_chart(fig, use_container_width=True)

colA,colB = st.columns(2)

with colA:
    st.subheader("Delay Distribution")
    fig = px.histogram(df, x='Delay Gap', nbins=30, color_discrete_sequence=['orange'])
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("Delivery Status")
    fig = px.pie(df, names='Status')
    st.plotly_chart(fig, use_container_width=True)

colC,colD = st.columns(2)

with colC:
    st.subheader("Mode Efficiency")
    mode_perf = df.groupby('Ship Mode')['Delay Gap'].mean().reset_index()
    fig = px.bar(mode_perf, x='Ship Mode', y='Delay Gap', color='Delay Gap')
    st.plotly_chart(fig, use_container_width=True)

with colD:
    st.subheader(" Orders by Mode")
    fig = px.bar(df['Ship Mode'].value_counts().reset_index(),
                 x='Ship Mode', y='count')
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Geographic Heatmap")

state_abbrev = {'California':'CA','Texas':'TX','New York':'NY','Florida':'FL','Washington':'WA'}

geo = df.groupby('State/Province')['Delay Gap'].mean().reset_index()
geo['code'] = geo['State/Province'].map(state_abbrev)

fig = px.choropleth(geo, locations='code', locationmode="USA-states",
                    color='Delay Gap', scope="usa")

st.plotly_chart(fig, use_container_width=True)
colE,colF = st.columns(2)

with colE:
    st.subheader(" Region Risk")
    risk = df.groupby('Region')['Status'].apply(lambda x: (x=='Delayed').mean()).reset_index(name='Risk')
    fig = px.bar(risk, x='Region', y='Risk', color='Risk')
    st.plotly_chart(fig, use_container_width=True)

with colF:
    st.subheader("Delay by Mode")
    risk_mode = df.groupby('Ship Mode')['Status'].apply(lambda x: (x=='Delayed').mean()).reset_index(name='Risk')
    fig = px.bar(risk_mode, x='Ship Mode', y='Risk', color='Risk')
    st.plotly_chart(fig, use_container_width=True)

colG,colH = st.columns(2)

with colG:
    st.subheader(" Best States")
    st.dataframe(df.groupby('State/Province')['Delay Gap'].mean().nsmallest(5))

with colH:
    st.subheader("Worst States")
    st.dataframe(df.groupby('State/Province')['Delay Gap'].mean().nlargest(5))
