"""
Multi-Timeframe (MTF) & Benchmark Confluence Analyzer
Fetches 15m, 1H, 1D data and Nifty 50 (^NSEI) to calculate MTF Alignment score (0-3).
Blocks high-conviction signals if timeframes conflict.
"""

import yfinance as yf
import pandas as pd

class MTFAnalyzer:
    @staticmethod
    def fetch_mtf_data(symbol):
        """Fetches 15m, 1H, 1D data for the symbol and Nifty (^NSEI)."""
        sym_clean = symbol.upper().replace(".NS", "")
        ticker_str = f"{sym_clean}.NS"

        try:
            # 15m data (last 5 days)
            df_15m = yf.Ticker(ticker_str).history(period="5d", interval="15m")
            # 1H data (last 1 month)
            df_1h = yf.Ticker(ticker_str).history(period="1mo", interval="1h")
            # 1D data (last 6 months)
            df_1d = yf.Ticker(ticker_str).history(period="6mo", interval="1d")
            # Nifty 50 benchmark (1mo, 1d)
            df_nifty = yf.Ticker("^NSEI").history(period="1mo", interval="1d")

            return {
                "15m": df_15m,
                "1h": df_1h,
                "1d": df_1d,
                "nifty": df_nifty
            }
        except Exception as e:
            print(f"Error fetching MTF data for {symbol}: {e}")
            return None

    @staticmethod
    def calculate_alignment_score(mtf_data):
        """
        Calculates MTF Alignment Score (0 to 3) and Nifty trend check.
        Returns alignment score, breakdown dictionary, and whether signal should be blocked.
        """
        if not mtf_data or any(mtf_data[k].empty for k in ["15m", "1h", "1d"]):
            return {"score": 1, "blocked": False, "summary": "Insufficient MTF data"}

        try:
            # Check 15m trend (Price vs 20 EMA)
            c15 = mtf_data["15m"]["Close"]
            ema20_15m = c15.ewm(span=20).mean().iloc[-1]
            trend_15m = c15.iloc[-1] > ema20_15m

            # Check 1H trend
            c1h = mtf_data["1h"]["Close"]
            ema20_1h = c1h.ewm(span=20).mean().iloc[-1]
            trend_1h = c1h.iloc[-1] > ema20_1h

            # Check 1D trend
            c1d = mtf_data["1d"]["Close"]
            ema50_1d = c1d.ewm(span=50).mean().iloc[-1]
            trend_1d = c1d.iloc[-1] > ema50_1d

            # Check Nifty trend
            cnifty = mtf_data["nifty"]["Close"]
            ema20_nifty = cnifty.ewm(span=20).mean().iloc[-1]
            nifty_bullish = cnifty.iloc[-1] > ema20_nifty

            # Score calculation (count how many timeframes are bullish)
            bullish_count = sum([trend_15m, trend_1h, trend_1d])

            # If 15m fights 1H/1D or Nifty, block high conviction
            blocked = False
            if trend_15m != trend_1d and not nifty_bullish == trend_15m:
                blocked = True

            summary = (
                f"• 15m Trend: {'🟢 Bullish' if trend_15m else '🔴 Bearish'}\n"
                f"• 1H Trend: {'🟢 Bullish' if trend_1h else '🔴 Bearish'}\n"
                f"• 1D Trend: {'🟢 Bullish' if trend_1d else '🔴 Bearish'}\n"
                f"• Nifty 50 Benchmark: {'🟢 Bullish' if nifty_bullish else '🔴 Bearish'}\n"
                f"• Alignment Score: {bullish_count}/3 timeframes aligned."
            )

            return {
                "score": bullish_count,
                "blocked": blocked,
                "summary": summary,
                "trend_15m": trend_15m,
                "trend_1d": trend_1d
            }
        except Exception as e:
            print(f"Error calculating MTF alignment: {e}")
            return {"score": 2, "blocked": False, "summary": "MTF calculation error, using default."}
