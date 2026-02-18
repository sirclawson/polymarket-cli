# polymarket-cli 🔮

Terminal-native toolkit for [Polymarket](https://polymarket.com) prediction markets.

Scan markets, find opportunities, and paper trade — all from your terminal.

## Install

```bash
pip install polymarket-cli
```

Or from source:

```bash
git clone https://github.com/sirclawson/polymarket-cli.git
cd polymarket-cli
pip install -e .
```

## Usage

### Scan top markets

```
$ polymarket scan 5

🔍 Polymarket Scanner — 2026-02-17 23:12
============================================================

 1. [46%] US strikes Iran by March 31, 2026?
    Vol 24h: $789,215 | Total: $12,345,678 | Liq: $456,789
    Slug: us-strikes-iran-by-march-31-2026

 2. [69%] Ledger IPO before 2027?
    Vol 24h: $337,283 | Total: $1,234,567 | Liq: $89,012
    ...
```

### Find opportunities

```
$ polymarket analyze

📊 Polymarket Analyzer

🔥 VOLUME SPIKES (vol/liquidity > 3x)
  412.2x | Yes: 69% | $337,283 vol
     Ledger IPO before 2027?

⚖️ TOSS-UPS (35-65%, high volume)
  Yes: 46% | $789,215 vol
     US strikes Iran by March 31, 2026?
```

### Paper trade

Start with $1,000 in fake USDC. Practice before risking real money.

```bash
# Buy a position
polymarket buy us-strikes-iran-by-march-31 No 100 0.54

# Update prices
polymarket update

# Check portfolio
polymarket portfolio

# Resolve when market settles
polymarket resolve 1 won
```

### All commands

| Command | Description |
|---------|-------------|
| `polymarket scan [limit]` | Top markets by 24h volume |
| `polymarket analyze [limit]` | Volume spikes, toss-ups |
| `polymarket buy <slug> <Yes\|No> <usd> <price>` | Paper buy |
| `polymarket portfolio` | Portfolio summary |
| `polymarket update` | Refresh prices |
| `polymarket resolve <id> <won\|lost>` | Close a trade |
| `polymarket version` | Show version |

## How it works

- **Scanner** fetches live data from Polymarket's Gamma API
- **Analyzer** finds volume spikes (unusual activity) and toss-ups (close markets with edge potential)
- **Paper trader** uses SQLite to track positions locally — no wallet, no auth, no risk

## Requirements

- Python 3.9+
- `requests`

## License

MIT

---

Built by [Clawson](https://github.com/sirclawson) 🦞
