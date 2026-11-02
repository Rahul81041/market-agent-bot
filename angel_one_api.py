"""
Angel One SmartAPI Client
Connects to Angel One SmartAPI for trading operations.

Install required package first:
pip install requests python-dotenv

Usage:
1. Fill in your credentials in angel_one_config.py
2. This client handles authentication and API calls
"""

import requests
import time
import hashlib
import hmac
import base64
import json
from datetime import datetime
from typing import Optional, Dict, Any
import os
import sys

# Import config
config_path = os.path.join(os.path.dirname(__file__), 'angel_one_config.py')
if os.path.exists(config_path):
    sys.path.insert(0, os.path.dirname(__file__))
    from angel_one_config import (
        ANGEL_API_KEY,
        ANGEL_API_SECRET,
        ANGEL_USER_ID,
        ANGEL_PASSWORD
    )

# Angel One API Endpoints
API_BASE_URL = "https://mapi.tradeangel.com"
API_LOGIN = "/v1/session/login"
API_TOKEN = "/v1/session/token"
API_PROFILE = "/v1/user/profile"
API_BALANCE = "/v1/margins/equity"
API_POSITIONS = "/v1/positions"
API_ORDERS = "/v1/orders"
API_PLACE_ORDER = "/v1/orders"
API_CANCEL_ORDER = "/v1/orders/{order_id}"
API_HOLDINGS = "/v1/holdings"

class AngelOneClient:
    """Client for Angel One SmartAPI"""

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or ANGEL_API_KEY
        self.api_secret = api_secret or ANGEL_API_SECRET
        self.user_id = ANGEL_USER_ID
        self.password = ANGEL_PASSWORD

        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-User-Type': 'User',
            'X-Product-Type': 'PRO'
        })

        self.session_token = None
        self.public_token = None
        self.is_authenticated = False

    def generate_session_token(self, api_secret: str, timestamp: str) -> str:
        """Generate session token using HMAC-SHA256"""
        message = timestamp + self.api_key
        signature = hmac.new(
            api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def login(self) -> bool:
        """Login to Angel One API and get session token"""
        if not self.api_key or not self.api_secret:
            print("❌ Error: API Key or Secret not configured!")
            print("Please edit angel_one_config.py and add your credentials.")
            return False

        timestamp = str(int(time.time()))
        password = hashlib.sha256(
            (self.password + self.api_key + timestamp).encode()
        ).hexdigest()

        payload = {
            "clientcode": self.user_id,
            "password": password,
            "totp": "",  # Add if you have 2FA enabled
            "timestamp": timestamp,
            "source": "API"
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_LOGIN}",
                json=payload,
                timeout=30
            )
            data = response.json()

            if data.get('status') == 'success':
                self.session_token = data.get('data', {}).get('sessiontoken')
                self.public_token = data.get('data', {}).get('publictoken')

                if self.session_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.session_token}'
                    })
                    self.is_authenticated = True
                    print("✅ Successfully logged in to Angel One!")
                    return True
                else:
                    print(f"❌ Login failed: No session token received")
                    return False
            else:
                print(f"❌ Login failed: {data.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def get_profile(self) -> Optional[Dict]:
        """Get user profile"""
        if not self.is_authenticated:
            if not self.login():
                return None

        try:
            response = self.session.get(f"{API_BASE_URL}{API_PROFILE}")
            return response.json()
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None

    def get_balance(self) -> Optional[Dict]:
        """Get available margin and balance"""
        if not self.is_authenticated:
            if not self.login():
                return None

        try:
            response = self.session.get(f"{API_BASE_URL}{API_BALANCE}")
            data = response.json()

            if data.get('status') == 'success':
                return data.get('data', {})
            return None
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None

    def get_positions(self) -> Optional[Dict]:
        """Get current positions"""
        if not self.is_authenticated:
            if not self.login():
                return None

        try:
            response = self.session.get(f"{API_BASE_URL}{API_POSITIONS}")
            data = response.json()

            if data.get('status') == 'success':
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return None

    def get_holdings(self) -> Optional[Dict]:
        """Get holdings"""
        if not self.is_authenticated:
            if not self.login():
                return None

        try:
            response = self.session.get(f"{API_BASE_URL}{API_HOLDINGS}")
            data = response.json()

            if data.get('status') == 'success':
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error fetching holdings: {e}")
            return None

    def get_orders(self) -> Optional[Dict]:
        """Get order book"""
        if not self.is_authenticated:
            if not self.login():
                return None

        try:
            response = self.session.get(f"{API_BASE_URL}{API_ORDERS}")
            data = response.json()

            if data.get('status') == 'success':
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return None

    def place_order(
        self,
        symbol: str,
        qty: int,
        price: float = 0,
        order_type: str = "BUY",
        product_type: str = "MIS",
        exchange: str = "NSE"
    ) -> Optional[Dict]:
        """Place an order

        order_type: BUY, SELL
        product_type: MIS (Intraday), NRML (Delivery), CNC (Cash and Carry)
        exchange: NSE, BSE
        """
        if not self.is_authenticated:
            if not self.login():
                return None

        payload = {
            "symbol": symbol,
            "exchange": exchange,
            "transaction_type": order_type.upper(),
            "quantity": qty,
            "order_type": "LIMIT" if price > 0 else "MARKET",
            "price": price if price > 0 else 0,
            "product_type": product_type.upper(),
            "trigger_price": 0,
            "disclosed_quantity": 0,
            "validity": "DAY",
            "tag": "TRADING_AGENT"
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}{API_PLACE_ORDER}",
                json=payload,
                timeout=30
            )
            data = response.json()
            return data
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def cancel_order(self, order_id: str) -> Optional[Dict]:
        """Cancel an order"""
        if not self.is_authenticated:
            if not self.login():
                return None

        try:
            response = self.session.delete(
                f"{API_BASE_URL}{API_CANCEL_ORDER.format(order_id=order_id)}"
            )
            return response.json()
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return None

    def square_off_all(self) -> Dict[str, Any]:
        """Square off all intraday positions"""
        if not self.is_authenticated:
            if not self.login():
                return {"status": "error", "message": "Not authenticated"}

        positions = self.get_positions()
        if not positions:
            return {"status": "error", "message": "No positions found"}

        results = []
        for pos in positions:
            if pos.get('product_type') == 'MIS':  # Intraday position
                qty = pos.get('quantity', 0)
                if qty > 0:
                    order_type = "SELL" if pos.get('order_type') == "BUY" else "BUY"
                    result = self.place_order(
                        symbol=pos.get('symbol'),
                        qty=qty,
                        order_type=order_type,
                        product_type="MIS",
                        exchange=pos.get('exchange')
                    )
                    results.append(result)

        return {"status": "success", "message": f"Square off initiated for {len(results)} positions", "results": results}

    def get_live_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """Get live market price for a symbol"""
        # Use NSE India API for price lookup
        try:
            # For NSE symbols
            symbol_clean = symbol.replace("-EQ", "").replace(".NS", "")
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol_clean}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data and 'priceInfo' in data:
                return data['priceInfo'].get('lastPrice')
            return None
        except Exception as e:
            print(f"Error getting price: {e}")
            return None


# Example usage
if __name__ == "__main__":
    client = AngelOneClient()

    if client.login():
        print("\n--- Account Info ---")
        profile = client.get_profile()
        print(f"Profile: {profile}")

        print("\n--- Balance ---")
        balance = client.get_balance()
        print(f"Balance: {balance}")

        print("\n--- Positions ---")
        positions = client.get_positions()
        print(f"Positions: {positions}")

        print("\n--- Orders ---")
        orders = client.get_orders()
        print(f"Orders: {orders}")
    else:
        print("❌ Login failed. Please check your credentials in angel_one_config.py")
