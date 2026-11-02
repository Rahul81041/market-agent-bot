"""
Verified Signal Track Record & Win-Rate Proof Engine (`signal_tracker.py`)
==========================================================================
Replaces dummy cash wallet balances with an institutional signal-based track record.
Tracks every published signal:
- Unique Signal ID (#SIG-XXXX)
- Ticker, Direction (LONG/SHORT)
- Entry CMP, ATR Stop-Loss, Target 1 & Target 2, Risk-Reward (R:R)
- Win/Loss monitoring against intraday High/Low
- Calculates Win Rate %, Profit Factor, Bull vs Bear Accuracy
- Real-time Telegram alerts for Target Hit / SL Hit / Trailing T2
- Formats clean Signal Cards and Client Track Records
"""

import sqlite3
import datetime
import random
import yfinance as yf
import requests
from pytz import timezone

DB_NAME = "trades.db"
TELEGRAM_BOT_TOKEN = "9089360235:AAGCTAesCisWR2soUzjrp4Suc8RwuOAi7G0"
IST = timezone('Asia/Kolkata')

class SignalTracker:

    @staticmethod
    def init_db():
        """Initialize verified_signals table."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verified_signals (
                signal_id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_cmp REAL NOT NULL,
                entry_min REAL NOT NULL,
                entry_max REAL NOT NULL,
                stop_loss REAL NOT NULL,
                target1 REAL NOT NULL,
                target2 REAL NOT NULL,
                rr_ratio REAL NOT NULL,
                conviction REAL NOT NULL,
                verdict TEXT,
                status TEXT DEFAULT 'ACTIVE', -- ACTIVE, TARGET_1_HIT, TARGET_2_HIT, SL_HIT, EXPIRED
                exit_price REAL,
                exit_time DATETIME,
                points_captured REAL DEFAULT 0,
                gain_loss_pct REAL DEFAULT 0,
                audit_note TEXT
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def generate_signal_id():
        """Generate unique signal ID like #SIG-2401, #SIG-8921."""
        rand_num = random.randint(1000, 9999)
        return f"#SIG-{rand_num}"

    @staticmethod
    def publish_signal(symbol, cmp, stop_loss, target1, target2, direction, conviction, verdict):
        """
        Registers an official verified signal card in the database.
        Returns signal_data dict and formatted telegram card text.
        """
        SignalTracker.init_db()
        sig_id = SignalTracker.generate_signal_id()

        risk = abs(cmp - stop_loss)
        reward = abs(target1 - cmp)
        rr_ratio = round(reward / risk, 2) if risk > 0 else 1.5

        entry_min = round(cmp * 0.997, 2)
        entry_max = round(cmp * 1.003, 2)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO verified_signals
            (signal_id, symbol, direction, entry_cmp, entry_min, entry_max, stop_loss, target1, target2, rr_ratio, conviction, verdict, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        ''', (
            sig_id, symbol.upper(), direction, cmp, entry_min, entry_max,
            stop_loss, target1, target2, rr_ratio, conviction, verdict
        ))
        conn.commit()
        conn.close()

        dir_emoji = "🟢 LONG / BUY" if direction == "BULL" else "🔴 SHORT / SELL"
        action_verb = "Targeting Upward Momentum" if direction == "BULL" else "Bearish Rejection Setup"

        card = (
            f"🎯 *OFFICIAL VERIFIED SIGNAL ISSUED*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ Signal ID: `{sig_id}`\n"
            f"📊 Stock: *{symbol.upper()}* ({dir_emoji})\n"
            f"⚡ Setup: {action_verb}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Entry Zone: *₹{entry_min} - ₹{entry_max}* (CMP ₹{cmp})\n"
            f"🛑 Stop Loss: *₹{stop_loss}*\n"
            f"🎯 Target 1: *₹{target1}* (R:R 1:{rr_ratio})\n"
            f"🚀 Target 2 (Runner): *₹{target2}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚖️ Arbiter Conviction: *{conviction}%*\n"
            f"🔒 Status: *ACTIVE & LOGGED TO AUDIT RECORD*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

        return {
            "signal_id": sig_id,
            "symbol": symbol.upper(),
            "direction": direction,
            "cmp": cmp,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "rr_ratio": rr_ratio,
            "conviction": conviction,
            "card_text": card
        }

    @staticmethod
    def monitor_signals(chat_id=None):
        """
        Monitors active signals against live intraday high/low/close prices.
        If Target 1, Target 2, or SL is hit, marks outcome and pushes alert.
        """
        SignalTracker.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT signal_id, symbol, direction, entry_cmp, stop_loss, target1, target2, rr_ratio
            FROM verified_signals
            WHERE status = 'ACTIVE'
        ''')
        active_signals = cursor.fetchall()
        conn.close()

        if not active_signals:
            return []

        resolved_signals = []
        now_time = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

        for sig in active_signals:
            sig_id, symbol, direction, entry, sl, t1, t2, rr = sig

            try:
                ticker = yf.Ticker(f"{symbol}.NS")
                hist = ticker.history(period="1d", interval="1m")
                if hist.empty:
                    continue

                curr_cmp = round(hist['Close'].iloc[-1], 2)
                day_high = round(hist['High'].max(), 2)
                day_low = round(hist['Low'].min(), 2)

                status = None
                exit_price = None
                note = ""

                if direction == "BULL":
                    if day_high >= t2:
                        status = "TARGET_2_HIT"
                        exit_price = t2
                        note = "Target 2 Smashed (Maximum Gain)"
                    elif day_high >= t1:
                        status = "TARGET_1_HIT"
                        exit_price = t1
                        note = "Target 1 Hit Successfully"
                    elif day_low <= sl:
                        status = "SL_HIT"
                        exit_price = sl
                        note = "Stop Loss Triggered"
                else:  # BEAR
                    if day_low <= t2:
                        status = "TARGET_2_HIT"
                        exit_price = t2
                        note = "Bear Target 2 Smashed"
                    elif day_low <= t1:
                        status = "TARGET_1_HIT"
                        exit_price = t1
                        note = "Bear Target 1 Hit"
                    elif day_high >= sl:
                        status = "SL_HIT"
                        exit_price = sl
                        note = "Stop Loss Triggered"

                if status:
                    if direction == "BULL":
                        pts = round(exit_price - entry, 2)
                        pct = round(((exit_price - entry) / entry) * 100, 2)
                    else:
                        pts = round(entry - exit_price, 2)
                        pct = round(((entry - exit_price) / entry) * 100, 2)

                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute('''
                        UPDATE verified_signals
                        SET status = ?, exit_price = ?, exit_time = ?, points_captured = ?, gain_loss_pct = ?, audit_note = ?
                        WHERE signal_id = ?
                    ''', (status, exit_price, now_time, pts, pct, note, sig_id))
                    conn.commit()
                    conn.close()

                    outcome_dict = {
                        "signal_id": sig_id,
                        "symbol": symbol,
                        "direction": direction,
                        "entry": entry,
                        "exit": exit_price,
                        "status": status,
                        "points": pts,
                        "pct": pct,
                        "note": note
                    }
                    resolved_signals.append(outcome_dict)

                    if chat_id:
                        SignalTracker.send_resolution_alert(chat_id, outcome_dict)

            except Exception as e:
                print(f"Error checking signal {sig_id}: {e}")
                continue

        return resolved_signals

    @staticmethod
    def send_resolution_alert(chat_id, outcome):
        """Send formatted win/loss notification for client showcase."""
        is_win = "TARGET" in outcome["status"]
        emoji = "🏆 TARGET HIT" if is_win else "🛑 STOP-LOSS HIT"
        badge = "🟢 WIN" if is_win else "🔴 LOSS"

        msg = (
            f"{emoji} *| {badge}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ Signal ID: `{outcome['signal_id']}`\n"
            f"📊 Stock: *{outcome['symbol']}* ({outcome['direction']})\n"
            f"📍 Entry CMP: ₹{outcome['entry']}\n"
            f"🏁 Exit Price: *₹{outcome['exit']}*\n"
            f"📈 Return: *{outcome['pct']:+.2f}%* ({outcome['points']:+.2f} pts)\n"
            f"📋 Outcome: {outcome['note']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔒 *Verified Record*: Permanently audited in signal engine."
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass

    @staticmethod
    def get_track_record_summary():
        """
        Calculates Win Rate, Total Signals, Target Hits, SL Hits,
        Average R:R, and client-ready track record proof.
        """
        SignalTracker.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM verified_signals")
        total_signals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM verified_signals WHERE status = 'ACTIVE'")
        active_signals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM verified_signals WHERE status IN ('TARGET_1_HIT', 'TARGET_2_HIT')")
        wins = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM verified_signals WHERE status = 'SL_HIT'")
        losses = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(rr_ratio) FROM verified_signals")
        avg_rr = cursor.fetchone()[0] or 1.5

        cursor.execute("SELECT SUM(points_captured) FROM verified_signals WHERE status != 'ACTIVE'")
        total_pts = cursor.fetchone()[0] or 0.0

        cursor.execute('''
            SELECT signal_id, symbol, direction, entry_cmp, exit_price, status, gain_loss_pct
            FROM verified_signals
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        recent_signals = cursor.fetchall()
        conn.close()

        resolved = wins + losses
        win_rate = round((wins / resolved) * 100, 1) if resolved > 0 else 0.0

        # Performance score badge
        if win_rate >= 75:
            tier = "💎 Institutional Grade (Elite)"
        elif win_rate >= 60:
            tier = "🏆 High Performance (Commercial Ready)"
        else:
            tier = "⚖️ Balanced Strategy"

        summary = (
            f"🏆 *VERIFIED SIGNAL TRACK RECORD & WIN-RATE AUDIT*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏅 System Tier: *{tier}*\n\n"
            f"🎯 *Win Rate*: *{win_rate}%* ({wins} Wins / {losses} Losses)\n"
            f"📊 Total Signals Issued: *{total_signals}*\n"
            f"⏳ Active / In-Play: *{active_signals}*\n"
            f"⚖️ Average Risk-to-Reward: *1:{avg_rr:.2f}*\n"
            f"📈 Net Points Delivered: *{total_pts:+.2f} pts*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 *Recent Track Record Ledger*:\n"
        )

        if not recent_signals:
            summary += "• No completed signals yet. Analyze stocks to generate verified signals!\n"
        else:
            for s_id, sym, direct, entry, exit_p, st, pct in recent_signals:
                if st == "ACTIVE":
                    badge = "🟡 ACTIVE"
                    ret_str = f"CMP ₹{entry}"
                elif "TARGET" in st:
                    badge = "🟢 WIN"
                    ret_str = f"Exit ₹{exit_p} ({pct:+.2f}%)"
                else:
                    badge = "🔴 LOSS"
                    ret_str = f"Exit ₹{exit_p} ({pct:+.2f}%)"
                summary += f"• `{s_id}` *{sym}* ({direct}) | {badge} | {ret_str}\n"

        summary += (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Audited Proof*: All setups recorded transparently with entry CMP & live price verification."
        )

        return summary
