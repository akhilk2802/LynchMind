import streamlit as st
from utils.data_loader import get_dow30_tickers, get_stock_info
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="📈 Stock Analysis", layout="wide")
st.title("📈 Stock Analysis")

# ----------------- Sidebar: Chart Controls -----------------
st.sidebar.header("📊 Chart Controls")
range_option = st.sidebar.selectbox("📅 Select Date Range", ["1d", "5d", "1mo", "6mo", "1y", "5y"])
show_ma = st.sidebar.checkbox("Show Moving Averages", value=True)

interval_map = {
    "1d": "5m",
    "5d": "5m",
    "1mo": "1h",
    "6mo": "1d",
    "1y": "1d",
    "5y": "1wk"
}
interval = interval_map[range_option]

# ----------------- Ticker Selection by Company Name -----------------
@st.cache_data(ttl=86400)
def get_company_name_mapping():
    mapping = {}
    for ticker in get_dow30_tickers():
        try:
            name = yf.Ticker(ticker).info.get("shortName", ticker)
            mapping[name] = ticker
        except:
            continue
    return mapping

company_to_ticker = get_company_name_mapping()
company_names = sorted(company_to_ticker.keys())
selected_name = st.selectbox("Choose a company", company_names)
ticker = company_to_ticker[selected_name]

# ----------------- Fetch Stock Info -----------------
info = get_stock_info(ticker)
yf_info = yf.Ticker(ticker).info
hist = yf.Ticker(ticker).history(period=range_option, interval=interval)

# ----------------- Company Overview -----------------
st.subheader(f"{info.get('name', ticker)} ({ticker})")
st.markdown("### 🏢 Company Overview")
st.write(yf_info.get("longBusinessSummary", "No company description available."))

# ----------------- KPIs (5 + 5 Format) -----------------
# ----------------- KPIs (First row: price + market info, Second and Third row: ratios/metrics) -----------------
st.markdown("### 🔑 Key Performance Indicators (KPIs)")

# Row 2: Original financial KPIs
row2 = st.columns(5)
row2[0].metric("PEG Ratio", info.get("peg_ratio", "N/A"))
row2[1].metric("P/E Ratio", f"{round(info.get('pe_ratio', 0), 2)}" if info.get("pe_ratio") else "N/A" )
row2[2].metric("Debt/Equity", info.get("de_ratio", "N/A"))
row2[3].metric("Cash", f"${info.get('cash', 0):,}" if info.get("cash") else "N/A")
row2[4].metric("Debt", f"${info.get('debt', 0):,}" if info.get("debt") else "N/A")

st.write("")
# Row 3
row3 = st.columns(5)
row3[0].metric("Dividend Yield", f"{round(info.get('div_yield', 0), 2)}%" if info.get("div_yield") else "N/A")
row3[1].metric("Price/Cash Flow", round(info.get("price_to_cashflow", 0), 2) if info.get("price_to_cashflow") else "N/A")
row3[2].metric("Gross Margin", f"{round(info.get('gross_margin', 0) * 100, 2)}%" if info.get("gross_margin") else "N/A")
row3[3].metric("Operating Margin", f"{round(info.get('operating_margin', 0) * 100, 2)}%" if info.get("operating_margin") else "N/A")
row3[4].metric("ROE / ROA", f"{round(info.get('roe', 0) * 100, 2)}% / {round(info.get('roa', 0) * 100, 2)}%" if info.get("roe") and info.get("roa") else "N/A")

st.write("")
# ----------------- Candlestick Chart -----------------
# st.markdown("### 📉 Stock Price & Volume Chart")

# Moving Averages
if show_ma and not hist.empty:
    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()

volume_colors = ["green" if close >= open_ else "red" for open_, close in zip(hist["Open"], hist["Close"])]

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=hist.index,
    open=hist["Open"],
    high=hist["High"],
    low=hist["Low"],
    close=hist["Close"],
    name="Price"
))

fig.add_trace(go.Bar(
    x=hist.index,
    y=hist["Volume"],
    name="Volume",
    marker=dict(color=volume_colors),
    yaxis="y2",
    opacity=0.4,
    showlegend=False
))

# Add MAs
if show_ma and "MA20" in hist.columns:
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["MA20"],
        mode="lines",
        name="20MA",
        line=dict(color="orange", width=1.5)
    ))
if show_ma and "MA50" in hist.columns:
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["MA50"],
        mode="lines",
        name="50MA",
        line=dict(color="green", width=1.5)
    ))

fig.update_layout(
    title=f"{ticker} – {range_option} Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    yaxis2=dict(
        overlaying='y',
        side='right',
        title='Volume',
        showgrid=False
    ),
    xaxis_rangeslider_visible=False,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ----------------- Key Metrics Table (Styled) -----------------
#Row 1: Price, Close, 52W High/Low, Market Cap
st.markdown("---")
row1 = st.columns(5)
row1[0].metric("Open", f"${hist['Open'].iloc[0]:.2f}" if not hist.empty else "N/A")
row1[1].metric("Close", f"${hist['Close'].iloc[-1]:.2f}" if not hist.empty else "N/A")
row1[2].metric("52W High", f"${yf_info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(yf_info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A")
row1[3].metric("52W Low", f"${yf_info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(yf_info.get('fiftyTwoWeekLow'), (int, float)) else "N/A")
row1[4].metric("Market Cap", f"${yf_info.get('marketCap', 0) / 1e9:.2f}B" if isinstance(yf_info.get('marketCap'), (int, float)) else "N/A")
st.write("")

# ------------- PEG Ratio Analysis -------------------
st.markdown("---")
st.subheader("Peter Lynch's Favorite Metric")

# st.subheader("Peter Lynch's Favorite Metric")

try:
    pe_ratio = yf_info.get('trailingPE', None)
    earnings_growth = yf_info.get('earningsGrowth', None) * 100 if yf_info.get('earningsGrowth') else None
    forward_eps = yf_info.get('forwardEps', None)
    current_eps = yf_info.get('trailingEps', None)
    peg_from_api = yf_info.get('pegRatio', None)

    # Calculate PEG manually if not available
    if pe_ratio and earnings_growth and earnings_growth > 0:
        peg_calculated = pe_ratio / earnings_growth
    elif pe_ratio and current_eps and forward_eps and current_eps > 0:
        projected_growth = ((forward_eps / current_eps) - 1) * 100
        peg_calculated = pe_ratio / projected_growth if projected_growth > 0 else None
    else:
        peg_calculated = None

    peg = peg_from_api if peg_from_api else peg_calculated

    col1, col2 = st.columns(2)

    with col1:
        if peg:
            # Gauge
            peg_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=peg,
                title={'text': "PEG Ratio"},
                gauge={
                    'axis': {'range': [0, 3]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 1], 'color': "green"},
                        {'range': [1, 2], 'color': "yellow"},
                        {'range': [2, 3], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 1
                    }
                }
            ))
            peg_fig.update_layout(height=300)
            st.plotly_chart(peg_fig, use_container_width=True)

            # Verdict
            if peg < 1:
                st.success("**Lynch's View**: Potentially undervalued. PEG < 1 suggests you're getting growth at a reasonable price.")
            elif peg < 1.5:
                st.info("**Lynch's View**: Fairly valued. PEG between 1–1.5 is typically considered reasonable.")
            else:
                st.warning("**Lynch's View**: Potentially overvalued. PEG > 1.5 suggests you're paying too much for growth.")
        else:
            st.warning("PEG ratio not available or not enough data to calculate.")

    with col2:
        st.markdown("### Understanding PEG Ratio")
        st.markdown("""
        The PEG ratio (Price/Earnings to Growth) compares a stock's P/E ratio to its earnings growth rate.
        
        **Formula**: PEG = P/E Ratio ÷ Earnings Growth Rate (%)
        
        **Lynch's Rule of Thumb**:
        - PEG < 1: Undervalued
        - PEG ≈ 1: Fairly Valued
        - PEG > 1.5: Overvalued
        """)

        st.markdown("### Calculation Components")
        calc_data = {
            "Metric": ["P/E Ratio", "Earnings Growth Rate (%)", "Resulting PEG Ratio"],
            "Value": [
                f"{pe_ratio:.2f}" if pe_ratio else "N/A",
                f"{earnings_growth:.2f}%" if earnings_growth else "N/A",
                f"{peg:.2f}" if peg else "N/A"
            ]
        }
        st.table(pd.DataFrame(calc_data))

except Exception as e:
    st.error(f"Error calculating PEG ratio: {e}")
st.write("")
st.write("")
st.write("")
# ------------- Ten Bagger Potential -------------------
st.markdown("---")
st.subheader("Can this stock 10x?")

# st.subheader("Can this stock 10x?")

try:
    current_price = hist['Close'].iloc[-1]
    target_price = current_price * 10
    revenue_growth = yf_info.get('revenueGrowth', 0) if yf_info.get('revenueGrowth') else 0
    market_cap = yf_info.get('marketCap', 0)
    profit_margin = yf_info.get('profitMargins', 0) if yf_info.get('profitMargins') else 0
    inst_ownership = yf_info.get('heldPercentInstitutions', 0) if yf_info.get('heldPercentInstitutions') else 0

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### From ${current_price:.2f} to ${target_price:.2f}")
        growth_rates = [5, 10, 15, 20, 25, 30]
        years_needed = []

        for rate in growth_rates:
            years = np.log(10) / np.log(1 + rate/100)
            years_needed.append(round(years, 1))

        df_10x = pd.DataFrame({
            "Annual Growth Rate (%)": growth_rates,
            "Years to 10x": years_needed
        })
        st.table(df_10x)

        if revenue_growth > 0:
            company_years = np.log(10) / np.log(1 + revenue_growth)
            st.markdown(f"**At current revenue growth of {revenue_growth*100:.1f}%, this stock could 10x in {company_years:.1f} years.**")

    with col2:
        st.markdown("### Lynch Criteria for Ten Baggers")

        score = 0
        max_score = 4
        checklist = []

        if market_cap < 2e9:
            score += 1
            checklist.append("✅ Small market cap (< $2B)")
        elif market_cap < 10e9:
            score += 0.5
            checklist.append("⚠️ Medium market cap ($2B–$10B)")
        else:
            checklist.append("❌ Large market cap (> $10B)")

        if profit_margin > 0.15:
            score += 1
            checklist.append(f"✅ High profit margin ({profit_margin*100:.1f}%)")
        elif profit_margin > 0.08:
            score += 0.5
            checklist.append(f"⚠️ Moderate profit margin ({profit_margin*100:.1f}%)")
        else:
            checklist.append(f"❌ Low profit margin ({profit_margin*100:.1f}%)")

        if revenue_growth > 0.20:
            score += 1
            checklist.append(f"✅ Strong revenue growth ({revenue_growth*100:.1f}%)")
        elif revenue_growth > 0.10:
            score += 0.5
            checklist.append(f"⚠️ Moderate revenue growth ({revenue_growth*100:.1f}%)")
        else:
            checklist.append(f"❌ Weak revenue growth ({revenue_growth*100:.1f}%)")

        if inst_ownership < 0.3:
            score += 1
            checklist.append(f"✅ Low institutional ownership ({inst_ownership*100:.1f}%)")
        elif inst_ownership < 0.6:
            score += 0.5
            checklist.append(f"⚠️ Moderate institutional ownership ({inst_ownership*100:.1f}%)")
        else:
            checklist.append(f"❌ High institutional ownership ({inst_ownership*100:.1f}%)")

        for line in checklist:
            st.markdown(line)

        potential = (score / max_score) * 100

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=potential,
            title={'text': "Ten Bagger Potential"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        gauge.update_layout(height=250)
        st.plotly_chart(gauge, use_container_width=True)

        if potential >= 70:
            st.success("**High potential**: This stock shows many traits of a Ten Bagger.")
        elif potential >= 30:
            st.info("**Moderate potential**: Decent fundamentals, but further research needed.")
        else:
            st.warning("**Low potential**: Doesn't align with Lynch's Ten Bagger traits.")

except Exception as e:
    st.error(f"Error in Ten Bagger analysis: {e}")

# ------------- Lynch Custom Rule-Based Checklist -------------------
st.write("")
st.write("")
st.write("")
st.markdown("---")
st.subheader("Lynch Custom Rule-Based Checklist")

try:
    # Rules 1–6 from get_stock_info()
    peg_ratio = info.get("peg_ratio", None)
    pe_ratio = info.get("pe_ratio", None)
    debt_to_equity = info.get("de_ratio", None)
    total_cash = info.get("cash", 0)
    total_debt = info.get("debt", 0)
    dividend_yield = info.get("div_yield", 0)
    price_to_cashflow = info.get("price_to_cashflow", None)

    # Rules 7–8 from yfinance
    eps_growth = (yf_info.get('earningsGrowth') or 0) * 100
    insider_ownership = (yf_info.get('heldPercentInsiders') or 0) * 100

    pe_growth_ratio = (pe_ratio / eps_growth) if pe_ratio and eps_growth > 0 else None

    rules = [
        {
            "rule": "PEG Ratio < 1",
            "pass": isinstance(peg_ratio, (int, float)) and peg_ratio < 1,
            "explanation": f"PEG Ratio is {peg_ratio:.2f}. Ideally < 1 means undervalued relative to growth." if peg_ratio is not None else "PEG Ratio not available."
        },
        {
            "rule": "P/E Ratio < 20",
            "pass": isinstance(pe_ratio, (int, float)) and pe_ratio < 20,
            "explanation": (
                f"Lynch prefers companies where P/E is at or below the growth rate. "
                f"Current P/E ({pe_ratio:.2f}) to growth ({eps_growth:.2f}%) ratio is {pe_growth_ratio:.2f}."
                if pe_growth_ratio is not None else "P/E or growth data unavailable for ratio."
            )
        },
        {
            "rule": "Debt/Equity < 0.5",
            "pass": isinstance(debt_to_equity, (int, float)) and debt_to_equity < 0.5,
            "explanation": f"Debt/Equity is {debt_to_equity:.2f}. Lynch liked companies with little debt." if debt_to_equity is not None else "Not available."
        },
        {
            "rule": "Cash > Debt",
            "pass": total_cash > total_debt,
            "explanation": f"Company has ${total_cash:,} in cash vs ${total_debt:,} in debt. Strong financial position."
        },
        {
            "rule": "Dividend Yield > 2%",
            "pass": isinstance(dividend_yield, (int, float)) and dividend_yield > 2,
            "explanation": f"Dividend Yield is {dividend_yield:.2f}%. Lynch favored income-generating stocks."
        },
        {
            "rule": "Price to Cash Flow > 5",
            "pass": isinstance(price_to_cashflow, (int, float)) and price_to_cashflow > 5,
            "explanation": f"Price/Cash Flow is {price_to_cashflow:.2f}. Higher values may indicate overvaluation." if price_to_cashflow is not None else "Not available."
        },
        {
            "rule": "EPS Growth > 10%",
            "pass": eps_growth > 10,
            "explanation": f"EPS Growth is {eps_growth:.2f}%. Lynch sought consistent double-digit growth."
        },
        {
            "rule": "Insider Ownership > 5%",
            "pass": insider_ownership > 5,
            "explanation": f"Insiders own {insider_ownership:.2f}%. Indicates skin in the game."
        }
    ]

    passed = sum(1 for r in rules if r["pass"])
    total = len(rules)
    score = int((passed / total) * 100)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Lynch Score")
        st.progress(score / 100)
        st.write(f"{score}% ({passed}/{total} rules passed)")
        if score >= 80:
            st.success("✅ Lynch would likely approve this stock.")
        elif score >= 50:
            st.info("⚠️ Mixed results. Some promising traits.")
        else:
            st.warning("❌ Likely not a Lynch-style investment.")

    with col2:
        st.markdown("### Rule Evaluation")
        for rule in rules:
            icon = "✅" if rule["pass"] else "❌"
            st.markdown(f"{icon} **{rule['rule']}**")
            st.caption(rule["explanation"])
            st.write("")

except Exception as e:
    st.error(f"Error evaluating Lynch checklist: {e}")

