"""
Angel One SmartAPI Configuration
DO NOT share this file! Keep it secure.

To use:
1. Get your API Key and Secret from Angel One Developer Portal
2. Add your API Key, Secret, and User ID below
3. This file is gitignored by default
"""

# ========== ANGEL ONE CREDENTIALS ==========
# Get these from: https://mapi.tradeangel.com/developer/console
ANGEL_API_KEY = ""          # Your API Key (from Angel One)
ANGEL_API_SECRET = ""       # Your Secret Key (from Angel One)
ANGEL_USER_ID = ""          # Your Angel One User ID
ANGEL_PASSWORD = ""         # Your Angel One Password

# =========== TRADING SETTINGS ==============
# These control your agent's behavior
DEFAULT_CAPITAL = 100000        # Default capital for position sizing (₹)
DEFAULT_RISK_PERCENT = 1.0      # Default risk per trade (%)
MAX_DAILY_LOSS = 5000           # Max loss limit per day (₹)
MAX_TRADES_PER_DAY = 10         # Max trades allowed per day
AUTO_SQUARE_OFF_TIME = "15:10"  # Time to auto-square off intraday positions

# =========== INSTRUMENT SETTINGS ============
# Which markets do you trade?
ENABLE_EQUITY = True        # Delivery/Intraday equity
ENABLE_FNO = True           # Futures & Options
ENABLE_MF = False           # Mutual Funds

# =========== STRATEGY SETTINGS ==============
# Default strategy parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
MA_SHORT = 20
MA_LONG = 50
STOPLOSS_MULTIPLIER = 2.0   # ATR multiplier for stop loss
TAKEPROFIT_RATIO = 2.5      # Target/Risk ratio
