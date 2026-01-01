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

        # ---------- BASIC METRICS ----------
        total_in = df["credit"].sum()
        total_out = df["debit"].sum()
        net_cash = total_in - total_out

        days = df["date"].nunique()
        avg_daily_in = total_in / days
        avg_daily_out = total_out / days

        burn_rate = avg_daily_out
        current_balance = df.iloc[-1]["balance"]

        survival_days = (
            current_balance / burn_rate if burn_rate > 0 else 0
        )

        # ---------- STRESS METRICS ----------
        threshold = avg_daily_out * 7
        low_balance_days = (df["balance"] < threshold).sum()
        negative_days = ((df["credit"] - df["debit"]) < 0).sum()

        # ---------- ADVANCED INSIGHTS ----------
        df["net_daily"] = df["credit"] - df["debit"]
        highest_expense_day = df.loc[df["debit"].idxmax()]["date"].date()
        highest_expense_amount = df["debit"].max()

        cash_volatility = df["net_daily"].std()

        # ---------- DISPLAY ----------
        st.subheader("📊 Cash Overview")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Inflow", f"₹{total_in:,.0f}")
        col2.metric("Total Outflow", f"₹{total_out:,.0f}")
        col3.metric("Net Cash", f"₹{net_cash:,.0f}")

        st.subheader("📈 Daily Averages")
        col4, col5 = st.columns(2)

        col4.metric("Avg Daily Inflow", f"₹{avg_daily_in:,.0f}")
        col5.metric("Avg Daily Outflow", f"₹{avg_daily_out:,.0f}")

        st.subheader("🔥 Cash Survival")
        col6, col7 = st.columns(2)

        col6.metric("Burn Rate (₹/day)", f"₹{burn_rate:,.0f}")
        col7.metric("Cash Survival Days", f"{survival_days:.1f} days")

        st.subheader("🚨 Risk Indicators")

        if low_balance_days > 5 or negative_days > 7:
            st.error("🔴 HIGH CASH STRESS")
        else:
            st.success("🟢 Cash position looks stable")

        st.write(f"Low balance days: {low_balance_days}")
        st.write(f"Negative cash days: {negative_days}")

        st.subheader("🔍 Key Insights")
        st.write(
            f"📅 Highest expense day: **{highest_expense_day}** "
            f"(₹{highest_expense_amount:,.0f})"
        )

        if cash_volatility > avg_daily_out:
            st.warning("⚠️ Cash flow is highly unpredictable")
        else:
            st.success("✅ Cash flow is relatively stable")

