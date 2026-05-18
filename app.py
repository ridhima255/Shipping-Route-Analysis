import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("Dataset Column Checker")

df = pd.read_csv("data.csv")

st.write(df.columns)
