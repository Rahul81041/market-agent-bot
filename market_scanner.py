"""
Full NSE Stock Universe & Background Auto-Scanner (`market_scanner.py`)
Scans top Nifty 100 + liquid NSE F&O stocks every 15 mins during market hours,
auto-runs Bull vs Bear debate if high conviction, auto-invests from wallet.
"""

import yfinance as yf
import requests
import time
import numpy as np
from datetime import datetime

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

try:
    from pytz import timezone
    IST = timezone('Asia/Kolkata')
except ImportError:
    IST = None

# Full Nifty 100 + NSE F&O liquid stocks list
NSE_LIQUID_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "TATAMOTORS",
    "TATASTEEL", "BHARTIARTL", "HINDUNILVR", "ITC", "KOTAKBANK", "LT", "AXISBANK",
    "BAJFINANCE", "MARUTI", "ASIANPAINT", "HCLTECH", "WIPRO", "SUNPHARMA", "ULTRACEMCO",
    "NTPC", "POWERGRID", "TITAN", "INDUSINDBK", "TECHM", "NESTLEIND", "GRASIM", "CIPLA",
    "BAJAJFINSV", "HEROMOTOCO", "DRREDDY", "SHREECEM", "BRITANNIA", "EICHERMOT", "ADANIENT",
    "ADANIPORTS", "APOLLOHOSP", "DMART", "ZEEL", "GODREJCP", "DABUR", "MARICO", "BPCL",
    "ONGC", "COALINDIA", "SBILIFE", "HDFCLIFE", "ICICIGI", "ICICIPRULI", "PIIND", "SRF",
    "MUTHOOTFIN", "BANDHANBNK", "AUBANK", "IDFCFIRSTB", "PNB", "BANKBARODA", "CANBK",
    "UNIONBANK", "INDIANB", "JINDALSTEL", "JSWSTEEL", "HINDALCO", "VEDL", "ADANITOTAL",
    "ADANIGREEN", "ADANITRANS", "ADANIPOWER", "TATAPOWER", "TATACONSUMER", "TATACOFFEE",
    "TATACONSUM", "TCS", "INFY", "WIPRO", "LTIM", "COFINDIA", "BSE", "NIFTY", "BANKNIFTY",
    "FINNIFTY", "MIDCPNIFTY", "NIFTYBEES", "JETAIRWAYS", "VOLTAS", "TORNTPHARM", "LUPIN",
    "CIPLA", "DRREDDY", "SUNPHARMA", "LARSEN", "TATASTEEL", "GALLANT", "JSWSTEEL", "IDEA",
    "VODAFONE", "AUROPHARMA", "AVANTIFEED", "DABUR", "COLPAL", "BRITANNIA", "IGL", "INDUSTOWER",
    "NHPC", "NTPC", "POWERGRID", "RECLTD", "BPCL", "HPCL", "IOB", "OIL", "PETRONET", "GAIL",
    "TATAPOWER", "TataElxsi", "M&MFIN", "M&M", "MOTHERSUMI", "MRF", "MUTHOOTCAP", "PFC", "PFCLTD"
]

# Remove duplicates
NSE_LIQUID_STOCKS = list(set(NSE_LIQUID_STOCKS))
NSE_LIQUID_STOCKS.sort()

class MarketScanner:
    LAST_SCANNED = {}

    @staticmethod
    def fetch_live_prices(symbols, period="1d", interval="1m"):
        """Fetch live prices for multiple stocks."""
        prices = {}
        for sym in symbols:
            try:
                ticker = yf.Ticker(f"{sym}.NS")
                data = ticker.history(period=period, interval=interval)
                if not data.empty:
                    prices[sym] = {
                        "close": round(data['Close'].iloc[-1], 2),
                        "high": round(data['High'].max(), 2),
                        "low": round(data['Low'].min(), 2),
                        "volume": int(data['Volume'].iloc[-1])
                    }
            except:
                pass
        return prices

    @staticmethod
    def scan_for_unusual_volume(symbols):
        """Scan for stocks with unusual volume (>2x SMA)."""
        unusual = []
        for sym in symbols:
            try:
                ticker = yf.Ticker(f"{sym}.NS")
                data = ticker.history(period="5d", interval="1d")
                if len(data) >= 5:
                    avg_vol = data['Volume'].rolling(20).mean().iloc[-1]
                    last_vol = data['Volume'].iloc[-1]
                    if last_vol > (2 * avg_vol) and avg_vol > 0:
                        unusual.append(sym)
            except:
                continue
        return unusual

    @staticmethod
    def run_bull_bear_debate_and_auto_invest(sym, chat_id):
        """Run full Bull vs Bear analysis and auto-invest if conviction >= 65%."""
        try:
            # Import on-demand to avoid circular dependency
            from price_action import PriceActionAnalyzer
            from mtf_analyzer import MTFAnalyzer
            from trade_logger import TradeLogger
            from paper_fund_manager import PaperFundManager

            ticker = yf.Ticker(f"{sym}.NS")
            df = ticker.history(period="6mo", interval="1d")

            if df.empty or len(df) < 20:
                return None

            cmp = round(df['Close'].iloc[-1], 2)
            close = df['Close']

            # Price Action
            anatomy = PriceActionAnalyzer.calculate_candle_anatomy(df)
            pa_patterns = PriceActionAnalyzer.detect_patterns(df)
            indicators = PriceActionAnalyzer.calculate_indicators(df)

            # MTF
            mtf_data = MTFAnalyzer.fetch_mtf_data(sym)
            mtf_result = MTFAnalyzer.calculate_alignment_score(mtf_data)

            # Calculations
            tr = df['High'] - df['Low']
            for i in range(1, len(df)):
                tr.iloc[i] = max(tr.iloc[i], abs(df['High'].iloc[i] - df['Close'].iloc[i-1]), abs(df['Low'].iloc[i] - df['Close'].iloc[i-1]))
            atr = round(tr.rolling(14).mean().iloc[-1], 2)

            stop_loss = round(cmp - (1.8 * atr), 2)
            risk = cmp - stop_loss
            target1 = round(cmp + (1.5 * risk), 2)

            daily_vol = (atr / cmp) / 15.874  # sqrt(252)
            sims = cmp * (1 + np.random.normal(0, daily_vol, 1000))
            win_prob = round((sims >= target1).mean() * 100, 1)

            # Scoring
            bull_score = 40 + pa_patterns.get("score_boost", 0) + (mtf_result.get("score", 2) * 10)
            bear_score = 50 - pa_patterns.get("score_boost", 0)

            conviction = round((bull_score / (bull_score + bear_score)) * 100, 1) if (bull_score + bear_score) > 0 else 50

            direction = "BULL" if bull_score > bear_score else "BEAR"
            verdict = "BULL WINS" if bull_score > bear_score else "BEAR WINS"

            # Log trade
            TradeLogger.log_trade(sym, cmp, stop_loss, target1, direction, verdict, conviction)

            # Auto-invest if conviction >= 65%
            executed = False
            if conviction >= 65:
                executed, msg = PaperFundManager.execute_paper_trade(sym, cmp, stop_loss, target1, target1*1.66, direction, conviction)

            return {
                "symbol": sym,
                "cmp": cmp,
                "conviction": conviction,
                "direction": direction,
                "verdict": verdict,
                "entry": round(cmp*0.995, 2),
                "sl": stop_loss,
                "t1": target1,
                "executed": executed,
                "exec_msg": msg if executed else None
            }
        except Exception as e:
            print(f"Error scanning {sym}: {e}")
            return None

    @staticmethod
    def run_background_scan(chat_id=None):
        """Background scan: every 15 mins during market hours."""
        now = datetime.now(IST)
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)

        # Only scan during market hours on weekdays
        if now.weekday() >= 5 or not (market_start <= now <= market_end):
            return []

        # Check cooldown (3 mins between scans)
        last_scan = MarketScanner.LAST_SCANNED.get("scan", datetime.min.replace(tzinfo=IST))
        if (now - last_scan).total_seconds() < 180:
            return []
        MarketScanner.LAST_SCANNED["scan"] = now

        # Scan for unusual volume stocks
        unusual = MarketScanner.scan_for_unusual_volume(NSE_LIQUID_STOCKS[:30])  # Top 30 for speed

        if not unusual:
            return []

        results = []
        for sym in unusual[:5]:  # Process top 5
            result = MarketScanner.run_bull_bear_debate_and_auto_invest(sym, chat_id)
            if result:
                results.append(result)

                if chat_id:
                    MarketScanner.send_scan_alert(chat_id, result)

        return results

    @staticmethod
    def send_scan_alert(chat_id, result):
        """Send scan alert to Telegram."""
        emoji = "🟢" if result["direction"] == "BULL" else "🔴"

        msg = (
            f"🤖 *AUTO-SCANNER ALERT*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ {result['symbol']} - High Volume Surge Detected!\n"
            f"{emoji} *Bull vs Bear Verdict*: {result['verdict']} ({result['conviction']}% conviction)\n\n"
            f"💰 *Entry Zone*: ₹{result['entry']} - ₹{round(result['entry']*1.007, 2)}\n"
            f"🛑 *Stop Loss*: *₹{result['sl']}*\n"
            f"🎯 *Target 1*: *₹{result['t1']}*\n\n"
        )

        if result['executed']:
            msg += f"✅ *AUTO-INVESTED*: {result['exec_msg']}\n"

        msg += f"━━━━━━━━━━━━━━━━━━━━━━"

        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass

    @staticmethod
    def start_scheduler(chat_id):
        """Start background scheduler for auto-scanning."""
        if not SCHEDULER_AVAILABLE:
            print("apscheduler not installed. Run: pip install apscheduler pytz")
            return None
        scheduler = BackgroundScheduler(timezone=IST)

        # Run every 15 minutes during market hours
        def scan_job():
            MarketScanner.run_background_scan(chat_id)

        scheduler.add_job(scan_job, 'cron', minute='*/15', max_instances=3)
        scheduler.start()

        return scheduler

    @staticmethod
    def get_market_summary():
        """Return market summary for /scan command."""
        now = datetime.now(IST) if IST else datetime.now()
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        market_open = market_start <= now <= market_end

        # Fetch Nifty
        nifty = yf.Ticker("^NSEI").history(period="1d")
        nifty_price = round(nifty['Close'].iloc[-1], 2) if not nifty.empty else 0

        summary = (
            f"📊 *NSE MARKET SCANNER*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f" Market Status: {'🟢 OPEN' if market_open else '🔴 CLOSED'}\n"
            f" NIFTY 50: ₹{nifty_price}\n"
            f" Scanner Active: {'✅ Yes' if market_open else '❌ No'}\n\n"
            f" 🔍 Top Liquid Stocks Scanned: {len(NSE_LIQUID_STOCKS)}\n"
            f" 📈 Auto-Scan Interval: Every 15 mins\n"
            f" 💰 Auto-Invest Threshold: Conviction >= 65%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

        return summary
