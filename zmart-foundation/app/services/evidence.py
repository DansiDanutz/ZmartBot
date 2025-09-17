from .connectors import cryptometer, kingfisher, binance
from .riskmetric import risk_score
from ..schemas import EvidenceItem

async def build_evidence(symbol: str) -> list[EvidenceItem]:
    cm = await cryptometer.momentum_bias(symbol)
    kf = await kingfisher.clusters(symbol)
    price = await binance.get_price(symbol)
    risk = risk_score(symbol)
    
    # Format indicators cleanly - join first 3 for brevity
    indicators_text = ", ".join(cm['indicators'][:3])
    
    return [
        EvidenceItem(source="Cryptometer", text=f"Momentum bias short={int(cm['bias_short']*100)}% ({indicators_text})"),
        EvidenceItem(source="KingFisher", text=f"Liq cluster near ${kf['below'][0]['price']:.2f} (below)"),
        EvidenceItem(source="Binance", text=f"Spot ~ ${price:.2f}"),
        EvidenceItem(source="RiskMetric", text=f"Macro risk ≈ {risk:.2f}"),
    ]
