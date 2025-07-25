import streamlit as st
import json
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="📊 Entry Signal Scanner", layout="wide")
st.title("📈 Entry Signal Dashboard")

# Load JSON
try:
    with open(r"C:\Users\OEM\Documents\Jack\signal_results.json") as f:
        signal_by_date = json.load(f)
except FileNotFoundError:
    st.error("🚫 signal_results.json not found. Run generate_signals.py first.")
    signal_by_date = {}

# Get last 5 business days (weekdays only)
today = pd.Timestamp.today()
business_days = pd.bdate_range(end=today, periods=6).strftime('%Y-%m-%d').tolist()

# Display
st.subheader("✅ Entry Signals in Last 5 Business Days")

for date in reversed(business_days):  # show most recent first
    st.markdown(f"**📅 {date}**")
    tickers = signal_by_date.get(date, [])
    if tickers:
        st.write(sorted(tickers))
    else:
        st.info(f"❌ No signals found on {date}")
