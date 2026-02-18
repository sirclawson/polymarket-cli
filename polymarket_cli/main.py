"""CLI entry point for polymarket-cli."""
import sys


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return

    cmd = args[0]
    rest = args[1:]

    if cmd == "scan":
        from .scanner import print_scan
        limit = int(rest[0]) if rest else 30
        print_scan(limit)

    elif cmd == "analyze":
        from .analyzer import print_analysis
        limit = int(rest[0]) if rest else 100
        print_analysis(limit)

    elif cmd == "buy":
        from .paper_trader import buy
        if len(rest) < 4:
            print("Usage: polymarket buy <slug> <Yes|No> <amount_usd> <price>")
            print("  e.g: polymarket buy will-eth-hit-5000 Yes 50 0.35")
            sys.exit(1)
        slug, outcome, amount, price = rest[0], rest[1], float(rest[2]), float(rest[3])
        db_path = _get_opt(rest[4:], "--db")
        buy(slug, outcome, amount, price, db_path)

    elif cmd == "portfolio":
        from .paper_trader import portfolio
        db_path = _get_opt(rest, "--db")
        portfolio(db_path)

    elif cmd == "update":
        from .paper_trader import update_prices
        db_path = _get_opt(rest, "--db")
        update_prices(db_path)

    elif cmd == "resolve":
        from .paper_trader import resolve
        if len(rest) < 2:
            print("Usage: polymarket resolve <trade_id> <won|lost>")
            sys.exit(1)
        trade_id = int(rest[0])
        won = rest[1].lower() in ("won", "win", "yes", "true", "1")
        db_path = _get_opt(rest[2:], "--db")
        resolve(trade_id, won, db_path)

    elif cmd == "version":
        from . import __version__
        print(f"polymarket-cli v{__version__}")

    else:
        print(f"Unknown command: {cmd}")
        print_help()
        sys.exit(1)


def _get_opt(args, flag):
    """Extract a --flag value from args."""
    for i, a in enumerate(args):
        if a == flag and i + 1 < len(args):
            return args[i + 1]
    return None


def print_help():
    print("""polymarket-cli — Terminal-native toolkit for Polymarket

Commands:
  scan [limit]                         Scan top markets by 24h volume
  analyze [limit]                      Find volume spikes, toss-ups, opportunities
  buy <slug> <Yes|No> <usd> <price>    Paper trade: buy a position
  portfolio                            Show paper trading portfolio
  update                               Update prices for open positions
  resolve <id> <won|lost>              Resolve a paper trade
  version                              Show version

Examples:
  polymarket scan 20
  polymarket analyze
  polymarket buy will-eth-hit-5000 Yes 50 0.35
  polymarket portfolio
  polymarket update
  polymarket resolve 3 won

Options:
  --db <path>    Custom database path (default: ~/.polymarket-cli/trades.db)
""")


if __name__ == "__main__":
    main()
