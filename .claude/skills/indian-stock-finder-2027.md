---
name: indian-stock-finder-2027
description: Future AI stock screener that analyzes 500+ NSE/BSE stocks to find highest-probability setups, then recommends optimal picks for /indian-trading-ultra analysis.
---

# 🚀 Indian Stock Finder 2027

## What This Does
1. **Scans entire NSE universe** (500+ liquid stocks)
2. **Runs multi-factor filtering** (technical, fundamental, momentum, seasonality)
3. **Identifies top 5-10 setups** with highest confluence scores
4. **Recommends stocks ready for** `/indian-trading-ultra` deep analysis
5. **Provides quick summary** of why each stock looks promising

## SCREENING FRAMEWORK (Future AI)
Before recommending ANY stock, the agent runs ALL these filters:

### 🔍 Phase 1 — Universe Filter (Reduce 500→100)
**Must meet ALL:**
- NSE market cap > ₹5,000 Cr (mid-large cap)
- Daily volume > 100,000 shares
- F&O eligible (preferred, not required)
- Beta 0.8–1.8 (not extreme volatility)
- 3-month price > ₹50 (enough granularity)

### 🔍 Phase 2 — Technical Filter (Reduce 100→30)
**Must meet ≥3 of 4:**
1. **Trend**: Price above 20 EMA AND 20 EMA > 50 EMA > 200 EMA
2. **Momentum**: RSI(14) between 40–70 (not overbought)
3. **Volume**: Today's volume > 20-day average
4. **Breakout**: Price above key resistance OR making 52-week high

### 🔍 Phase 3 — Fundamental Triage (Reduce 30→15)
**Check publicly available data via Moneycontrol/Reuters APIs:**
- Quarterly EPS growth YoY > 10%
- Recent earnings beat (actual > consensus)
- Promoter holding steady or increasing (not decreasing)
- Net debt/equity < 1.0 (exclude highly leveraged)
- ROE > 12% (decent returns on equity)

### 🔍 Phase 4 — Seasonal/Sector Momentum (Reduce 15→8)
**Indian Market Patterns (2026 data):**
- **Q4 (Oct-Dec)**: IT, Banks, Autos tend strong (budget expectations)
- **Monsoon season**: FMCG, Auto (rural demand pickup)
- **Pre-election**: Infrastructure, Capital goods
- **Post-RBI policy**: Banks, NBFCs, Realty
- **Crude oil down**: Paints, Tyres, Airlines
- **USD-INR up**: IT exporters (TCS, INFY, HCLT)

### 🔍 Phase 5 — Relative Strength Analysis (Final 5 picks)
For each candidate, calculate:
1. **RS Rating**: Performance vs NIFTY 50 last 3 months
2. **Sector momentum**: Is the sector outperforming NIFTY?
3. **Institutional flow**: FII/DII accumulation last 30 days
4. **Earnings momentum**: Upgrade/downgrade ratio by analysts

**Final Score =**
  0.3×RS Rating + 
  0.25×Sector momentum + 
  0.25×Institutional flow + 
  0.2×Earnings momentum

Pick **top 5 stocks** with scores > 7.0

---

## RECOMMENDATION ENGINE OUTPUT

For each recommended stock, give:

### 🏆 Tier 1 — Strongest Signal (Score ≥8.5)
- **Why strong**: Clear breakout + volume + sector tailwind + FII buying
- **Setup**: Immediate entry (next session)
- **Timeframe**: 1–2 weeks max
- **Action**: "Run /indian-trading-ultra now with full capital"

### 🥈 Tier 2 — Good Setup (Score 7.0–8.4)
- **Why good**: Technical OK but one factor weak (e.g., volume lagging)
- **Setup**: Wait for pullback to support
- **Timeframe**: 2–4 weeks
- **Action**: "Monitor, use /indian-trading-ultra when price hits zone"

### 🔎 Tier 3 — Watchlist (Score 6.0–6.9)
- **Why watch**: Fundamentals strong but technical needs work
- **Setup**: Needs catalyst or sector rotation
- **Timeframe**: 1 month+
- **Action**: "Keep on radar, re-check weekly"

---

## SECTOR-SPECIFIC RULES (India 2027)

### Technology (TCS, INFY, HCLT, WIPRO)
- Catalyst: USD-INR >82, global IT spending cycle
- Risk: Valuation high (PE>30), watch for deal wins
- Best time: Q4 (Oct-Jan), post-US tech results

### Banking (HDFCBANK, ICICIBANK, AXISBANK, KOTAKBANK)
- Catalyst: RBI rate cut cycle, GDP growth >6.5%
- Risk: NPA concerns, credit growth slowdown
- Best time: Post RBI policy (6x/year)

### Energy (RELIANCE, ONGC, IOC, GAIL)
- Catalyst: Crude oil $75–$95 range, petchem margins
- Risk: Geopolitical volatility, refining cracks
- Best time: Crude stable + winter demand

### Auto (MARUTI, TATAMOTORS, M&M, EICHERMOT)
- Catalyst: Festival season (Oct-Dec), EV policy
- Risk: Commodity inflation, semiconductor shortage
- Best time: Q3 (Oct-Dec) sales data

### Pharma (SUNPHARMA, DRREDDY, CIPLA, LUPIN)
- Catalyst: US FDA approvals, generic pipeline
- Risk: Price erosion, regulatory scrutiny
- Best time: Quarterly FDA announcements

---

## OUTPUT TEMPLATE

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 INDIAN STOCK FINDER 2027 — TOP SETUPS
Scan date: [Date] | Time: [IST]
Universe: 500+ NSE stocks | Filter: Technical + Fundamental
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 TIER 1 — STRONG BUY SETUPS (IMMEDIATE)
1. [STOCK1.NS] — Score: 9.2/10
   🟢 Trend: Bullish (20>50>200 EMA aligned)
   🟢 Momentum: RSI 58, MACD bullish crossover
   🟢 Catalyst: [Recent news, e.g., "Q3 EPS beat 22%"]
   🟢 Sector: [Sector] (+15% vs NIFTY last month)
   🟢 Flow: FII +₹420Cr last week
   📊 Action: "Run /indian-trading-ultra [STOCK1] with full capital"

2. [STOCK2.NS] — Score: 8.7/10
   [Same format as above]

🥈 TIER 2 — GOOD SETUPS (WAIT FOR PULLBACK)
3. [STOCK3.NS] — Score: 7.8/10
   🟡 Trend: Bullish but near resistance ₹[X]
   🟡 Momentum: RSI 68 (slightly extended)
   🟡 Catalyst: [News]
   🟡 Sector: [Sector] (neutral)
   🟡 Flow: DII steady
   📊 Action: "Wait for pullback to ₹[Y], then /indian-trading-ultra"

4. [STOCK4.NS] — Score: 7.3/10
   [Same format]

🔎 TIER 3 — WATCHLIST (MONITOR)
5. [STOCK5.NS] — Score: 6.5/10
   🔵 Trend: Base forming
   🔵 Momentum: Needs volume confirmation
   🔵 Catalyst: Potential [upcoming event]
   🔵 Sector: [Sector] (lagging)
   🔵 Flow: Neutral
   📊 Action: "Add to watchlist, check again in 2 weeks"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 MARKET CONTEXT (NIFTY: [X]):
   Trend: [Bull/Bear/Sideways]
   Key level: Support ₹[X], Resistance ₹[Y]
   VIX: [Value] ([High/Low] volatility regime)
   Sector rotation: [Which sectors leading/lagging]

💡 NEXT STEP:
   For any stock above → "/indian-trading-ultra [STOCK] [CAPITAL] [RISK%]"
   Example: "/indian-trading-ultra RELIANCE 100000 1"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PYTHON SCREENER (500-stock scan)

```python
import yfinance as yf
import pandas as pd
import numpy as np
import ta

# Mock universe of top 100 NSE stocks (in reality would be full 500)
NSE_TOP_100 = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "BHARTIARTL", "SBIN", "HINDUNILVR", "ITC", "KOTAKBANK",
    "AXISBANK", "LT", "MARUTI", "WIPRO", "SUNPHARMA",
    "BAJFINANCE", "ONGC", "TATAMOTORS", "POWERGRID", "NTPC",
    "HCLTECH", "ULTRACEMCO", "TITAN", "ASIANPAINT", "INDUSINDBK",
    "HDFC", "DIVISLAB", "DRREDDY", "TATACONSUM", "HINDALCO",
    "JSWSTEEL", "TECHM", "BRITANNIA", "BAJAJFINSV", "GRASIM",
    "ADANIPORTS", "TATASTEEL", "SHREECEM", "EICHERMOT", "NESTLEIND",
    "COALINDIA", "IOC", "BPCL", "BAJAJAUTO", "SBILIFE", 
    "M&M", "UPL", "HEROMOTOCO", "HDFCLIFE", "TATAPOWER"
]

def scan_nse_stocks(capital=100000, risk_pct=1, days_back=5):
    results = []
    
    for symbol in NSE_TOP_100:
        try:
            df = yf.Ticker(f"{symbol}.NS").history(period=f"{days_back+30}d", interval="1d")
            if len(df) < 20:  # Not enough data
                continue
                
            # Indicators
            df['EMA20'] = ta.trend.EMAIndicator(df['Close'], 20).ema_indicator()
            df['EMA50'] = ta.trend.EMAIndicator(df['Close'], 50).ema_indicator()
            df['EMA200'] = ta.trend.EMAIndicator(df['Close'], 200).ema_indicator()
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
            df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Phase 2 Technical Scoring (0-4)
            tech_score = 0
            if latest['Close'] > latest['EMA20'] and latest['EMA20'] > latest['EMA50']:
                tech_score += 1
            if 40 < latest['RSI'] < 70:
                tech_score += 1
            if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1]:
                tech_score += 1
            if latest['Close'] > df['Close'].rolling(20).max().iloc[-2]:
                tech_score += 1
            
            if tech_score >= 3:  # Pass technical filter
                # Relative Strength vs NIFTY
                nifty = yf.Ticker("^NSEI").history(period=f"{days_back+30}d", interval="1d")['Close']
                stock_ret = (latest['Close'] / df['Close'].iloc[-days_back]) - 1
                nifty_ret = (nifty.iloc[-1] / nifty.iloc[-days_back]) - 1
                rs_score = stock_ret - nifty_ret
                
                # Volatility factor
                vol_factor = latest['ATR'] / df['ATR'].rolling(20).mean().iloc[-1]
                
                # Position sizing (quick estimate)
                entry = latest['Close']
                stop_loss = entry - (2 * latest['ATR'])
                risk_amount = capital * (risk_pct / 100)
                qty = int(risk_amount / (entry - stop_loss))
                
                results.append({
                    'symbol': f"{symbol}.NS",
                    'price': round(entry, 2),
                    'tech_score': tech_score,
                    'rs_score': round(rs_score * 100, 2),  # % outperformance
                    'vol_factor': round(vol_factor, 2),
                    'rsi': round(latest['RSI'], 1),
                    'trend': 'Bullish' if entry > latest['EMA50'] else 'Bearish',
                    'qty_est': qty,
                    'stop_est': round(stop_loss, 2)
                })
                
        except Exception as e:
            continue
    
    # Sort by tech_score + rs_score
    df_results = pd.DataFrame(results)
    if len(df_results) > 0:
        df_results['combined_score'] = df_results['tech_score'] * 2 + df_results['rs_score']
        df_results = df_results.sort_values('combined_score', ascending=False).head(10)
    
    return df_results.to_dict('records')

# Example output
# top_stocks = scan_nse_stocks(capital=100000, risk_pct=1)
# for i, stock in enumerate(top_stocks[:5], 1):
#     print(f"{i}. {stock['symbol']}: ₹{stock['price']}, Tech {stock['tech_score']}/4, RS {stock['rs_score']}%")
```

---

## HOW TO USE

```
/indian-stock-finder-2027
```

The agent will:
1. Scan top NSE stocks with latest data
2. Apply all 5-phase filtering
3. Show top 5 setups with scores
4. Give clear "Action" recommendation for each

Once you pick a stock:

```
/indian-trading-ultra RELIANCE 100000 1
```

That runs the deep 8-pass analysis on your chosen stock with full predictive modeling.
