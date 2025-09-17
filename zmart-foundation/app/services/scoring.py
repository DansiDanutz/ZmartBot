from ..schemas import SnapshotResponse, BestEntryResponse, TargetsResponse, PlanBResponse, LadderResponse, LadderStep
from .evidence import build_evidence
from .connectors import cryptometer, kingfisher, binance

def _stance_from_probs(long_prob: float, short_prob: float) -> str:
    if max(long_prob, short_prob) < 0.55:
        return "wait"
    return "long" if long_prob > short_prob else "short"

async def get_snapshot(symbol: str) -> SnapshotResponse:
    ev = await build_evidence(symbol)
    cm = await cryptometer.momentum_bias(symbol)
    long_prob = cm["bias_long"]
    short_prob = cm["bias_short"]
    stance = _stance_from_probs(long_prob, short_prob)
    return SnapshotResponse(symbol=symbol.upper(), long_prob=long_prob, short_prob=short_prob, stance=stance, evidence=ev)

async def get_best_entry(symbol: str) -> BestEntryResponse:
    ev = await build_evidence(symbol)
    kf = await kingfisher.clusters(symbol)
    # Select largest nearby cluster, fallback to current price ± 1%
    if kf["below"]:
        best = kf["below"][0]["price"]
    else:
        price = await binance.get_price(symbol)
        best = round(price * 0.99, 2)  # 1% below as fallback
    return BestEntryResponse(symbol=symbol.upper(), best_entry=best, est_prob=0.8, evidence=ev)

async def get_targets(symbol: str) -> TargetsResponse:
    price = await binance.get_price(symbol)
    tp = [round(price*0.97,2), round(price*0.94,2)]
    sr = [round(price*1.01,2), round(price*0.99,2)]
    return TargetsResponse(symbol=symbol.upper(), tp=tp, sr=sr, trail_rule="Trail remainder by 1% below local peak.")

async def get_plan_b(symbol: str) -> PlanBResponse:
    price = await binance.get_price(symbol)
    invalid = round(price*1.02,2)
    notes = [
        "Pause on strength; re-enter only on failed breakout.",
        "If funding + OI flip with news window, consider hedge path.",
        "Avoid chasing; wait for rejection signal."
    ]
    return PlanBResponse(symbol=symbol.upper(), invalidation=invalid, notes=notes)

async def get_ladder(symbol: str, bankroll: float) -> LadderResponse:
    price = await binance.get_price(symbol)
    steps = [
        LadderStep(level_name="Entry A", price=price, bankroll_pct=1.0, leverage_cap=20.0),
        LadderStep(level_name="Add B", price=round(price*1.01,2), bankroll_pct=2.0, leverage_cap=10.0),
        LadderStep(level_name="Add C", price=round(price*1.02,2), bankroll_pct=4.0, leverage_cap=5.0),
    ]
    caps = {"max_attempts": 3, "halt_on_regime_flip": True}
    alerts = [f"Touch {s.price} ({s.level_name})" for s in steps]
    return LadderResponse(symbol=symbol.upper(), steps=steps, caps=caps, alerts=alerts)
