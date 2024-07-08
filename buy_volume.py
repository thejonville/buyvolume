#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

def main():
    st.title("Stock Buy/Sell Volume Proxy Tracker")

    # User input for stock symbol
    symbol = st.text_input("Enter stock symbol (e.g., AAPL):", "AAPL")

    # User input for start date and time
    start_date = st.date_input("Select start date:", datetime.now() - timedelta(days=30))
    start_time = st.time_input("Select start time:", datetime.min.time())

    # Combine date and time
    start_datetime = datetime.combine(start_date, start_time)

    # Get current date and time
    end_datetime = datetime.now()

    if st.button("Fetch Buy/Sell Volume Proxy Data"):
        # Fetch data using yfinance
        data = yf.download(symbol, start=start_datetime, end=end_datetime, interval="1d")

        if not data.empty:
            # Calculate daily price change
            data['Price_Change'] = data['Close'] - data['Open']
            
            # Create proxies for buy and sell volumes
            data['Buy_Volume_Proxy'] = data.apply(lambda row: row['Volume'] if row['Price_Change'] >= 0 else 0, axis=1)
            data['Sell_Volume_Proxy'] = data.apply(lambda row: row['Volume'] if row['Price_Change'] < 0 else 0, axis=1)

            # Display the data
            st.subheader(f"Buy/Sell Volume Proxy Data for {symbol}")
            st.write(data[['Close', 'Volume', 'Price_Change', 'Buy_Volume_Proxy', 'Sell_Volume_Proxy']])

            # Plot the data using Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(x=data.index, y=data['Buy_Volume_Proxy'], name='Buy Volume Proxy', marker_color='green'))
            fig.add_trace(go.Bar(x=data.index, y=data['Sell_Volume_Proxy'], name='Sell Volume Proxy', marker_color='red'))
            fig.update_layout(title='Buy vs Sell Volume Proxy', barmode='stack', xaxis_title='Date', yaxis_title='Volume')
            st.plotly_chart(fig)

            # Calculate and display statistics
            total_volume = data['Volume'].sum()
            buy_volume_proxy = data['Buy_Volume_Proxy'].sum()
            sell_volume_proxy = data['Sell_Volume_Proxy'].sum()
            buy_ratio = (buy_volume_proxy / total_volume) * 100 if total_volume > 0 else 0
            sell_ratio = (sell_volume_proxy / total_volume) * 100 if total_volume > 0 else 0

            st.subheader("Volume Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Volume", f"{total_volume:,}")
            with col2:
                st.metric("Buy Volume Proxy", f"{buy_volume_proxy:,}", f"{buy_ratio:.2f}%")
            with col3:
                st.metric("Sell Volume Proxy", f"{sell_volume_proxy:,}", f"{sell_ratio:.2f}%")

        else:
            st.error("No data available for the selected period.")

if __name__ == "__main__":
    main()

