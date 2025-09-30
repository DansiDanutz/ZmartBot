#!/usr/bin/env python3
"""
KingFisher Advanced Analytics Dashboard
Real-time analytics and performance monitoring
"""

import asyncio
import httpx
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KingFisherAnalytics:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.analytics_data = {
            "processed_symbols": [],
            "success_rate": 0.0,
            "total_analyses": 0,
            "failed_analyses": 0,
            "average_processing_time": 0.0,
            "last_24h_activity": [],
            "top_symbols": [],
            "system_health": {}
        }
        
    async def get_airtable_data(self) -> Dict[str, Any]:
        """Get data from Airtable for analytics"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/records")
                
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    logger.error(f"❌ Failed to get Airtable data: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error getting Airtable data: {e}")
            return {}
    
    async def calculate_success_rate(self, records: List[Dict]) -> float:
        """Calculate success rate from processed records"""
        if not records:
            return 0.0
        
        successful = sum(1 for record in records if record.get('fields', {}).get('Result'))
        total = len(records)
        
        return (successful / total) * 100 if total > 0 else 0.0
    
    async def get_top_symbols(self, records: List[Dict], limit: int = 10) -> List[Dict]:
        """Get most frequently processed symbols"""
        symbol_counts = {}
        
        for record in records:
            symbol = record.get('fields', {}).get('Symbol')
            if symbol:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        # Sort by count and return top symbols
        sorted_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"symbol": symbol, "count": count, "percentage": (count / len(records)) * 100}
            for symbol, count in sorted_symbols[:limit]
        ]
    
    async def get_recent_activity(self, records: List[Dict], hours: int = 24) -> List[Dict]:
        """Get recent activity from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_records = []
        for record in records:
            created_time = record.get('createdTime')
            if created_time:
                try:
                    record_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    if record_time > cutoff_time:
                        recent_records.append(record)
                except:
                    continue
        
        return recent_records
    
    async def calculate_processing_metrics(self, records: List[Dict]) -> Dict[str, Any]:
        """Calculate processing performance metrics"""
        if not records:
            return {
                "total_analyses": 0,
                "failed_analyses": 0,
                "success_rate": 0.0,
                "average_processing_time": 0.0
            }
        
        total = len(records)
        successful = sum(1 for record in records if record.get('fields', {}).get('Result'))
        failed = total - successful
        success_rate = (successful / total) * 100 if total > 0 else 0.0
        
        # Estimate processing time (mock calculation)
        avg_processing_time = 2.5  # seconds per analysis
        
        return {
            "total_analyses": total,
            "failed_analyses": failed,
            "success_rate": success_rate,
            "average_processing_time": avg_processing_time
        }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Check KingFisher server
                health_response = await client.get(f"{self.base_url}/health")
                server_healthy = health_response.status_code == 200
                
                # Check Airtable connection
                airtable_response = await client.get(f"{self.base_url}/api/v1/airtable/status")
                airtable_connected = airtable_response.status_code == 200
                
                return {
                    "server_healthy": server_healthy,
                    "airtable_connected": airtable_connected,
                    "last_check": datetime.now().isoformat(),
                    "overall_status": "healthy" if server_healthy and airtable_connected else "degraded"
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking system health: {e}")
            return {
                "server_healthy": False,
                "airtable_connected": False,
                "last_check": datetime.now().isoformat(),
                "overall_status": "unhealthy",
                "error": str(e)
            }
    
    async def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        logger.info("📊 Generating analytics report...")
        
        # Get Airtable data
        airtable_data = await self.get_airtable_data()
        records = airtable_data.get('records', [])
        
        # Calculate metrics
        success_rate = await self.calculate_success_rate(records)
        top_symbols = await self.get_top_symbols(records)
        recent_activity = await self.get_recent_activity(records)
        processing_metrics = await self.calculate_processing_metrics(records)
        system_health = await self.check_system_health()
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_symbols_processed": len(records),
                "success_rate": f"{success_rate:.1f}%",
                "recent_activity_count": len(recent_activity),
                "system_status": system_health['overall_status']
            },
            "performance": processing_metrics,
            "top_symbols": top_symbols,
            "recent_activity": [
                {
                    "symbol": record.get('fields', {}).get('Symbol', 'Unknown'),
                    "timestamp": record.get('createdTime', ''),
                    "has_analysis": bool(record.get('fields', {}).get('Result'))
                }
                for record in recent_activity
            ],
            "system_health": system_health
        }
        
        return report
    
    def print_analytics_dashboard(self, report: Dict[str, Any]):
        """Print formatted analytics dashboard"""
        print("\n" + "="*80)
        print("🐟 KingFisher Analytics Dashboard")
        print("="*80)
        
        # Summary
        summary = report['summary']
        print(f"\n📊 SUMMARY")
        print(f"   Total Symbols Processed: {summary['total_symbols_processed']}")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Recent Activity (24h): {summary['recent_activity_count']}")
        print(f"   System Status: {summary['system_status'].upper()}")
        
        # Performance
        performance = report['performance']
        print(f"\n⚡ PERFORMANCE")
        print(f"   Total Analyses: {performance['total_analyses']}")
        print(f"   Failed Analyses: {performance['failed_analyses']}")
        print(f"   Success Rate: {performance['success_rate']:.1f}%")
        print(f"   Avg Processing Time: {performance['average_processing_time']:.1f}s")
        
        # Top Symbols
        print(f"\n🏆 TOP SYMBOLS")
        for i, symbol_data in enumerate(report['top_symbols'][:5], 1):
            print(f"   {i}. {symbol_data['symbol']}: {symbol_data['count']} analyses ({symbol_data['percentage']:.1f}%)")
        
        # Recent Activity
        print(f"\n🕒 RECENT ACTIVITY (Last 24h)")
        for activity in report['recent_activity'][:10]:
            status = "✅" if activity['has_analysis'] else "❌"
            print(f"   {status} {activity['symbol']} - {activity['timestamp'][:19]}")
        
        # System Health
        health = report['system_health']
        print(f"\n🔧 SYSTEM HEALTH")
        print(f"   Server: {'✅ Healthy' if health['server_healthy'] else '❌ Unhealthy'}")
        print(f"   Airtable: {'✅ Connected' if health['airtable_connected'] else '❌ Disconnected'}")
        print(f"   Last Check: {health['last_check'][:19]}")
        
        print("\n" + "="*80)

async def main():
    """Main analytics function"""
    analytics = KingFisherAnalytics()
    
    print("🚀 Starting KingFisher Analytics Dashboard...")
    
    # Generate and display report
    report = await analytics.generate_analytics_report()
    analytics.print_analytics_dashboard(report)
    
    print("\n✅ Analytics dashboard complete!")

if __name__ == "__main__":
    asyncio.run(main()) 