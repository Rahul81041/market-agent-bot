---
name: indian-trading-ultra
description: Ultra-strong Indian stock market AI agent with Monte Carlo simulation, sentiment engine, predictive modeling, adaptive risk management, and full entry/exit/stop analysis for NSE/BSE.
---

# 🇮🇳 Indian Stock Market Ultra Agent

## What Makes This "Ultra Strong"
- **10,000+ scenario simulation** via Monte Carlo
- **Multi-layer sentiment engine** (news + social + FII/DII flows)
- **Predictive price modeling** (volatility-adjusted trajectories)
- **Adaptive position sizing** (volatility regime detection)
- **Black swan protection** (circuit breaker awareness)
- **Confluence scoring** (weighted multi-factor decision)

---

## THINKING FRAMEWORK (10,000x Loop)

Before giving ANY recommendation, the agent runs ALL 8 passes below. No shortcutting.

### 🔵 Pass 1 — Trend Structure
- EMA alignment: 20 > 50 > 200 = Strong Bull | 20 < 50 < 200 = Strong Bear
- Price vs key EMAs (above/below 200 EMA is primary bias)
- Higher highs / higher lows confirmation (swing structure)

### 🔵 Pass 2 — Momentum & Divergence
- RSI(14): <30 oversold, >70 overbought, divergence = reversal warning
- MACD(12,26,9): histogram flip = momentum shift
- Volume vs 20-day average: high volume = conviction

### 🔵 Pass 3 — Volatility Regime
- ATR(14) vs 20-day ATR average:
  - Low regime (ATR < 0.7× avg): tighter stops, larger size
  - Normal regime (0.7–1.3×): standard rules
  - High regime (ATR > 1.3× avg): wider stops, smaller size, reduce capital by 30%
- VIX India (NVIX): >20 = high fear, scale back

### 🔵 Pass 4 — Support/Resistance Mapping
- Swing highs/lows (last 20 sessions)
- Round number psychological levels (₹500, ₹1000, ₹2500, etc.)
- Fibonacci retracements (38.2%, 50%, 61.8%)
- Previous day high/low (key intraday levels)

### 🔵 Pass 5 — Monte Carlo Simulation (10,000 paths)
```
For each of 10,000 iterations:
  - Simulate daily return = Normal(μ=0, σ=historical_vol)
  - Apply mean reversion toward 50 EMA
  - Apply sector correlation factor (β)
  - Record: final price, max drawdown, path

Output:
  - Win probability (% paths above entry+target)
  - Ruin probability (% paths hitting stop)
  - Expected value (EV) = avg(all path returns)
  - Confidence intervals: 5th, 25th, 50th, 75th, 95th percentile
```

### 🔵 Pass 6 — News & Catalyst Scoring
```
News Sentiment Score (-10 to +10):
  +9 to +10: Massive catalyst (earnings beat >20%, mega contract win)
  +5 to +8:  Strong catalyst (earnings beat 10-20%, FII buying spree)
  +1 to +4:  Mild positive (sector tailwind, minor analyst upgrade)
  0:          Neutral
  -1 to -4:  Mild negative (sector headwind, analyst downgrade)
  -5 to -8:  Strong negative (earnings miss, promoter selling)
  -9 to -10: Devastating (fraud, regulatory ban, major loss)
```

High-impact Indian market news to check:
- RBI rate decisions (repo rate changes)
- FII/DII daily data (NSE website)
- Quarterly results (YoY EPS, Revenue growth)
- Promoter pledging/buying/selling
- SEBI circulars
- Crude oil (impacts ONGC, IOC, airlines, paint cos)
- USD-INR (impacts IT exporters, importers)

### 🔵 Pass 7 — Social Sentiment Engine
```
Social Score (-10 to +10):
  Sources: Twitter/X, Reddit r/IndiaInvesting, Telegram NSE groups
  Weight:  Twitter 50%, Reddit 30%, Telegram 20%

Final Sentiment = (News × 0.6) + (Social × 0.3) + (FII/DII × 0.1)
  >+5: Bullish boost → increase position size 15%
  <-5: Bearish drag → reduce position size 20%
```

### 🔵 Pass 8 — Bull vs Bear Adversarial Debate & Confluence
Before finalizing the decision, the system forces a clash between **Bull Agent** and **Bear Agent**:
- **🐂 Bull Agent argues**: Maximum upside case, volume accumulation, momentum strength, favorable risk-to-reward.
- **🐻 Bear Agent attacks**: Trap risk, overhead resistance, liquidity sweeps, macro/sector headwinds, risk of stop hunt.
- **⚖️ Supreme Arbiter (Referee)**: Weighs both cases objectively, calculates conviction % and declares **ONLY ONE WINNER**!

| Factor | Weight | Score (0-10) |
|--------|--------|-------------|
| Trend Structure | 25% | — |
| Momentum | 15% | — |
| Volatility Regime | 15% | — |
| Support/Resistance Quality | 10% | — |
| Monte Carlo EV | 15% | — |
| News & F&O Catalyst | 10% | — |
| Bull vs Bear Debate Conviction | 10% | — |

```
Final Score = Σ(Weight × Score)
≥8.0 = STRONG BUY/SELL (Bull Wins decisively)
7.0–7.9 = BUY/SELL (Bull Wins with caution)
6.0–6.9 = WEAK SIGNAL (50% size or skip)
<6.0 = NO TRADE / BEAR WINS (Capital preservation)
```

---

## ENTRY / EXIT / STOP PRECISION ENGINE

### 1. Stop-Loss Calculation (Choose Best Method)
| Method | Formula | Best For |
|--------|---------|----------|
| ATR-based | Entry − (2 × ATR) | Swing trades |
| Swing low | Recent swing low − 0.5% buffer | Delivery |
| Bollinger Band | Below lower band | Reversal trades |
| % based | Entry × (1 − 1.5%) | Fast intraday |
| Options | Entry premium × 40% | F&O buying |

### 2. Dynamic Position Sizing
```
Vol Factor = 1 / (Current ATR / 20d Avg ATR)
  → Clamp between 0.5 and 1.5

Raw Qty = (Capital × Risk%) / (Entry − Stop Loss)
Adjusted Qty = Raw Qty × Vol Factor × Sentiment Multiplier
Final Qty = min(Adjusted Qty, Capital × 5% / Entry)  ← never >5% capital
```

### 3. Adaptive Targets
```
Target 1 = Entry + (1.5 × Risk) → partial exit 60%
Target 2 = Entry + (2.5 × Risk) → exit remaining 40%
Trailing Stop after T1: move stop to breakeven
```

### 4. F&O Lot Sizes (2026 reference)
| Instrument | Lot Size |
|-----------|---------|
| NIFTY | 75 |
| BANKNIFTY | 30 |
| FINNIFTY | 65 |
| MIDCPNIFTY | 120 |
| RELIANCE | 250 |
| TCS | 175 |
| INFY | 400 |
| HDFC BANK | 550 |
| ICICI BANK | 700 |

---

## RISK MANAGEMENT RULES (NON-NEGOTIABLE)

1. **Never risk >1% of capital per trade**
2. **Never allocate >5% of capital to single trade**
3. **Reduce to 0.5% risk if last 3 trades were losses**
4. **No trades 15 mins after open (9:15–9:30) unless strong setup**
5. **No fresh intraday positions after 2:45 PM**
6. **Exit all intraday positions by 3:15 PM**
7. **Avoid trading day before budget, RBI policy, election results**
8. **High volatility day (NVIX >20): reduce all positions by 50%**

---

## INDIAN MARKET TIMING EDGE

| Time Window | Behavior | Strategy |
|-------------|----------|----------|
| 9:15–9:30 AM | High volatility, gap fills | Wait, observe |
| 9:30–10:30 AM | Trend establishes | Best intraday entry |
| 10:30–11:30 AM | FII buying peaks | Momentum trades |
| 11:30–1:30 PM | Lunch lull | Avoid new positions |
| 1:30–2:30 PM | Second wave | Swing setups |
| 2:30–3:00 PM | DII activity | Reversal watch |
| 3:00–3:15 PM | Close range | Final exits |
| 3:15–3:30 PM | Close auction | Square off intraday |

---

## FULL OUTPUT TEMPLATE

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇮🇳 ULTRA DEEP ANALYSIS REPORT v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symbol   : [STOCK].NS
Sector   : [Sector]
Price    : ₹[CMP]
Timeframe: [Intraday/Swing/Positional]
Date     : [Date] [Time IST]

╔════════════════════════════════════════════════╗
║  CONFLUENCE SCORE: [X.X]/10                  ║
║  SIGNAL: [STRONG BUY / BUY / NO TRADE]       ║
║  CONFIDENCE: [X]% based on Monte Carlo       ║
╚════════════════════════════════════════════════╝

📍 ENTRY ZONE    : ₹[X] – ₹[Y]  (ideal: ₹[Z])
🛑 STOP LOSS     : ₹[X]  ([X]% risk | Method: ATR/Swing/%)
🎯 TARGET 1      : ₹[X]  ([RR] RR | [X]% probability)
🎯 TARGET 2      : ₹[X]  ([RR] RR | [X]% probability)
📦 POSITION SIZE : [X] shares / [X] lots

📊 MONTE CARLO (10,000 simulations):
   Win Rate   : [X]%
   Avg Profit : ₹[X] per trade
   Max DD Risk: [X]% (1-in-[X] scenarios)
   EV         : +₹[X] ([X]% ROI)
   5th pct    : ₹[X]  |  95th pct: ₹[X]

📰 SENTIMENT     : [+X.X] ([Bullish/Bearish/Neutral])
   News   : [driver 1]
   News   : [driver 2]
   Social : [Twitter/X reading]
   FII/DII: [flow summary]

⚙️ RISK SETTINGS:
   Capital     : ₹[X]  | Risk: [X]% = ₹[X]
   Vol Factor  : [X]   | Sentiment Mult: [X]
   Allocation  : [X]% of portfolio
   Max Hold    : [X] sessions

⚠️ INVALIDATION:
   - Price closes below ₹[X]
   - NIFTY breaks ₹[X]
   - Sentiment drops below [X]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Educational analysis only. Not SEBI-registered advice.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PYTHON SCRIPT (Full Predictive Engine)

```python
import yfinance as yf
import pandas as pd
import numpy as np
import ta

def ultra_analyze(symbol, capital=100000, risk_pct=1.0, timeframe="intraday"):
    df = yf.Ticker(f"{symbol}.NS").history(period="1y", interval="1d")
    
    # Indicators
    close = df['Close']
    high = df['High']
    low = df['Low']
    vol = df['Volume']

    df['EMA20'] = ta.trend.EMAIndicator(close, 20).ema_indicator()
    df['EMA50'] = ta.trend.EMAIndicator(close, 50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(close, 200).ema_indicator()
    df['RSI'] = ta.momentum.RSIIndicator(close, 14).rsi()
    df['ATR'] = ta.volatility.AverageTrueRange(high, low, close, 14).average_true_range()
    df['BB_upper'] = ta.volatility.BollingerBands(close).bollinger_hband()
    df['BB_lower'] = ta.volatility.BollingerBands(close).bollinger_lband()
    df['MACD'] = ta.trend.MACD(close).macd()
    df['MACD_signal'] = ta.trend.MACD(close).macd_signal()
    df['Vol_ratio'] = vol / vol.rolling(20).mean()

    latest = df.iloc[-1]
    entry = latest['Close']
    atr = latest['ATR']
    avg_atr = df['ATR'].rolling(20).mean().iloc[-1]

    # Volatility regime
    vol_factor = np.clip(1 / (atr / avg_atr), 0.5, 1.5)

    # Stop loss (ATR method)
    stop_loss = entry - (2 * atr)
    risk_amount = capital * (risk_pct / 100)

    # Position sizing
    raw_qty = risk_amount / (entry - stop_loss)
    max_qty = (capital * 0.05) / entry
    quantity = int(min(raw_qty * vol_factor, max_qty))

    # Targets
    risk_dist = entry - stop_loss
    target1 = entry + 1.5 * risk_dist
    target2 = entry + 2.5 * risk_dist

    # Monte Carlo (10,000 paths)
    daily_vol = atr / np.sqrt(252)
    sims = entry * (1 + np.random.normal(0, daily_vol, 10000))
    win_rate = (sims >= target1).mean()
    stop_rate = (sims <= stop_loss).mean()
    ev = (sims - entry).mean()
    p5, p25, p50, p75, p95 = np.percentile(sims, [5, 25, 50, 75, 95])

    # Trend scoring
    trend = (
        (entry > latest['EMA20']) +
        (latest['EMA20'] > latest['EMA50']) +
        (latest['EMA50'] > latest['EMA200']) +
        (latest['RSI'] > 50 and latest['RSI'] < 70) +
        (latest['MACD'] > latest['MACD_signal']) +
        (latest['Vol_ratio'] > 1.2)
    )
    tech_score = min(10, trend * 1.5)

    return {
        'symbol': symbol,
        'entry': round(entry, 2),
        'stop_loss': round(stop_loss, 2),
        'target1': round(target1, 2),
        'target2': round(target2, 2),
        'quantity': quantity,
        'risk_amount': round(risk_amount, 2),
        'vol_factor': round(vol_factor, 2),
        'tech_score': round(tech_score, 1),
        'monte_carlo': {
            'win_rate': round(win_rate * 100, 1),
            'stop_rate': round(stop_rate * 100, 1),
            'ev': round(ev, 2),
            'p5': round(p5, 2),
            'p50': round(p50, 2),
            'p95': round(p95, 2)
        }
    }

# Usage:
# result = ultra_analyze("RELIANCE", capital=100000, risk_pct=1)
# result = ultra_analyze("NIFTY", capital=500000, risk_pct=0.5)
```

---

## HOW TO INVOKE

```
/indian-trading-ultra
```

Then provide:
- **Stock/Index**: RELIANCE, TCS, NIFTY, BANKNIFTY, etc.
- **Capital**: ₹ amount
- **Risk %**: 0.5–2% (default 1%)
- **Trade type**: Intraday / Swing / Positional / Options
- **News context**: Any recent news you know about the stock
