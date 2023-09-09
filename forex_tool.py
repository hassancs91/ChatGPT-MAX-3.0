import streamlit as st
from forex_python.converter import CurrencyRates
import plotly.graph_objs as go
from collections import deque
from alpha_vantage.foreignexchange import ForeignExchange
import time
import openai
import requests

currency_rates = CurrencyRates()

api_key_openai = ""
api_key_alpha_vantage = "FQ136LID1XFHOBZA"

def get_openai_response(api_key, question):
    openai.api_key = api_key
    response = openai.Completion.create(prompt=question, max_tokens=150)
    return response.choices[0].text.strip()

def get_currency_pairs():
    """Get a list of currency pairs."""
    currencies = list(currency_rates.get_rates('USD').keys())
    currency_pairs = [(base, target) for base in currencies for target in currencies if base != target]
    return currency_pairs

def fetch_historical_data(api_key, base_currency, target_currency):
    cc = ForeignExchange(key=api_key)
    data, _ = cc.get_currency_exchange_daily(from_symbol=base_currency, to_symbol=target_currency, outputsize='compact')  # 'full' for longer history
    return data


def analyze_with_openai(api_key, text):
    openai.api_key = api_key
    return "analysis of text"
    prompt = f"Analyze the following news: {text}"  # This can be customized
    response = openai.Completion.create(prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

# Alpha Vantage news fetch function
def fetch_alpha_vantage_news(api_key, symbol="MSFT", page_size=5):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    # Assuming 'news' is the key in the JSON response (adjust based on actual response structure)
    if 'news' in data:
        return data['news'][:page_size]
    else:
        return []

def main():
    # Sidebar Configuration
    st.sidebar.title("Configuration")
    api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
    if api_key:
        openai.api_key = api_key

    base_currency, target_currency = st.sidebar.selectbox("Select Currency Pair", get_currency_pairs(), format_func=lambda x: f"{x[0]}/{x[1]}")
    target_price = st.sidebar.number_input(f"Alert when {base_currency}/{target_currency} exceeds:", value=1.0, step=0.01)

    # Alert Display
    current_price = currency_rates.get_rate(base_currency, target_currency)
    if current_price > target_price:
        st.warning(f"Alert! {base_currency}/{target_currency} exceeded the target price. Current price: {current_price}")

    # Real-time price chart
    # For demonstration purposes, let's use a static chart here.
    fig = go.Figure(data=[go.Line(y=[current_price for _ in range(10)], name=f"{base_currency}/{target_currency}")])
    fig.update_layout(title=f"{base_currency}/{target_currency} Real-time Price", xaxis_title="Time", yaxis_title="Price")
    st.plotly_chart(fig)



    # Displaying and Analyzing News at the top
    st.subheader("Latest News Analysis")
    news_items = fetch_alpha_vantage_news(api_key_alpha_vantage, symbol="MSFT")  # Modify symbol as needed
    for item in news_items:
        news_text = item  # Adjust based on the actual structure of news data
        analysis = analyze_with_openai(api_key_openai, news_text)
        st.write(f"**News:** {news_text}")
        st.write(f"**Analysis:** {analysis}")



    st.subheader("Price History Table & Chart")
    # Price History Table & Chart
    # Mocking last month data here for simplicity. You might want to replace this with real historical data.
    #FQ136LID1XFHOBZA
    historical_data = fetch_historical_data("FQ136LID1XFHOBZA", base_currency, target_currency)
    last_30_days_data = dict(list(historical_data.items())[-30:])

    prices = list(last_30_days_data.values())
    dates = list(last_30_days_data.keys())
    # Create a DataFrame for table display
    import pandas as pd
    df = pd.DataFrame({
        'Date': dates,
        'Open': [data['1. open'] for data in prices],
        'High': [data['2. high'] for data in prices],
        'Low': [data['3. low'] for data in prices],
        'Close': [data['4. close'] for data in prices]
    })

    st.write("Price History for Last Month:")
    st.table(df)  # Displaying data in table format

    fig_history = go.Figure(data=[go.Line(x=dates, y=[data['4. close'] for data in prices], name=f"{base_currency}/{target_currency} last month")])
    fig_history.update_layout(title=f"{base_currency}/{target_currency} Price History", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig_history)

    # Question & Answer section
    # Chatbot
    st.subheader("Forex Chatbot")

    # Use session state to maintain a list of user questions and bot answers
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Your Question:")

    if st.button("Ask"):
        if api_key_openai and user_input:
            response = get_openai_response(api_key_openai, user_input)
            
            # Update chat history
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", response))

    # Display the chat history in a text area
    chat_content = "\n\n".join([f"{item[0]}: {item[1]}" for item in st.session_state.chat_history])
    st.text_area("Chat", chat_content, height=300)  # you can adjust height as needed

if __name__ == "__main__":
    main()
