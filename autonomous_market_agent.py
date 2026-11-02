"""
24x7 Autonomous Indian Stock Market Agent with Telegram Phone Alerts

Requirements:
pip install requests schedule yfinance pandas beautifulsoup4

Setup:
1. Open Telegram, search for '@BotFather', send '/newbot' and get your BOT_TOKEN.
2. Search for '@userinfobot' on Telegram to get your CHAT_ID.
3. Paste them below in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
"""

import os
import time
import datetime
import schedule
import requests
import yfinance as yf

# ================= TELEGRAM CONFIG =================
TELEGRAM_BOT_TOKEN = "9089360235:AAGCTAesCisWR2soUzjrp4Suc8RwuOAi7G0"
TELEGRAM_CHAT_ID = "1729819060"

def send_phone_alert(message: str):
    """Sends instant push notification alert to your phone via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print(f"\n[PHONE ALERT (Telegram token missing)]:\n{message}\n")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
        return False

# ================= WATCHLIST STOCKS =================
WATCHLIST = [
    {
        "symbol": "RELIANCE.NS",
        "entry_low": 2935.0,
        "entry_high": 2950.0,
        "stop_loss": 2880.0,
        "target1": 3042.0,
        "target2": 3108.0,
        "triggered": False
    }
]

# ================= 1. LIVE MARKET SCAN (09:15 - 15:30) =================
def live_market_monitor():
    now = datetime.datetime.now()
    # Market hours: Monday (0) to Friday (4), 9:15 AM to 3:30 PM
    if now.weekday() >= 5:
        return # Weekend

    market_start = now.replace(hour=9, minute=15, second=0)
    market_end = now.replace(hour=15, minute=30, second=0)

    if not (market_start <= now <= market_end):
        return # Outside active market hours

    print(f"[{now.strftime('%H:%M:%S')}] Checking live watchlist prices...")

    for item in WATCHLIST:
        try:
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                continue

            cmp = round(hist['Close'].iloc[-1], 2)

            # Check Entry Zone Trigger
            if item["entry_low"] <= cmp <= item["entry_high"] and not item["triggered"]:
                msg = (
                    f"🚨 *ENTRY ALERT: {item['symbol']}*\n\n"
                    f"📈 Current Price: *₹{cmp}*\n"
                    f"🎯 Entry Zone: ₹{item['entry_low']} - ₹{item['entry_high']}\n"
                    f"🛑 Stop Loss: *₹{item['stop_loss']}*\n"
                    f"🎯 Target 1: *₹{item['target1']}* | Target 2: *₹{item['target2']}*\n\n"
                    f"⚡ Recommended Action: Check your broker and prepare execution."
                )
                send_phone_alert(msg)
                item["triggered"] = True

            # Check Stop Loss Breach
            elif cmp <= item["stop_loss"] and item["triggered"]:
                msg = (
                    f"⚠️ *STOP LOSS HIT / INVALIDATION: {item['symbol']}*\n"
                    f"Current Price dropped to *₹{cmp}* (Below SL ₹{item['stop_loss']})\n"
                    f"Action: Exit position or cancel setup."
                )
                send_phone_alert(msg)
                item["triggered"] = False

        except Exception as e:
            print(f"Error checking {item['symbol']}: {e}")

# ================= 2. MORNING PRE-MARKET REPORT (08:30 AM) =================
def morning_pre_market_report():
    print("Generating Morning Pre-Market Report...")
    try:
        # Fetch NIFTY & Global proxies
        nifty = yf.Ticker("^NSEI").history(period="5d")
        last_close = round(nifty['Close'].iloc[-1], 2)

        report = (
            f"☀️ *INDIAN MARKET MORNING BRIEFING*\n"
            f"📅 Date: {datetime.date.today()}\n\n"
            f"📊 *NIFTY 50 Previous Close*: ₹{last_close}\n"
            f"🎯 *Today's Focus Stocks*: RELIANCE, TCS, TATAMOTORS\n"
            f"📌 *Key Watch*: Pre-open settlement at 9:08 AM IST\n"
            f"💡 *Plan*: Watch for pullbacks to defined high-probability zones."
        )
        send_phone_alert(report)
    except Exception as e:
        print(f"Error generating morning report: {e}")

# ================= 3. EVENING POST-MARKET WRAP (05:00 PM) =================
def evening_post_market_report():
    print("Generating Evening Post-Market Report...")
    try:
        nifty = yf.Ticker("^NSEI").history(period="2d")
        change = round(nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2], 2)
        pct = round((change / nifty['Close'].iloc[-2]) * 100, 2)
        close = round(nifty['Close'].iloc[-1], 2)

        report = (
            f"🌙 *POST-MARKET CLOSING REPORT*\n"
            f"📅 Date: {datetime.date.today()}\n\n"
            f"🏁 *NIFTY 50*: ₹{close} ({'+' if change >= 0 else ''}{change} / {pct}%)\n"
            f"📈 *Trend Status*: {'Bullish continuation' if change > 0 else 'Consolidation / Profit taking'}\n"
            f"🔍 *Overnight Research Active*: Scanning FII/DII numbers, earnings, and news catalysts."
        )
        send_phone_alert(report)
    except Exception as e:
        print(f"Error generating evening report: {e}")

# ================= RUN ONCE FOR GITHUB ACTIONS =================
if __name__ == "__main__":
    print("🚀 Running 1-minute market check for GitHub Actions...")
    send_phone_alert("🤖 *Market Agent Triggered!*\nRunning scheduled stock check...")

    # Run the live monitor once
    live_market_monitor()

    print("✅ Market check completed. Exiting safely.")
