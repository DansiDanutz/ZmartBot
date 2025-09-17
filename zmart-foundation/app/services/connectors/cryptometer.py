import httpx
import os
from loguru import logger
import asyncio


async def momentum_bias(symbol: str) -> dict:
    """Fetch real momentum bias from Cryptometer API with retries and timeout."""
    base_url = os.getenv("CRYPTOMETER_BASE")
    api_key = os.getenv("CRYPTOMETER_API_KEY")
    
    # Fallback to safe defaults if env not configured
    if not base_url or not api_key:
        logger.warning("Cryptometer not configured, using fallback data")
        return {
            "bias_short": 0.6,
            "bias_long": 0.4,
            "indicators": ["RSI_1h=oversold", "MACD_1h=bearish", "EMA9_21_1h=below"]
        }
    
    timeout = httpx.Timeout(10.0)
    retry_count = 3
    
    for attempt in range(retry_count):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{base_url}/momentum/{symbol}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={"timeframe": "1h"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Map API response to expected schema
                return {
                    "bias_short": float(data.get("short_bias", 0.5)),
                    "bias_long": float(data.get("long_bias", 0.5)), 
                    "indicators": data.get("indicators", [
                        f"RSI_1h={data.get('rsi_signal', 'neutral')}",
                        f"MACD_1h={data.get('macd_signal', 'neutral')}", 
                        f"EMA9_21_1h={data.get('ema_signal', 'neutral')}"
                    ])
                }
                
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.warning(f"Cryptometer API attempt {attempt + 1} failed: {e}")
            if attempt == retry_count - 1:
                logger.error("Cryptometer API failed after retries, using fallback")
                return {
                    "bias_short": 0.55,
                    "bias_long": 0.45,
                    "indicators": ["RSI_1h=error", "MACD_1h=error", "EMA9_21_1h=error"]
                }
            await asyncio.sleep(1.0)  # Brief delay before retry


def momentum_bias_sync(symbol: str) -> dict:
    """Synchronous wrapper for backward compatibility."""
    return asyncio.run(momentum_bias(symbol))
