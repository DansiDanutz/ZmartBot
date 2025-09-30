#!/usr/bin/env python3
"""
Real-Time KingFisher Image Analyzer
Monitors Telegram channel, analyzes images, stores results, creates summaries
"""

import asyncio
import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import httpx
import cv2
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ImageAnalysis:
    """Analysis result for a single image"""
    image_id: str
    symbol: str
    timestamp: datetime
    significance_score: float
    market_sentiment: str
    confidence: float
    liquidation_clusters: List[Dict]
    toxic_flow: float
    image_path: str
    analysis_data: Dict[str, Any]

@dataclass
class SymbolSummary:
    """Summary for a trading symbol based on multiple images"""
    symbol: str
    last_update: datetime
    total_images: int
    average_significance: float
    dominant_sentiment: str
    high_significance_count: int
    recent_trend: str
    risk_level: str
    latest_analysis: Optional[ImageAnalysis]

class RealTimeAnalyzer:
    """Real-time KingFisher image analyzer with persistent storage"""
    
    def __init__(self, db_path: str = "kingfisher_analysis.db"):
        self.db_path = db_path
        self.telegram_service = None
        self.image_processor = None
        self.airtable_service = None
        self.analysis_cache = {}
        self.symbol_summaries = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for storing analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id TEXT UNIQUE,
                symbol TEXT,
                timestamp TEXT,
                significance_score REAL,
                market_sentiment TEXT,
                confidence REAL,
                liquidation_clusters TEXT,
                toxic_flow REAL,
                image_path TEXT,
                analysis_data TEXT
            )
        ''')
        
        # Create symbol summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbol_summaries (
                symbol TEXT PRIMARY KEY,
                last_update TEXT,
                total_images INTEGER,
                average_significance REAL,
                dominant_sentiment TEXT,
                high_significance_count INTEGER,
                recent_trend TEXT,
                risk_level TEXT,
                latest_analysis_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    async def start_monitoring(self, telegram_service, image_processor, airtable_service=None):
        """Start real-time monitoring of KingFisher channel"""
        self.telegram_service = telegram_service
        self.image_processor = image_processor
        self.airtable_service = airtable_service
        
        logger.info("🚀 Starting real-time KingFisher monitoring...")
        
        # Test Airtable connection if available
        if self.airtable_service:
            airtable_connected = await self.airtable_service.test_connection()
            if airtable_connected:
                logger.info("✅ Airtable integration active")
            else:
                logger.warning("⚠️ Airtable connection failed, using local storage only")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        return True
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                # Check for new images from Telegram
                new_images = await self._get_new_images()
                
                for image_data in new_images:
                    await self._process_new_image(image_data)
                
                # Update symbol summaries
                await self._update_symbol_summaries()
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _get_new_images(self) -> List[Dict]:
        """Get new images from Telegram channel"""
        # This would integrate with your Telegram service
        # For now, we'll simulate getting new images
        return []
    
    async def _process_new_image(self, image_data: Dict):
        """Process a new image and store analysis"""
        try:
            image_path = image_data.get('path')
            symbol = image_data.get('symbol', 'UNKNOWN')
            image_id = image_data.get('id', str(datetime.now().timestamp()))
            
            logger.info(f"🔍 Processing new image for {symbol}: {image_path}")
            
            # Analyze the image
            analysis_result = await self.image_processor.process_image(image_path)
            
            # Create analysis object
            analysis = ImageAnalysis(
                image_id=image_id,
                symbol=symbol,
                timestamp=datetime.now(),
                significance_score=analysis_result.get('significance_score', 0),
                market_sentiment=analysis_result.get('market_sentiment', 'neutral'),
                confidence=analysis_result.get('confidence', 0),
                liquidation_clusters=analysis_result.get('liquidation_clusters', []),
                toxic_flow=analysis_result.get('toxic_flow', 0),
                image_path=image_path,
                analysis_data=analysis_result
            )
            
            # Store analysis in database
            await self._store_analysis(analysis)
            
            # Store in Airtable if available
            if self.airtable_service:
                await self._store_analysis_in_airtable(analysis)
            
            # Update cache
            self.analysis_cache[image_id] = analysis
            
            # Send alert if high significance
            if analysis.significance_score > 0.7:
                await self._send_high_significance_alert(analysis)
            
            logger.info(f"✅ Image analysis completed for {symbol}")
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
    
    async def _store_analysis_in_airtable(self, analysis: ImageAnalysis):
        """Store analysis in Airtable"""
        try:
            analysis_data = {
                "image_id": analysis.image_id,
                "symbol": analysis.symbol,
                "timestamp": analysis.timestamp.isoformat(),
                "significance_score": analysis.significance_score,
                "market_sentiment": analysis.market_sentiment,
                "confidence": analysis.confidence,
                "liquidation_clusters": analysis.liquidation_clusters,
                "toxic_flow": analysis.toxic_flow,
                "image_path": analysis.image_path,
                "analysis_data": analysis.analysis_data
            }
            
            success = await self.airtable_service.store_image_analysis(analysis_data)
            if success:
                logger.info(f"💾 Stored analysis for {analysis.symbol} in Airtable")
            else:
                logger.error(f"❌ Failed to store analysis for {analysis.symbol} in Airtable")
                
        except Exception as e:
            logger.error(f"Error storing analysis in Airtable: {e}")
    
    async def _store_analysis(self, analysis: ImageAnalysis):
        """Store analysis result in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO image_analyses 
                (image_id, symbol, timestamp, significance_score, market_sentiment, 
                 confidence, liquidation_clusters, toxic_flow, image_path, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis.image_id,
                analysis.symbol,
                analysis.timestamp.isoformat(),
                analysis.significance_score,
                analysis.market_sentiment,
                analysis.confidence,
                json.dumps(analysis.liquidation_clusters),
                analysis.toxic_flow,
                analysis.image_path,
                json.dumps(analysis.analysis_data)
            ))
            
            conn.commit()
            logger.info(f"💾 Stored analysis for {analysis.symbol}")
            
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
        finally:
            conn.close()
    
    async def _update_symbol_summaries(self):
        """Update summaries for all symbols"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all symbols
            cursor.execute("SELECT DISTINCT symbol FROM image_analyses")
            symbols = [row[0] for row in cursor.fetchall()]
            
            for symbol in symbols:
                summary = await self._calculate_symbol_summary(symbol)
                await self._store_symbol_summary(summary)
                
                # Store in Airtable if available
                if self.airtable_service:
                    await self._store_summary_in_airtable(summary)
                
        except Exception as e:
            logger.error(f"Error updating symbol summaries: {e}")
        finally:
            conn.close()
    
    async def _store_summary_in_airtable(self, summary: SymbolSummary):
        """Store symbol summary in Airtable"""
        try:
            summary_data = {
                "symbol": summary.symbol,
                "last_update": summary.last_update.isoformat(),
                "total_images": summary.total_images,
                "average_significance": summary.average_significance,
                "dominant_sentiment": summary.dominant_sentiment,
                "high_significance_count": summary.high_significance_count,
                "recent_trend": summary.recent_trend,
                "risk_level": summary.risk_level,
                "latest_analysis_id": summary.latest_analysis.image_id if summary.latest_analysis else None
            }
            
            success = await self.airtable_service.store_symbol_summary(summary_data)
            if success:
                logger.info(f"💾 Stored summary for {summary.symbol} in Airtable")
            else:
                logger.error(f"❌ Failed to store summary for {summary.symbol} in Airtable")
                
        except Exception as e:
            logger.error(f"Error storing summary in Airtable: {e}")
    
    async def _calculate_symbol_summary(self, symbol: str) -> SymbolSummary:
        """Calculate summary for a specific symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all analyses for this symbol
            cursor.execute('''
                SELECT * FROM image_analyses 
                WHERE symbol = ? 
                ORDER BY timestamp DESC
            ''', (symbol,))
            
            rows = cursor.fetchall()
            
            if not rows:
                return SymbolSummary(
                    symbol=symbol,
                    last_update=datetime.now(),
                    total_images=0,
                    average_significance=0,
                    dominant_sentiment='neutral',
                    high_significance_count=0,
                    recent_trend='stable',
                    risk_level='low',
                    latest_analysis=None
                )
            
            # Calculate summary statistics
            total_images = len(rows)
            significance_scores = [row[4] for row in rows]
            sentiments = [row[5] for row in rows]
            
            average_significance = sum(significance_scores) / len(significance_scores)
            high_significance_count = sum(1 for score in significance_scores if score > 0.7)
            
            # Determine dominant sentiment
            sentiment_counts = {}
            for sentiment in sentiments:
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
            
            # Determine recent trend (last 5 images)
            recent_scores = significance_scores[:5]
            if len(recent_scores) >= 2:
                if recent_scores[0] > recent_scores[-1] * 1.1:
                    recent_trend = 'increasing'
                elif recent_scores[0] < recent_scores[-1] * 0.9:
                    recent_trend = 'decreasing'
                else:
                    recent_trend = 'stable'
            else:
                recent_trend = 'stable'
            
            # Determine risk level
            if average_significance > 0.8:
                risk_level = 'high'
            elif average_significance > 0.6:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            # Get latest analysis
            latest_row = rows[0]
            latest_analysis = ImageAnalysis(
                image_id=latest_row[1],
                symbol=latest_row[2],
                timestamp=datetime.fromisoformat(latest_row[3]),
                significance_score=latest_row[4],
                market_sentiment=latest_row[5],
                confidence=latest_row[6],
                liquidation_clusters=json.loads(latest_row[7]),
                toxic_flow=latest_row[8],
                image_path=latest_row[9],
                analysis_data=json.loads(latest_row[10])
            )
            
            return SymbolSummary(
                symbol=symbol,
                last_update=datetime.now(),
                total_images=total_images,
                average_significance=average_significance,
                dominant_sentiment=dominant_sentiment,
                high_significance_count=high_significance_count,
                recent_trend=recent_trend,
                risk_level=risk_level,
                latest_analysis=latest_analysis
            )
            
        except Exception as e:
            logger.error(f"Error calculating summary for {symbol}: {e}")
            return SymbolSummary(
                symbol=symbol,
                last_update=datetime.now(),
                total_images=0,
                average_significance=0,
                dominant_sentiment='neutral',
                high_significance_count=0,
                recent_trend='stable',
                risk_level='low',
                latest_analysis=None
            )
        finally:
            conn.close()
    
    async def _store_symbol_summary(self, summary: SymbolSummary):
        """Store symbol summary in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO symbol_summaries 
                (symbol, last_update, total_images, average_significance, 
                 dominant_sentiment, high_significance_count, recent_trend, 
                 risk_level, latest_analysis_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary.symbol,
                summary.last_update.isoformat(),
                summary.total_images,
                summary.average_significance,
                summary.dominant_sentiment,
                summary.high_significance_count,
                summary.recent_trend,
                summary.risk_level,
                summary.latest_analysis.image_id if summary.latest_analysis else None
            ))
            
            conn.commit()
            self.symbol_summaries[summary.symbol] = summary
            
        except Exception as e:
            logger.error(f"Error storing symbol summary: {e}")
        finally:
            conn.close()
    
    async def _send_high_significance_alert(self, analysis: ImageAnalysis):
        """Send alert for high significance analysis"""
        if self.telegram_service:
            message = f"""
🚨 HIGH SIGNIFICANCE ALERT!

📊 Symbol: {analysis.symbol}
🎯 Significance: {analysis.significance_score:.2%}
📈 Sentiment: {analysis.market_sentiment.title()}
🎯 Confidence: {analysis.confidence:.2%}
🔴 Liquidation Clusters: {len(analysis.liquidation_clusters)}
🟢 Toxic Flow: {analysis.toxic_flow:.2%}
⏰ Time: {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ IMMEDIATE ATTENTION REQUIRED!
"""
            await self.telegram_service.send_notification(message)
        
        # Store alert in Airtable if available
        if self.airtable_service:
            alert_data = {
                "symbol": analysis.symbol,
                "significance_score": analysis.significance_score,
                "market_sentiment": analysis.market_sentiment,
                "confidence": analysis.confidence,
                "liquidation_clusters": analysis.liquidation_clusters,
                "toxic_flow": analysis.toxic_flow,
                "alert_level": "High" if analysis.significance_score > 0.8 else "Medium",
                "timestamp": analysis.timestamp.isoformat()
            }
            await self.airtable_service.store_high_significance_alert(alert_data)
    
    async def get_symbol_summary(self, symbol: str) -> Optional[SymbolSummary]:
        """Get summary for a specific symbol"""
        return self.symbol_summaries.get(symbol)
    
    async def get_all_summaries(self) -> Dict[str, SymbolSummary]:
        """Get all symbol summaries"""
        return self.symbol_summaries.copy()
    
    async def get_recent_analyses(self, symbol: str = None, limit: int = 10) -> List[ImageAnalysis]:
        """Get recent analyses for a symbol or all symbols"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if symbol:
                cursor.execute('''
                    SELECT * FROM image_analyses 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (symbol, limit))
            else:
                cursor.execute('''
                    SELECT * FROM image_analyses 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            analyses = []
            
            for row in rows:
                analysis = ImageAnalysis(
                    image_id=row[1],
                    symbol=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    significance_score=row[4],
                    market_sentiment=row[5],
                    confidence=row[6],
                    liquidation_clusters=json.loads(row[7]),
                    toxic_flow=row[8],
                    image_path=row[9],
                    analysis_data=json.loads(row[10])
                )
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error getting recent analyses: {e}")
            return []
        finally:
            conn.close()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total analyses
            cursor.execute("SELECT COUNT(*) FROM image_analyses")
            total_analyses = cursor.fetchone()[0]
            
            # Total symbols
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM image_analyses")
            total_symbols = cursor.fetchone()[0]
            
            # High significance count
            cursor.execute("SELECT COUNT(*) FROM image_analyses WHERE significance_score > 0.7")
            high_significance_count = cursor.fetchone()[0]
            
            # Average significance
            cursor.execute("SELECT AVG(significance_score) FROM image_analyses")
            avg_significance = cursor.fetchone()[0] or 0
            
            return {
                'total_analyses': total_analyses,
                'total_symbols': total_symbols,
                'high_significance_count': high_significance_count,
                'average_significance': avg_significance,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close() 