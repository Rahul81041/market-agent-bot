"""
Real-Time Market News & Shock Radar (`live_news_sentinel.py`)
Scrapes live RSS feeds from Indian financial sources every 3 minutes,
detects critical breaking headlines, identifies affected tickers, and pushes alerts to Telegram.
STRICTLY NO MOCK DATA - Only real live feeds.
"""

import feedparser
import sqlite3
import requests
import re
import os
from datetime import datetime
from pytz import timezone

DB_NAME = "trades.db"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
IST = timezone('Asia/Kolkata')

# Real Indian financial RSS feeds
RSS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "https://www.livemint.com/rss/markets",
    "https://news.google.com/rss/search?q=NSE+India+stock+market&hl=en-IN&gl=IN&ceid=IN:en"
]

# Critical keywords that trigger alerts
CRITICAL_KEYWORDS = [
    "earnings", "profit", "loss", "order win", "contract", "block deal",
    "rbi", "sebi", "policy", "rate cut", "rate hike", "repo rate",
    "crash", "plunge", "surge", "rally", "upper circuit", "lower circuit",
    "geopolitical", "war", "election", "budget", "gst", "acquisition",
    "merger", "buyback", "dividend", "results", "quarterly", "annual general meeting"
]

# Common NSE stock name patterns
NSE_TICKER_PATTERNS = [
    r'\b(RELIANCE|TCS|INFY|HDFCBANK|ICICIBANK|SBIN|TATAMOTORS|TATASTEEL|BHARTIARTL|HINDUNILVR|ITC|KOTAKBANK|LT|AXISBANK|BAJFINANCE|MARUTI|ASIANPAINT|HCLTECH|WIPRO|SUNPHARMA|ULTRACEMCO|NTPC|POWERGRID|TITAN|INDUSINDBK|TECHM|NESTLEIND|GRASIM|CIPLA|BAJAJFINSV|HEROMOTOCO|DRREDDY|SHREECEM|BRITANNIA|EICHERMOT|ADANIENT|ADANIPORTS|APOLLOHOSP|DMART|ZEEL|GODREJCP|DABUR|MARICO|BPCL|ONGC|COALINDIA|SBILIFE|HDFCLIFE|ICICIGI|ICICIPRULI|PIIND|SRF|MUTHOOTFIN|BANDHANBNK|AUBANK|IDFCFIRSTB|PNB|BANKBARODA|CANBK|UNIONBANK|INDIANB|JINDALSTEL|JSWSTEEL|TATASTEEL|HINDALCO|VEDL|ADANITOTAL|ADANIGREEN|ADANITRANS|ADANIPOWER)\b'
]

class LiveNewsSentinel:

    @staticmethod
    def init_db():
        """Initialize news_headlines table for deduplication."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_headlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT UNIQUE,
                link TEXT,
                source TEXT,
                processed INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def is_duplicate(title):
        """Check if headline already processed."""
        LiveNewsSentinel.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM news_headlines WHERE title = ?', (title,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def save_headline(title, link, source):
        """Save headline to prevent re-processing."""
        LiveNewsSentinel.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO news_headlines (title, link, source) VALUES (?, ?, ?)', (title, link, source))
            conn.commit()
        except:
            pass  # Duplicate, ignore
        conn.close()

    @staticmethod
    def extract_tickers(text):
        """Extract NSE ticker symbols from news text."""
        tickers = set()
        text_upper = text.upper()

        for pattern in NSE_TICKER_PATTERNS:
            matches = re.findall(pattern, text_upper)
            tickers.update(matches)

        return list(tickers)

    @staticmethod
    def is_critical(text):
        """Check if headline contains critical keywords."""
        text_lower = text.lower()
        for keyword in CRITICAL_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    @staticmethod
    def fetch_live_news(chat_id=None):
        """Fetch and process live RSS feeds. Returns breaking alerts."""
        alerts = []

        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url, timeout=15)
                source = feed.feed.get('title', 'Unknown')

                for entry in feed.entries[:10]:  # Process last 10 headlines
                    title = entry.get('title', '')
                    link = entry.get('link', '')

                    if not title or LiveNewsSentinel.is_duplicate(title):
                        continue

                    # Check if critical
                    is_crit = LiveNewsSentinel.is_critical(title)
                    tickers = LiveNewsSentinel.extract_tickers(title)

                    if is_crit or tickers:
                        # Save headline
                        LiveNewsSentinel.save_headline(title, link, source)

                        # Determine urgency
                        urgency = "🚨 BREAKING" if is_crit else "📰 MARKET NEWS"

                        # Fetch live price for affected tickers
                        price_info = ""
                        if tickers:
                            first_ticker = tickers[0]
                            try:
                                import yfinance as yf
                                stock = yf.Ticker(f"{first_ticker}.NS")
                                data = stock.history(period="1d")
                                if not data.empty:
                                    price = round(data['Close'].iloc[-1], 2)
                                    price_info = f"\n💰 *Live Price*: {first_ticker} @ ₹{price}"
                            except:
                                pass

                        alert = {
                            "urgency": urgency,
                            "title": title,
                            "link": link,
                            "source": source,
                            "tickers": tickers,
                            "price_info": price_info
                        }
                        alerts.append(alert)

                        # Push to Telegram
                        if chat_id:
                            LiveNewsSentinel.send_news_alert(chat_id, alert)
            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")
                continue

        return alerts

    @staticmethod
    def send_news_alert(chat_id, alert):
        """Send breaking news alert to Telegram."""
        tickers_str = ", ".join(alert["tickers"]) if alert["tickers"] else "Market-wide"

        msg = (
            f"{alert['urgency']} *MARKET ALERT*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📰 *{alert['title']}*\n\n"
            f"📊 *Affected Tickers*: {tickers_str}"
            f"{alert['price_info']}\n"
            f"🔗 [Read Full Article]({alert['link']})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ {datetime.now(IST).strftime('%H:%M:%S IST')}"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass

    @staticmethod
    def get_recent_news_summary(limit=5):
        """Return recent news for /news command."""
        LiveNewsSentinel.init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, source, timestamp
            FROM news_headlines
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        news = cursor.fetchall()
        conn.close()

        if not news:
            return "📰 No recent news captured yet. Run `/news` to fetch live headlines."

        summary = f"📰 *RECENT MARKET NEWS*\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for title, source, ts in news:
            time_str = ts.split()[1][:5] if ' ' in ts else ts[:5]
            summary += f"• [{time_str}] {title[:80]}...\n"

        summary += "━━━━━━━━━━━━━━━━━━━━━━"
        return summary
