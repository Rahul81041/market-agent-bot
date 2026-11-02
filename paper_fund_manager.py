"""
Autonomous Signal Portfolio & Track Record Engine (`paper_fund_manager.py`)
============================================================================
Delegates signal logging to SignalTracker and maintains backwards compatibility
for wallet queries, while formatting output as a verified performance track record.
"""

from signal_tracker import SignalTracker

class PaperFundManager:

    @staticmethod
    def init_db():
        SignalTracker.init_db()

    @staticmethod
    def execute_paper_trade(symbol, entry_price, stop_loss, target1, target2, direction, conviction):
        """
        Registers an official institutional signal card instead of managing cash balances.
        Returns execution status and summary.
        """
        try:
            verdict = "BULL WINS" if direction == "BULL" else "BEAR WINS"
            sig = SignalTracker.publish_signal(symbol, entry_price, stop_loss, target1, target2, direction, conviction, verdict)
            return True, f"Signal Logged: {sig['signal_id']} for {symbol} | Target: ₹{target1} | SL: ₹{stop_loss}"
        except Exception as e:
            return False, f"Signal logging failed: {str(e)}"

    @staticmethod
    def monitor_open_positions(chat_id=None):
        """Monitors active signals against live ticks for target/SL hits."""
        return SignalTracker.monitor_signals(chat_id)

    @staticmethod
    def get_wallet_summary():
        """Returns the verified track record and win-rate proof summary."""
        return SignalTracker.get_track_record_summary()
