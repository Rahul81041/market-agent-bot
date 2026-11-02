---
name: indian-trading-wizard
description: Interactive conversational wizard for Indian stock analysis — guides user through manual input or auto-scan, then auto-runs ultra analysis on selected stock.
---

# Indian Trading Wizard

## Flow

### Step 1: Ask user
```
┌─────────────────────────────────────────────────────┐
│  INDIAN TRADING WIZARD                              │
│  What would you like to do?                         │
│                                                     │
│  1️⃣  Enter stock manually                           │
│  2️⃣  Find best stocks for me                        │
│  3️⃣  Quick scan NIFTY 50                            │
│                                                     │
│  Type 1, 2, or 3...
└─────────────────────────────────────────────────────┘
```

### Step 2: If "1" (Manual)
```
📝 MANUAL ENTRY
Enter: [STOCK] [CAPITAL] [RISK%]
Example: RELIANCE 100000 1
```

### Step 2: If "2" (Auto-Find)
Show top 5 stocks with scores. User selects A, B, C, D, or E.

### Step 2: If "3" (Quick NIFTY 50)
Show top 3 NIFTY 50 stocks. User selects 1, 2, or 3.

### Step 3: Auto-run ultra
Automatically run `/indian-trading-ultra [STOCK] [CAPITAL] [RISK%]`

### Step 4: Show result
Display full ultra analysis report.

### Step 5: Ask next action
```
NEXT ACTIONS:
[TRADE NOW] [WATCH] [ANOTHER] [EXIT]
```

## Usage
```
/indian-trading-wizard
```