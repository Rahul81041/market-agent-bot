"""
Telegram Visual Chart & Dark-Mode Candlestick Generator
Generates dark-mode charts with mplfinance showing last 60 candles, EMAs, VWAP,
and horizontal lines for Entry, Stop-Loss, and Targets.
"""

import os
import requests

TELEGRAM_BOT_TOKEN = "9089360235:AAGCTAesCisWR2soUzjrp4Suc8RwuOAi7G0"

# Graceful optional import for matplotlib / mplfinance
try:
    import matplotlib
    matplotlib.use('Agg') # Non-interactive backend
    import mplfinance as mpf
    CHART_LIBS_AVAILABLE = True
except ImportError:
    CHART_LIBS_AVAILABLE = False

class ChartGenerator:
    @staticmethod
    def generate_chart(symbol, df, entry, sl, t1, t2):
        """
        Generates a dark-mode candlestick chart for the last 60 candles with key levels.
        Saves to a temp PNG and returns the file path.
        """
        if not CHART_LIBS_AVAILABLE:
            print("matplotlib or mplfinance not installed. Please run: pip install matplotlib mplfinance")
            return None

        try:
            sym_clean = symbol.upper().replace(".NS", "")

            # Take last 60 candles
            chart_df = df.tail(60).copy()
            if chart_df.empty or len(chart_df) < 10:
                return None

            # Ensure proper datetime index and OHLCV columns
            chart_df.columns = [col.capitalize() for col in chart_df.columns]
            if 'Date' in chart_df.columns:
                chart_df.set_index('Date', inplace=True)

            # Calculate EMAs for plotting
            ema20 = chart_df['Close'].ewm(span=20).mean()
            ema50 = chart_df['Close'].ewm(span=50).mean()

            # Custom dark style
            mc = mpf.make_marketcolors(
                up='#00ffcc', down='#ff3366',
                edge='inherit',
                wick={'up':'#00ffcc', 'down':'#ff3366'},
                volume='in'
            )
            s = mpf.make_mpf_style(
                marketcolors=mc,
                base_mpf_style='nightclouds',
                facecolor='#121212',
                figcolor='#1e1e1e',
                gridcolor='#2c2c2c',
                gridstyle='--',
                rc={'font.size': 10}
            )

            # Additional plots (EMAs)
            addplots = [
                mpf.make_plot(ema20, color='#ff9900', width=1.2, secondary_y=False),
                mpf.make_plot(ema50, color='#3399ff', width=1.2, secondary_y=False)
            ]

            # Horizontal lines for entry, SL, T1, T2
            hlines = dict(
                hlines=[entry, sl, t1, t2],
                colors=['#00ffcc', '#ff3366', '#33cc33', '#33cc33'],
                linestyle='--',
                linewidths=1.2
            )

            filename = f"chart_{sym_clean}.png"
            filepath = os.path.abspath(filename)

            mpf.plot(
                chart_df,
                type='candle',
                style=s,
                volume=True,
                addplot=addplots,
                hlines=hlines,
                title=f"\n{sym_clean} Institutional Setup (20 EMA: Orange | 50 EMA: Blue)",
                ylabel='Price (INR)',
                ylabel_lower='Volume',
                savefig=dict(fname=filepath, dpi=150, bbox_inches='tight')
            )

            return filepath
        except Exception as e:
            print(f"Error generating chart for {symbol}: {e}")
            return None

    @staticmethod
    def send_photo(chat_id, image_path, caption, reply_markup=None):
        """Sends photo with caption using Telegram sendPhoto API."""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        try:
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': caption[:1024],  # Telegram caption limit
                    'parse_mode': 'Markdown'
                }
                if reply_markup:
                    import json
                    data['reply_markup'] = json.dumps(reply_markup)

                res = requests.post(url, files=files, data=data, timeout=20)
                return res.status_code == 200
        except Exception as e:
            print(f"Error sending photo to Telegram: {e}")
            return False

    @staticmethod
    def get_chart_inline_keyboard(symbol):
        """Returns inline keyboard buttons required by user requirements."""
        return {
            "inline_keyboard": [
                [
                    {"text": "📊 MTF Breakdown", "callback_data": f"mtf_{symbol}"},
                    {"text": "🕯️ Candle Anatomy", "callback_data": f"anatomy_{symbol}"}
                ],
                [
                    {"text": "📌 Track Paper Trade", "callback_data": f"track_{symbol}"}
                ],
                [
                    {"text": "🔙 Main Menu", "callback_data": "main_menu"}
                ]
            ]
        }
