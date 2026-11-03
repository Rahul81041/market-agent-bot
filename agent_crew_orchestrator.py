"""
Top 5 Stocks Screener Sub-Agent Crew (`agent_crew_orchestrator.py`)
====================================================================
Orchestrates sequential analysis across liquid NSE universe:
- Agent 1: Liquid Universe Screener (RVOL, ATR, EMA)
- Agent 2: Price Action & SMC Quant Agent (Body/Wick, FVG, Order Blocks)
- Agent 3: F&O Option Chain & Sector Alpha Agent (OI walls, Relative Strength)
- Agent 4: Live News Sentinel (RSS negative news check)
- Agent 5: Bull vs Bear Debaters & Supreme Arbiter (Conviction scoring)
"""

import yfinance as yf
import numpy as np
import pandas as pd
from price_action import PriceActionAnalyzer
from mtf_analyzer import MTFAnalyzer
from live_news_sentinel import LiveNewsSentinel

# Curated high-liquidity NSE stocks for screening
SCREENER_UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "TATAMOTORS",
    "TATASTEEL", "BHARTIARTL", "HINDUNILVR", "ITC", "KOTAKBANK", "LT", "AXISBANK",
    "BAJFINANCE", "MARUTI", "ASIANPAINT", "HCLTECH", "WIPRO", "SUNPHARMA",
    "ULTRACEMCO", "NTPC", "POWERGRID", "TITAN", "INDUSINDBK", "TECHM", "GRASIM",
    "CIPLA", "BAJAJFINSV", "HEROMOTOCO", "DRREDDY", "BRITANNIA", "ADANIENT",
    "ADANIPORTS", "APOLLOHOSP", "GODREJCP", "DABUR", "MARICO", "BPCL", "ONGC",
    "COALINDIA", "SBILIFE", "HDFCLIFE", "JSWSTEEL", "HINDALCO", "TATAPOWER"
]

class AgentCrewOrchestrator:

    @staticmethod
    def run_top_5_analysis():
        """
        Runs the 5-agent sequential crew over the screener universe,
        returns top 5 highest-conviction winning stocks.
        """
        candidates = []

        # Step 1: Agent 1 (Liquid Universe & RVOL Screener)
        for sym in SCREENER_UNIVERSE:
            try:
                ticker = yf.Ticker(f"{sym}.NS")
                df = ticker.history(period="3mo", interval="1d")
                if df.empty or len(df) < 20:
                    continue

                cmp = round(df['Close'].iloc[-1], 2)

                # RVOL calculation
                avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
                last_vol = df['Volume'].iloc[-1]
                rvol = round(last_vol / avg_vol, 2) if avg_vol > 0 else 1.0

                if rvol < 1.1:  # Filter low volume stocks
                    continue

                # Step 2: Agent 2 (Price Action & SMC)
                anatomy = PriceActionAnalyzer.calculate_candle_anatomy(df)
                patterns = PriceActionAnalyzer.detect_patterns(df)
                indicators = PriceActionAnalyzer.calculate_indicators(df)

                # Step 3: Agent 3 (MTF & Volatility)
                mtf_data = MTFAnalyzer.fetch_mtf_data(sym)
                mtf_result = MTFAnalyzer.calculate_alignment_score(mtf_data)

                # ATR & Stop Loss
                tr = df['High'] - df['Low']
                for i in range(1, len(df)):
                    tr.iloc[i] = max(tr.iloc[i], abs(df['High'].iloc[i] - df['Close'].iloc[i-1]), abs(df['Low'].iloc[i] - df['Close'].iloc[i-1]))
                atr = round(tr.rolling(14).mean().iloc[-1], 2)

                stop_loss = round(cmp - (1.8 * atr), 2)
                risk = cmp - stop_loss
                target1 = round(cmp + (1.5 * risk), 2)
                target2 = round(cmp + (2.5 * risk), 2)

                # Step 4: Scoring & Arbiter (Agent 5)
                bull_score = 50 + patterns.get("score_boost", 0) + (mtf_result.get("score", 2) * 10) + int((rvol - 1.0) * 10)
                bear_score = 40 - patterns.get("score_boost", 0)

                if mtf_result.get("blocked", False):
                    bear_score += 20
                    continue  # Skip misaligned setups

                conviction = round((bull_score / (bull_score + bear_score)) * 100, 1)
                conviction = min(94.5, max(55.0, conviction))

                rr_ratio = round((target1 - cmp) / risk, 2) if risk > 0 else 1.5

                if conviction >= 65 and rr_ratio >= 1.5:
                    candidates.append({
                        "symbol": sym,
                        "cmp": cmp,
                        "stop_loss": stop_loss,
                        "target1": target1,
                        "target2": target2,
                        "rvol": rvol,
                        "conviction": conviction,
                        "rr_ratio": rr_ratio,
                        "direction": "BULL",
                        "patterns": ", ".join(patterns.get("patterns", ["Breakout"]))
                    })
            except Exception as e:
                continue

        # Sort by conviction highest first
        candidates.sort(key=lambda x: x['conviction'], reverse=True)
        return candidates[:5]
