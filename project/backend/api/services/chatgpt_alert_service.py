#!/usr/bin/env python3
"""
Real Technical Analysis Alert Service
Generates alerts based on ACTUAL Binance API data - NO MOCK DATA
"""

import asyncio
import logging
import json
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import openai
from openai import OpenAI
from .technical_analysis_service import technical_analysis_service

logger = logging.getLogger(__name__)

@dataclass
class AlertData:
    """Alert data structure"""
    symbol: str
    alert_type: str
    indicator: str
    value: float
    threshold: float
    timeframe: str
    price: float
    timestamp: datetime
    confidence: float

@dataclass
class ChatGPTAlert:
    """Real technical analysis alert"""
    title: str
    description: str
    analysis: str
    recommendation: str
    risk_level: str
    timestamp: datetime
    symbol: str
    alert_type: str
    real_data: bool = True

class RealTechnicalAlertService:
    """Real technical analysis alert service - NO MOCK DATA"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Real Technical Alert Service"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Real alerts will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("✅ Real Technical Alert Service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                self.enabled = False

        # Alert templates for real data scenarios
        self.alert_templates = {
            "golden_cross": {
                "title": "🔄 Golden Cross Detected!",
                "description": "EMA12 crossed above EMA26",
                "analysis": "This bullish signal indicates potential upward momentum",
                "recommendation": "Consider long positions with proper risk management",
                "risk_level": "medium"
            },
            "death_cross": {
                "title": "⚠️ Death Cross Detected!",
                "description": "EMA12 crossed below EMA26",
                "analysis": "This bearish signal indicates potential downward momentum",
                "recommendation": "Consider short positions or exit long positions",
                "risk_level": "high"
            },
            "rsi_overbought": {
                "title": "📈 RSI Overbought Alert!",
                "description": "RSI indicates overbought conditions",
                "analysis": "Price may be due for a correction or reversal",
                "recommendation": "Consider taking profits or waiting for pullback",
                "risk_level": "medium"
            },
            "rsi_oversold": {
                "title": "📉 RSI Oversold Alert!",
                "description": "RSI indicates oversold conditions",
                "analysis": "Price may be due for a bounce or reversal",
                "recommendation": "Consider buying opportunities with proper risk management",
                "risk_level": "medium"
            },
            "macd_bullish": {
                "title": "🚀 MACD Bullish Signal!",
                "description": "MACD line crossed above signal line",
                "analysis": "Momentum is turning bullish",
                "recommendation": "Consider long positions",
                "risk_level": "medium"
            },
            "macd_bearish": {
                "title": "📉 MACD Bearish Signal!",
                "description": "MACD line crossed below signal line",
                "analysis": "Momentum is turning bearish",
                "recommendation": "Consider short positions or exit longs",
                "risk_level": "medium"
            },
            "bollinger_upper": {
                "title": "⚡ Price at Bollinger Upper Band!",
                "description": "Price reached upper Bollinger Band",
                "analysis": "Price may be overextended and due for reversal",
                "recommendation": "Consider taking profits or waiting for pullback",
                "risk_level": "medium"
            },
            "bollinger_lower": {
                "title": "💎 Price at Bollinger Lower Band!",
                "description": "Price reached lower Bollinger Band",
                "analysis": "Price may be oversold and due for bounce",
                "recommendation": "Consider buying opportunities",
                "risk_level": "medium"
            }
        }



    async def perform_real_technical_analysis(self, symbol: str) -> Dict:
        """Perform REAL technical analysis using database data"""
        try:
            # Perform real technical analysis using database data
            analysis = await technical_analysis_service.get_technical_analysis(symbol)
            
            if not analysis:
                return {
                    "error": "No database data available",
                    "real_data": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            analysis["real_data"] = True
            analysis["data_source"] = "Database"
            analysis["symbol"] = symbol
            
            logger.info(f"✅ Real technical analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in real technical analysis for {symbol}: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "real_data": False,
                "timestamp": datetime.now().isoformat()
            }

    async def generate_real_alert(self, alert_data: AlertData) -> ChatGPTAlert:
        """Generate alert based on REAL technical analysis - NO MOCK DATA"""
        if not self.enabled:
            return self._generate_no_data_alert(alert_data)

        try:
            # Perform REAL technical analysis
            real_analysis = await self.perform_real_technical_analysis(alert_data.symbol)
            
            if not real_analysis.get("real_data", False):
                return self._generate_no_data_alert(alert_data)
            
            # Create prompt with REAL analysis data
            prompt = self._create_real_analysis_prompt(alert_data, real_analysis)

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency trading analyst. Generate alerts based ONLY on REAL technical analysis data from Binance API. NEVER mention patterns that are not actually detected. Be specific, professional, and provide clear risk management advice."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from ChatGPT")

            # Parse response
            alert = self._parse_real_alert_response(content, alert_data, real_analysis)
            logger.info(f"✅ Generated REAL alert for {alert_data.symbol}: {alert.title}")
            return alert

        except Exception as e:
            logger.error(f"❌ Error generating real alert: {e}")
            return self._generate_no_data_alert(alert_data)

    def _create_real_analysis_prompt(self, alert_data: AlertData, real_analysis: Dict) -> str:
        """Create prompt with REAL technical analysis data from database"""
        
        current_price = real_analysis.get("current_price", alert_data.price)
        data_source = real_analysis.get("data_source", "Database")
        
        # Build REAL pattern summary from database data
        detected_patterns = []
        
        # Check EMA data for crossovers
        ema_data = real_analysis.get("ema_data", {})
        if ema_data:
            for timeframe, data in ema_data.items():
                if data.get("golden_cross_detected"):
                    detected_patterns.append(f"✅ REAL Golden Cross ({timeframe}): EMA12 > EMA26")
                if data.get("death_cross_detected"):
                    detected_patterns.append(f"⚠️ REAL Death Cross ({timeframe}): EMA12 < EMA26")
        
        # Check RSI data
        rsi_data = real_analysis.get("rsi_data", {})
        if rsi_data:
            for timeframe, data in rsi_data.items():
                rsi_value = data.get("rsi_value")
                signal_status = data.get("signal_status")
                if rsi_value and signal_status:
                    detected_patterns.append(f"📊 REAL RSI ({timeframe}): {rsi_value:.2f} - {signal_status}")
        
        # Check MACD data
        macd_data = real_analysis.get("macd_data", {})
        if macd_data:
            for timeframe, data in macd_data.items():
                signal_status = data.get("signal_status")
                if signal_status:
                    detected_patterns.append(f"📈 REAL MACD ({timeframe}): {signal_status}")
        
        # Check Bollinger Bands data
        bb_data = real_analysis.get("bollinger_bands_timeframes", {})
        if bb_data:
            for timeframe, data in bb_data.items():
                band_position = data.get("band_position")
                if band_position:
                    detected_patterns.append(f"📊 REAL Bollinger Bands ({timeframe}): Price at {band_position}")
        
        # Check Stochastic data
        stoch_data = real_analysis.get("stochastic_data", {})
        if stoch_data:
            for timeframe, data in stoch_data.items():
                signal_status = data.get("signal_status")
                if signal_status:
                    detected_patterns.append(f"📊 REAL Stochastic ({timeframe}): {signal_status}")
        
        if not detected_patterns:
            detected_patterns.append("📊 NO REAL PATTERNS DETECTED - Market is neutral")
        
        return f"""
Generate a trading alert for {alert_data.symbol} based on REAL database data:

Symbol: {alert_data.symbol}
Current Price: ${current_price:.2f} (REAL from Database)
Timeframe: {alert_data.timeframe}
Data Source: {data_source}

REAL TECHNICAL PATTERNS DETECTED (from actual database data):
{chr(10).join(detected_patterns)}

CRITICAL: Only mention patterns that are ACTUALLY detected. If no patterns are detected, say "No significant patterns detected" and provide general market analysis.

Please provide:
1. A compelling title (max 50 characters)
2. Brief description of what was ACTUALLY detected
3. Technical analysis based on REAL data
4. Trading recommendation
5. Risk level (low/medium/high)

Format as JSON:
{{
    "title": "Alert Title",
    "description": "What was actually detected",
    "analysis": "Real technical analysis",
    "recommendation": "Trading advice",
    "risk_level": "medium"
}}

Be honest, professional, and based ONLY on real data.
"""

    def _parse_real_alert_response(self, content: str, alert_data: AlertData, real_analysis: Dict) -> ChatGPTAlert:
        """Parse ChatGPT response for real alert"""
        try:
            # Try to extract JSON from response
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                data = json.loads(json_str)
            else:
                # Fallback parsing
                lines = content.split('\n')
                data = {
                    "title": lines[0] if lines else "Real Technical Alert",
                    "description": lines[1] if len(lines) > 1 else "Real pattern detected",
                    "analysis": lines[2] if len(lines) > 2 else "Real technical analysis",
                    "recommendation": lines[3] if len(lines) > 3 else "Monitor closely",
                    "risk_level": "medium"
                }
            
            return ChatGPTAlert(
                title=data.get("title", "Real Technical Alert"),
                description=data.get("description", "Real pattern detected"),
                analysis=data.get("analysis", "Real technical analysis"),
                recommendation=data.get("recommendation", "Monitor closely"),
                risk_level=data.get("risk_level", "medium"),
                timestamp=alert_data.timestamp,
                symbol=alert_data.symbol,
                alert_type=alert_data.alert_type,
                real_data=True
            )
            
        except Exception as e:
            logger.error(f"Error parsing real alert response: {e}")
            return self._generate_no_data_alert(alert_data)

    def _generate_no_data_alert(self, alert_data: AlertData) -> ChatGPTAlert:
        """Generate alert when no real data is available"""
        return ChatGPTAlert(
            title="📊 No Real Data Available",
            description=f"Unable to fetch real data for {alert_data.symbol}",
            analysis="Real-time data from Binance API is required for technical analysis",
            recommendation="Check data connection and try again",
            risk_level="medium",
            timestamp=alert_data.timestamp,
            symbol=alert_data.symbol,
            alert_type=alert_data.alert_type,
            real_data=False
        )

    async def generate_multiple_real_alerts(self, alerts_data: List[AlertData]) -> List[ChatGPTAlert]:
        """Generate multiple alerts based on REAL data"""
        if not alerts_data:
            return []
        
        # Generate alerts concurrently
        tasks = [self.generate_real_alert(alert_data) for alert_data in alerts_data]
        alerts = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_alerts = []
        for alert in alerts:
            if isinstance(alert, ChatGPTAlert):
                valid_alerts.append(alert)
            else:
                logger.error(f"Failed to generate real alert: {alert}")
        
        return valid_alerts

# Global instance - NO MOCK DATA
chatgpt_alert_service = RealTechnicalAlertService()
