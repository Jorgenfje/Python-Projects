import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Mini Dashboard", layout="wide")

st.title("Mini Dashboard - Time series demo")

# load demo CSV
DATA_PATH = Path(__file__).parent / "demo_data.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
df = df.sort_values("timestamp")

# sidebar controls
st.sidebar.header("Controls")
resample = st.sidebar.selectbox("Resample interval", ["None", "H", "D"])
show_hist = st.sidebar.checkbox("Show histogram", value=True)
window = st.sidebar.slider("Rolling window (points)", 1, 10, 3)

# resample if requested
if resample != "None":
    df = df.set_index("timestamp").resample(resample).mean().interpolate().reset_index()

# main plot
df["rolling"] = df["value"].rolling(window=window, min_periods=1).mean()
fig = px.line(df, x="timestamp", y=["value", "rolling"], labels={"value":"value","timestamp":"time"}, title="Value over time")
st.plotly_chart(fig, use_container_width=True)

# histogram
if show_hist:
    fig2 = px.histogram(df, x="value", nbins=20, title="Value distribution")
    st.plotly_chart(fig2, use_container_width=True)

# download data
csv = df.to_csv(index=False)
st.download_button("Download CSV", csv, file_name="export.csv", mime="text/csv")

st.markdown("**Notes:** Demo app. Replace demo_data.csv with real data.")
