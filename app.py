import streamlit as st
import pandas as pd
import plotly.express as px

#PAGE SETUP 
st.set_page_config(page_title="Shipping Dashboard", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color:#4ECDC4;'>🚀 Shipping Analytics Dashboard</h1>",
    unsafe_allow_html=True
)

#  LOAD DATA 
df = pd.read_csv("data.csv")

#  STYLE FUNCTION 
def clean_fig(fig):
    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=18),
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,  # FIX SIZE (important)
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_traces(marker=dict(line=dict(width=0)))
    return fig

#  ROW 1 
col1, col2 = st.columns(2)

with col1:
    ship_eff = df['Ship Mode'].value_counts().reset_index()
    ship_eff.columns = ['Ship Mode', 'Count']

    fig1 = px.bar(
        ship_eff,
        x='Count',
        y='Ship Mode',
        orientation='h',
        color='Count',
        color_continuous_scale='Tealgrn',
        title="🚚 Ship Mode"
    )
    st.plotly_chart(clean_fig(fig1), use_container_width=True)

with col2:
    fig2 = px.histogram(
        df,
        x='Lead Time',
        nbins=20,
        color_discrete_sequence=['#4ECDC4'],
        title="⏳ Lead Time"
    )
    st.plotly_chart(clean_fig(fig2), use_container_width=True)

# ---------------- ROW 2 ----------------
col3, col4 = st.columns(2)

with col3:
    delay_counts = df['Delayed'].value_counts().reset_index()
    delay_counts.columns = ['Status', 'Count']

    fig3 = px.pie(
        delay_counts,
        names='Status',
        values='Count',
        hole=0.5,
        color_discrete_sequence=['#FF6B6B', '#4ECDC4'],
        title="⚠️ Delay"
    )
    st.plotly_chart(clean_fig(fig3), use_container_width=True)

with col4:
    state_counts = df['State'].value_counts().head(10).reset_index()
    state_counts.columns = ['State', 'Orders']

    fig4 = px.bar(
        state_counts,
        x='State',
        y='Orders',
        color='Orders',
        color_continuous_scale='Blues',
        title="🌍 Top States"
    )
    fig4.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(clean_fig(fig4), use_container_width=True)

# ---------------- ROW 3 ----------------
col5, col6 = st.columns(2)

with col5:
    ship_mode_count = df['Ship Mode'].value_counts().reset_index()
    ship_mode_count.columns = ['Ship Mode', 'Count']

    fig5 = px.bar(
        ship_mode_count,
        x='Ship Mode',
        y='Count',
        color='Ship Mode',
        title="📦 Ship Mode Count"
    )
    st.plotly_chart(clean_fig(fig5), use_container_width=True)

with col6:
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    orders_time = df.groupby(df['Order Date'].dt.to_period("M")).size().reset_index()
    orders_time.columns = ['Month', 'Orders']
    orders_time['Month'] = orders_time['Month'].astype(str)

    fig6 = px.line(
        orders_time,
        x='Month',
        y='Orders',
        markers=True,
        title="📈 Orders Trend"
    )
    fig6.update_traces(line=dict(width=3, color='#4ECDC4'))
    st.plotly_chart(clean_fig(fig6), use_container_width=True)
