#!/usr/bin/env python3
"""
Automated Health Check Scheduler - Runs periodic system health checks
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/health_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HealthScheduler')

class AutomatedHealthScheduler:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.dashboard_url = "http://localhost:8080"
        self.health_data = {
            "checks_performed": 0,
            "last_check": None,
            "status_history": [],
            "alerts": []
        }
        
    async def check_api_health(self, session):
        """Check main API endpoints health"""
        endpoints = [
            "/v1/health",
            "/v1/signals/snapshot?symbol=ETH",
            "/v1/pools/1"
        ]
        
        results = {"healthy": 0, "total": len(endpoints), "details": {}}
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                async with session.get(f"{self.base_url}{endpoint}") as resp:
                    response_time = (time.time() - start_time) * 1000
                    
                    if resp.status == 200:
                        results["healthy"] += 1
                        results["details"][endpoint] = {
                            "status": "healthy",
                            "response_time": round(response_time, 2),
                            "status_code": resp.status
                        }
                    else:
                        results["details"][endpoint] = {
                            "status": "warning",
                            "response_time": round(response_time, 2),
                            "status_code": resp.status
                        }
                        
            except Exception as e:
                results["details"][endpoint] = {
                    "status": "error",
                    "error": str(e),
                    "response_time": None
                }
                
        return results
    
    async def check_frontend_health(self, session):
        """Check frontend application health"""
        try:
            async with session.get(self.frontend_url, timeout=5) as resp:
                return {
                    "status": "healthy" if resp.status == 200 else "warning",
                    "status_code": resp.status,
                    "accessible": True
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "accessible": False
            }
    
    async def check_dashboard_health(self, session):
        """Check monitoring dashboard health"""
        try:
            async with session.get(self.dashboard_url, timeout=5) as resp:
                return {
                    "status": "healthy" if resp.status == 200 else "warning", 
                    "status_code": resp.status,
                    "accessible": True
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "accessible": False
            }
    
    def analyze_health_trends(self):
        """Analyze health trends and generate alerts"""
        alerts = []
        
        if len(self.health_data["status_history"]) >= 3:
            recent_checks = self.health_data["status_history"][-3:]
            
            # Check for consistent API issues
            api_failures = sum(1 for check in recent_checks if check["api"]["healthy"] < 2)
            if api_failures >= 2:
                alerts.append({
                    "severity": "high",
                    "message": f"API health degraded in {api_failures}/3 recent checks",
                    "timestamp": datetime.now().isoformat(),
                    "type": "api_degradation"
                })
            
            # Check for frontend downtime
            frontend_failures = sum(1 for check in recent_checks if check["frontend"]["status"] != "healthy")
            if frontend_failures >= 2:
                alerts.append({
                    "severity": "medium", 
                    "message": f"Frontend issues detected in {frontend_failures}/3 recent checks",
                    "timestamp": datetime.now().isoformat(),
                    "type": "frontend_issues"
                })
                
        return alerts
    
    async def perform_health_check(self):
        """Perform comprehensive health check"""
        logger.info("🔍 Starting automated health check...")
        check_start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Run all health checks concurrently
            api_task = self.check_api_health(session)
            frontend_task = self.check_frontend_health(session)
            dashboard_task = self.check_dashboard_health(session)
            
            api_health, frontend_health, dashboard_health = await asyncio.gather(
                api_task, frontend_task, dashboard_task
            )
        
        # Compile results
        check_duration = time.time() - check_start_time
        timestamp = datetime.now()
        
        health_status = {
            "timestamp": timestamp.isoformat(),
            "check_duration": round(check_duration, 3),
            "api": api_health,
            "frontend": frontend_health,
            "dashboard": dashboard_health,
            "overall_status": self.calculate_overall_status(api_health, frontend_health, dashboard_health)
        }
        
        # Update health data
        self.health_data["checks_performed"] += 1
        self.health_data["last_check"] = timestamp.isoformat()
        self.health_data["status_history"].append(health_status)
        
        # Keep only last 20 checks
        if len(self.health_data["status_history"]) > 20:
            self.health_data["status_history"].pop(0)
        
        # Analyze trends and generate alerts
        new_alerts = self.analyze_health_trends()
        self.health_data["alerts"].extend(new_alerts)
        
        # Keep only last 10 alerts
        if len(self.health_data["alerts"]) > 10:
            self.health_data["alerts"] = self.health_data["alerts"][-10:]
        
        # Log results
        self.log_health_status(health_status, new_alerts)
        
        # Save health data
        await self.save_health_data()
        
        return health_status
    
    def calculate_overall_status(self, api_health, frontend_health, dashboard_health):
        """Calculate overall system status"""
        api_score = api_health["healthy"] / api_health["total"]
        frontend_score = 1.0 if frontend_health["status"] == "healthy" else 0.5 if frontend_health["status"] == "warning" else 0.0
        dashboard_score = 1.0 if dashboard_health["status"] == "healthy" else 0.5 if dashboard_health["status"] == "warning" else 0.0
        
        overall_score = (api_score * 0.5 + frontend_score * 0.3 + dashboard_score * 0.2)
        
        if overall_score >= 0.8:
            return "healthy"
        elif overall_score >= 0.5:
            return "warning"
        else:
            return "critical"
    
    def log_health_status(self, health_status, new_alerts):
        """Log health check results"""
        overall_status = health_status["overall_status"]
        api_healthy = health_status["api"]["healthy"]
        api_total = health_status["api"]["total"]
        
        status_emoji = "✅" if overall_status == "healthy" else "⚠️" if overall_status == "warning" else "❌"
        
        logger.info(f"{status_emoji} Health Check #{self.health_data['checks_performed']} - Overall: {overall_status.upper()}")
        logger.info(f"📊 API: {api_healthy}/{api_total} healthy | Frontend: {health_status['frontend']['status']} | Dashboard: {health_status['dashboard']['status']}")
        logger.info(f"⏱️  Check duration: {health_status['check_duration']}s")
        
        if new_alerts:
            logger.warning(f"🚨 {len(new_alerts)} new alerts generated")
            for alert in new_alerts:
                logger.warning(f"   • {alert['severity'].upper()}: {alert['message']}")
    
    async def save_health_data(self):
        """Save health data to file"""
        try:
            with open('/Users/dansidanutz/Desktop/ZmartBot/health_data.json', 'w') as f:
                json.dump(self.health_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save health data: {e}")
    
    async def run_scheduler(self, interval_seconds=30):
        """Run the health check scheduler"""
        logger.info(f"🚀 Starting Automated Health Scheduler (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.perform_health_check()
                await asyncio.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("🛑 Health scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in health check: {e}")
                await asyncio.sleep(interval_seconds)

async def main():
    """Main function"""
    scheduler = AutomatedHealthScheduler()
    
    # Run initial health check
    await scheduler.perform_health_check()
    
    # Start continuous monitoring (every 30 seconds)
    await scheduler.run_scheduler(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Health scheduler stopped.")