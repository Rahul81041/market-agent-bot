---
name: indian-trading
description: Indian stock market (NSE/BSE) trading tools, technical analysis, F&O lot sizes, brokerage & tax calculator, and risk management.
---

# Indian Stock Market Trading Skill

Use this skill whenever the user discusses trading, investing, technical analysis, options, futures, or risk management on the Indian Stock Market (NSE/BSE).

## 1. Market Overview & Timings (IST)
- **Normal Trading Session**: 09:15 AM to 03:30 PM (Monday to Friday)
- **Pre-open Session**: 09:00 AM to 09:08 AM (Order entry/modification)
- **Equilibrium Price Discovery**: 09:08 AM to 09:15 AM
- **Post-close Session**: 03:40 PM to 04:00 PM

## 2. Indices & Options Expiry (As of 2026)
- **NIFTY 50**: Thursday expiry
- **BANKNIFTY**: Wednesday expiry
- **FINNIFTY**: Tuesday expiry
- **MIDCPNIFTY**: Monday expiry
- **SENSEX (BSE)**: Friday expiry

## 3. Position Sizing & Risk Management Formula
$$\text{Risk Amount} = \text{Total Capital} \times \text{Risk % per Trade (e.g., 1%)}$$
$$\text{Quantity} = \frac{\text{Risk Amount}}{\text{Entry Price} - \text{Stop Loss Price}}$$

For Futures & Options (F&O):
$$\text{Total Lots} = \left\lfloor \frac{\text{Quantity}}{\text{Lot Size}} \right\rfloor$$

## 4. Indian Taxation & Transaction Charges (Reference)
- **STT (Securities Transaction Tax)**: Higher on F&O sell side and intraday sell side.
- **GST**: 18% on brokerage + exchange transaction charges.
- **SEBI Turnover Charges**: Applicable per crore.
- **Stamp Duty**: Varies by state on buy side.
- **Capital Gains**: 
  - STCG (Short Term Capital Gains - holding < 1 year for equity): taxed at higher rate.
  - LTCG (Long Term Capital Gains - holding > 1 year for equity): taxed above threshold.

## 5. Technical Indicators Popular in NSE
- **Moving Averages**: 20 EMA (short-term trend), 50 EMA (medium-term), 200 EMA (long-term structural trend).
- **Momentum**: RSI (14), MACD (12, 26, 9).
- **Trend/Volatility**: Supertrend (7, 3), Bollinger Bands (20, 2).

## 6. Actionable Prompts & Calculators You Can Ask Claude For:
- Calculate exact stop-loss and position size for any stock or Nifty/BankNifty option.
- Review a trading setup (Risk-Reward ratio).
- Generate a Python script using `yfinance` to pull historical NSE stock data (e.g., `RELIANCE.NS`, `TCS.NS`, `NIFTY`).
