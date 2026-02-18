"""Market scanner — find top markets, extreme prices, opportunities."""
from .api import fetch_markets, parse_prices


def scan(limit=30):
    """Scan top markets by 24h volume. Returns formatted market data."""
    markets = fetch_markets(limit=limit)
    results = []
    for m in markets:
        yes_price, no_price = parse_prices(m)
        results.append({
            "question": m.get("question", "?"),
            "slug": m.get("slug", ""),
            "yes_price": yes_price,
            "no_price": no_price,
            "volume_24h": float(m.get("volume24hr", 0)),
            "volume_total": float(m.get("volumeNum", 0)),
            "liquidity": float(m.get("liquidityNum", 0)),
        })
    return results


def print_scan(limit=30):
    """Print formatted scan results."""
    from datetime import datetime
    print("=" * 60)
    print(f"🔍 Polymarket Scanner — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    results = scan(limit)
    for i, m in enumerate(results, 1):
        yp = f"{m['yes_price']*100:.0f}%" if m['yes_price'] else "?"
        print(f"{i:2}. [{yp}] {m['question'][:70]}")
        print(f"    Vol 24h: ${m['volume_24h']:,.0f} | Total: ${m['volume_total']:,.0f} | Liq: ${m['liquidity']:,.0f}")
        print(f"    Slug: {m['slug']}")
        print()
