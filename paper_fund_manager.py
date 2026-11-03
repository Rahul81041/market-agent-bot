"""
Multi-User Paper Trading Portfolio Manager (`paper_fund_manager.py`)
=====================================================================
- Each Telegram user gets their own isolated portfolio (by chat_id)
- Clean slate: 0 open positions, ₹1,00,000 dummy cash on first use
- NO hardcoded stocks - user must explicitly trigger investments
- Signal tracking via SignalTracker
"""

import sqlite3
import datetime
from signal_tracker import SignalTracker

DB_NAME = "trades.db"
INITIAL_CAPITAL = 100000.0

class PaperFundManager:

    @staticmethod
    def init_db():
        """Initialize multi-user portfolio tables"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # User portfolios - one per chat_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_portfolios (
                chat_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_deposited REAL DEFAULT ?,
                current_balance REAL DEFAULT ?,
                total_invested REAL DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0
            )
        ''', (INITIAL_CAPITAL, INITIAL_CAPITAL))

        # Active positions per user
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                entry_price REAL,
                quantity INTEGER,
                stop_loss REAL,
                target1 REAL,
                target2 REAL,
                direction TEXT,
                invested_amount REAL,
                status TEXT DEFAULT 'OPEN'
            )
        ''',)

        conn.commit()
        conn.close()

    @staticmethod
    def get_or_create_portfolio(chat_id):
        """Get user's portfolio, create clean slate if doesn't exist"""
        PaperFundManager.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM user_portfolios WHERE chat_id = ?', (str(chat_id),))
        portfolio = cursor.fetchone()

        if not portfolio:
            # Create fresh portfolio for new user
            cursor.execute('''
                INSERT INTO user_portfolios (chat_id, total_deposited, current_balance)
                VALUES (?, ?, ?)
            ''', (str(chat_id), INITIAL_CAPITAL, INITIAL_CAPITAL))
            conn.commit()
            portfolio = (str(chat_id), datetime.datetime.now(), INITIAL_CAPITAL, INITIAL_CAPITAL, 0, 0, 0, 0)

        conn.close()
        return portfolio

    @staticmethod
    def execute_paper_trade(chat_id, symbol, entry_price, stop_loss, target1, target2, direction, amount=20000):
        """
        Execute paper trade for specific user with explicit amount.
        Returns (success, message)
        """
        # Validate amount
        if amount <= 0:
            return False, "Invalid amount"

        portfolio = PaperFundManager.get_or_create_portfolio(chat_id)
        current_balance = portfolio[3]  # current_balance column

        if amount > current_balance:
            return False, f"Insufficient balance. Available: ₹{current_balance:.2f}"

        # Calculate quantity based on amount
        quantity = int(amount / entry_price)
        if quantity <= 0:
            return False, "Amount too small for even 1 share"

        invested = quantity * entry_price

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Deduct from balance
            new_balance = current_balance - invested
            cursor.execute('''
                UPDATE user_portfolios
                SET current_balance = ?, total_invested = total_invested + ?, total_trades = total_trades + 1
                WHERE chat_id = ?
            ''', (new_balance, invested, str(chat_id)))

            # Add position
            cursor.execute('''
                INSERT INTO user_positions
                (chat_id, symbol, entry_price, quantity, stop_loss, target1, target2, direction, invested_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(chat_id), symbol.upper(), entry_price, quantity, stop_loss, target1, target2, direction, invested))

            conn.commit()
            conn.close()

            # Also log to SignalTracker
            verdict = "BULL WINS" if direction == "BULL" else "BEAR WINS"
            SignalTracker.publish_signal(symbol, entry_price, stop_loss, target1, target2, direction, 65, verdict)

            return True, f"✅ Paper Trade Executed: {quantity} shares of {symbol} @ ₹{entry_price} (₹{invested:.2f})"

        except Exception as e:
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_portfolio_summary(chat_id):
        """Get user's clean portfolio dashboard"""
        portfolio = PaperFundManager.get_or_create_portfolio(chat_id)
        chat_id_str, created, deposited, balance, invested, pnl, total_trades, wins = portfolio

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol, entry_price, quantity, direction, invested_amount
            FROM user_positions WHERE chat_id = ? AND status = 'OPEN'
        ''', (str(chat_id),))
        open_positions = cursor.fetchall()
        conn.close()

        win_rate = round((wins / total_trades * 100), 1) if total_trades > 0 else 0
        pnl_pct = round((pnl / deposited * 100), 2) if deposited > 0 else 0

        # Build clean message
        msg = (
            f"🏦 *DUMMY PORTFOLIO DASHBOARD*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Available Dummy Cash: *₹{balance:,.2f}*\n"
            f"📊 Invested Margin: *₹{invested:,.2f}*\n"
            f"📈 Net Portfolio Equity: *₹{balance:,.2f}* ({pnl_pct:+.2f}%)\n\n"
            f"📋 *ACTIVE WATCHLIST* ({len(open_positions)} Open Trades):\n"
        )

        if not open_positions:
            msg += (
                f"✨ Your watchlist is currently clean!\n\n"
                f"👉 Tap *'🔥 Find Top 5 Stocks'* or search any stock "
                f"to start a risk-free Paper Trade and test our AI's accuracy "
                f"before using real capital."
            )
        else:
            for sym, entry, qty, direction, amt in open_positions:
                dir_emoji = "🟢" if direction == "BULL" else "🔴"
                msg += f"\n• {dir_emoji} *{sym}*: {qty} shares @ ₹{entry} (₹{amt:,.0f})"

        msg += (
            f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Trades: {total_trades} | Win Rate: {win_rate}% | Wins: {wins}"
        )

        return msg

    @staticmethod
    def monitor_positions(chat_id=None):
        """Monitor open positions and auto-close if targets/SL hit"""
        import yfinance as yf
        import os
        from pytz import timezone
        import requests

        IST = timezone('Asia/Kolkata')
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

        PaperFundManager.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, chat_id, symbol, entry_price, quantity, stop_loss, target1, target2, direction, invested_amount
            FROM user_positions WHERE status = 'OPEN'
        ''')
        positions = cursor.fetchall()

        if not positions:
            conn.close()
            return []

        now = datetime.datetime.now(IST)
        market_start = now.replace(hour=9, minute=15, second=0)
        market_end = now.replace(hour=15, minute=30, second=0)

        # Only check during market hours on weekdays
        if now.weekday() >= 5 or not (market_start <= now <= market_end):
            conn.close()
            return []

        closed = []

        for pos in positions:
            pos_id, chat_id, symbol, entry, qty, sl, t1, t2, direction, invested = pos

            try:
                ticker = yf.Ticker(f"{symbol}.NS")
                hist = ticker.history(period="1d", interval="1m")
                if hist.empty:
                    continue

                curr_price = hist['Close'].iloc[-1]
                high = hist['High'].max()
                low = hist['Low'].min()

                exit_price = None
                reason = None

                if direction == "BULL":
                    if high >= t2:
                        exit_price = t2
                        reason = "Target 2 Hit"
                    elif high >= t1:
                        exit_price = t1
                        reason = "Target 1 Hit"
                    elif low <= sl:
                        exit_price = sl
                        reason = "Stop Loss Hit"
                else:
                    if low <= t2:
                        exit_price = t2
                        reason = "Bear Target 2"
                    elif low <= t1:
                        exit_price = t1
                        reason = "Bear Target 1"
                    elif high >= sl:
                        exit_price = sl
                        reason = "Stop Loss Hit"

                if exit_price:
                    exit_value = exit_price * qty
                    pnl = exit_value - invested
                    pnl_pct = (pnl / invested) * 100
                    is_win = 1 if pnl > 0 else 0

                    # Update position
                    cursor.execute('UPDATE user_positions SET status = ? WHERE id = ?', (reason, pos_id))

                    # Update portfolio
                    cursor.execute('''
                        UPDATE user_portfolios
                        SET current_balance = current_balance + ?, total_pnl = total_pnl + ?, winning_trades = winning_trades + ?
                        WHERE chat_id = ?
                    ''', (exit_value, pnl, is_win, str(chat_id)))

                    conn.commit()

                    closed.append({
                        "symbol": symbol,
                        "entry": entry,
                        "exit": exit_price,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "reason": reason,
                        "chat_id": chat_id
                    })

                    # Send Telegram alert
                    emoji = "🟢" if pnl > 0 else "🔴"
                    msg = (
                        f"{emoji} *PAPER TRADE CLOSED*\n\n"
                        f"📊 Symbol: *{symbol}*\n"
                        f"📍 Entry: ₹{entry} → Exit: ₹{exit_price}\n"
                        f"💰 P&L: *₹{pnl:.2f}* ({pnl_pct:+.2f}%)\n"
                        f"🏁 Reason: {reason}"
                    )
                    try:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=10)
                    except:
                        pass

            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")
                continue

        conn.close()
        return closed