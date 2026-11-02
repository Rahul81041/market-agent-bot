"""
Mathematical Price Action and Candlestick Anatomy Module
Calculates candle anatomy, institutional patterns (Pin Bar, Engulfing, Inside Bar),
VWAP, PDH/PDL, and EMA distances.
"""

import numpy as np
import pandas as pd

class PriceActionAnalyzer:
    @staticmethod
    def calculate_candle_anatomy(df):
        """
        Calculates body ratio and wick ratios for the latest candle.
        bodyRatio = abs(close - open) / (high - low)
        upperWickRatio = (high - max(open, close)) / (high - low)
        lowerWickRatio = (min(open, close) - low) / (high - low)
        """
        if df.empty or len(df) < 1:
            return {}

        latest = df.iloc[-1]
        o, h, l, c = latest['Open'], latest['High'], latest['Low'], latest['Close']
        hl_range = h - l if h != l else 0.001

        body = abs(c - o)
        body_ratio = round(body / hl_range, 3)
        upper_wick_ratio = round((h - max(o, c)) / hl_range, 3)
        lower_wick_ratio = round((min(o, c) - l) / hl_range, 3)

        return {
            "bodyRatio": body_ratio,
            "upperWickRatio": upper_wick_ratio,
            "lowerWickRatio": lower_wick_ratio
        }

    @staticmethod
    def detect_patterns(df):
        """
        Detects institutional patterns:
        - Pin Bar Rejection (wick > 60%)
        - Bullish/Bearish Engulfing with Volume > 1.5x SMA(20)
        - Inside Bar compression
        """
        if df.empty or len(df) < 5:
            return {"pattern": "None", "score_boost": 0}

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        o, h, l, c = latest['Open'], latest['High'], latest['Low'], latest['Close']
        p_o, p_h, p_l, p_c = prev['Open'], prev['High'], prev['Low'], prev['Close']

        hl_range = h - l if h != l else 0.001
        upper_wick = (h - max(o, c)) / hl_range
        lower_wick = (min(o, c) - l) / hl_range

        # Volume check
        if 'Volume' in df.columns:
            vol = latest['Volume']
            sma_vol = df['Volume'].rolling(20).mean().iloc[-1]
            high_vol = vol > (1.5 * sma_vol) if not pd.isna(sma_vol) else True
        else:
            high_vol = True

        patterns = []
        boost = 0

        # 1. Pin Bar Rejection
        if lower_wick > 0.6:
            patterns.append("🟢 Bullish Pin Bar Rejection")
            boost += 15
        elif upper_wick > 0.6:
            patterns.append("🔴 Bearish Pin Bar Rejection")
            boost -= 15

        # 2. Engulfing
        if c > o and p_c < p_o and c >= p_h and l <= p_l and high_vol:
            patterns.append("🔥 Bullish Engulfing (High Volume)")
            boost += 25
        elif c < o and p_c > p_o and l <= p_l and c <= p_l and high_vol:
            patterns.append("💥 Bearish Engulfing (High Volume)")
            boost -= 25

        # 3. Inside Bar
        if h <= p_h and l >= p_l:
            patterns.append("📦 Inside Bar (Volatility Compression)")
            boost += 5

        return {
            "patterns": patterns if patterns else ["⚖️ Normal Price Action"],
            "score_boost": boost
        }

    @staticmethod
    def calculate_indicators(df):
        """Calculates Intraday VWAP, PDH/PDL, and EMA distance"""
        if df.empty or len(df) < 20:
            return {}

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume'] if 'Volume' in df.columns else pd.Series(1, index=df.index)

        # VWAP approximation
        v = volume
        tp = (high + low + close) / 3
        vwap = round((tp * v).cumsum() / v.cumsum().iloc[-1], 2) if v.cumsum().iloc[-1] > 0 else close.iloc[-1]

        # Previous Day High / Low (using last 1-2 days)
        pdh = round(high.tail(20).max(), 2)
        pdl = round(low.tail(20).min(), 2)

        # EMAs
        ema20 = round(close.ewm(span=20).mean().iloc[-1], 2)
        ema50 = round(close.ewm(span=50).mean().iloc[-1], 2)
        ema200 = round(close.ewm(span=200).mean().iloc[-1], 2) if len(close) >= 200 else ema50

        cmp = round(close.iloc[-1], 2)

        return {
            "vwap": vwap.iloc[-1] if hasattr(vwap, 'iloc') else vwap,
            "pdh": pdh,
            "pdl": pdl,
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200,
            "cmp_vs_ema20_pct": round(((cmp - ema20) / ema20) * 100, 2)
        }
