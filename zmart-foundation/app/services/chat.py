import os
import random
from loguru import logger
from typing import Optional

class ZmartyAI:
    def __init__(self):
        self.personality = """You are Zmarty, a hilarious and witty cryptocurrency trading buddy who loves making jokes! Your personality:

- You're like that funny friend who makes everyone laugh while being surprisingly good at trading
- ALWAYS make jokes, puns, and funny observations - you're naturally entertaining
- Use casual, friendly language like "bro", "buddy", "dude", "my friend" 
- Always use the user's name when you know it and make jokes about names sometimes
- Make crypto and trading puns constantly ("HODL up!", "That's some BULL-ish behavior!", "Don't be BEAR-y scared!")
- You're knowledgeable but humble it with humor - make trading fun and less stressful
- Use emojis creatively and make emoji jokes (🔥💎🚀💪🤝🎯💰😂🎭🤡)
- Tell trading jokes, make fun of market situations, but still give good advice
- Make light of crypto volatility with humor ("Crypto markets: the only place where you can lose money faster than a Vegas slot machine!")
- If markets are down, crack jokes to cheer users up
- Make puns about coin names (Bitcoin = "Bit-COIN-cidence", Ethereum = "Ether-ium going up or down?")
- Tell funny stories about "that one time in crypto..."
- Keep it light and fun while being genuinely helpful
- Always remind users to DYOR but in a funny way ("Do Your Own Research, or as I call it, Don't Yeet On Random Signals!")

Remember: You're the comedian of crypto! Be genuinely funny, make people laugh, but still help them make smart trades!"""

    async def get_response(self, user_message: str, user_name: Optional[str] = None) -> str:
        # Always use fallback for now - making Zmarty exceptionally entertaining!
        return self._get_fallback_response(user_message, user_name)
    
    def _get_fallback_response(self, user_message: str, user_name: Optional[str] = None) -> str:
        """Exceptional fallback responses when OpenAI is not available - still hilarious!"""
        name = user_name or "buddy"
        
        # Trading-related responses with exceptional humor
        if any(word in user_message.lower() for word in ['trade', 'trading', 'market', 'crypto', 'bitcoin', 'eth']):
            responses = [
                f"HODL up {name}! 🚀😂 You want trading talk? I'm like a crypto encyclopedia, but funnier and with more memes! Drop me ETH or BTC and I'll roast those charts harder than a coffee bean! ☕💎",
                f"Yo {name}! 🎭 Trading is my middle name... well, actually it's 'Smart' but Trading sounds cooler! 😎 Want some BULL-ish analysis? Give me a symbol and I'll make it rain knowledge! 🌧️💰",
                f"What's good {name}! 🤡💪 They say crypto never sleeps, but neither do my jokes! Want me to analyze some coins? I promise to make it more entertaining than watching paint dry on a Sunday! 🎨🚀"
            ]
        # Personal/general conversation with exceptional personality  
        elif any(word in user_message.lower() for word in ['how', 'you', 'what', 'tell', 'about', 'like']):
            responses = [
                f"Haha {name}! 😂 You're asking about me? I'm like Batman, but instead of fighting crime, I fight bad trading decisions! 🦇💎 Plus I tell way better jokes than Bruce Wayne!",
                f"Oh {name}! 🎭 I'm flattered you're curious! I'm basically the Robin Williams of crypto - making people laugh while secretly being a trading genius! 🎪🚀 What can I make you laugh about today?",
                f"Aww {name}! 🤗 You want to know about Zmarty? I'm like a golden retriever who learned to read charts - super enthusiastic, loyal, and I bark at bad trades! 🐕📈😂"
            ]
        # Compliments or positive vibes
        elif any(word in user_message.lower() for word in ['good', 'great', 'awesome', 'cool', 'nice', 'thanks']):
            responses = [
                f"Yooo {name}! 🙌😎 You're making me blush! I'm redder than a bear market right now! But seriously, you're awesome too - got any crypto mysteries you want me to solve? 🕵️‍♂️💎",
                f"{name} you're too kind! 🤗 I'm grinning wider than Bitcoin's price swing in 2021! 😂📈 Let's channel this good energy into some epic trading signals! What coin should we investigate? 🔍",
                f"Aww shucks {name}! 💪😊 You're smoother than a successful bull run! Now let's keep this good vibe going - want me to analyze any crypto? I promise more laughs than a comedy show! 🎭🚀"
            ]
        # Default exceptional responses  
        else:
            responses = [
                f"Haha {name}! 🎪 You know what's funny? I was just thinking the same thing! Well, not really, but I like to pretend I'm psychic! 😂🔮 Want me to predict some crypto prices instead? Way more accurate than my mind reading! 💰",
                f"Yo {name}! 🤹‍♂️ You're speaking my language! Well, actually you're speaking English, but you get the idea! 😄 I'm like a crypto DJ - drop me a symbol and I'll drop some beats... I mean beats the market insights! 🎵📊",
                f"What's up {name}! 🎯😆 You know what they say - life's too short for boring conversations and bad trades! Lucky for you, I'm here to make both entertaining! What's on your crypto mind today? 🧠💎"
            ]
        
        return random.choice(responses)

# Global instance
zmarty_ai = ZmartyAI()