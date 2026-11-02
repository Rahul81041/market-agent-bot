"""
Full NSE/BSE Listed Stock Universe (`stock_universe.py`)
Downloads, caches, and provides fuzzy search for 2000+ Indian stocks across sectors.
"""

import csv
import os
import json
import requests
import time
from datetime import datetime
import difflib  # Using difflib instead of fuzzysearch for built-in fuzzy matching

CSV_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
LOCAL_CACHE = "nse_equity_list.csv"
NSE_CACHE_EXPIRY = 3600 * 24 * 7  # 7 days

class StockUniverse:
    def __init__(self):
        self._universe = {}
        self._nse_to_bse = {
            'RELIANCE': 'RELIANCE', 'TCS': 'TCS', 'HDFCBANK': 'HDFCBANK', 'INFY': 'INFY',
            'ICICIBANK': 'ICICIBANK', 'SBIN': 'SBIN', 'TATAMOTORS': 'TATAMOTORS',
            'BHARTIARTL': 'BHARTIARTL', 'HINDUNILVR': 'HINDUNILVR', 'ITC': 'ITC',
            'KOTAKBANK': 'KOTAKBANK', 'LT': 'LT', 'AXISBANK': 'AXISBANK', 'BAJFINANCE': 'BAJFINANCE',
            'MARUTI': 'MARUTI', 'ASIANPAINT': 'ASIANPAINT', 'HCLTECH': 'HCLTECH', 'WIPRO': 'WIPRO',
            'SUNPHARMA': 'SUNPHARMA', 'ULTRACEMCO': 'ULTRACEMCO', 'NTPC': 'NTPC', 'POWERGRID': 'POWERGRID',
            'TITAN': 'TITAN', 'INDUSINDBK': 'INDUSINDBK', 'TECHM': 'TECHM', 'NESTLEIND': 'NESTLEIND',
            'GRASIM': 'GRASIM', 'CIPLA': 'CIPLA', 'BAJAJFINSV': 'BAJAJFINSV', 'HEROMOTOCO': 'HEROMOTOCO',
            'DRREDDY': 'DRREDDY', 'SHREECEM': 'SHREECEM', 'BRITANNIA': 'BRITANNIA', 'EICHERMOT': 'EICHERMOT',
            'ADANIENT': 'ADANIENT', 'ADANIPORTS': 'ADANIPORTS', 'APOLLOHOSP': 'APOLLOHOSP',
            'DMART': 'DMART', 'ZEEL': 'ZEEL', 'GODREJCP': 'GODREJCP', 'DABUR': 'DABUR', 'MARICO': 'MARICO',
            'BPCL': 'BPCL', 'ONGC': 'ONGC', 'COALINDIA': 'COALINDIA', 'SBILIFE': 'SBILIFE',
            'HDFCLIFE': 'HDFCLIFE', 'ICICIGI': 'ICICIGI', 'ICICIPRULI': 'ICICIPRULI', 'PIIND': 'PIIND',
            'SRF': 'SRF', 'MUTHOOTFIN': 'MUTHOOTFIN', 'BANDHANBNK': 'BANDHANBNK', 'AUBANK': 'AUBANK',
            'IDFCFIRSTB': 'IDFCFIRSTB', 'PNB': 'PNB', 'BANKBARODA': 'BANKBARODA', 'CANBK': 'CANBK',
            'UNIONBANK': 'UNIONBANK', 'INDIANB': 'INDIANB', 'JINDALSTEL': 'JINDALSTEL', 'JSWSTEEL': 'JSWSTEEL',
            'TATASTEEL': 'TATASTEEL', 'HINDALCO': 'HINDALCO', 'VEDL': 'VEDL', 'ADANITOTAL': 'ADANITOTAL',
            'ADANIGREEN': 'ADANIGREEN', 'ADANITRANS': 'ADANITRANS', 'ADANIPOWER': 'ADANIPOWER',
            'TATAPOWER': 'TATAPOWER', 'TATACONSUMER': 'TATACONSUMER', 'TATACOFFEE': 'TATACOFFEE',
            'TATACONSUM': 'TATACONSUM', 'TCS': 'TCS', 'INFY': 'INFY', 'WIPRO': 'WIPRO', 'LTIM': 'LTIM',
            'COFINDIA': 'COFINDIA', 'BSE': 'BSE', 'NIFTY': 'NIFTY', 'BANKNIFTY': 'BANKNIFTY',
            'FINNIFTY': 'FINNIFTY', 'MIDCPNIFTY': 'MIDCPNIFTY', 'NIFTYBEES': 'NIFTYBEES', 'JETAIRWAYS': 'JETAIRWAYS',
            'VOLTAS': 'VOLTAS', 'TORNTPHARM': 'TORNTPHARM', 'LUPIN': 'LUPIN', 'CIPLA': 'CIPLA', 'DRREDDY': 'DRREDDY',
            'SUNPHARMA': 'SUNPHARMA', 'LARSEN': 'LARSEN', 'TATASTEEL': 'TATASTEEL', 'GALLANT': 'GALLANT',
            'JSWSTEEL': 'JSWSTEEL', 'IDEA': 'IDEA', 'VODAFONE': 'VODAFONE', 'AUROPHARMA': 'AUROPHARMA',
            'AVANTIFEED': 'AVANTIFEED', 'DABUR': 'DABUR', 'COLPAL': 'COLPAL', 'BRITANNIA': 'BRITANNIA',
            'IGL': 'IGL', 'INDUSTOWER': 'INDUSTOWER', 'NHPC': 'NHPC', 'NTPC': 'NTPC', 'POWERGRID': 'POWERGRID',
            'RECLTD': 'RECLTD', 'BPCL': 'BPCL', 'HPCL': 'HPCL', 'IOB': 'IOB', 'OIL': 'OIL', 'PETRONET': 'PETRONET',
            'GAIL': 'GAIL', 'TATAPOWER': 'TATAPOWER', 'TataElxsi': 'TataElxsi', 'M&MFIN': 'M&MFIN', 'M&M': 'M&M',
            'MOTHERSUMI': 'MOTHERSUMI', 'MRF': 'MRF', 'MUTHOOTCAP': 'MUTHOOTCAP', 'PFC': 'PFC', 'PFCLTD': 'PFCLTD'
        }
        self._sectors = {
            'NIFTY_50': [], 'NIFTY_NEXT_50': [], 'MIDCAP': [], 'BANKING': [], 'FINANCIALS': [],
            'IT': [], 'PHARMA': [], 'AUTO': [], 'CONSUMER': [], 'METAL': [], 'ENERGY': [],
            'REAL_ESTATE': [], 'INFRASTRUCTURE': [], 'DEFENCE': [], 'PSU': [], 'OTHER': []
        }

    def is_cache_valid(self):
        """Check if CSV file is fresh and has data."""
        if not os.path.exists(LOCAL_CACHE):
            return False
        file_stat = os.stat(LOCAL_CACHE)
        age = time.time() - file_stat.st_mtime
        return age < NSE_CACHE_EXPIRY

    def fetch_nse_list(self):
        """Download latest NSE equity list from NSE website."""
        try:
            response = requests.get(CSV_URL, timeout=30)
            if response.status_code == 200:
                with open(LOCAL_CACHE, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Failed to fetch NSE list: {e}")
        return False

    def load_universe(self):
        """Load NSE CSV and populate stock data, also load local cache if fresh."""
        self._universe.clear()

        if not self.is_cache_valid():
            if self.fetch_nse_list():
                print("NSE Equity List downloaded successfully.")
            else:
                print("Using cached NSE list (download failed).")

        if os.path.exists(LOCAL_CACHE):
            with open(LOCAL_CACHE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol = row.get('SYMBOL', '').strip().upper()
                    company = row.get('COMPANY NAME', '').strip().upper()
                    series = row.get('SERIES', '').strip()
                    if series != 'EQ':
                        continue
                    if not symbol or not company:
                        continue
                    sector = self._categorize_stock(symbol, company)
                    self._universe[symbol] = {
                        'company': company,
                        'sector': sector,
                        'ticker': symbol
                    }

        if not self._universe:
            self._load_fallback_universe()

        print(f"Loaded {len(self._universe)} NSE stocks into universe.")

    def _categorize_stock(self, symbol, company):
        """Categorize stock into sectors."""
        if symbol in ['RELIANCE', 'TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TCS', 'IRTC']:
            return 'NIFTY_50'
        if 'BANK' in symbol or 'FIN' in symbol:
            return 'BANKING'
        if 'PHARMA' in company or 'PHARMA' in symbol:
            return 'PHARMA'
        if 'AUTO' in symbol or 'MOTOR' in symbol or 'MARUTI' in symbol:
            return 'AUTO'
        if 'IT' in symbol or 'TECH' in company:
            return 'IT'
        if 'BANKING' in symbol:
            return 'FINANCIALS'
        if 'MID' in symbol or 'SMALL' in company:
            return 'MIDCAP'
        if 'DEFENCE' in symbol or 'ARMY' in company:
            return 'DEFENCE'
        if 'PSU' in symbol or 'GOVERNMENT' in company:
            return 'PSU'
        return 'OTHER'

    def _load_fallback_universe(self):
        """Fallback for offline scenarios (pre-populated with common NSE stocks)."""
        fallback_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "TATAMOTORS", "ASHOKLEY",
            "BHARTIARTL", "HINDUNILVR", "ITC", "GODREJCP", "DABUR", "MARICO", "BPCL", "ONGC", "COALINDIA",
            "POWERGRID", "NTPC", "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL", "TEL", "TATAELXSI",
            "ADANIENT", "ADANIPORTS", "ADANIGREEN", "ADANIPOWER", "TATAPOWER", "TATACONSUMER", "TATACOFFEE",
            "TATACONSUM", "TCS", "INFY", "WIPRO", "LTIM", "COFINDIA", "BSE", "NIFTY", "BANKNIFTY",
            "FINNIFTY", "MIDCPNIFTY", "NIFTYBEES", "JETAIRWAYS", "VOLTAS", "TORNTPHARM", "LUPIN",
            "CIPLA", "DRREDDY", "SUNPHARMA", "LARSEN", "TATASTEEL", "GALLANT", "JSWSTEEL", "IDEA",
            "VODAFONE", "AUROPHARMA", "AVANTIFEED", "DABUR", "COLPAL", "BRITANNIA", "IGL", "INDUSTOWER",
            "NHPC", "NTPC", "POWERGRID", "RECLTD", "BPCL", "HPCL", "IOB", "OIL", "PETRONET", "GAIL",
            'TATAPOWER', 'TataElxsi', 'M&MFIN', 'M&M', 'MOTHERSUMI', 'MRF', 'MUTHOOTCAP', 'PFC', 'PFCLTD'
        ]
        for sym in fallback_symbols:
            self._universe[sym] = {
                'company': f"{sym} LTD",
                'sector': 'NIFTY_50',
                'ticker': sym
            }

    def search_stocks(self, query, limit=10):
        """Fuzzy search stocks by ticker or company name using difflib."""
        if not query or len(query) < 1:
            return []

        query_upper = query.upper()
        results = []

        for symbol, data in self._universe.items():
            score = 0
            if query_upper == symbol:
                score = 100
            elif symbol.startswith(query_upper):
                score = 90
            elif query_upper in symbol:
                score = 80
            elif query_upper in data['company']:
                score = 70
            # Use difflib for fuzzy matching
            elif difflib.SequenceMatcher(None, query_upper, symbol).ratio() > 0.6:
                score = 50
            elif difflib.SequenceMatcher(None, query_upper, data['company']).ratio() > 0.6:
                score = 40

            if score > 0:
                results.append({
                    'ticker': symbol,
                    'company': data['company'],
                    'sector': data['sector'],
                    'score': score
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def get_stocks_by_sector(self, sector, limit=100):
        """Get all stocks in a specific sector."""
        results = []
        for symbol, data in self._universe.items():
            if data['sector'] == sector:
                results.append({
                    'ticker': symbol,
                    'company': data['company'],
                    'sector': sector
                })
        return results[:limit]

    def get_all_symbols(self):
        """Return list of all ticker symbols."""
        return list(self._universe.keys())

    def get_sector_summary(self):
        """Return summary of stocks by sector."""
        summary = {}
        for sector in self._sectors.keys():
            count = len(self.get_stocks_by_sector(sector))
            if count > 0:
                summary[sector] = count
        return summary

    def export_to_json(self, filename='stock_universe.json'):
        """Export current universe to JSON for backup."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self._universe, f, ensure_ascii=False, indent=2)
        print(f"Universe exported to {filename}")

    def import_from_json(self, filename='stock_universe.json'):
        """Import universe from JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self._universe = json.load(f)
            print(f"Universe imported from {filename}")
        else:
            print(f"File {filename} not found.")