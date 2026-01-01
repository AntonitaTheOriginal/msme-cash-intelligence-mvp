import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="MSME Cash Intelligence MVP", layout="centered")

st.title("💰 MSME Cash Intelligence – MVP")
st.write("Upload your bank statement (CSV). Read-only. No data stored.")

# ------------------ FILE UPLOAD ------------------
uploaded_file = st.file_uploader("Upload Bank Statement (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.lower() for c in df.columns]

    required = {"date", "credit", "debit", "balance"}
    if not required.issubset(df.columns):
        st.error("CSV must contain columns: date, credit, debit, balance")
    else:
        df["date"] = pd.to_datetime(df["date"])

        # ------------------ BASIC METRICS ------------------
        total_in = df["credit"].sum()
        total_out = df["debit"].sum()
        net_cash = total_in - total_out

        days = df["date"].nunique()
        avg_daily_in = total_in / days
        avg_daily_out = total_out / days

        burn_rate = avg_daily_out
        current_balance = df.iloc[-1]["balance"]
        survival_days = current_balance / burn_rate if burn_rate > 0 else 0

        # ------------------ STRESS METRICS ------------------
        threshold = avg_daily_out * 7
        low_balance_days = (df["balance"] < threshold).sum()
        negative_days = ((df["credit"] - df["debit"]) < 0).sum()

        # ------------------ ADVANCED INSIGHTS ------------------
        df["net_daily"] = df["credit"] - df["debit"]
        highest_expense_day = df.loc[df["debit"].idxmax()]["date"].date()
        highest_expense_amount = df["debit"].max()
        cash_volatility = df["net_daily"].std()

        # ------------------ DISPLAY ------------------
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

        # ------------------ CASH FLOW LINE CHART ------------------
        st.subheader("📉 Cash Balance Trend")
        st.line_chart(df.set_index("date")[["balance"]])

        # ------------------ EXPENSE CATEGORY SPLIT ------------------
        st.subheader("📊 Expense Category Split")

        if "description" not in df.columns:
            df["description"] = "general expense"

        def categorize(desc):
            desc = desc.lower()
            if "rent" in desc:
                return "Rent"
            elif "salary" in desc or "wage" in desc:
                return "Salaries"
            elif "electric" in desc or "eb" in desc:
                return "Utilities"
            elif "purchase" in desc or "stock" in desc:
                return "Inventory"
            else:
                return "Others"

        df["category"] = df["description"].apply(categorize)
        expense_summary = df.groupby("category")["debit"].sum()
        st.bar_chart(expense_summary)

        # ------------------ CASH STRESS CALENDAR ------------------
        st.subheader("📆 Cash Stress Calendar")
        df["stress"] = df["balance"] < threshold
        st.dataframe(df[["date", "balance", "stress"]])

        # ==================================================
        # 📦 PRODUCT PROFIT INTELLIGENCE (NEW)
        # ==================================================
        st.divider()
        st.header("📦 Product Profit Intelligence")

        product_data = {
            "product": ["Product A", "Product B", "Product C", "Product D"],
            "selling_price": [120, 90, 60, 40],
            "cost_price": [70, 55, 40, 30],
            "quantity": [1200, 1500, 2000, 2500]
        }

        prod_df = pd.DataFrame(product_data)

        prod_df["profit_per_unit"] = prod_df["selling_price"] - prod_df["cost_price"]
        prod_df["product_profit"] = prod_df["profit_per_unit"] * prod_df["quantity"]

        total_profit = prod_df["product_profit"].sum()
        prod_df["contribution_percent"] = (prod_df["product_profit"] / total_profit) * 100

        st.subheader("📊 Profit Contribution by Product (%)")
        st.bar_chart(prod_df.set_index("product")["contribution_percent"])

        # ------------------ MARGIN DROP SIMULATION ------------------
        st.subheader("📉 Margin Drop Impact Simulation")

        margin_drop = st.slider(
            "Simulate margin drop (%)",
            min_value=0,
            max_value=30,
            value=10
        ) / 100

        prod_df["new_selling_price"] = prod_df["selling_price"] * (1 - margin_drop)
        prod_df["new_profit_per_unit"] = prod_df["new_selling_price"] - prod_df["cost_price"]
        prod_df["new_product_profit"] = prod_df["new_profit_per_unit"] * prod_df["quantity"]

        prod_df["profit_loss"] = prod_df["product_profit"] - prod_df["new_product_profit"]

        st.bar_chart(prod_df.set_index("product")["profit_loss"])

        most_sensitive = prod_df.loc[prod_df["profit_loss"].idxmax(), "product"]

        st.info(
            f"🔴 **{most_sensitive}** is the most margin-sensitive product. "
            "Price reductions here will impact overall company profit the most."
        )

        # ------------------ PDF REPORT ------------------
        st.subheader("🧾 Download Monthly Report")

        if st.button("Generate PDF Report"):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            text = c.beginText(40, 800)

            text.textLine("MSME CASH INTELLIGENCE REPORT")
            text.textLine("")
            text.textLine(f"Total Inflow: ₹{total_in:,.0f}")
            text.textLine(f"Total Outflow: ₹{total_out:,.0f}")
            text.textLine(f"Net Cash: ₹{net_cash:,.0f}")
            text.textLine(f"Burn Rate: ₹{burn_rate:,.0f} / day")
            text.textLine(f"Cash Survival Days: {survival_days:.1f}")
            text.textLine(f"Low Balance Days: {low_balance_days}")

            c.drawText(text)
            c.showPage()
            c.save()

            st.download_button(
                label="📥 Download PDF",
                data=buffer.getvalue(),
                file_name="msme_cash_report.pdf",
                mime="application/pdf"
            )
