"""Polymarket API client — Gamma API for market data."""
import requests

GAMMA_API = "https://gamma-api.polymarket.com"
DEFAULT_TIMEOUT = 15


def fetch_markets(limit=50, active=True, closed=False, order="volume24hr", ascending=False):
    """Fetch markets from Gamma API."""
    params = {
        "limit": limit,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "order": order,
        "ascending": str(ascending).lower(),
    }
    r = requests.get(f"{GAMMA_API}/markets", params=params, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def fetch_market_by_slug(slug):
    """Fetch a single market by slug."""
    r = requests.get(f"{GAMMA_API}/markets", params={"slug": slug, "limit": 1}, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    markets = r.json()
    if not markets:
        return None
    return markets[0]


def parse_prices(market):
    """Extract Yes/No prices from market data."""
    yes_price = None
    no_price = None
    try:
        outcomes = market.get("outcomePrices", "[]")
        if isinstance(outcomes, str):
            import json
            outcomes = json.loads(outcomes)
        if len(outcomes) >= 2:
            yes_price = float(outcomes[0])
            no_price = float(outcomes[1])
    except (ValueError, IndexError, TypeError):
        pass
    return yes_price, no_price
