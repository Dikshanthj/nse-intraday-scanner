import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(page_title="NSE Broad Market Alpha Engine", page_icon="🦅", layout="wide")

st.title("🦅 NSE Broad Market Top 10 Intraday Engine")
st.write("Scans an expanded database of Nifty 100, Midcap momentum leaders, and highly liquid F&O counters.")

# FIXED DATASET: Cleaned tickers to ensure smooth Yahoo Finance parsing
BROAD_NSE_DATABASE = [
    # --- Mega Cap Pillars ---
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", 
    "INFY.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
    # --- Banking & Financial Services Leaders ---
    "AXISBANK.NS", "KOTAKBANK.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "SHRIRAMFIN.NS",
    "CHOLAFIN.NS", "MUTHOOTFIN.NS", "RECLTD.NS", "PFC.NS", "INDUSINDBK.NS", "PNB.NS",
    "CANBK.NS", "BANKBARODA.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",
    # --- High-Momentum Conglomerates & Retail ---
    "TRENT.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", 
    "DMART.NS", "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "TIINDIA.NS", "EICHERMOT.NS",
    # --- Energy, Utilities & Commodities ---
    "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "COALINDIA.NS", "BPCL.NS", "IOC.NS", 
    "GAIL.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JINDALSTEL.NS",
    # --- Tech, Telecom, Infrastructure & Industrials ---
    "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "BEL.NS", "HAL.NS", "BHEL.NS",
    "DIXON.NS", "IRFC.NS", "RVNL.NS", "CONCOR.NS", "GMRINFRA.NS", "DLF.NS",
    # --- Healthcare, Pharma & Consumables ---
    "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS",
    "MAXHEALTH.NS", "LUPIN.NS", "AUROPHARMA.NS", "BIOCON.NS", "NESTLEIND.NS", 
    "BRITANNIA.NS", "TATACONSUM.NS", "VBL.NS", "GODREJPROP.NS", "COLPAL.NS"
]

REWARD_RATIO = 2.0  # Rigid mathematical 1:2 Risk-to-Reward ratio

if st.button("🦅 Run Broad Market Quantitative Scan"):
    with st.spinner("Analyzing broad-market data blocks, volume anomalies, and pattern setups..."):
        try:
            qualified_pool = []
            
            # Batch request market frames for our entire expanded universe
            tickers_string = " ".join(BROAD_NSE_DATABASE)
            data = yf.download(tickers_string, period="2d", group_by="ticker", progress=False)
            
            for ticker in BROAD_NSE_DATABASE:
                try:
                    # FIXED: Bulletproof column checks to bypass ambiguous truth arrays
                    if ticker not in data.columns.get_level_values(0):
                        continue
                        
                    df_ticker = data[ticker].dropna()
                    if df_ticker.empty or len(df_ticker) < 2:
                        continue
                    
                    # Extract clean closing OHLC details
                    close = float(df_ticker['Close'].iloc[-1])
                    day_high = float(df_ticker['High'].iloc[-1])
                    day_low = float(df_ticker['Low'].iloc[-1])
                    day_open = float(df_ticker['Open'].iloc[-1])
                    volume = int(df_ticker['Volume'].iloc[-1])
                    
                    # Rate of Change calculation
                    prev_close = float(df_ticker['Close'].iloc[-2])
                    pct_change = ((close - prev_close) / prev_close) * 100
                    
                    # INTRADAY DEFENSE GRID 
                    # Rejects crashing counters from our high-yield long-momentum matrix
                    if pct_change <= 0:
                        continue
                    
                    day_range = day_high - day_low
                    if day_range == 0:
                        continue
                    
                    # High-Close Proximity Fraction (HCPF) Pattern Verification
                    hcpf = (day_high - close) / day_range
                    
                    # Filter out hyper-volatile or low-volume data gaps
                    historical_volatility = (day_range / close) * 100
                    if historical_volatility > 5.0 or volume < 500000:
                        continue
                    
                    # Level Generation Math
                    entry_trigger = round(close * 1.002, 2)
                    calculated_risk = min(0.80, historical_volatility * 0.4)
                    stop_loss = round(close * (1 - (calculated_risk / 100)), 2)
                    
                    risk_per_share = entry_trigger - stop_loss
                    target = round(entry_trigger + (risk_per_share * REWARD_RATIO), 2)
                    expected_yield_pct = ((target - entry_trigger) / entry_trigger) * 100
                    
                    # Compounded ranking algorithm balancing price-action velocity and institutional accumulation
                    accumulation_score = (pct_change * 2.5) + (1.0 - hcpf)
                    
                    symbol_clean = ticker.replace(".NS", "")
                    qualified_pool.append({
                        "RANKING SCORE": accumulation_score,
                        "STOCK TICKER": symbol_clean,
                        "VERIFIED CLOSE (₹)": close,
                        "ENTRY TRIGGER (₹)": entry_trigger,
                        "TARGET (PROFIT) (₹)": target,
                        "STOP-LOSS (RISK) (₹)": stop_loss,
                        "EXPECTED YIELD (%)": f"{expected_yield_pct:.2f}%"
                    })
                except Exception:
                    # Skip problematic individual stocks silently instead of crashing the app
                    continue
            
            # Step 2: Filter and Render the Final Top 10 Slice
            if qualified_pool:
                df = pd.DataFrame(qualified_pool).sort_values(by="RANKING SCORE", ascending=False)
                
                # Constrain the data stream to output exactly the Top 10
                top_10_df = df.head(10).reset_index(drop=True)
                top_10_df.index = top_10_df.index + 1
                
                st.success("🎯 Execution Success: Expanded Top 10 Safe Intraday Alpha Stocks Compiled.")
                st.dataframe(
                    top_10_df.drop(columns=["RANKING SCORE"]).set_index("STOCK TICKER").style.format({
                        "VERIFIED CLOSE (₹)": "₹{:,.2f}",
                        "ENTRY TRIGGER (₹)": "₹{:,.2f}",
                        "TARGET (PROFIT) (₹)": "₹{:,.2f}",
                        "STOP-LOSS (RISK) (₹)": "₹{:,.2f}"
                    }),
                    use_container_width=True
                )
            else:
                st.error("No active equities cleared the expanded filtering parameters.")
                
            st.markdown("""
            ### 🛠️ Ironclad Execution Architecture (iPhone Operational Use)
            1. **The 9:30 AM Validation Anchor:** Do not look at your trading terminal before 9:30 AM IST. Let market opening volatility clear out completely.
            2. **The Gap-Up Circuit Breaker:** If any target stock gaps up past its designated **ENTRY TRIGGER** during the pre-open market session, delete the stock from your trade watchlist for that day.
            3. **Absolute Manual Liquidation:** If the trading terminal has not reached your target or stop-loss by **3:00 PM IST**, trigger a market order and clear all positions immediately.
            """)
            
        except Exception as e:
            st.error(f"System Error: {str(e)}")
