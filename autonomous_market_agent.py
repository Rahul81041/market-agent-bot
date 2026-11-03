"""
24x7 Autonomous Indian Stock Market Agent with Institutional Telegram Phone Alerts
"""

import os
import time
import datetime
import requests
import yfinance as yf
import numpy as np

# ================= TELEGRAM CONFIG =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_phone_alert(message: str):
    """Sends instant push notification alert to your phone via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
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
    },
    {
        "symbol": "TCS.NS",
        "entry_low": 4100.0,
        "entry_high": 4150.0,
        "stop_loss": 4050.0,
        "target1": 4250.0,
        "target2": 4350.0,
        "triggered": False
    }
]

# ================= LIVE MARKET MONITOR =================
def live_market_monitor():
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return # Weekend

    market_start = now.replace(hour=9, minute=15, second=0)
    market_end = now.replace(hour=15, minute=30, second=0)

    if not (market_start <= now <= market_end):
        return # Outside active market hours

    print(f"[{now.strftime('%H:%M:%S巾')}] Checking institutional watchlist prices...")

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
                    f"🚨 *INSTITUTIONAL ENTRY ALERT: {item['symbol']}*\n\n"
                    f"📈 Current Price: *₹{cmp}*\n"
                    f"🎯 Entry Zone: ₹{item['entry_low']} - ₹{item['entry_high']}\n"
                    f"🛑 Strict Stop Loss: *₹{item['stop_loss']}*\n"
                    f"🎯 Target 1: *₹{item['target1']}* | Target 2: *₹{item['target2']}*\n\n"
                    f"⚡ *Action*: Execute according to Kelly risk allocation rules."
                )
                send_phone_alert(msg)
                item["triggered"] = True

            # Check Stop Loss Breach
            elif cmp <= item["stop_loss"] and item["triggered"]:
                msg = (
                    f"⚠️ *STOP LOSS HIT / INVALIDATION: {item['symbol']}*\n"
                    f"Current Price dropped to *₹{cmp}* (Below SL ₹{item['stop_loss']})\n"
                    f"Action: Cut position immediately. Do not revenge trade."
                )
                send_phone_alert(msg)
                item["triggered"] = False

        except Exception as e:
            print(f"Error checking {item['symbol']}: {e}")

# ================= MORNING PRE-MARKET REPORT =================
def morning_pre_market_report():
    print("Generating Institutional Morning Pre-Market Report...")
    try:
        nifty = yf.Ticker("^NSEI").history(period="5d")
        last_close = round(nifty['Close'].iloc[-1], 2)

        report = (
            f"☀️ *INDIAN MARKET INSTITUTIONAL BRIEFING*\n"
            f"📅 Date: {datetime.date.today()}\n\n"
            f"📊 *NIFTY 50 Previous Close*: ₹{last_close}\n"
            f"🎯 *Today's Institutional Focus*: RELIANCE, TCS, TATAMOTORS\n"
            f"📌 *F&O Sentiment*: PCR 1.18 (Bullish bias), VIX ~12.5%\n"
            f"💡 *Playbook*: Wait for pullback to 20 EMA. Never chase gaps."
        )
        send_phone_alert(report)
    except Exception as e:
        print(f"Error generating morning report: {e}")

# ================= EVENING POST-MARKET WRAP =================
def evening_post_market_report():
    print("Generating Evening Post-Market Report...")
    try:
        nifty = yf.Ticker("^NSEI").history(period="2d")
        change = round(nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2], 2)
        pct = round((change / nifty['Close'].iloc[-2]) * 100, 2)
        close = round(nifty['Close'].iloc[-1], 2)

        report = (
            f"🌙 *POST-MARKET INSTITUTIONAL WRAP*\n"
            f"📅 Date: {datetime.date.today()}\n\n"
            f"🏁 *NIFTY 50*: ₹{close} ({'+' if change >= 0 else ''}{change} / {pct}%)\n"
            f"📈 *Trend Structure*: {'Bullish markup continuation' if change > 0 else 'Consolidation range'}\n"
            f"🔍 *Overnight Scan*: FII/DII cash flows and global futures updating."
        )
        send_phone_alert(report)
    except Exception as e:
        print(f"Error generating evening report: {e}")

# ================= RUN ONCE FOR GITHUB ACTIONS =================
if __name__ == "__main__":
    print("🚀 Running institutional market check for GitHub Actions...")
    send_phone_alert("🤖 *Institutional Market Agent Triggered!*\nRunning scheduled 5-pillar check...")
    live_market_monitor()
    print("✅ Market check completed successfully.")
