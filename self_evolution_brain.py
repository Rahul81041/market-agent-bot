"""
Self-Healing Mistake Learner & Evolution Engine (`self_evolution_brain.py`)
When a paper trade closes in LOSS, triggers post-mortem analysis, identifies the flaw,
saves lessons to learned_rules.json + evolution_log table, and adapts indicator weights.
"""

import sqlite3
import json
import os
import datetime
import requests

DB_NAME = "trades.db"
RULES_FILE = "learned_rules.json"
TELEGRAM_BOT_TOKEN = "9089360235:AAGCTAesCisWR2soUzjrp4Suc8RwuOAi7G0"

class SelfEvolutionBrain:

    @staticmethod
    def init_db():
        """Initialize evolution_log table."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                loss_amount REAL,
                identified_flaw TEXT,
                rule_created TEXT,
                indicator_penalized TEXT,
                weight_adjustment REAL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def load_learned_rules():
        """Load learned rules from JSON file."""
        if os.path.exists(RULES_FILE):
            try:
                with open(RULES_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "rules": [],
            "indicator_weights": {
                "rsi_overbought": 1.0,
                "upper_wick_heavy": 1.0,
                "mtf_misalignment": 1.0,
                "volume_low": 1.0,
                "nifty_opposite": 1.0
            }
        }

    @staticmethod
    def save_learned_rules(rules_data):
        """Save learned rules to JSON file."""
        try:
            with open(RULES_FILE, 'w') as f:
                json.dump(rules_data, f, indent=2)
        except Exception as e:
            print(f"Error saving rules: {e}")

    @staticmethod
    def post_mortem_analysis(symbol, entry_snapshot, loss_amount):
        """
        Analyze why trade failed and identify specific flaw.
        entry_snapshot: dict with {rsi, upper_wick, lower_wick, mtf_score, volume_surge, nifty_trend, etc}
        """
        flaws = []
        rules_created = []
        indicators_penalized = []

        # Rule 1: RSI Overbought on entry
        if entry_snapshot.get("rsi", 50) > 70:
            flaws.append(f"Entered long when RSI was overbought ({entry_snapshot['rsi']})")
            rules_created.append("Never buy when RSI > 70 unless MTF score is 3/3 and Nifty bullish")
            indicators_penalized.append("rsi_overbought")

        # Rule 2: Heavy Upper Wick (rejection candle ignored)
        if entry_snapshot.get("upper_wick_ratio", 0) > 0.5:
            flaws.append(f"Ignored heavy upper wick rejection ({entry_snapshot['upper_wick_ratio']:.2f})")
            rules_created.append("Avoid buying if upper wick ratio > 50% at resistance zone")
            indicators_penalized.append("upper_wick_heavy")

        # Rule 3: MTF Misalignment
        if entry_snapshot.get("mtf_score", 3) < 2:
            flaws.append(f"Traded with poor MTF alignment (score {entry_snapshot['mtf_score']}/3)")
            rules_created.append("Require MTF alignment score >= 2/3 for conviction > 70%")
            indicators_penalized.append("mtf_misalignment")

        # Rule 4: Low volume entry
        if not entry_snapshot.get("volume_surge", False):
            flaws.append("Entered without volume confirmation (no surge detected)")
            rules_created.append("Demand volume > 1.4x SMA before breakout entries")
            indicators_penalized.append("volume_low")

        # Rule 5: Traded against Nifty trend
        if entry_snapshot.get("nifty_trend") != entry_snapshot.get("stock_trend"):
            flaws.append("Stock direction opposed Nifty 50 benchmark trend")
            rules_created.append("Never trade stock opposite to Nifty unless sector-specific catalyst")
            indicators_penalized.append("nifty_opposite")

        # Default flaw if nothing specific identified
        if not flaws:
            flaws.append("Market structure invalidation or unpredictable external shock")
            rules_created.append("Tighten stop-loss buffer to 1.5x ATR instead of 1.8x ATR")

        return {
            "flaws": flaws,
            "rules": rules_created,
            "indicators": indicators_penalized
        }

    @staticmethod
    def learn_from_loss(symbol, entry_snapshot, loss_amount, chat_id=None):
        """
        Triggered when paper trade closes in LOSS.
        Runs post-mortem, updates weights, saves to DB & JSON, pushes lesson to Telegram.
        """
        SelfEvolutionBrain.init_db()

        # Analyze
        analysis = SelfEvolutionBrain.post_mortem_analysis(symbol, entry_snapshot, loss_amount)

        # Load current rules
        rules_data = SelfEvolutionBrain.load_learned_rules()

        # Penalize indicators
        for indicator in analysis["indicators"]:
            if indicator in rules_data["indicator_weights"]:
                old_weight = rules_data["indicator_weights"][indicator]
                # Reduce weight by 15% (more conservative)
                rules_data["indicator_weights"][indicator] = round(old_weight * 0.85, 3)

        # Add new rules (keep last 20 rules)
        for rule in analysis["rules"]:
            if rule not in rules_data["rules"]:
                rules_data["rules"].append(rule)
        rules_data["rules"] = rules_data["rules"][-20:]  # Keep only recent 20

        # Save to JSON
        SelfEvolutionBrain.save_learned_rules(rules_data)

        # Log to database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO evolution_log
            (symbol, loss_amount, identified_flaw, rule_created, indicator_penalized, weight_adjustment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            loss_amount,
            "; ".join(analysis["flaws"]),
            "; ".join(analysis["rules"]),
            ", ".join(analysis["indicators"]),
            -0.15
        ))
        conn.commit()
        conn.close()

        # Push Telegram notification
        if chat_id:
            SelfEvolutionBrain.send_learning_update(chat_id, symbol, loss_amount, analysis, rules_data)

        return analysis

    @staticmethod
    def send_learning_update(chat_id, symbol, loss, analysis, rules_data):
        """Send self-learning update to Telegram."""
        msg = (
            f"🧠 *SELF-LEARNING UPDATE*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ Lost *₹{abs(loss):.2f}* on *{symbol}*\n\n"
            f"🔍 *Why I Failed*:\n"
        )
        for flaw in analysis["flaws"][:2]:  # Show top 2 flaws
            msg += f"• {flaw}\n"

        msg += f"\n📝 *New Rule in My Brain*:\n"
        for rule in analysis["rules"][:1]:  # Show primary rule
            msg += f"• {rule}\n"

        msg += f"\n⚙️ *Indicator Weight Adjustments*:\n"
        for ind in analysis["indicators"][:2]:
            weight = rules_data["indicator_weights"].get(ind, 1.0)
            msg += f"• {ind}: {weight:.2f}\n"

        msg += f"\n💡 I will NEVER repeat this mistake again."

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass

    @staticmethod
    def get_active_rules_for_prompt():
        """Returns top learned rules as a string to inject into Bull/Bear/Arbiter prompts."""
        rules_data = SelfEvolutionBrain.load_learned_rules()
        if not rules_data["rules"]:
            return ""

        prompt_injection = "\n🧠 **EVOLVED RULES (Self-Learned from Past Losses)**:\n"
        for i, rule in enumerate(rules_data["rules"][-10:], 1):  # Last 10 rules
            prompt_injection += f"{i}. {rule}\n"

        return prompt_injection

    @staticmethod
    def get_brain_summary():
        """Return brain summary for /brain or /mistakes command."""
        SelfEvolutionBrain.init_db()
        rules_data = SelfEvolutionBrain.load_learned_rules()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT symbol, loss_amount, identified_flaw, rule_created FROM evolution_log ORDER BY timestamp DESC LIMIT 5')
        recent_mistakes = cursor.fetchall()
        conn.close()

        summary = (
            f"🧠 *AI BRAIN EVOLUTION REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📚 Total Learned Rules: *{len(rules_data['rules'])}*\n\n"
        )

        # Active Rules
        if rules_data["rules"]:
            summary += f"📝 *Top Active Rules*:\n"
            for i, rule in enumerate(rules_data["rules"][-5:], 1):
                summary += f"{i}. {rule}\n"
            summary += "\n"

        # Indicator Weights
        summary += f"⚙️ *Evolved Indicator Weights*:\n"
        for key, val in rules_data["indicator_weights"].items():
            emoji = "🔴" if val < 0.7 else ("🟡" if val < 0.9 else "🟢")
            summary += f"{emoji} {key}: {val:.2f}\n"

        # Recent Mistakes
        if recent_mistakes:
            summary += f"\n❌ *Recent Mistakes Learned From*:\n"
            for sym, loss, flaw, rule in recent_mistakes[:3]:
                summary += f"• {sym}: Lost ₹{abs(loss):.0f} → {flaw[:50]}...\n"

        summary += "━━━━━━━━━━━━━━━━━━━━━━"
        return summary
