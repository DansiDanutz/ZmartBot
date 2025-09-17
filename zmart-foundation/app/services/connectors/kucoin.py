import random
async def get_price(symbol: str) -> float:
    base = 2400.0 if symbol.upper()=="ETH" else 60000.0
    return round(base + random.uniform(-50, 50), 2)
