import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go

# Setup
companies = ["Doc", "Grumpy", "Happy", "Sleepy", "Bashful", "Sneezy", "Dopey"]
months = pd.date_range(start="2020-01-01", periods=60, freq='M')
news_events = [
    ("Positive Earnings Report", 0.10),
    ("Scandal Exposed", -0.15),
    ("New Tech Launched", 0.15),
    ("Regulation Hit", -0.10),
    ("Market Crash", -0.20),
    ("Buyout Rumors", 0.20)
]

# Simulate stock data
def simulate_stock_data():
    np.random.seed(42)
    base_prices = {c: random.uniform(100, 500) for c in companies}
    price_data = []
    events = []
    ohlc_data = {c: [] for c in companies}

    for date in months:
        daily_data = {}
        monthly_event = random.choice(companies + [None])
        event_text = ""

        for c in companies:
            last_price = base_prices[c] if len(price_data) == 0 else price_data[-1][c]
            change = np.random.normal(0, 0.05)

            if c == monthly_event:
                event = random.choice(news_events)
                change += event[1]
                event_text = f"{c}: {event[0]} ({event[1]*100:+.1f}%)"

            new_price = max(10, round(last_price * (1 + change), 2))
            base_prices[c] = new_price
            daily_data[c] = new_price

            open_p = round(last_price, 2)
            close_p = new_price
            high_p = round(max(open_p, close_p) * (1 + random.uniform(0.01, 0.05)), 2)
            low_p = round(min(open_p, close_p) * (1 - random.uniform(0.01, 0.05)), 2)
            ohlc_data[c].append([date, open_p, high_p, low_p, close_p])

        price_data.append(daily_data)
        events.append((date.strftime("%b %Y"), event_text))

    df_prices = pd.DataFrame(price_data, index=months)
    df_events = pd.DataFrame(events, columns=["Month", "Event"])
    df_ohlc = {c: pd.DataFrame(ohlc_data[c], columns=["Date", "Open", "High", "Low", "Close"]).set_index("Date") for c in companies}
    return df_prices, df_events, df_ohlc

# Initialize
df_prices, df_events, df_ohlc = simulate_stock_data()
portfolio = {c: 0 for c in companies}
balance = 100000

# App Interface
st.title("📈 Stock Market Simulator - Educational App")

# Portfolio Display
st.sidebar.header("Portfolio")
st.sidebar.write("**Balance:** ₹{:.2f}".format(balance))
for c in companies:
    st.sidebar.write(f"{c}: {portfolio[c]} shares")

# News Events Table
st.subheader("Recent Market Events")
st.dataframe(df_events.tail(10))

# Stock Selection
selected_stock = st.selectbox("Select a Company", companies)

# Charts
st.subheader(f"📊 {selected_stock} - Price Line Chart")
st.line_chart(df_prices[selected_stock])

st.subheader(f"🕯️ {selected_stock} - Candlestick Chart")
df_candle = df_ohlc[selected_stock].reset_index()
fig = go.Figure(data=[go.Candlestick(x=df_candle['Date'],
                                     open=df_candle['Open'],
                                     high=df_candle['High'],
                                     low=df_candle['Low'],
                                     close=df_candle['Close'])])
st.plotly_chart(fig)

# Buy/Sell Interface
st.subheader("💼 Trade Simulator")
action = st.radio("Action", ["Buy", "Sell"])
quantity = st.slider("Quantity", 1, 100, 10)
current_price = df_prices[selected_stock].iloc[-1]
total_cost = current_price * quantity

if st.button("Execute Trade"):
    if action == "Buy":
        if total_cost <= balance:
            portfolio[selected_stock] += quantity
            balance -= total_cost
            st.success(f"Bought {quantity} of {selected_stock} at ₹{current_price:.2f}")
        else:
            st.error("Insufficient balance.")
    elif action == "Sell":
        if portfolio[selected_stock] >= quantity:
            portfolio[selected_stock] -= quantity
            balance += total_cost
            st.success(f"Sold {quantity} of {selected_stock} at ₹{current_price:.2f}")
        else:
            st.error("Not enough stock to sell.")

# Final Note
st.info("This is a hypothetical educational app. Prices, events, and trades are all simulated.")
