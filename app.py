import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Shipping Route Analysis Dashboard")

df = pd.read_csv('data.csv')

df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

route_analysis = df.groupby(['State/Province']).agg({
    'Lead Time': 'mean'
}).reset_index()

top_routes = route_analysis.nsmallest(10, 'Lead Time')

st.subheader("Top Fastest Routes")

fig, ax = plt.subplots()
sns.barplot(data=top_routes, x='Lead Time', y='State/Province', ax=ax)
st.pyplot(fig)