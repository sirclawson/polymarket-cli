"""Market analyzer — volume spikes, toss-ups, momentum detection."""
from .api import fetch_markets, parse_prices
from datetime import datetime


def analyze(limit=100):
    """Analyze markets for opportunities. Returns categorized results."""
    markets = fetch_markets(limit=limit)
    
    volume_spikes = []
    toss_ups = []
    
    for m in markets:
        yes_price, no_price = parse_prices(m)
        if not yes_price:
            continue
        
        vol = float(m.get("volume24hr", 0))
        liq = float(m.get("liquidityNum", 0))
        
        entry = {
            "question": m.get("question", "?"),
            "slug": m.get("slug", ""),
            "yes_price": yes_price,
            "volume_24h": vol,
            "liquidity": liq,
        }
        
        # Volume spikes: vol/liquidity ratio > 3x
        if liq > 0 and vol / liq > 3:
            entry["spike_ratio"] = vol / liq
            volume_spikes.append(entry)
        
        # Toss-ups: 35-65% range with decent volume
        if 0.35 <= yes_price <= 0.65 and vol > 50000:
            toss_ups.append(entry)
    
    volume_spikes.sort(key=lambda x: x["spike_ratio"], reverse=True)
    toss_ups.sort(key=lambda x: x["volume_24h"], reverse=True)
    
    return {"volume_spikes": volume_spikes[:15], "toss_ups": toss_ups[:15]}


def print_analysis(limit=100):
    """Print formatted analysis."""
    print("=" * 60)
    print(f"📊 Polymarket Analyzer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    results = analyze(limit)
    
    print("\n🔥 VOLUME SPIKES (vol/liquidity > 3x)")
    print("-" * 50)
    for m in results["volume_spikes"]:
        print(f"  {m['spike_ratio']:6.1f}x | Yes: {m['yes_price']*100:.0f}% | ${m['volume_24h']:,.0f} vol")
        print(f"     {m['question'][:65]}")
    
    print("\n⚖️ TOSS-UPS (35-65%, high volume)")
    print("-" * 50)
    for m in results["toss_ups"]:
        print(f"  Yes: {m['yes_price']*100:.0f}% | ${m['volume_24h']:,.0f} vol")
        print(f"     {m['question'][:65]}")
