#!/usr/bin/env python3
"""
OpenAI Trading Advice API Route
Provides on-demand ChatGPT-5/GPT-4 trading advice based on technical indicators
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import openai

from ..config.settings import settings
from ..config.api_keys_manager import get_api_key, is_service_available

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/openai", tags=["openai"])

class TradingAdviceRequest(BaseModel):
    prompt: str
    symbol: str
    model: Optional[str] = "gpt-5"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 800

# Initialize OpenAI client using API keys manager
openai_client = None
openai_api_key = None

try:
    # Try to get OpenAI API key from the API keys manager
    openai_config = get_api_key('openai')
    if openai_config and openai_config.get('api_key') and openai_config.get('api_key') != 'YOUR_API_KEY_HERE':
        openai_api_key = openai_config.get('api_key')
        openai_client = openai.OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized successfully from API keys manager")
    elif settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_key_here":
        # Fallback to settings if API manager doesn't have it
        openai_api_key = settings.OPENAI_API_KEY
        openai_client = openai.OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized successfully from settings")
    else:
        logger.warning("OpenAI API key not configured in API keys manager or settings")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    openai_client = None

@router.post("/trading-advice")
async def generate_trading_advice(request: TradingAdviceRequest) -> Dict[str, Any]:
    """
    Generate professional trading advice using ChatGPT-4/5 or demo mode
    
    Args:
        request: Trading advice request with prompt and symbol
    
    Returns:
        AI-generated trading advice or demo response
    """
    
    # Check if OpenAI is properly configured - REQUIRE REAL API KEY
    if not openai_client or not openai_api_key:
        logger.error(f"OpenAI API key required for {request.symbol}")
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Please add your OpenAI API key to the API keys manager to use ChatGPT-5 analysis."
        )
    
    try:
        logger.info(f"Generating AI trading advice for {request.symbol}")
        
        # Enhanced system prompt for user-friendly trading advice with win rates
        system_prompt = f"""Hey there DANSIDANUTZ! 👋 You're talking to your friendly neighborhood crypto trading expert who's here to make sense of this wild market chaos! 

        🎯 **My Mission**: Give you crystal-clear trading insights with actual numbers and a sprinkle of humor (because let's face it, trading without laughs leads to tears! 😅)

        📊 **What I ALWAYS provide**:
        1. **WIN RATE ESTIMATES** for both directions:
           - 🟢 LONG position probability (0-100%)
           - 🔴 SHORT position probability (0-100%)
        
        2. **SPECIFIC TRIGGER PRICES**:
           - 🎯 Optimal long entry price
           - 🎯 Optimal short entry price
           - 🛡️ Stop-loss levels for both
           - 💰 Take-profit targets
        
        3. **WAITING STRATEGY**:
           - Better opportunity prices to watch
           - Higher probability setups coming up
           - "Don't chase, wait for this..." advice
        
        4. **FRIENDLY TONE**:
           - Use trading jokes, poker analogies, and gambling references
           - Keep it personal and conversational  
           - Make complex analysis digestible
           - Think poker mindset: odds, bluffs, all-in moments, folding bad hands
           - Remember: We're in this crypto roller coaster together! 🎢

        📈 **Technical Arsenal**: RSI, MACD, Bollinger Bands, EMA, Stochastic, ADX, Volume, Support/Resistance
        
        🎪 **My Style**: Think of me as that poker-savvy trader friend who knows when to hold 'em, fold 'em, and when to go all-in! I'll tell you when you're holding pocket aces vs. when you should fold that 7-2 offsuit. 
        
        🃏 **Poker Mindset**: 
        - Calculate the odds before making any move
        - Know when to bluff (fake breakouts) vs. when it's the real deal  
        - Understand position sizing (don't go all-in on a weak hand)
        - Sometimes the best play is to fold and wait for a better spot
        
        ⚠️ **Golden Rule**: Every response MUST include specific win rates and exact price levels. No vague "maybe" or "could be" - give DANSIDANUTZ the actionable intel with poker-style confidence!
        
        📝 **FORMATTING REQUIREMENTS**:
        - Use clear section headers with emojis (🎰, 🎯, ⏰, 🃏, 💰)
        - Separate sections with decorative lines (═══════════════)
        - Add percentage calculations for stop-loss and take-profit
        - Use bullet points with consistent spacing
        - Keep sections organized and scannable
        - Use bold text for emphasis
        - Include visual separators between major sections"""
        
        # Map ChatGPT-5 request to latest available model
        model_mapping = {
            'gpt-5': 'gpt-4',  # ChatGPT-5 -> GPT-4 (latest available)
            'chatgpt-5': 'gpt-4',
            'gpt-4-5': 'gpt-4',
            'gpt-4': 'gpt-4',
            'gpt-4-turbo': 'gpt-4-turbo-preview'
        }
        
        actual_model = model_mapping.get(request.model, 'gpt-4')
        logger.info(f"Using model: {actual_model} (requested: {request.model})")
        
        # Make API call to ChatGPT
        response = openai_client.chat.completions.create(
            model=actual_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        # Extract advice from response
        advice_content = response.choices[0].message.content.strip()
        
        # Log successful generation
        token_usage = response.usage
        logger.info(f"AI advice generated for {request.symbol} - {token_usage.total_tokens} tokens used")
        
        return {
            "success": True,
            "advice": advice_content,
            "symbol": request.symbol,
            "model": request.model,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tokens_used": {
                    "prompt": token_usage.prompt_tokens,
                    "completion": token_usage.completion_tokens,
                    "total": token_usage.total_tokens
                },
                "model_info": {
                    "model": response.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                }
            }
        }
        
    except openai.RateLimitError as e:
        logger.warning(f"OpenAI rate limit exceeded for {request.symbol}: {e}")
        raise HTTPException(
            status_code=429,
            detail="AI service rate limit exceeded. Please try again in a moment."
        )
    except openai.APIError as e:
        logger.error(f"OpenAI API error for {request.symbol}: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error generating AI advice for {request.symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate trading advice. Please try again."
        )

def generate_demo_advice(prompt: str, symbol: str) -> str:
    """
    Generate user-friendly demo trading advice with win rates and specific prices
    
    Args:
        prompt: Analysis prompt with technical indicators
        symbol: Trading symbol
    
    Returns:
        User-friendly demo trading advice with win rates and trigger prices
    """
    import re
    import random
    
    # Extract technical indicators from prompt for realistic advice
    rsi_match = re.search(r'RSI:\s*([\d.]+)', prompt)
    macd_match = re.search(r'MACD.*Line\s*([-\d.]+).*Signal\s*([-\d.]+)', prompt)
    bb_match = re.search(r'Position\s*"?(\w+)"?', prompt)
    trend_match = re.search(r'Trend:\s*(\w+)', prompt)
    price_match = re.search(r'Current Price:\s*\$?([\d,]+\.?\d*)', prompt)
    
    rsi = float(rsi_match.group(1)) if rsi_match else 50.0
    bb_position = bb_match.group(1) if bb_match else "middle"
    trend = trend_match.group(1) if trend_match else "neutral"
    
    # Extract current price or use demo price
    if price_match:
        current_price = float(price_match.group(1).replace(',', ''))
    else:
        # Demo prices based on symbol
        demo_prices = {'BTCUSDT': 60000, 'ETHUSDT': 3200, 'SOLUSDT': 140, 'XRPUSDT': 0.50}
        current_price = demo_prices.get(symbol, 50000)
    
    # Calculate win rates based on technical conditions
    if rsi > 70 and bb_position == "upper_band":
        long_win_rate = random.randint(25, 40)  # Overbought = lower long probability
        short_win_rate = random.randint(70, 85)
    elif rsi < 30 and bb_position == "lower_band":
        long_win_rate = random.randint(75, 90)  # Oversold = higher long probability
        short_win_rate = random.randint(20, 35)
    elif trend == "bullish":
        long_win_rate = random.randint(65, 80)
        short_win_rate = random.randint(30, 45)
    elif trend == "bearish":
        long_win_rate = random.randint(25, 40)
        short_win_rate = random.randint(65, 80)
    else:
        long_win_rate = random.randint(45, 55)
        short_win_rate = random.randint(45, 55)
    
    # Calculate specific trigger prices
    long_entry = current_price * 0.985  # 1.5% below current
    long_stop = long_entry * 0.95      # 5% stop loss
    long_target = long_entry * 1.12    # 12% target
    
    short_entry = current_price * 1.015  # 1.5% above current
    short_stop = short_entry * 1.05     # 5% stop loss
    short_target = short_entry * 0.88   # 12% target
    
    wait_for_long = current_price * 0.97   # Better long opportunity
    wait_for_short = current_price * 1.03  # Better short opportunity
    
    # Fun trading/poker jokes
    jokes = [
        "Time to see what cards the market is dealing us! 🃏",
        "This setup reminds me of pocket aces - looks promising, but don't get cocky! 🅰️🅰️",
        "Market's been bluffing lately, but I think we're about to see the real cards! 🎭",
        "Sometimes you gotta fold a mediocre hand to wait for the nuts! 🃏",
        "Don't go all-in on a 7-2 offsuit - even if it 'feels' lucky! 😅",
        "The house always wins... unless you play smarter than the house! 🏠",
        "Bulls make money, bears make money, but fish get eaten by sharks! 🦈"
    ]
    
    advice = f"""
🎉 **Hey DANSIDANUTZ!** Time for some {symbol} action!
{random.choice(jokes)}

═══════════════════════════════════════════════════════════

🎰 **THE ODDS** (Your Hand Strength)

🟢 **LONG Position**: {long_win_rate}% probability
   {
       "🔥 Strong hand - bet with confidence!" if long_win_rate >= 70
       else "👍 Decent hand - moderate bet" if long_win_rate >= 55
       else "🤏 Weak hand - small bet or fold"
   }

🔴 **SHORT Position**: {short_win_rate}% probability  
   {
       "🔥 Strong hand - bet with confidence!" if short_win_rate >= 70
       else "👍 Decent hand - moderate bet" if short_win_rate >= 55  
       else "🤏 Weak hand - small bet or fold"
   }

═══════════════════════════════════════════════════════════

🎯 **SPECIFIC TRIGGER PRICES**

📈 **LONG SETUP:**
   • Entry Price:      ${long_entry:,.2f}
   • Stop-Loss:        ${long_stop:,.2f}  (-{((long_entry-long_stop)/long_entry*100):.1f}%)
   • Take-Profit:      ${long_target:,.2f} (+{((long_target-long_entry)/long_entry*100):.1f}%)

📉 **SHORT SETUP:**
   • Entry Price:      ${short_entry:,.2f}
   • Stop-Loss:        ${short_stop:,.2f}  (+{((short_stop-short_entry)/short_entry*100):.1f}%)
   • Take-Profit:      ${short_target:,.2f} (-{((short_entry-short_target)/short_entry*100):.1f}%)

═══════════════════════════════════════════════════════════

⏰ **WAITING STRATEGY** (For Higher Win Rates)

🎯 Better LONG opportunity:  Wait for ${wait_for_long:,.2f}
🎯 Better SHORT opportunity: Wait for ${wait_for_short:,.2f}

═══════════════════════════════════════════════════════════

🃏 **READING THE MARKET'S CARDS**

RSI at {rsi:.1f} {
    "is like holding pocket aces - looks great but could get cracked! 🚨" if rsi > 70
    else "is like getting dealt pocket kings in early position - time to raise! 🛒" if rsi < 30
    else "is giving us a suited connector - decent hand, play it smart ⚖️"
}

Combined with the **{trend}** trend, this feels like a **{
    "SHORT" if short_win_rate > long_win_rate else "LONG"
}** hand worth playing.

═══════════════════════════════════════════════════════════

💰 **POSITION SIZING & RISK MANAGEMENT**

• Risk only 2-3% of your total portfolio
• Even Phil Ivey doesn't bet the farm on every hand! 🎰
• Set your stops and stick to them - discipline wins the game

═══════════════════════════════════════════════════════════

⚠️ **DEMO MODE ALERT**
This is demo analysis! For the real ChatGPT-5 magic with live market 
intelligence, configure your OpenAI API key! ✨

═══════════════════════════════════════════════════════════
    """
    
    return advice.strip()

@router.get("/status")
async def get_openai_status() -> Dict[str, Any]:
    """
    Get OpenAI service status
    
    Returns:
        Service status and configuration
    """
    # Check API keys manager status
    openai_manager_status = is_service_available('openai')
    openai_config = get_api_key('openai')
    
    return {
        "success": True,
        "service_available": openai_client is not None,
        "api_key_configured": openai_api_key is not None,
        "api_keys_manager": {
            "openai_configured": openai_manager_status,
            "service_active": openai_config.get('is_active', False) if openai_config else False,
            "last_used": openai_config.get('last_used') if openai_config else None,
            "usage_count": openai_config.get('usage_count', 0) if openai_config else 0
        },
        "supported_models": ["gpt-5", "chatgpt-5", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "endpoints": {
            "trading_advice": "/openai/trading-advice",
            "status": "/openai/status"
        },
        "configuration": {
            "default_model": "gpt-5",
            "actual_model_used": "gpt-4",
            "default_temperature": 0.7,
            "default_max_tokens": 800,
            "model_mapping": "gpt-5 -> gpt-4 (latest available)",
            "rate_limits": "Varies by OpenAI plan"
        }
    }