import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(page_title="Top 20 Intraday Alpha Engine", page_icon="🛡️", layout="wide")

st.title("🛡️ Institutional-Grade Top 20 Low-Risk Intraday Engine")
st.write("Applies a multi-layered mathematical defense grid using zero-block market data streams.")

# Direct structural ticker list of highly liquid Large-Caps on the NSE to completely avoid operator penny stocks
NIFTY_LIQUID_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", 
    "INFY.NS", "SBI.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", 
    "LT.NS", "BAJAJFINSV.NS", "AXISBANK.NS", "M&M.NS", "MARUTI.NS", 
    "SUNPHARMA.NS", "KOTAKBANK.NS", "TITAN.NS", "ULTRACEMCO.NS", "TRENT.NS",
    "NTPC.NS", "POWERGRID.NS", "TATAMOTORS.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "ONGC.NS", "COALINDIA.NS", "JSWSTEEL.NS", "HINDALCO.NS", "TATASTEEL.NS",
    "GRASIM.NS", "NESTLEIND.NS", "ASIANPAINT.NS", "TECHM.NS", "WIPRO.NS",
    "HCLTECH.NS", "APOLLOHOSP.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS"
]

REWARD_RATIO = 2.0  # Hardcoded mathematical 1:2 Risk-to-Reward ratio

if st.button("🚀 Run Full Quantitative Scan (Generate Top 20)"):
    with st.spinner("Analyzing liquid order blocks, volatility spreads, and volume profiles..."):
        try:
            qualified_pool = []
            
            # Download live market data for all liquid tickers at once
            tickers_string = " ".join(NIFTY_LIQUID_TICKERS)
            data = yf.download(tickers_string, period="2d", group_by="ticker", progress=False)
            
            for ticker in NIFTY_LIQUID_TICKERS:
                if ticker not in data.columns.levels[0]:
                    continue
                    
                df_ticker = data[ticker].dropna()
                if len(df_ticker) < 2:
                    continue
                
                # Fetch closing and structural parameters
                close = float(df_ticker['Close'].iloc[-1])
                day_high = float(df_ticker['High'].iloc[-1])
                day_low = float(df_ticker['Low'].iloc[-1])
                day_open = float(df_ticker['Open'].iloc[-1])
                volume = int(df_ticker['Volume'].iloc[-1])
                
                # Calculate basic percentage change from previous day's close
                prev_close = float(df_ticker['Close'].iloc[-2])
                pct_change = ((close - prev_close) / prev_close) * 100
                
                # LAYER 1: Exclude non-momentum or declining stocks for the long-bias list
                if pct_change <= 0:
                    continue
                
                # LAYER 2: Intraday Structural Range Analysis
                day_range = day_high - day_low
                if day_range == 0:
                    continue
                
                # LAYER 3: High-Close Proximity Fraction (HCPF Pattern Evaluation)
                hcpf = (day_high - close) / day_range
                if hcpf > 0.25:  # Rejects stocks that gave up more than 25% of their daily gains
                    continue
                
                # LAYER 4: Micro-Noise Volatility Filter
                historical_volatility = (day_range / close) * 100
                if historical_volatility > 4.5:  # Rejects high-risk, erratic movements
                    continue
                
                # LAYER 5: Entry, Target, and 1:2 Risk Framing Level Generation
                entry_trigger = round(close * 1.002, 2)
                calculated_risk = min(0.75, historical_volatility * 0.4)
                stop_loss = round(close * (1 - (calculated_risk / 100)), 2)
                
                risk_per_share = entry_trigger - stop_loss
                target = round(entry_trigger + (risk_per_share * REWARD_RATIO), 2)
                expected_yield_pct = ((target - entry_trigger) / entry_trigger) * 100
                
                # Ranking metric based on daily volume profile and close stability
                accumulation_score = (1.0 - hcpf) * (volume / 1000000)
                
                symbol_clean = ticker.replace(".NS", "")
                qualified_pool.append({
                    "RANKING SCORE": accumulation_score,
                    "STOCK TICKER": symbol_clean,
                    "VERIFIED CLOSE": close,
                    "ENTRY TRIGGER (₹)": entry_trigger,
                    "TARGET (PROFIT) (₹)": target,
                    "STOP-LOSS (RISK) (₹)": stop_loss,
                    "EXPECTED YIELD (%)": f"{expected_yield_pct:.2f}%",
                    "HCPF FILTER": round(hcpf, 3)
                })
            
            # Step 3: Sort and Render Data
            if qualified_pool:
                df = pd.DataFrame(qualified_pool).sort_values(by="RANKING SCORE", ascending=False)
                top_20_df = df.head(20).reset_index(drop=True)
                top_20_df.index = top_20_df.index + 1
                
                st.success(f"🎯 Execution Success: Top {len(top_20_df)} Low-Risk Alpha Stocks Compiled.")
                st.dataframe(
                    top_20_df.drop(columns=["RANKING SCORE"]).set_index("STOCK TICKER").style.format({
                        "VERIFIED CLOSE": "₹{:,.2f}",
                        "ENTRY TRIGGER (₹)": "₹{:,.2f}",
                        "TARGET (PROFIT) (₹)": "₹{:,.2f}",
                        "STOP-LOSS (RISK) (₹)": "₹{:,.2f}"
                    }),
                    use_container_width=True
                )
            else:
                st.error("No active equities cleared the stringent low-risk defense filters at this hour.")
                
            st.markdown("""
            ### 🛠️ Ironclad Execution Architecture (iPhone Operational Use)
            1. **The 9:30 AM Validation Anchor:** Do not look at your trading terminal before 9:30 AM IST. Let market opening volatility clear out completely.
            2. **The Gap-Up Circuit Breaker:** If any target stock gaps up past its designated **ENTRY TRIGGER** during the pre-open market session, delete the stock from your trade watchlist for that day.
            3. **Absolute Manual Liquidation:** If the trading terminal has not reached your target or stop-loss by **3:00 PM IST**, trigger a market order and clear all positions immediately.
            """)
            
        except Exception as e:
            st.error(f"Data Link Interruption: {str(e)}")
