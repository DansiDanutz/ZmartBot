import httpx
import os
from loguru import logger
import asyncio
from typing import Dict, List


async def clusters(symbol: str) -> Dict[str, List[dict]]:
    """Fetch KingFisher clusters from Supabase with fallback."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Fallback if not configured
    if not supabase_url or not supabase_key:
        logger.warning("Supabase not configured, using fallback cluster data")
        return {
            "below": [{"price": 2430.0, "size": "large"}], 
            "above": [{"price": 2520.0, "size": "medium"}]
        }
    
    try:
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Query last 50 clusters for symbol, ordered by timestamp desc
            response = await client.get(
                f"{supabase_url}/rest/v1/kf_clusters",
                headers={
                    "Authorization": f"Bearer {supabase_key}",
                    "apikey": supabase_key,
                    "Content-Type": "application/json"
                },
                params={
                    "symbol": f"eq.{symbol}",
                    "order": "ts.desc",
                    "limit": "50"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Group by side
            above_clusters = []
            below_clusters = []
            
            for row in data:
                cluster_info = {
                    "price": float(row["price"]),
                    "size": row["size"],
                    "notional": row.get("notional", 0)
                }
                
                if row["side"] == "above":
                    above_clusters.append(cluster_info)
                elif row["side"] == "below":
                    below_clusters.append(cluster_info)
            
            # Sort by price (descending for above, ascending for below)
            above_clusters.sort(key=lambda x: x["price"], reverse=True)
            below_clusters.sort(key=lambda x: x["price"])
            
            return {
                "above": above_clusters[:10],  # Top 10 clusters
                "below": below_clusters[:10]   # Top 10 clusters
            }
            
    except Exception as e:
        logger.error(f"Failed to fetch KingFisher clusters from Supabase: {e}")
        # Return fallback data on error
        return {
            "below": [{"price": 2430.0, "size": "large", "notional": 5000000}], 
            "above": [{"price": 2520.0, "size": "medium", "notional": 2000000}]
        }


def clusters_sync(symbol: str) -> Dict[str, List[dict]]:
    """Synchronous wrapper for backward compatibility."""
    return asyncio.run(clusters(symbol))
