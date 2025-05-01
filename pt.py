
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Investment Insights", layout="wide")
st.title("📊 Investment Insights Platform")

# Sidebar navigation
menu = st.sidebar.radio("Choose a tool", [
    "Consumer Credit Tool",
    "Investment Banking Tools",
    "Market Analytics",
    "M&A / Due Diligence"
])

# -------- Module 1: Consumer Credit Tool --------
if menu == "Consumer Credit Tool":
    st.header("💳 Consumer Credit Tool")

    if "loans" not in st.session_state:
        st.session_state.loans = []

    st.sidebar.subheader("➕ Add Loan")
    customer = st.sidebar.text_input("Customer Name")
    amount = st.sidebar.number_input("Loan Amount (SEK)", min_value=0.0)
    interest = st.sidebar.number_input("Interest Rate (%)", min_value=0.0)
    term = st.sidebar.number_input("Loan Term (months)", min_value=1, value=60)
    monthly_payment = st.sidebar.number_input("Monthly Payment (SEK)", min_value=0.0)
    bank = st.sidebar.text_input("Bank")

    if st.sidebar.button("Add Loan"):
        if customer and bank:
            st.session_state.loans.append({
                "Customer": customer,
                "Amount": amount,
                "Interest Rate": interest,
                "Monthly Payment": monthly_payment,
                "Bank": bank,
                "Term": term
            })
        else:
            st.sidebar.warning("Please enter customer name and bank.")

    if st.session_state.loans:
        df = pd.DataFrame(st.session_state.loans)
        df["Annual Interest"] = df["Amount"] * df["Interest Rate"] / 100
        total_amount = df["Amount"].sum()
        weighted_rate = (df["Amount"] * df["Interest Rate"]).sum() / total_amount
        total_monthly = df["Monthly Payment"].sum()

        st.subheader("📊 Loans Overview")
        st.dataframe(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Loan Amount", f"{total_amount:,.0f} SEK")
        col2.metric("Weighted Interest Rate", f"{weighted_rate:.2f}%")
        col3.metric("Total Monthly Payments", f"{total_monthly:,.0f} SEK")

# -------- Module 2: Investment Banking Tools --------
elif menu == "Investment Banking Tools":
    st.header("🏦 Investment Banking Tools")

    st.subheader("💰 Discounted Cash Flow (DCF)")
    cf = st.number_input("Annual Cash Flow (SEK)", value=1000.0)
    r = st.number_input("Discount Rate (%)", value=10.0) / 100
    n = st.number_input("Years", value=5)

    dcf_value = sum([cf / (1 + r)**t for t in range(1, int(n)+1)])
    st.metric("DCF Value", f"{dcf_value:,.2f} SEK")

    st.subheader("📈 Terminal Value")
    g = st.number_input("Growth Rate (%)", value=2.0) / 100
    terminal_value = (cf * (1 + g)) / (r - g) if r > g else 0
    terminal_discounted = terminal_value / (1 + r)**n
    st.metric("Discounted Terminal Value", f"{terminal_discounted:,.2f} SEK")

    st.subheader("📊 Multiples")
    net_income = st.number_input("Net Income", value=800.0)
    ebitda = st.number_input("EBITDA", value=1200.0)
    book_value = st.number_input("Book Value", value=3000.0)

    pe = dcf_value / net_income if net_income else 0
    ev_ebitda = dcf_value / ebitda if ebitda else 0
    pb = dcf_value / book_value if book_value else 0

    st.write(f"P/E: {pe:.2f}, EV/EBITDA: {ev_ebitda:.2f}, P/B: {pb:.2f}")

    st.subheader("🧪 Sensitivity Analysis")
    rates = [x / 100 for x in range(5, 16)]
    results = {f"{int(x*100)}%": sum([cf / (1 + x)**t for t in range(1, int(n)+1)]) for x in rates}
    st.bar_chart(pd.DataFrame.from_dict(results, orient="index", columns=["DCF Value"]))

# -------- Module 3: Market Analytics --------
elif menu == "Market Analytics":
    st.header("📈 Market Analytics")

    tickers = st.text_input("Enter comma-separated tickers", value="AAPL, MSFT")
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    if tickers:
        price_data = {}
        for t in tickers:
            hist = yf.Ticker(t).history(period="1y")
            if not hist.empty:
                price_data[t] = hist["Close"]

        if price_data:
            st.line_chart(pd.DataFrame(price_data))

    selected = st.selectbox("Select ticker for snapshot", tickers)
    if selected:
        info = yf.Ticker(selected).info
        st.write(f"Company: {info.get('longName', '-')}")
        st.write(f"Price: {info.get('currentPrice', '-')} USD")
        st.write(f"P/E: {info.get('trailingPE', '-')}, P/B: {info.get('priceToBook', '-')}, EV/EBITDA: {info.get('enterpriseToEbitda', '-')}")


# -------- Module 4: M&A / Due Diligence --------
elif menu == "M&A / Due Diligence":
    st.header("🤝 M&A / Due Diligence")

    st.subheader("🔍 Target Company Overview")
    company_name = st.text_input("Target Company Name")
    deal_value = st.number_input("Estimated Deal Value (SEK)", min_value=0.0)
    ebitda = st.number_input("Target EBITDA", min_value=0.0)
    ev_ebitda = deal_value / ebitda if ebitda else 0

    if company_name:
        st.write(f"**Company:** {company_name}")
        st.write(f"**Estimated EV/EBITDA:** {ev_ebitda:.2f}")

    st.subheader("📊 Scenario Analysis: Financing Structure")
    equity_input = st.number_input("Equity Contribution (SEK)", min_value=0.0, value=0.0)
    interest_rate = st.number_input("Debt Interest Rate (%)", min_value=0.0, value=5.0)
    years = st.number_input("Investment Horizon (years)", min_value=1, value=5)
    exit_ebitda_multiple = st.number_input("Exit EBITDA Multiple", min_value=0.0, value=8.0)
    ebitda_growth = st.number_input("Annual EBITDA Growth Rate (%)", min_value=0.0, value=5.0) / 100

    if deal_value > 0 and equity_input > 0 and ebitda > 0:
        debt_input = deal_value - equity_input
        annual_ebitda = ebitda * ((1 + ebitda_growth) ** years)
        exit_value = annual_ebitda * exit_ebitda_multiple
        interest_cost = debt_input * (interest_rate / 100) * years
        equity_return = exit_value - interest_cost - debt_input
        irr = (equity_return / equity_input) ** (1 / years) - 1

        st.metric("Total Exit Value", f"{exit_value:,.0f} SEK")
        st.metric("Estimated IRR", f"{irr*100:.2f}%")
        st.metric("Total Interest Cost", f"{interest_cost:,.0f} SEK")
        st.metric("Debt / Equity Ratio", f"{(debt_input / equity_input):.2f}")

        if st.button("📄 Export Scenario to PDF (function disabled)"):
            st.warning("PDF export is currently disabled in this version.")
