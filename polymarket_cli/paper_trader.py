"""Paper trading system — track hypothetical bets with fake USDC."""
import sqlite3
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

from .api import GAMMA_API

DEFAULT_DB = Path.home() / ".polymarket-cli" / "trades.db"
INITIAL_BALANCE = 1000.0


def get_db(db_path=None):
    """Get or create the paper trading database."""
    path = Path(db_path) if db_path else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_slug TEXT NOT NULL,
        question TEXT,
        outcome TEXT NOT NULL,
        entry_price REAL NOT NULL,
        current_price REAL,
        amount_usd REAL NOT NULL,
        shares REAL NOT NULL,
        status TEXT DEFAULT 'open',
        pnl REAL DEFAULT 0,
        opened_at TEXT,
        closed_at TEXT
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS portfolio (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    # Initialize balance
    row = db.execute("SELECT value FROM portfolio WHERE key='cash'").fetchone()
    if not row:
        db.execute("INSERT INTO portfolio (key, value) VALUES ('cash', ?)", (str(INITIAL_BALANCE),))
        db.execute("INSERT INTO portfolio (key, value) VALUES ('initial', ?)", (str(INITIAL_BALANCE),))
        db.commit()
    return db


def get_cash(db):
    row = db.execute("SELECT value FROM portfolio WHERE key='cash'").fetchone()
    return float(row["value"]) if row else 0


def set_cash(db, amount):
    db.execute("UPDATE portfolio SET value=? WHERE key='cash'", (str(amount),))
    db.commit()


def buy(slug, outcome, amount_usd, price, db_path=None):
    """Place a paper buy order."""
    db = get_db(db_path)
    cash = get_cash(db)
    if amount_usd > cash:
        print(f"❌ Insufficient funds: ${cash:.2f} available, ${amount_usd:.2f} needed")
        return

    # Fetch market info
    r = requests.get(f"{GAMMA_API}/markets", params={"slug": slug, "limit": 1}, timeout=15)
    markets = r.json()
    if not markets:
        print(f"❌ Market not found: {slug}")
        return

    question = markets[0].get("question", slug)
    shares = amount_usd / price
    now = datetime.now(timezone.utc).isoformat()

    db.execute(
        "INSERT INTO trades (market_slug, question, outcome, entry_price, current_price, amount_usd, shares, opened_at) VALUES (?,?,?,?,?,?,?,?)",
        (slug, question, outcome, price, price, amount_usd, shares, now)
    )
    set_cash(db, cash - amount_usd)
    db.commit()

    payout = shares  # $1 per share if correct
    profit = payout - amount_usd
    print(f"✅ PAPER BUY: {outcome} @ {price*100:.1f}%")
    print(f"   {question}")
    print(f"   Spent: ${amount_usd:.2f} → {shares:.1f} shares")
    print(f"   If correct: ${payout:.2f} payout (${profit:.2f} profit)")
    print(f"   Balance: ${cash - amount_usd:.2f}")


def update_prices(db_path=None):
    """Update current prices for all open trades."""
    db = get_db(db_path)
    trades = db.execute("SELECT * FROM trades WHERE status='open'").fetchall()
    if not trades:
        print("No open trades.")
        return

    print(f"Updating {len(trades)} open trades...")
    for trade in trades:
        try:
            r = requests.get(f"{GAMMA_API}/markets", params={"slug": trade["market_slug"], "limit": 1}, timeout=15)
            markets = r.json()
            if not markets:
                continue
            m = markets[0]
            outcomes = m.get("outcomePrices", "[]")
            if isinstance(outcomes, str):
                outcomes = json.loads(outcomes)
            if not outcomes:
                continue

            if trade["outcome"].lower() in ("yes", "up"):
                price = float(outcomes[0])
            else:
                price = float(outcomes[1]) if len(outcomes) > 1 else 1 - float(outcomes[0])

            db.execute("UPDATE trades SET current_price=? WHERE id=?", (price, trade["id"]))
        except Exception:
            continue

    db.commit()
    print("✅ Prices updated.")


def portfolio(db_path=None):
    """Display portfolio summary."""
    db = get_db(db_path)
    cash = get_cash(db)
    initial = float(db.execute("SELECT value FROM portfolio WHERE key='initial'").fetchone()["value"])

    open_trades = db.execute("SELECT * FROM trades WHERE status='open' ORDER BY id DESC").fetchall()
    closed_trades = db.execute("SELECT * FROM trades WHERE status!='open' ORDER BY closed_at DESC LIMIT 10").fetchall()

    position_value = sum(t["shares"] * (t["current_price"] or t["entry_price"]) for t in open_trades)
    total_value = cash + position_value
    realized = sum(t["pnl"] for t in closed_trades)
    unrealized = sum(t["shares"] * ((t["current_price"] or t["entry_price"]) - t["entry_price"]) for t in open_trades)
    wins = len([t for t in closed_trades if t["pnl"] > 0])
    losses = len([t for t in closed_trades if t["pnl"] < 0])
    total_pnl = total_value - initial

    print("=" * 50)
    print("📊 PAPER TRADING PORTFOLIO")
    print("=" * 50)
    print(f"  Cash:           ${cash:.2f}")
    print(f"  Positions:      ${position_value:.2f}")
    print(f"  Total Value:    ${total_value:.2f}")
    print(f"  Initial:        ${initial:.2f}")
    print(f"  Total P&L:      ${total_pnl:+.2f} ({total_pnl/initial*100:+.1f}%)")
    print(f"  Realized:       ${realized:+.2f}")
    print(f"  Unrealized:     ${unrealized:+.2f}")
    if wins or losses:
        print(f"  Win/Loss:       {wins}W / {losses}L")

    if open_trades:
        print(f"\n📈 OPEN POSITIONS ({len(open_trades)})")
        print("-" * 50)
        for t in open_trades:
            cp = t["current_price"] or t["entry_price"]
            upnl = t["shares"] * (cp - t["entry_price"])
            arrow = "📈" if upnl >= 0 else "📉"
            print(f"  #{t['id']} {arrow} {t['outcome']} @ {t['entry_price']*100:.1f}% → {cp*100:.1f}% | ${upnl:+.2f}")
            print(f"     {t['question'][:55]}")

    if closed_trades:
        print(f"\n📜 RECENT CLOSED ({len(closed_trades)})")
        print("-" * 50)
        for t in closed_trades:
            icon = "✅" if t["pnl"] > 0 else "❌"
            print(f"  #{t['id']} {icon} {t['outcome']} | ${t['pnl']:+.2f}")
            print(f"     {t['question'][:55]}")


def resolve(trade_id, won, db_path=None):
    """Resolve a trade as won or lost."""
    db = get_db(db_path)
    trade = db.execute("SELECT * FROM trades WHERE id=?", (trade_id,)).fetchone()
    if not trade:
        print(f"❌ Trade #{trade_id} not found")
        return
    if trade["status"] != "open":
        print(f"❌ Trade #{trade_id} already closed")
        return

    cash = get_cash(db)
    now = datetime.now(timezone.utc).isoformat()

    if won:
        pnl = trade["shares"] - trade["amount_usd"]  # shares * $1 - cost
        new_cash = cash + trade["shares"]
        status = "won"
    else:
        pnl = -trade["amount_usd"]
        new_cash = cash
        status = "lost"

    db.execute("UPDATE trades SET status=?, pnl=?, closed_at=? WHERE id=?",
               (status, pnl, now, trade_id))
    set_cash(db, new_cash)
    db.commit()

    icon = "✅" if won else "❌"
    print(f"{icon} Trade #{trade_id} resolved: {status} (${pnl:+.2f})")
    print(f"   Balance: ${new_cash:.2f}")
