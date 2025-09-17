import json
from datetime import datetime, timezone
from typing import Any
from schemas.kingfisher import Cluster

def parse_clusters_from_json(symbol: str, raw: dict[str,Any]) -> list[Cluster]:
    clusters: list[Cluster] = []
    now = datetime.now(timezone.utc)
    for side in ("above","below"):
        for c in raw.get(side, []):
            clusters.append(Cluster(
                symbol=symbol.upper(),
                side=side, price=float(c["price"]),
                size=c.get("size","medium"),
                notional=(float(c["notional"]) if c.get("notional") else None),
                ts=(datetime.fromisoformat(c["ts"]) if c.get("ts") else now)
            ))
    return clusters
