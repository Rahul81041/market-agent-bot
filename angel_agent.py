"""
Personal Trading Agent (Angel One Integration)
CLI Interface for managing your trading account, analyzing stocks, and executing orders.

Usage:
python angel_agent.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from angel_one_api import AngelOneClient

def print_banner():
    print("""
    ======================================================
    🤖 ANGEL ONE PERSONAL TRADING AGENT v1.0
    ======================================================
    1. Check Account Balance & Margin
    2. View Open Positions & Holdings
    3. View Today's Order Book
    4. Run Ultra Analysis (Stock Finder + Deep Analysis)
    5. Place Trade Order (Semi-Auto / Manual)
    6. Square Off All Intraday Positions (Emergency Exit)
    7. Test API Connection
    8. Exit
    ======================================================
    """)

def main():
    client = AngelOneClient()

    while True:
        print_banner()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            print("\n🔄 Fetching account balance...")
            balance = client.get_balance()
            if balance:
                print(f"💰 Account Balance / Margin: {balance}")
            else:
                print("❌ Could not fetch balance. Check your login credentials in angel_one_config.py")

        elif choice == "2":
            print("\n🔄 Fetching open positions & holdings...")
            positions = client.get_positions()
            holdings = client.get_holdings()
            print(f"📊 Positions: {positions}")
            print(f"📦 Holdings: {holdings}")

        elif choice == "3":
            print("\n🔄 Fetching order book...")
            orders = client.get_orders()
            print(f"📋 Orders: {orders}")

        elif choice == "4":
            print("\n🔍 Running Stock Analysis & Ultra Wizard...")
            print("To run deep analysis, use the wizard skill or type:")
            print("  /indian-trading-wizard")
            print("  /indian-trading-ultra [STOCK] [CAPITAL] [RISK%]")

        elif choice == "5":
            print("\n🛒 Place Trade Order (Semi-Auto)")
            symbol = input("Enter stock symbol (e.g., RELIANCE): ").strip().upper()
            qty = int(input("Enter quantity: ").strip())
            order_type = input("Order type (BUY/SELL): ").strip().upper()
            product = input("Product type (MIS for Intraday / NRML for Delivery): ").strip().upper()
            price = float(input("Limit price (0 for Market order): ").strip() or "0")

            confirm = input(f"⚠️ Confirm {order_type} {qty} shares of {symbol} at {'Market' if price==0 else price}? (y/n): ").strip().lower()
            if confirm == 'y':
                print(f"🚀 Placing order...")
                result = client.place_order(symbol=symbol, qty=qty, price=price, order_type=order_type, product_type=product)
                print(f"Result: {result}")
            else:
                print("❌ Order cancelled.")

        elif choice == "6":
            confirm = input("⚠️ WARNING: Square off ALL intraday positions? (yes/no): ").strip().lower()
            if confirm == 'yes':
                print("🚨 Squaring off all MIS positions...")
                result = client.square_off_all()
                print(result)
            else:
                print("❌ Cancelled.")

        elif choice == "7":
            print("\n🔌 Testing connection to Angel One...")
            if client.login():
                print("✅ Connection successful!")
            else:
                print("❌ Connection failed. Please check angel_one_config.py")

        elif choice == "8":
            print("👋 Exiting Personal Trading Agent. Happy trading!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 8.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
