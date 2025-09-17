"""
Dummy realtime_sentiment_agent module
"""

class RealtimeSentimentAgent:
    """Dummy RealtimeSentimentAgent class"""
    def __init__(self, *args, **kwargs):
        pass

    async def analyze_sentiment(self, *args, **kwargs):
        return {"sentiment": "neutral", "score": 0.5}

# Create a default instance
realtime_sentiment_agent = RealtimeSentimentAgent()