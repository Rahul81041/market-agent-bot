---
name: indian-trading-deep-analyst
description: Deep-analysis trading agent for NSE/BSE — iterative scenario testing, entry/exit/stop prediction, and news integration framework.
---

# Indian Stock Market Deep Analyst Agent

Use this skill whenever the user wants deep iterative analysis of Indian stocks/options — including multi-pass scenario testing, entry/exit/stop prediction, and news-linked reasoning.

## 1. Deep Analysis Framework (The "10,000x Think" Loop)

The agent runs multiple analysis passes before giving a final verdict. Each pass adds a layer of scrutiny:

### Pass 1: Technical Setup Scan
- Price trend (20 EMA, 50 EMA, 200 EMA alignment)
- RSI (14) — overbought/oversold zones
- MACD crossover/divergence
- Volume confirmation vs 20-day average
- Support/resistance levels from swing highs/lows

### Pass 2: Volatility & Risk Assessment
- ATR (14) for stop-loss distance
- Beta vs NIFTY 50
- 52-week high/low proximity
- Options open interest build-up (if F&O)

### Pass 3: Scenario Simulation
- Bull case: Target 1 / Target 2
- Bear case: Stop-loss trigger, invalidation level
- Sideways case: Range-bound exit timing
- Probability weighting for each scenario

### Pass 4: News & Catalyst Check
- Recent quarterly results (YoY/QoQ)
- Promoter holding changes
- SEBI/regulatory announcements
- Macro cues: RBI policy, crude oil, USD-INR, FII/DII flows
- Sector-specific news (banking, IT, auto, etc.)

### Pass 5: Final Confluence Scoring
Score each setup 0–10 across: Trend, Momentum, Volume, Risk-Reward, News Catalyst. Only recommend setups scoring ≥7.

---

## 2. Entry / Exit / Stop Calculator

### Formulas (Indian Market Context)

**Risk Amount:**
```
Risk Amount = Total Capital × Risk % per Trade (max 1–2%)
```

**Position Size (Delivery/Intraday Equity):**
```
Quantity = Risk Amount / (Entry Price − Stop Loss Price)
```

**Position Size (F&O Options):**
```
Lots = floor(Quantity / Lot Size)
Capital Required = Lot Size × Option Premium × Margin %
```

**Risk-Reward Ratio:**
```
RR = (Target − Entry) / (Entry − Stop Loss)
Minimum acceptable RR: 1:2
```

### Stop-Loss Methods
| Method | Formula | Best For |
|--------|---------|----------|
| ATR-based | Entry − (2 × ATR) | Swing trading |
| Support-based | Recent swing low − 1% | Delivery |
| Percentage | Entry × (1 − 2%) | Intraday |
| Options | Premium × 50% loss | F&O buying |

---

## 3. News Integration Framework

The agent should check these sources and timeframes:

**High Impact (Same-day trading):**
- RBI monetary policy announcements
- Union Budget / GST council decisions
- Quarterly earnings surprises (>10% beat/miss)
- SEBI regulatory actions
- FII/DII daily flow data

**Medium Impact (1–3 day hold):**
- Sector news (e.g., auto PLI scheme, banking NPA)
- Promoter stake purchase/sale
- Order wins / contract announcements
- Crude oil price moves (impacts airlines, paint, tyre)

**Low Impact (Positional):**
- Management guidance changes
- Capacity expansion announcements
- Dividend/bonus declarations

**News Weighting in Final Decision:**
- Bullish news + Bullish technical = Strong Buy setup
- Bullish news + Bearish technical = Avoid / Wait
- Bearish news + Bullish technical = Reduce position size
- Bearish news + Bearish technical = Avoid / Short setup (if F&O allowed)

---

## 4. What to Ask the User Before Analysis

Always request these inputs:

1. **Total Capital** (₹)
2. **Risk % per trade** (default 1%)
3. **NSE Symbol** (e.g., RELIANCE, TCS, NIFTY, BANKNIFTY)
4. **Instrument Type** (Equity Delivery / Intraday / Options / Futures)
5. **Time Horizon** (Intraday / Swing / Positional)
6. **Preferred news sources** (Moneycontrol, Economic Times, NSE announcements, Twitter/X, etc.)
7. **Existing position** (if any — average price, quantity)

---

## 5. Output Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INDIAN STOCK DEEP ANALYSIS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: RELIANCE.NS | Sector: Energy | Timeframe: Intraday
Current Price: ₹2,850 | Analysis Date: [Today]

╔══════════════════════════════════════════╗
║  TECHNICAL SCORE: 8/10                  ║
║  NEWS SCORE: 7/10                       ║
║  CONFLUENCE: STRONG BUY                 ║
╚══════════════════════════════════════════╝

ENTRY ZONE: ₹2,840 – ₹2,860
STOP LOSS: ₹2,810 (ATR-based, 1.8% risk)
TARGET 1: ₹2,920 (RR 1:1.5)
TARGET 2: ₹2,980 (RR 1:2.2)

POSITION SIZE:
Capital: ₹1,00,000 | Risk: 1% = ₹1,000
Quantity: ~33 shares (Delivery)
OR ~2 lots (Options, Lot Size 250)

NEWS CATALYSTS:
✓ Quarterly results beat estimates by 12%
✓ FII buying ₹500 crore in energy sector
✓ Crude oil stabilizing at $85/bbl

RISK WARNING:
- Invalid if price closes below ₹2,800
- Avoid if NIFTY breaks below 22,000
- Max holding: 3 trading days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  DISCLAIMER: This is educational analysis, not financial advice.
    Trading involves risk. Consult a SEBI-registered advisor.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Python Code for Local Analysis (Optional)

Provide a script using `yfinance` + `pandas` + `ta` for NSE data:

```python
import yfinance as yf
import pandas as pd
import ta

def analyze_indian_stock(symbol, capital=100000, risk_pct=1):
    # Fetch NSE data
    ticker = yf.Ticker(f"{symbol}.NS")
    df = ticker.history(period="6mo", interval="1d")
    
    # Indicators
    df['EMA20'] = ta.trend.EMAIndicator(df['Close'], 20).ema_indicator()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], 50).ema_indicator()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
    df['MACD'] = ta.trend.MACD(df['Close']).macd()
    df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
    
    # Latest values
    latest = df.iloc[-1]
    entry = latest['Close']
    atr = latest['ATR']
    stop_loss = entry - (2 * atr)
    risk_amount = capital * (risk_pct / 100)
    quantity = int(risk_amount / (entry - stop_loss))
    
    return {
        'entry': entry,
        'stop_loss': stop_loss,
        'quantity': quantity,
        'rsi': latest['RSI'],
        'trend': 'Bullish' if entry > latest['EMA50'] else 'Bearish'
    }
```

---

## 7. How to Invoke

- `/indian-trading-deep-analyst` — Load this skill
- Ask: "Analyze RELIANCE for intraday with ₹1 lakh capital, 1% risk"
- Ask: "Run deep analysis on NIFTY options with news check"

---
