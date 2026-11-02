---
name: indian-trading-v2
description: Enhanced deep-analysis trading agent with predictive modeling, risk optimization, and sentiment integration for NSE/BSE.
---

# Indian Stock Market Deep Analyst v2

## Core Upgrades (The "10,000x Think+" Loop)

### Pass 1-2: Technical + Volatility Regime
- **Volatility Regime Detection**: Low (ATR<0.5%) → tight stops; High (ATR>1.5%) → wide stops, smaller positions
- **Beta-adjusted Risk**: High beta (β>1.2) → reduce size 30%; Low beta (β<0.8) → increase 20%

### Pass 3: Monte Carlo Simulation (10,000 paths)
- Random walks using historical volatility + mean reversion + sector correlation
- Outputs: Win rate, max drawdown probability, Expected Value (EV)

### Pass 4: Sentiment Engine
```
Sentiment = 0.6×News + 0.3×Social + 0.1×EventTiming
Bullish: >+5 → +15% size; Bearish: <-5 → -20% size
```

### Pass 5: Confluence Scoring (Weighted)
| Factor | Weight | Min Score |
|--------|--------|-----------|
| Technical | 30% | 0-10 |
| Risk-Reward | 25% | 0-10 |
| News | 20% | 0-10 |
| Monte Carlo EV | 15% | 0-10 |
| Sentiment | 10% | 0-10 |
**Threshold: ≥7.5**

---

## Dynamic Position Sizing
```
Position = min(
  (Risk / (Entry-SL)) × (1 / (ATR / 20d_avg_ATR)),
  Capital × 5%
)
```

## Adaptive Risk-Reward Table
| Volatility | Risk % | RR Target | Stop Distance |
|------------|--------|-----------|---------------|
| Low (ATR<0.5%) | 1.5% | 1:2.5 | Entry - 1.2% |
| Normal (0.5-1%) | 1% | 1:2.0 | Entry - 1.5% |
| High (>1%) | 0.8% | 1:1.8 | Entry - 2.0% |

---

## Output Template (v2)
```
SYMBOL: RELIANCE.NS | Timeframe: Intraday
Price: ₹2,850 | Sentiment: +6.2 (Bullish)

TECHNICAL: 8.5/10 | RISK: 9.2/10 | CONFLUENCE: 8.7/10 (STRONG BUY)

ENTRY: ₹2,840–2,860 | STOP: ₹2,810 (1.8%, VolFactor: 0.85)
T1: ₹2,920 (1.5×R, 62% prob) | T2: ₹2,980 (2.2×R, 38% prob)

MONTE CARLO: Win 69% | Avg Profit ₹1,920 | Max DD 11.8% | EV +₹1,580 (15.8% ROI)

SENTIMENT: Q3 beat 14% | FII +₹650Cr (24h +18%) | Crude $83 | Social +7.8

POSITION: 31 shares (Delivery) | Max Hold: 2 days | Alloc: 4.2%
INVALID IF: <₹2,800 or NIFTY <22,100
```

---

## Quick Python (predictive)
```python
def analyze_v2(symbol, capital=100000, risk=1):
    df = yf.Ticker(f"{symbol}.NS").history(period="1y")
    # EMA20/50/200, RSI, MACD, BBands, ATR
    atr = df['ATR'].iloc[-1]
    entry = df['Close'].iloc[-1]
    vol_factor = 1 / (atr / df['ATR'].mean())
    sl = entry - 2*atr
    qty = min(capital*0.05/entry, (capital*risk/100)/(entry-sl)*vol_factor)
    
    # Monte Carlo (10k sims)
    sims = np.random.normal(entry, atr, 10000)
    win = (sims > sl).mean()
    ev = (sims - entry).mean()
    return {'entry':entry, 'sl':sl, 'qty':int(qty), 'win_rate':win, 'ev':ev}
```

---

## Usage
```
/indian-trading-v2
Analyze RELIANCE intraday ₹1L capital 1% risk Moneycontrol news
```