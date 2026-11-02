"""
Full NSE/BSE Trading Bot with Autonomous Paper-Trading Agency
=================================================================
Features:
- Full NSE/BSE Stock Universe (2200+ stocks)
- Category-based market explorer with pagination
- Autonomous virtual fund (₹100,000) with auto-execution
- Self-healing brain (learns from losses)
- Live news sentinel (RSS feeds)
- EOD Report at 3:40 PM IST daily
- Universal search: /ANY_STOCK, /debate ANY_STOCK, or plain text
"""

import os
import sys
import requests
import yfinance as yf
import numpy as np
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from stock_universe import StockUniverse

# Import all institutional modules
from price_action import PriceActionAnalyzer
from mtf_analyzer import MTFAnalyzer
from chart_generator import ChartGenerator
from trade_logger import TradeLogger
from paper_fund_manager import PaperFundManager
from signal_tracker import SignalTracker
from self_evolution_brain import SelfEvolutionBrain
from live_news_sentinel import LiveNewsSentinel
from market_scanner import MarketScanner

TELEGRAM_BOT_TOKEN = "9089360235:AAGCTAesCisWR2soUzjrp4Suc8RwuOAi7G0"
TELEGRAM_CHAT_ID = "1729819060"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
IST = timezone('Asia/Kolkata')

# Global universe instance
stock_universe = StockUniverse()

# ================= HELPER FUNCTIONS =================
def send_message(chat_id, text, reply_markup=None):
    """Send message to Telegram"""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

def get_main_menu():
    """Main menu with all commands"""
    return {
        "inline_keyboard": [
            [
                {"text": "⚔️ Bull vs Bear Debate", "callback_data": "menu_debate"},
                {"text": "🏆 Verified Track Record", "callback_data": "cmd_trackrecord"}
            ],
            [
                {"text": "🎯 Win-Rate Audit", "callback_data": "cmd_winrate"},
                {"text": "🧠 AI Brain & Mistakes", "callback_data": "cmd_brain"}
            ],
            [
                {"text": "📰 Live News Radar", "callback_data": "cmd_news"},
                {"text": "📊 Market Scanner", "callback_data": "cmd_scan"}
            ],
            [
                {"text": "📋 EOD Report (3:40 PM)", "callback_data": "cmd_eod"},
                {"text": "💡 How to Use", "callback_data": "help_custom"}
            ]
        ]
    }

def get_category_buttons():
    """Category buttons for market explorer"""
    return {
        "inline_keyboard": [
            [
                {"text": "🔥 Nifty 50", "callback_data": "cat_NIFTY_50"},
                {"text": "🚀 Midcap", "callback_data": "cat_MIDCAP"},
                {"text": "🏦 Banking", "callback_data": "cat_BANKING"},
            ],
            [
                {"text": "💻 IT & Tech", "callback_data": "cat_IT"},
                {"text": "⚡ PSU & Defence", "callback_data": "cat_DEFENCE"},
                {"text": "🔤 Browse All A-Z", "callback_data": "cat_ALL"}
            ],
            [
                {"text": "🔙 Back to Main Menu", "callback_data": "main_menu"}
            ]
        ]
    }

def get_stock_list_buttons(stocks, page=1, total_pages=1, category="ALL"):
    """Generate pagination buttons for stock list"""
    keyboard = []
    row = []
    for stock in stocks:
        row.append({"text": f"[{stock['ticker']}]", "callback_data": f"stock_{stock['ticker']}"})
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Pagination row
    pagination = []
    if page > 1:
        pagination.append({"text": "⬅️ Prev", "callback_data": f"page_{category}_{page-1}"})
    pagination.append({"text": f"{page}/{total_pages}", "callback_data": "page_info"})
    if page < total_pages:
        pagination.append({"text": "Next ➡️", "callback_data": f"page_{category}_{page+1}"})
    keyboard.append(pagination)

    # Back button
    keyboard.append([{"text": "🔙 Back to Categories", "callback_data": "menu_debate"}])

    return {"inline_keyboard": keyboard}

def get_search_match_buttons(matches):
    """Generate inline buttons for multiple search matches"""
    keyboard = []
    row = []
    for match in matches[:8]:  # Max 8 matches inline
        row.append({"text": f"[{match['ticker']}]", "callback_data": f"stock_{match['ticker']}"})
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([{"text": "🔙 Cancel", "callback_data": "main_menu"}])
    return {"inline_keyboard": keyboard}

# ================= AUTONOMOUS DEBATE & EXECUTION =================
def run_autonomous_debate(chat_id, symbol):
    """Execute full AI debate with auto-execution if conditions met"""
    try:
        sym_clean = symbol.upper().replace(".NS", "").strip()
        if not sym_clean:
            send_message(chat_id, "❌ Invalid symbol. Please try again.")
            return

        ticker = yf.Ticker(f"{sym_clean}.NS")
        df = ticker.history(period="6mo", interval="1d")

        if df.empty or len(df) < 20:
            send_message(chat_id, f"❌ Stock `{sym_clean}` ka data nahi mila. Symbol sahi check karein.")
            return

        send_message(chat_id, f"⏳ *Running AI Hedge Fund Analysis for {sym_clean}...*")

        cmp = round(df['Close'].iloc[-1], 2)
        high = df['High']
        low = df['Low']
        close = df['Close']

        # Price Action & Evolved Rules Injection
        anatomy = PriceActionAnalyzer.calculate_candle_anatomy(df)
        pa_patterns = PriceActionAnalyzer.detect_patterns(df)
        indicators = PriceActionAnalyzer.calculate_indicators(df)
        evolved_rules = SelfEvolutionBrain.get_active_rules_for_prompt()

        # Multi-Timeframe Confluence Analysis
        mtf_data = MTFAnalyzer.fetch_mtf_data(sym_clean)
        mtf_result = MTFAnalyzer.calculate_alignment_score(mtf_data)

        # Volatility & Risk Levels
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
        atr = round(tr.rolling(14).mean().iloc[-1], 2)
        stop_loss = round(cmp - (1.8 * atr), 2)
        risk = cmp - stop_loss
        target1 = round(cmp + (1.5 * risk), 2)
        target2 = round(cmp + (2.5 * risk), 2)

        # Monte Carlo Win Probability
        daily_vol = (atr / cmp) / np.sqrt(252)
        sims = cmp * (1 + np.random.normal(0, daily_vol, 1000))
        win_prob = round((sims >= target1).mean() * 100, 1)

        # Scoring
        bull_score = 40 + pa_patterns["score_boost"] + (mtf_result["score"] * 10)
        bear_score = 50 - pa_patterns["score_boost"]

        if mtf_result["blocked"]:
            bear_score += 25
            mtf_warning = "\n⚠️ *MTF Conflict*: Timeframes misaligned!"
        else:
            mtf_warning = "\n✅ *MTF Alignment*: Timeframes aligned."

        pattern_str = ", ".join(pa_patterns["patterns"])
        vwap = indicators.get("vwap", cmp)

        if bull_score > bear_score:
            winner = "🐂 BULL WINS!"
            direction = "BULL"
            conviction = round((bull_score / (bull_score + bear_score)) * 100, 1)
            verdict_text = (
                f"✅ *VERDICT: EXECUTE LONG / BUY*\n"
                f"🎯 Entry: ₹{round(cmp*0.995, 2)} - ₹{round(cmp*1.002, 2)}\n"
                f"🛑 SL: *₹{stop_loss}* | T1: *₹{target1}* | T2: *₹{target2}*"
            )
        else:
            winner = "🐻 BEAR WINS!"
            direction = "BEAR"
            conviction = round((bear_score / (bull_score + bear_score)) * 100, 1)
            verdict_text = (
                f"⚠️ *VERDICT: AVOID / STAY AWAY*\n"
                f"🚫 Reason: Bear dominance or price rejection.\n"
                f"🛑 Invalidation: ₹{indicators.get('pdh', cmp)}"
            )

        # Log Trade & Issue Official Verified Signal if Conviction >= 65%
        TradeLogger.log_trade(sym_clean, cmp, stop_loss, target1, direction, winner, conviction)
        exec_status = ""
        signal_card_text = ""
        rr_ratio = round((target1 - cmp) / risk, 2) if risk > 0 else 1.5

        if conviction >= 65 and rr_ratio >= 1.5:
            sig = SignalTracker.publish_signal(sym_clean, cmp, stop_loss, target1, target2, direction, conviction, winner)
            exec_status = f"\n🏷️ *OFFICIAL SIGNAL ISSUED*: `{sig['signal_id']}` (Logged to Track Record)"
            signal_card_text = f"\n\n{sig['card_text']}"
        elif conviction >= 55:
            exec_status = f"\n⚠️ *Signal On Watchlist*: Conviction {conviction}% (Threshold: 65% for Verified Signal)"

        report = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚔️ *HEDGE FUND DEBATE: {sym_clean}* ⚔️\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *CMP*: ₹{cmp} | *VWAP*: ₹{vwap} | *ATR*: ₹{atr}\n"
            f"🕯️ *Candle*: Body {anatomy.get('bodyRatio',0)}, WickU {anatomy.get('upperWickRatio',0)}, WickL {anatomy.get('lowerWickRatio',0)}\n"
            f"📊 *Patterns*: {pattern_str}\n"
            f"{mtf_warning}\n\n"
            f"⚖️ *ARBITER*: {winner} (Conviction: {conviction}%)\n"
            f"{verdict_text}\n"
            f"{exec_status}"
            f"{signal_card_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

        # Generate Chart & Send
        send_message(chat_id, f"📊 *Generating Chart for {sym_clean}...*")
        chart_path = ChartGenerator.generate_chart(sym_clean, df, cmp, stop_loss, target1, target2)

        if chart_path and os.path.exists(chart_path):
            ChartGenerator.send_photo(chat_id, chart_path, report, reply_markup=get_main_menu())
            try:
                os.remove(chart_path)
            except:
                pass
        else:
            send_message(chat_id, report, reply_markup=get_main_menu())

    except Exception as e:
        send_message(chat_id, f"❌ Debate error: {str(e)}")

# ================= BACKGROUND WORKERS & SCHEDULERS =================
def start_background_workers(chat_id):
    """Start all background schedulers"""
    scheduler = BackgroundScheduler(timezone=IST)

    # 1. Monitor open positions every 2 minutes
    def portfolio_monitor():
        try:
            PaperFundManager.monitor_open_positions(chat_id)
        except Exception as e:
            print(f"Portfolio monitor error: {e}")

    # 2. Poll news every 3 minutes
    def news_radar():
        try:
            LiveNewsSentinel.fetch_live_news(chat_id)
        except Exception as e:
            print(f"News radar error: {e}")

    # 3. Auto-scan every 15 minutes during market hours
    def market_scanner_job():
        now = datetime.datetime.now(IST)
        market_start = now.replace(hour=9, minute=15, second=0)
        market_end = now.replace(hour=15, minute=30, second=0)
        if now.weekday() < 5 and market_start <= now <= market_end:
            try:
                MarketScanner.run_background_scan(chat_id)
            except Exception as e:
                print(f"Market scanner error: {e}")

    # 4. EOD Report at 3:40 PM IST daily
    def eod_report():
        try:
            send_eod_report(chat_id)
        except Exception as e:
            print(f"EOD report error: {e}")

    # Add jobs
    scheduler.add_job(portfolio_monitor, 'interval', minutes=2, id='portfolio_monitor')
    scheduler.add_job(news_radar, 'interval', minutes=3, id='news_radar')
    scheduler.add_job(market_scanner_job, 'cron', minute='*/15', id='market_scanner')
    scheduler.add_job(eod_report, 'cron', hour=15, minute=40, id='eod_report')

    scheduler.start()
    print("🚀 Background schedulers started: Portfolio(2m), News(3m), Scanner(15m), EOD(15:40)")

def send_eod_report(chat_id):
    """Send End-of-Day Portfolio & P&L Report"""
    wallet = PaperFundManager.get_wallet_summary()
    brain = SelfEvolutionBrain.get_brain_summary()
    perf = TradeLogger.evaluate_performance()

    now = datetime.datetime.now(IST).strftime('%Y-%m-%d')

    report = (
        f"📊 *EOD REPORT - {now}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{wallet}\n\n"
        f"🧠 *TODAY'S SELF-LEARNING*:\n{brain}\n\n"
        f"📈 *PERFORMANCE TRACKER*:\n{perf}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Tomorrow's Trading Strategy* will be adapted based on today's lessons."
    )
    send_message(chat_id, report, reply_markup=get_main_menu())

# ================= PAGINATION & STOCK LIST =================
def get_stocks_for_category_page(category, page=1, page_size=12):
    """Get stocks for a specific category page"""
    if category == "ALL":
        symbols = stock_universe.get_all_symbols()
        stocks = [{"ticker": s, "company": stock_universe._universe.get(s, {}).get('company', s), "sector": "ALL"}
                  for s in symbols]
    else:
        stocks = stock_universe.get_stocks_by_sector(category, limit=1000)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return stocks[start_idx:end_idx], (len(stocks) + page_size - 1) // page_size

def handle_search_query(chat_id, query):
    """Handle universal search - /ANY_STOCK or plain text"""
    matches = stock_universe.search_stocks(query, limit=8)

    if not matches:
        send_message(chat_id, f"❌ No stocks found matching '{query}'. Try a different spelling or ticker.",
                    reply_markup=get_main_menu())
        return

    if len(matches) == 1:
        # Single match - run debate directly
        run_autonomous_debate(chat_id, matches[0]['ticker'])
    else:
        # Multiple matches - show options
        msg = f"🔍 *Found {len(matches)} matches for '{query}'*:\nTap a stock to analyze:"
        send_message(chat_id, msg, reply_markup=get_search_match_buttons(matches))

# ================= MAIN MESSAGE HANDLER =================
def handle_updates():
    global stock_universe
    offset = 0

    # Load stock universe on startup
    try:
        stock_universe.load_universe()
        print(f"📊 Loaded {len(stock_universe.get_all_symbols())} stocks into universe")
    except Exception as e:
        print(f"Warning: Could not load stock universe: {e}")

    print("🚀 Autonomous AI Hedge Fund Bot Active...")

    startup_msg = (
        "🚀 *NEW UPDATED BOT IS STARTED!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *Verified Signal Track Record Engine*\n"
        "✅ *Full NSE/BSE Universe* (2200+ stocks)\n"
        "✅ *Self-Evolution Brain* (learns from losses)\n"
        "✅ *Live News Radar* (RSS feeds)\n"
        "✅ *EOD Report* (Daily 3:40 PM IST)\n\n"
        "📋 *Available Commands*:\n"
        "• `/start` - Main menu\n"
        "• `/trackrecord` - Verified signal audit\n"
        "• `/winrate` - Win-rate dashboard\n"
        "• `/brain` - AI learned mistakes\n"
        "• `/news` - Breaking market news\n"
        "• `/scan` - Market scanner status\n"
        "• `/performance` - Trade audit report\n"
        "• `/eod` - End-of-day report\n"
        "• `/debate SYMBOL` - Full analysis\n"
        "• Type ANY stock name for instant analysis\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    send_message(TELEGRAM_CHAT_ID, startup_msg, reply_markup=get_main_menu())

    # Start background workers
    try:
        start_background_workers(TELEGRAM_CHAT_ID)
    except Exception as e:
        print(f"Scheduler start error: {e}")

    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=30"
            res = requests.get(url, timeout=35).json()

            for update in res.get("result", []):
                offset = update["update_id"] + 1

                # Callback queries (button clicks)
                if "callback_query" in update:
                    cq = update["callback_query"]
                    chat_id = cq["message"]["chat"]["id"]
                    data = cq["data"]

                    if data == "main_menu":
                        send_message(chat_id, "Main Menu:", reply_markup=get_main_menu())

                    elif data == "menu_debate":
                        send_message(
                            chat_id,
                            "⚔️ *SELECT STOCK CATEGORY*:\nChoose a category to browse stocks:",
                            reply_markup=get_category_buttons()
                        )

                    elif data == "cmd_trackrecord":
                        send_message(chat_id, SignalTracker.get_track_record_summary(), reply_markup=get_main_menu())

                    elif data == "cmd_winrate":
                        send_message(chat_id, SignalTracker.get_track_record_summary(), reply_markup=get_main_menu())

                    elif data == "cmd_brain":
                        send_message(chat_id, SelfEvolutionBrain.get_brain_summary(), reply_markup=get_main_menu())

                    elif data == "cmd_news":
                        send_message(chat_id, LiveNewsSentinel.get_recent_news_summary(), reply_markup=get_main_menu())

                    elif data == "cmd_scan":
                        send_message(chat_id, MarketScanner.get_market_summary(), reply_markup=get_main_menu())

                    elif data == "cmd_performance":
                        send_message(chat_id, TradeLogger.evaluate_performance(), reply_markup=get_main_menu())

                    elif data == "cmd_eod":
                        send_eod_report(chat_id)

                    elif data == "help_custom":
                        help_text = (
                            "💡 *BOT COMMANDS GUIDE*\n"
                            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            "📊 *Analysis Commands:*\n"
                            "• `/debate SYMBOL` - Full Bull vs Bear analysis\n"
                            "• Type stock name directly (e.g., `RELIANCE`, `TCS`)\n"
                            "• Browse via category menu\n\n"
                            "🏆 *Track Record & Performance:*\n"
                            "• `/trackrecord` - Verified signal ledger\n"
                            "• `/winrate` - Win-rate audit dashboard\n"
                            "• `/performance` - Trade audit report\n\n"
                            "🧠 *Brain & Learning:*\n"
                            "• `/brain` - View AI learned rules\n"
                            "• `/mistakes` - Same as /brain\n\n"
                            "📰 *News & Market:*\n"
                            "• `/news` - Breaking market news\n"
                            "• `/scan` - Market scanner status\n"
                            "• `/eod` - End-of-day report\n\n"
                            "━━━━━━━━━━━━━━━━━━━━━━\n"
                            "💡 Signals with conviction ≥65% are logged automatically!"
                        )
                        send_message(chat_id, help_text, reply_markup=get_main_menu())

                    # Category selection
                    elif data.startswith("cat_"):
                        category = data.replace("cat_", "")
                        stocks, total_pages = get_stocks_for_category_page(category, page=1)
                        stock_list = "\n".join([f"• {s['ticker']}" for s in stocks])
                        send_message(
                            chat_id,
                            f"📊 *{category.replace('_', ' ')} Stocks* (Page 1/{total_pages}):\n\n{stock_list}",
                            reply_markup=get_stock_list_buttons(stocks, 1, total_pages, category)
                        )

                    # Pagination
                    elif data.startswith("page_"):
                        parts = data.split("_")
                        if len(parts) >= 3:
                            category = parts[1]
                            page = int(parts[2])
                            stocks, total_pages = get_stocks_for_category_page(category, page)
                            stock_list = "\n".join([f"• {s['ticker']}" for s in stocks])
                            send_message(
                                chat_id,
                                f"📊 *{category.replace('_', ' ')} Stocks* (Page {page}/{total_pages}):\n\n{stock_list}",
                                reply_markup=get_stock_list_buttons(stocks, page, total_pages, category)
                            )

                    # Stock selection from list
                    elif data.startswith("stock_"):
                        ticker = data.replace("stock_", "")
                        run_autonomous_debate(chat_id, ticker)

                    elif data == "page_info":
                        send_message(chat_id, "📊 Use Prev/Next buttons to browse more stocks.", reply_markup=get_main_menu())

                # Text messages
                elif "message" in update and "text" in update["message"]:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg["text"].strip()

                    if text.startswith("/start"):
                        send_message(chat_id, "🤖 *Welcome back! Chat ID registered.*", reply_markup=get_main_menu())

                    elif text.startswith("/trackrecord") or text.startswith("/winrate"):
                        send_message(chat_id, SignalTracker.get_track_record_summary(), reply_markup=get_main_menu())

                    elif text.startswith("/wallet"):
                        send_message(chat_id, SignalTracker.get_track_record_summary(), reply_markup=get_main_menu())

                    elif text.startswith("/brain") or text.startswith("/mistakes"):
                        send_message(chat_id, SelfEvolutionBrain.get_brain_summary(), reply_markup=get_main_menu())

                    elif text.startswith("/news"):
                        send_message(chat_id, "⏳ *Polling live news feeds...*")
                        alerts = LiveNewsSentinel.fetch_live_news(chat_id)
                        if not alerts:
                            send_message(chat_id, "No new breaking news at this time.", reply_markup=get_main_menu())

                    elif text.startswith("/scan"):
                        send_message(chat_id, MarketScanner.get_market_summary(), reply_markup=get_main_menu())

                    elif text.startswith("/performance"):
                        send_message(chat_id, TradeLogger.evaluate_performance(), reply_markup=get_main_menu())

                    elif text.startswith("/eod"):
                        send_eod_report(chat_id)

                    elif text.startswith("/debate") or text.startswith("/analyze"):
                        parts = text.split()
                        if len(parts) > 1:
                            handle_search_query(chat_id, parts[1])
                        else:
                            send_message(chat_id, "Usage: /debate SYMBOL or /analyze SYMBOL", reply_markup=get_main_menu())

                    else:
                        # Universal search - treat as stock query
                        clean_text = text.replace("/", "").strip()
                        if clean_text:
                            handle_search_query(chat_id, clean_text)

        except Exception as e:
            print(f"Error in handle_updates: {e}")
            pass

if __name__ == "__main__":
    handle_updates()