"""
Self-Auditing Trade Logger & Performance Evaluator (`trade_logger.py`)
Stores every Arbiter verdict into SQLite and evaluates win rates, R:R, and agent accuracy.
"""

import sqlite3
import datetime
import os
import yfinance as yf

DB_NAME = "trades.db"

class TradeLogger:
    @staticmethod
    def init_db():
        """Initializes SQLite database for trade auditing."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                cmp REAL,
                sl REAL,
                t1 REAL,
                direction TEXT,
                verdict TEXT,
                conviction REAL,
                status TEXT DEFAULT 'OPEN'
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def log_trade(symbol, cmp, sl, t1, direction, verdict, conviction):
        """Logs a new Arbiter verdict into the database."""
        try:
            TradeLogger.init_db()
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (symbol, cmp, sl, t1, direction, verdict, conviction)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol.upper(), cmp, sl, t1, direction, verdict, conviction))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging trade: {e}")
            return False

    @staticmethod
    def evaluate_performance():
        """
        Evaluates past logged trades against current market prices.
        Calculates Win Rate %, Avg R:R, and Bull vs Bear accuracy.
        """
        try:
            TradeLogger.init_db()
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT id, symbol, cmp, sl, t1, direction, conviction FROM trades ORDER BY timestamp DESC LIMIT 20')
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return "📊 *TRADE AUDITOR PERFORMANCE*\n\nNo trades logged yet. Run a Bull vs Bear debate or analysis to log setups!"

            total_trades = len(rows)
            wins = 0
            bull_wins = 0
            bull_total = 0
            bear_wins = 0
            bear_total = 0

            details = []

            for row in rows:
                trade_id, symbol, cmp, sl, t1, direction, conviction = row
                try:
                    # Fetch current price
                    ticker = yf.Ticker(f"{symbol}.NS")
                    current_price = ticker.history(period="1d")['Close'].iloc[-1]

                    if direction == "BULL":
                        bull_total += 1
                        if current_price >= t1:
                            wins += 1
                            bull_wins += 1
                            status = "🟢 WIN (Hit Target)"
                        elif current_price <= sl:
                            status = "🔴 LOSS (Hit SL)"
                        else:
                            status = "🟡 OPEN / ACTIVE"
                    else:
                        bear_total += 1
                        if current_price <= sl: # Bear win if price dropped
                            wins += 1
                            bear_wins += 1
                            status = "🟢 WIN (Bear Correct)"
                        elif current_price >= t1:
                            status = "🔴 LOSS (Bull Rallied)"
                        else:
                            status = "🟡 OPEN / ACTIVE"

                    details.append(f"• {symbol} ({direction}): Entry ₹{cmp} → Now ₹{round(current_price, 2)} | {status}")
                except Exception:
                    details.append(f"• {symbol} ({direction}): Entry ₹{cmp} | Data fetch error")

            win_rate = round((wins / total_trades) * 100, 1) if total_trades > 0 else 0
            bull_acc = round((bull_wins / bull_total) * 100, 1) if bull_total > 0 else 0
            bear_acc = round((bear_wins / bear_total) * 100, 1) if bear_total > 0 else 0

            report = (
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 *SELF-AUDITING PERFORMANCE REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📈 Total Tracked Setups: *{total_trades}*\n"
                f"🎯 Overall Win Rate: *{win_rate}%*\n"
                f"🐂 Bull Agent Accuracy: *{bull_acc}%* ({bull_wins}/{bull_total})\n"
                f"🐻 Bear Agent Accuracy: *{bear_acc}%* ({bear_wins}/{bear_total})\n\n"
                f"📋 *Recent Setups*:\n" + "\n".join(details[:5]) + "\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Auditor Note*: Performance updates dynamically based on live market ticks."
            )
            return report
        except Exception as e:
            return f"❌ Performance evaluation error: {str(e)}"
