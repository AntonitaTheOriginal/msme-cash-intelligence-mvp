import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSME Cash Intelligence MVP", layout="centered")

st.title("💰 MSME Cash Intelligence – MVP")
st.write("Upload your bank statement (CSV). Read-only. No data stored.")

uploaded_file = st.file_uploader("Upload Bank Statement (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.lower() for c in df.columns]

    required = {"date", "credit", "debit", "balance"}
    if not required.issubset(df.columns):
        st.error("CSV must contain: date, credit, debit, balance")
    else:
        df["date"] = pd.to_datetime(df["date"])

        total_in = df["credit"].sum()
        total_out = df["debit"].sum()
        net = total_in - total_out

        avg_daily = total_out / df["date"].nunique()
        threshold = avg_daily * 7

        low_days = (df["balance"] < threshold).sum()
        neg_days = ((df["credit"] - df["debit"]) < 0).sum()

        st.subheader("📊 Cash Summary")
        st.metric("Money In", f"₹{total_in:,.0f}")
        st.metric("Money Out", f"₹{total_out:,.0f}")
        st.metric("Net Cash", f"₹{net:,.0f}")

        st.subheader("🚨 Cash Health")

        if low_days > 5 or neg_days > 7:
            st.error("🔴 High cash stress detected")
        else:
            st.success("🟢 Cash position looks stable")
