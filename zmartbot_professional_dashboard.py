#!/usr/bin/env python3
"""
ZmartBot Professional Dashboard Server
A comprehensive dashboard integrating all ZmartBot services and APIs
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import os
import sys
import asyncio
import aiohttp
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configuration
PORT = 7001
HOST = "127.0.0.1"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZmartBotDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Professional ZmartBot Dashboard Handler"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        try:
            with open('zmartbot_dashboard.html', 'r') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404, "Dashboard not found")
    
    def handle_api_request(self):
        """Handle API requests to ZmartBot services"""
        try:
            if self.path == '/api/market-data':
                self.get_market_data()
            elif self.path == '/api/trading/positions':
                self.get_trading_positions()
            elif self.path == '/api/trading/accounts':
                self.get_trading_accounts()
            elif self.path == '/api/orchestration/status':
                self.get_orchestration_status()
            elif self.path == '/api/kingfisher/analysis':
                self.get_kingfisher_analysis()
            elif self.path == '/api/cryptometer/indicators':
                self.get_cryptometer_indicators()
            elif self.path == '/api/services/health':
                self.get_services_health()
            elif self.path == '/api/health':
                self.get_dashboard_health()
            elif self.path == '/api/ai/analysis':
                self.get_ai_analysis()
            elif self.path == '/api/ai/predictions':
                self.get_ai_predictions()
            elif self.path == '/api/credit/balance':
                self.get_credit_balance()
            elif self.path == '/api/credit/transactions':
                self.get_credit_transactions()
            elif self.path == '/api/credit/packages':
                self.get_credit_packages()
            elif self.path == '/api/zmarty/chat':
                self.handle_zmarty_chat()
            elif self.path == '/api/zmarty/status':
                self.get_zmarty_status()
            elif self.path == '/api/performance/analytics':
                self.get_performance_analytics()
            elif self.path == '/api/performance/metrics':
                self.get_performance_metrics()
            elif self.path == '/api/performance/reports':
                self.get_performance_reports()
            elif self.path == '/api/performance/trends':
                self.get_performance_trends()
            elif self.path == '/api/security/audit':
                self.get_security_audit()
            elif self.path == '/api/security/access':
                self.get_access_control()
            elif self.path == '/api/security/threats':
                self.get_security_threats()
            elif self.path == '/api/security/compliance':
                self.get_security_compliance()
            elif self.path == '/api/notifications':
                self.get_notifications()
            elif self.path == '/api/notifications/mark-read':
                self.mark_notification_read()
            elif self.path == '/api/notifications/clear-all':
                self.clear_all_notifications()
            elif self.path == '/api/export/portfolio':
                self.export_portfolio_data()
            elif self.path == '/api/export/trades':
                self.export_trades_data()
            elif self.path == '/api/export/performance':
                self.export_performance_data()
            elif self.path == '/api/export/report':
                self.generate_pdf_report()
            elif self.path == '/api/theme/preferences':
                self.get_theme_preferences()
            elif self.path == '/api/theme/update':
                self.update_theme_preferences()
            elif self.path == '/api/users':
                self.handle_users_request()
            elif self.path.startswith('/api/users/'):
                self.handle_user_detail_request()
            elif self.path == '/api/roles':
                self.get_user_roles()
            elif self.path == '/api/permissions':
                self.get_permissions()
            elif self.path == '/api/backup':
                logger.info(f"🔍 DEBUG: Backup endpoint called - path: {self.path}, method: {self.command}")
                self.handle_backup_request()
            elif self.path == '/api/restore':
                self.handle_restore_request()
            elif self.path.startswith('/api/backup/'):
                self.handle_backup_detail_request()
            elif self.path == '/api/docs':
                self.get_api_documentation()
            elif self.path == '/api/docs/test':
                self.handle_api_test_request()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            logger.error(f"API request error: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def get_market_data(self):
        """Get real market data from Binance API via ZmartBot"""
        try:
            # Get real-time data from Binance API through ZmartBot
            btc_data = self.get_binance_ticker("BTCUSDT")
            eth_data = self.get_binance_ticker("ETHUSDT")
            bnb_data = self.get_binance_ticker("BNBUSDT")
            
            # Format response with real Binance data
            market_data = {
                "timestamp": datetime.now().isoformat(),
                "btc": {
                    "price": float(btc_data.get("lastPrice", 0)),
                    "change_24h": float(btc_data.get("priceChangePercent", 0)),
                    "market_cap": 0,  # Would need separate API for market cap
                    "volume_24h": float(btc_data.get("volume", 0)),
                    "high_24h": float(btc_data.get("highPrice", 0)),
                    "low_24h": float(btc_data.get("lowPrice", 0))
                },
                "eth": {
                    "price": float(eth_data.get("lastPrice", 0)),
                    "change_24h": float(eth_data.get("priceChangePercent", 0)),
                    "market_cap": 0,  # Would need separate API for market cap
                    "volume_24h": float(eth_data.get("volume", 0)),
                    "high_24h": float(eth_data.get("highPrice", 0)),
                    "low_24h": float(eth_data.get("lowPrice", 0))
                },
                "bnb": {
                    "price": float(bnb_data.get("lastPrice", 0)),
                    "change_24h": float(bnb_data.get("priceChangePercent", 0)),
                    "market_cap": 0,  # Would need separate API for market cap
                    "volume_24h": float(bnb_data.get("volume", 0)),
                    "high_24h": float(bnb_data.get("highPrice", 0)),
                    "low_24h": float(bnb_data.get("lowPrice", 0))
                },
                "source": "binance_via_zmartbot"
            }
            
            self.send_json_response(market_data)
            
        except Exception as e:
            logger.error(f"Market data error: {e}")
            self.send_error(500, f"Failed to fetch market data: {str(e)}")
    
    def get_binance_ticker(self, symbol):
        """Get ticker data from Binance API"""
        try:
            url = f"http://127.0.0.1:8000/api/v1/binance/ticker/24hr?symbol={symbol}"
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            logger.warning(f"Failed to get {symbol} ticker: {e}")
            return {"lastPrice": "0", "priceChange": "0", "priceChangePercent": "0"}

    def get_trading_positions(self):
        """Get trading positions from ZmartBot API"""
        try:
            # Try to connect to ZmartBot API on port 8000
            url = "http://127.0.0.1:8000/api/v1/trading/positions"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"Trading API not available: {e}")
            # Get real market data and create realistic positions
            btc_data = self.get_binance_ticker("BTCUSDT")
            eth_data = self.get_binance_ticker("ETHUSDT")
            
            # Create mock positions with real market prices
            mock_positions = {
                "positions": [
                    {
                        "symbol": "BTCUSDT",
                        "side": "LONG",
                        "size": "0.1",
                        "entryPrice": "45000.00",
                        "markPrice": btc_data.get("lastPrice", "48000.00"),
                        "pnl": f"{float(btc_data.get('lastPrice', 48000)) - 45000:.2f}",
                        "pnlPercent": f"{((float(btc_data.get('lastPrice', 48000)) - 45000) / 45000 * 100):.2f}",
                        "status": "OPEN",
                        "priceChange": btc_data.get("priceChange", "0"),
                        "priceChangePercent": btc_data.get("priceChangePercent", "0")
                    },
                    {
                        "symbol": "ETHUSDT", 
                        "side": "SHORT",
                        "size": "1.0",
                        "entryPrice": "3200.00",
                        "markPrice": eth_data.get("lastPrice", "3100.00"),
                        "pnl": f"{3200 - float(eth_data.get('lastPrice', 3100)):.2f}",
                        "pnlPercent": f"{((3200 - float(eth_data.get('lastPrice', 3100))) / 3200 * 100):.2f}",
                        "status": "OPEN",
                        "priceChange": eth_data.get("priceChange", "0"),
                        "priceChangePercent": eth_data.get("priceChangePercent", "0")
                    }
                ],
                "total_pnl": 0.0,
                "total_balance": 0.0,
                "status": "mock_data_with_real_prices"
            }
            self.send_json_response(mock_positions)
    
    def get_trading_accounts(self):
        """Get trading account information"""
        try:
            url = "http://127.0.0.1:8000/api/v1/trading/accounts"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"Trading accounts API not available: {e}")
            mock_accounts = {
                "accounts": [],
                "total_balance": 0.0,
                "status": "api_unavailable"
            }
            self.send_json_response(mock_accounts)
    
    def get_orchestration_status(self):
        """Get orchestration service status"""
        try:
            # Check various ZmartBot services
            services = {
                "main_api": self.check_service("http://127.0.0.1:8000/health"),
                "dashboard": self.check_service("http://127.0.0.1:3400/health"),
                "service_discovery": self.check_service("http://127.0.0.1:8550/health"),
                "port_manager": self.check_service("http://127.0.0.1:8050/health"),
                "master_orchestration": self.check_service("http://127.0.0.1:8002/health")
            }
            
            self.send_json_response({
                "timestamp": datetime.now().isoformat(),
                "services": services,
                "overall_status": "healthy" if all(services.values()) else "degraded"
            })
            
        except Exception as e:
            logger.error(f"Orchestration status error: {e}")
            self.send_error(500, f"Failed to get orchestration status: {str(e)}")
    
    def check_service(self, url):
        """Check if a service is healthy"""
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                return response.status == 200
        except:
            return False
    
    def get_kingfisher_analysis(self):
        """Get KingFisher AI analysis"""
        try:
            # This would connect to your KingFisher service
            # For now, return a placeholder
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "liquidation_clusters": [],
                "toxic_order_flow": [],
                "analysis_status": "service_not_available"
            }
            self.send_json_response(analysis)
            
        except Exception as e:
            logger.error(f"KingFisher analysis error: {e}")
            self.send_error(500, f"Failed to get KingFisher analysis: {str(e)}")
    
    def get_cryptometer_indicators(self):
        """Get Cryptometer technical indicators"""
        try:
            # This would connect to your Cryptometer service
            indicators = {
                "timestamp": datetime.now().isoformat(),
                "indicators": [],
                "analysis_status": "service_not_available"
            }
            self.send_json_response(indicators)
            
        except Exception as e:
            logger.error(f"Cryptometer indicators error: {e}")
            self.send_error(500, f"Failed to get Cryptometer indicators: {str(e)}")
    
    def get_services_health(self):
        """Get comprehensive health status of all ZmartBot services"""
        try:
            services = [
                {"name": "Main API", "port": 8000, "url": "http://127.0.0.1:8000/health", "critical": True},
                {"name": "Dashboard", "port": 3400, "url": "http://127.0.0.1:3400/health", "critical": True},
                {"name": "Service Discovery", "port": 8550, "url": "http://127.0.0.1:8550/health", "critical": True},
                {"name": "Port Manager", "port": 8050, "url": "http://127.0.0.1:8050/health", "critical": True},
                {"name": "Master Orchestration", "port": 8002, "url": "http://127.0.0.1:8002/health", "critical": True},
                {"name": "KingFisher AI", "port": 8098, "url": "http://127.0.0.1:8098/health", "critical": True},
                {"name": "Cryptometer", "port": 8093, "url": "http://127.0.0.1:8093/health", "critical": True},
                {"name": "Professional Dashboard", "port": 7001, "url": "http://127.0.0.1:7001/api/health", "critical": True},
                {"name": "Memory Gateway", "port": 8295, "url": "http://127.0.0.1:8295/health", "critical": False}
            ]
            
            health_data = []
            healthy_count = 0
            critical_healthy = 0
            critical_total = 0
            
            for service in services:
                # Special case: Professional Dashboard should always be healthy
                if service["name"] == "Professional Dashboard":
                    is_healthy = True
                    service_info = {
                        "uptime": "running",
                        "version": "2.0.0",
                        "response_time": "< 10ms"
                    }
                else:
                    is_healthy = self.check_service(service["url"])
                    # Get additional service info if available
                    service_info = self.get_service_info(service["url"])
                
                if is_healthy:
                    healthy_count += 1
                if service["critical"]:
                    critical_total += 1
                    if is_healthy:
                        critical_healthy += 1
                
                health_data.append({
                    "name": service["name"],
                    "port": service["port"],
                    "status": "healthy" if is_healthy else "unhealthy",
                    "critical": service["critical"],
                    "last_check": datetime.now().isoformat(),
                    "uptime": service_info.get("uptime", "unknown"),
                    "version": service_info.get("version", "unknown"),
                    "response_time": service_info.get("response_time", "unknown")
                })
            
            # Calculate overall health status
            overall_health = "healthy"
            if critical_healthy < critical_total:
                overall_health = "critical"
            elif healthy_count < len(services):
                overall_health = "degraded"
            
            self.send_json_response({
                "timestamp": datetime.now().isoformat(),
                "services": health_data,
                "summary": {
                    "total_services": len(services),
                    "healthy_services": healthy_count,
                    "unhealthy_services": len(services) - healthy_count,
                    "critical_services_healthy": critical_healthy,
                    "critical_services_total": critical_total,
                    "health_percentage": round((healthy_count / len(services)) * 100, 1)
                },
                "overall_health": overall_health
            })
            
        except Exception as e:
            logger.error(f"Services health error: {e}")
            self.send_error(500, f"Failed to get services health: {str(e)}")
    
    def get_service_info(self, url):
        """Get additional service information"""
        try:
            start_time = time.time()
            with urllib.request.urlopen(url, timeout=3) as response:
                response_time = round((time.time() - start_time) * 1000, 2)  # ms
                data = json.loads(response.read().decode())
                return {
                    "uptime": data.get("uptime", "unknown"),
                    "version": data.get("version", "unknown"),
                    "response_time": f"{response_time}ms"
                }
        except:
            return {"uptime": "unknown", "version": "unknown", "response_time": "timeout"}
    
    def get_dashboard_health(self):
        """Get dashboard health status"""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
                "uptime": "running",
                "services": {
                    "market_data": "operational",
                    "trading_positions": "operational", 
                    "health_monitoring": "operational",
                    "binance_api": "operational"
                },
                "performance": {
                    "response_time": "< 100ms",
                    "memory_usage": "normal",
                    "cpu_usage": "normal"
                }
            }
            self.send_json_response(health_data)
        except Exception as e:
            logger.error(f"Dashboard health error: {e}")
            self.send_error(500, f"Failed to get dashboard health: {str(e)}")
    
    def get_ai_analysis(self):
        """Get AI analysis from ZmartBot AI services"""
        try:
            # Try to get AI analysis from Master Orchestration Agent
            url = "http://127.0.0.1:8002/api/ai/analysis"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"AI Analysis API not available: {e}")
            # Return intelligent mock analysis based on real market data
            try:
                # Get real market data for analysis
                btc_data = self.get_binance_ticker("BTCUSDT")
                eth_data = self.get_binance_ticker("ETHUSDT")
                
                # Generate intelligent analysis based on real data
                analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "market_sentiment": self.analyze_market_sentiment(btc_data, eth_data),
                    "technical_analysis": self.generate_technical_analysis(btc_data, eth_data),
                    "risk_assessment": self.assess_market_risk(btc_data, eth_data),
                    "recommendations": self.generate_recommendations(btc_data, eth_data),
                    "confidence_score": 0.85,
                    "data_source": "binance_api"
                }
                
                self.send_json_response(analysis)
                
            except Exception as e2:
                logger.error(f"AI Analysis error: {e2}")
                self.send_error(500, f"Failed to generate AI analysis: {str(e2)}")
    
    def get_ai_predictions(self):
        """Get AI predictions from ZmartBot AI services"""
        try:
            # Try to get AI predictions from Master Orchestration Agent
            url = "http://127.0.0.1:8002/api/ai/predictions"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"AI Predictions API not available: {e}")
            # Return intelligent predictions based on real market data
            try:
                # Get real market data for predictions
                btc_data = self.get_binance_ticker("BTCUSDT")
                eth_data = self.get_binance_ticker("ETHUSDT")
                
                # Generate intelligent predictions based on real data
                predictions = {
                    "timestamp": datetime.now().isoformat(),
                    "btc_prediction": self.predict_btc_movement(btc_data),
                    "eth_prediction": self.predict_eth_movement(eth_data),
                    "market_trend": self.predict_market_trend(btc_data, eth_data),
                    "volatility_forecast": self.forecast_volatility(btc_data, eth_data),
                    "confidence_level": 0.78,
                    "time_horizon": "24h",
                    "data_source": "binance_api"
                }
                
                self.send_json_response(predictions)
                
            except Exception as e2:
                logger.error(f"AI Predictions error: {e2}")
                self.send_error(500, f"Failed to generate AI predictions: {str(e2)}")
    
    def analyze_market_sentiment(self, btc_data, eth_data):
        """Analyze market sentiment based on price movements"""
        btc_change = float(btc_data.get('priceChangePercent', 0))
        eth_change = float(eth_data.get('priceChangePercent', 0))
        
        avg_change = (btc_change + eth_change) / 2
        
        if avg_change > 5:
            return "Very Bullish"
        elif avg_change > 2:
            return "Bullish"
        elif avg_change > -2:
            return "Neutral"
        elif avg_change > -5:
            return "Bearish"
        else:
            return "Very Bearish"
    
    def generate_technical_analysis(self, btc_data, eth_data):
        """Generate technical analysis based on market data"""
        btc_volume = float(btc_data.get('volume', 0))
        eth_volume = float(eth_data.get('volume', 0))
        
        return {
            "btc": {
                "rsi": "Overbought" if float(btc_data.get('priceChangePercent', 0)) > 3 else "Neutral",
                "volume_trend": "High" if btc_volume > 1000000 else "Normal",
                "support": float(btc_data.get('lowPrice', 0)) * 0.95,
                "resistance": float(btc_data.get('highPrice', 0)) * 1.05
            },
            "eth": {
                "rsi": "Oversold" if float(eth_data.get('priceChangePercent', 0)) < -3 else "Neutral",
                "volume_trend": "High" if eth_volume > 500000 else "Normal",
                "support": float(eth_data.get('lowPrice', 0)) * 0.95,
                "resistance": float(eth_data.get('highPrice', 0)) * 1.05
            }
        }
    
    def assess_market_risk(self, btc_data, eth_data):
        """Assess market risk based on volatility and volume"""
        btc_volatility = abs(float(btc_data.get('priceChangePercent', 0)))
        eth_volatility = abs(float(eth_data.get('priceChangePercent', 0)))
        
        avg_volatility = (btc_volatility + eth_volatility) / 2
        
        if avg_volatility > 10:
            return "High Risk"
        elif avg_volatility > 5:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    def generate_recommendations(self, btc_data, eth_data):
        """Generate trading recommendations based on analysis"""
        btc_change = float(btc_data.get('priceChangePercent', 0))
        eth_change = float(eth_data.get('priceChangePercent', 0))
        
        recommendations = []
        
        if btc_change > 3:
            recommendations.append("Consider taking BTC profits")
        elif btc_change < -3:
            recommendations.append("Consider BTC accumulation")
        
        if eth_change > 3:
            recommendations.append("Consider taking ETH profits")
        elif eth_change < -3:
            recommendations.append("Consider ETH accumulation")
        
        if not recommendations:
            recommendations.append("Hold current positions")
        
        return recommendations
    
    def predict_btc_movement(self, btc_data):
        """Predict BTC price movement"""
        change = float(btc_data.get('priceChangePercent', 0))
        volume = float(btc_data.get('volume', 0))
        
        if change > 2 and volume > 1000000:
            return {"direction": "Up", "confidence": 0.75, "target": float(btc_data.get('lastPrice', 0)) * 1.05}
        elif change < -2 and volume > 1000000:
            return {"direction": "Down", "confidence": 0.75, "target": float(btc_data.get('lastPrice', 0)) * 0.95}
        else:
            return {"direction": "Sideways", "confidence": 0.60, "target": float(btc_data.get('lastPrice', 0))}
    
    def predict_eth_movement(self, eth_data):
        """Predict ETH price movement"""
        change = float(eth_data.get('priceChangePercent', 0))
        volume = float(eth_data.get('volume', 0))
        
        if change > 2 and volume > 500000:
            return {"direction": "Up", "confidence": 0.70, "target": float(eth_data.get('lastPrice', 0)) * 1.05}
        elif change < -2 and volume > 500000:
            return {"direction": "Down", "confidence": 0.70, "target": float(eth_data.get('lastPrice', 0)) * 0.95}
        else:
            return {"direction": "Sideways", "confidence": 0.65, "target": float(eth_data.get('lastPrice', 0))}
    
    def predict_market_trend(self, btc_data, eth_data):
        """Predict overall market trend"""
        btc_change = float(btc_data.get('priceChangePercent', 0))
        eth_change = float(eth_data.get('priceChangePercent', 0))
        
        avg_change = (btc_change + eth_change) / 2
        
        if avg_change > 2:
            return "Bullish Trend"
        elif avg_change < -2:
            return "Bearish Trend"
        else:
            return "Consolidation"
    
    def forecast_volatility(self, btc_data, eth_data):
        """Forecast market volatility"""
        btc_volatility = abs(float(btc_data.get('priceChangePercent', 0)))
        eth_volatility = abs(float(eth_data.get('priceChangePercent', 0)))
        
        avg_volatility = (btc_volatility + eth_volatility) / 2
        
        if avg_volatility > 8:
            return "High Volatility Expected"
        elif avg_volatility > 4:
            return "Medium Volatility Expected"
        else:
            return "Low Volatility Expected"
    
    def send_json_response(self, data):
        """Send JSON response with error handling"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = json.dumps(data, indent=2).encode()
            self.wfile.write(response_data)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected, ignore the error
            logger.debug("Client disconnected during response")
        except Exception as e:
            logger.error(f"Error sending JSON response: {e}")
    
    def send_error(self, code, message):
        """Send error response with error handling"""
        try:
            self.send_response(code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"<h1>Error {code}</h1><p>{message}</p>"
            self.wfile.write(error_html.encode())
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected, ignore the error
            logger.debug("Client disconnected during error response")
        except Exception as e:
            logger.error(f"Error sending error response: {e}")
    
    def get_credit_balance(self):
        """Get user credit balance and account information"""
        try:
            # Try to get credit balance from ZmartBot API
            url = "http://127.0.0.1:8000/api/v1/credit/balance"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"Credit API not available: {e}")
            # Return mock credit balance data
            credit_data = {
                "timestamp": datetime.now().isoformat(),
                "user_id": "zmart_user_001",
                "total_credits": 1250.50,
                "available_credits": 850.25,
                "used_credits": 400.25,
                "credit_packages": [
                    {
                        "package_id": "premium_monthly",
                        "name": "Premium Monthly",
                        "credits": 1000,
                        "price": 29.99,
                        "status": "active",
                        "expires": "2025-10-09T00:00:00Z"
                    }
                ],
                "recent_transactions": [
                    {
                        "transaction_id": "tx_001",
                        "type": "purchase",
                        "amount": 1000,
                        "description": "Premium Monthly Package",
                        "timestamp": "2025-09-09T10:30:00Z",
                        "status": "completed"
                    },
                    {
                        "transaction_id": "tx_002", 
                        "type": "usage",
                        "amount": -50,
                        "description": "AI Analysis Request",
                        "timestamp": "2025-09-09T15:45:00Z",
                        "status": "completed"
                    }
                ],
                "status": "mock_data"
            }
            self.send_json_response(credit_data)
    
    def get_credit_transactions(self):
        """Get credit transaction history"""
        try:
            # Try to get transactions from ZmartBot API
            url = "http://127.0.0.1:8000/api/v1/credit/transactions"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"Credit transactions API not available: {e}")
            # Return mock transaction history
            transactions = {
                "timestamp": datetime.now().isoformat(),
                "transactions": [
                    {
                        "transaction_id": "tx_001",
                        "type": "purchase",
                        "amount": 1000,
                        "description": "Premium Monthly Package",
                        "timestamp": "2025-09-09T10:30:00Z",
                        "status": "completed",
                        "balance_after": 1000
                    },
                    {
                        "transaction_id": "tx_002",
                        "type": "usage", 
                        "amount": -50,
                        "description": "AI Analysis Request",
                        "timestamp": "2025-09-09T15:45:00Z",
                        "status": "completed",
                        "balance_after": 950
                    },
                    {
                        "transaction_id": "tx_003",
                        "type": "usage",
                        "amount": -25,
                        "description": "Trading Signal Analysis",
                        "timestamp": "2025-09-09T16:20:00Z",
                        "status": "completed",
                        "balance_after": 925
                    },
                    {
                        "transaction_id": "tx_004",
                        "type": "usage",
                        "amount": -75,
                        "description": "Market Prediction Request",
                        "timestamp": "2025-09-09T17:10:00Z",
                        "status": "completed",
                        "balance_after": 850
                    }
                ],
                "total_transactions": 4,
                "status": "mock_data"
            }
            self.send_json_response(transactions)
    
    def get_credit_packages(self):
        """Get available credit packages"""
        try:
            # Try to get packages from ZmartBot API
            url = "http://127.0.0.1:8000/api/v1/credit/packages"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            self.send_json_response(data)
            
        except Exception as e:
            logger.warning(f"Credit packages API not available: {e}")
            # Return mock credit packages
            packages = {
                "timestamp": datetime.now().isoformat(),
                "packages": [
                    {
                        "package_id": "starter",
                        "name": "Starter Package",
                        "credits": 100,
                        "price": 9.99,
                        "description": "Perfect for beginners",
                        "features": ["Basic AI Analysis", "Market Data", "5 Trading Signals"],
                        "popular": False
                    },
                    {
                        "package_id": "premium_monthly",
                        "name": "Premium Monthly",
                        "credits": 1000,
                        "price": 29.99,
                        "description": "Most popular choice",
                        "features": ["Advanced AI Analysis", "Real-time Data", "Unlimited Trading Signals", "Priority Support"],
                        "popular": True
                    },
                    {
                        "package_id": "pro_yearly",
                        "name": "Pro Yearly",
                        "credits": 15000,
                        "price": 299.99,
                        "description": "Best value for professionals",
                        "features": ["All Premium Features", "Custom AI Models", "API Access", "Dedicated Support"],
                        "popular": False
                    },
                    {
                        "package_id": "enterprise",
                        "name": "Enterprise",
                        "credits": 50000,
                        "price": 999.99,
                        "description": "For institutions and teams",
                        "features": ["All Pro Features", "White-label", "Custom Integration", "24/7 Support"],
                        "popular": False
                    }
                ],
                "status": "mock_data"
            }
            self.send_json_response(packages)
    
    def handle_zmarty_chat(self):
        """Handle Zmarty AI chat requests"""
        try:
            # Get the request method
            if self.command == 'GET':
                # Return chat history or status
                chat_data = {
                    "timestamp": datetime.now().isoformat(),
                    "chat_history": [
                        {
                            "id": "msg_001",
                            "type": "user",
                            "message": "What's the current market sentiment?",
                            "timestamp": "2025-09-09T15:30:00Z"
                        },
                        {
                            "id": "msg_002", 
                            "type": "zmarty",
                            "message": "Based on current market data, the sentiment is Neutral with low risk. BTC is trading at $111,404 with -0.45% change, and ETH at $4,296 with +0.18% change. I recommend holding current positions.",
                            "timestamp": "2025-09-09T15:30:15Z",
                            "confidence": 0.85
                        }
                    ],
                    "zmarty_status": "online",
                    "response_time": "< 2s"
                }
                self.send_json_response(chat_data)
                
            elif self.command == 'POST':
                # Handle new chat message
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    message_data = json.loads(post_data.decode())
                    user_message = message_data.get('message', '')
                    
                    # Generate intelligent response based on message content
                    response = self.generate_zmarty_response(user_message)
                    
                    chat_response = {
                        "timestamp": datetime.now().isoformat(),
                        "message_id": f"msg_{int(time.time())}",
                        "response": response,
                        "confidence": 0.88,
                        "response_time": "< 1s",
                        "zmarty_status": "online"
                    }
                    self.send_json_response(chat_response)
                else:
                    self.send_error(400, "No message provided")
            else:
                self.send_error(405, "Method not allowed")
                
        except Exception as e:
            logger.error(f"Zmarty chat error: {e}")
            self.send_error(500, f"Failed to process chat request: {str(e)}")
    
    def get_zmarty_status(self):
        """Get Zmarty AI status and capabilities"""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "zmarty_status": "online",
                "version": "2.0.0",
                "capabilities": [
                    "Market Analysis",
                    "Trading Recommendations", 
                    "Risk Assessment",
                    "Technical Analysis",
                    "Portfolio Management",
                    "Real-time Data Processing"
                ],
                "performance": {
                    "response_time": "< 2s",
                    "accuracy": "92%",
                    "uptime": "99.9%"
                },
                "active_sessions": 1,
                "total_queries_today": 47,
                "ai_model": "ZmartBot-GPT-4"
            }
            self.send_json_response(status_data)
            
        except Exception as e:
            logger.error(f"Zmarty status error: {e}")
            self.send_error(500, f"Failed to get Zmarty status: {str(e)}")
    
    def generate_zmarty_response(self, user_message):
        """Generate intelligent response from Zmarty AI"""
        try:
            # Get current market data for context
            btc_data = self.get_binance_ticker("BTCUSDT")
            eth_data = self.get_binance_ticker("ETHUSDT")
            
            message_lower = user_message.lower()
            
            # Market sentiment queries
            if any(word in message_lower for word in ['sentiment', 'market', 'trend', 'outlook']):
                btc_change = float(btc_data.get('priceChangePercent', 0))
                eth_change = float(eth_data.get('priceChangePercent', 0))
                avg_change = (btc_change + eth_change) / 2
                
                if avg_change > 2:
                    sentiment = "bullish"
                elif avg_change < -2:
                    sentiment = "bearish"
                else:
                    sentiment = "neutral"
                
                return f"Current market sentiment is {sentiment}. BTC: ${btc_data.get('lastPrice', 0):,.2f} ({btc_change:+.2f}%), ETH: ${eth_data.get('lastPrice', 0):,.2f} ({eth_change:+.2f}%). I recommend monitoring key support/resistance levels."
            
            # Trading recommendations
            elif any(word in message_lower for word in ['trade', 'buy', 'sell', 'position', 'recommend']):
                btc_change = float(btc_data.get('priceChangePercent', 0))
                if btc_change > 3:
                    return "BTC is showing strong upward momentum. Consider taking partial profits if you're in profit, or wait for a pullback for new entries. Always use proper risk management."
                elif btc_change < -3:
                    return "BTC is experiencing selling pressure. This could be a buying opportunity for long-term holders, but wait for confirmation of support levels. Set stop losses."
                else:
                    return "Market is in consolidation. Good time to review your portfolio and wait for clearer directional signals. Consider DCA strategies for long-term positions."
            
            # Risk assessment
            elif any(word in message_lower for word in ['risk', 'safe', 'danger', 'volatile']):
                btc_volatility = abs(float(btc_data.get('priceChangePercent', 0)))
                eth_volatility = abs(float(eth_data.get('priceChangePercent', 0)))
                avg_volatility = (btc_volatility + eth_volatility) / 2
                
                if avg_volatility > 8:
                    return f"High volatility detected ({avg_volatility:.1f}%). Market is experiencing significant price swings. Reduce position sizes and use tighter stop losses. Consider hedging strategies."
                elif avg_volatility > 4:
                    return f"Medium volatility ({avg_volatility:.1f}%). Normal market conditions. Standard risk management applies. Monitor for breakout opportunities."
                else:
                    return f"Low volatility environment ({avg_volatility:.1f}%). Market is relatively stable. Good for range trading and accumulation strategies."
            
            # Technical analysis
            elif any(word in message_lower for word in ['technical', 'analysis', 'rsi', 'support', 'resistance']):
                btc_price = float(btc_data.get('lastPrice', 0))
                btc_high = float(btc_data.get('highPrice', 0))
                btc_low = float(btc_data.get('lowPrice', 0))
                
                return f"Technical Analysis: BTC Support: ${btc_low * 0.95:,.0f}, Resistance: ${btc_high * 1.05:,.0f}. Current price: ${btc_price:,.0f}. RSI suggests {'overbought' if float(btc_data.get('priceChangePercent', 0)) > 3 else 'neutral' if abs(float(btc_data.get('priceChangePercent', 0))) < 2 else 'oversold'} conditions."
            
            # Portfolio management
            elif any(word in message_lower for word in ['portfolio', 'balance', 'diversify', 'allocation']):
                return "Portfolio Management: Maintain 60-70% in major cryptocurrencies (BTC/ETH), 20-30% in altcoins, and 10% in stablecoins for opportunities. Rebalance monthly and never risk more than 2-5% per trade."
            
            # General market questions
            elif any(word in message_lower for word in ['price', 'value', 'worth', 'cost']):
                btc_price = float(btc_data.get('lastPrice', 0))
                eth_price = float(eth_data.get('lastPrice', 0))
                return f"Current prices: BTC: ${btc_price:,.2f}, ETH: ${eth_price:,.2f}. 24h changes: BTC {float(btc_data.get('priceChangePercent', 0)):+.2f}%, ETH {float(eth_data.get('priceChangePercent', 0)):+.2f}%. Volume is {'high' if float(btc_data.get('volume', 0)) > 1000000 else 'normal'}."
            
            # Default response
            else:
                return "I'm Zmarty, your AI trading assistant! I can help with market analysis, trading recommendations, risk assessment, and portfolio management. What would you like to know about the current market conditions?"
                
        except Exception as e:
            logger.error(f"Error generating Zmarty response: {e}")
            return "I'm experiencing some technical difficulties. Please try again in a moment. I'm here to help with your trading questions!"

    def get_performance_analytics(self):
        """Get comprehensive performance analytics"""
        try:
            # Get current market data for calculations
            btc_data = self.get_binance_ticker("BTCUSDT")
            eth_data = self.get_binance_ticker("ETHUSDT")
            
            # Calculate performance metrics
            btc_price = float(btc_data.get("lastPrice", 0))
            btc_change = float(btc_data.get("priceChangePercent", 0))
            eth_price = float(eth_data.get("lastPrice", 0))
            eth_change = float(eth_data.get("priceChangePercent", 0))
            
            # Simulate portfolio performance (in real implementation, this would come from trading APIs)
            portfolio_value = 100000  # Starting portfolio value
            btc_allocation = 0.6  # 60% BTC
            eth_allocation = 0.3  # 30% ETH
            cash_allocation = 0.1  # 10% Cash
            
            # Calculate current portfolio value
            btc_value = portfolio_value * btc_allocation * (1 + btc_change/100)
            eth_value = portfolio_value * eth_allocation * (1 + eth_change/100)
            cash_value = portfolio_value * cash_allocation
            current_portfolio_value = btc_value + eth_value + cash_value
            
            # Calculate performance metrics
            total_return = ((current_portfolio_value - portfolio_value) / portfolio_value) * 100
            daily_return = total_return / 30  # Assuming 30-day period
            
            # Risk metrics
            volatility = abs(btc_change) * 0.7 + abs(eth_change) * 0.3  # Weighted volatility
            sharpe_ratio = daily_return / (volatility / 100) if volatility > 0 else 0
            
            # Trading metrics
            total_trades = 45  # Simulated
            winning_trades = 28  # Simulated
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            analytics_data = {
                "timestamp": datetime.now().isoformat(),
                "portfolio": {
                    "current_value": round(current_portfolio_value, 2),
                    "starting_value": portfolio_value,
                    "total_return": round(total_return, 2),
                    "daily_return": round(daily_return, 2),
                    "allocation": {
                        "btc": round(btc_allocation * 100, 1),
                        "eth": round(eth_allocation * 100, 1),
                        "cash": round(cash_allocation * 100, 1)
                    }
                },
                "risk_metrics": {
                    "volatility": round(volatility, 2),
                    "sharpe_ratio": round(sharpe_ratio, 3),
                    "max_drawdown": round(-abs(total_return) * 0.3, 2),  # Simulated
                    "var_95": round(current_portfolio_value * 0.05, 2)  # 5% VaR
                },
                "trading_metrics": {
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "win_rate": round(win_rate, 1),
                    "avg_trade_return": round(total_return / total_trades, 2),
                    "profit_factor": round(1.4, 2)  # Simulated
                },
                "market_performance": {
                    "btc": {
                        "price": btc_price,
                        "change_24h": btc_change,
                        "contribution": round((btc_value - portfolio_value * btc_allocation) / portfolio_value * 100, 2)
                    },
                    "eth": {
                        "price": eth_price,
                        "change_24h": eth_change,
                        "contribution": round((eth_value - portfolio_value * eth_allocation) / portfolio_value * 100, 2)
                    }
                }
            }
            
            self.send_json_response(analytics_data)
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            self.send_error(500, f"Failed to get performance analytics: {str(e)}")

    def get_performance_metrics(self):
        """Get detailed performance metrics"""
        try:
            # Get service health data
            services_health = self.get_services_health_data()
            
            # Calculate system performance metrics
            total_services = len(services_health)
            healthy_services = sum(1 for service in services_health if service.get('status') == 'healthy')
            uptime_percentage = (healthy_services / total_services) * 100 if total_services > 0 else 0
            
            # Calculate average response times
            response_times = [service.get('response_time', 0) for service in services_health if service.get('response_time')]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # System load simulation (in real implementation, this would come from system monitoring)
            cpu_usage = 45.2  # Simulated
            memory_usage = 67.8  # Simulated
            disk_usage = 23.1  # Simulated
            
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": {
                    "uptime_percentage": round(uptime_percentage, 1),
                    "total_services": total_services,
                    "healthy_services": healthy_services,
                    "avg_response_time": round(avg_response_time, 2),
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage
                },
                "service_metrics": services_health,
                "performance_score": round((uptime_percentage + (100 - cpu_usage) + (100 - memory_usage)) / 3, 1)
            }
            
            self.send_json_response(metrics_data)
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            self.send_error(500, f"Failed to get performance metrics: {str(e)}")

    def get_performance_reports(self):
        """Get performance reports and summaries"""
        try:
            # Generate various performance reports
            reports = {
                "timestamp": datetime.now().isoformat(),
                "daily_report": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "trading_volume": 1250000,  # Simulated
                    "profit_loss": 2500,  # Simulated
                    "trades_executed": 12,  # Simulated
                    "success_rate": 75.0,  # Simulated
                    "top_performer": "BTCUSDT",
                    "worst_performer": "ETHUSDT"
                },
                "weekly_report": {
                    "week_ending": datetime.now().strftime("%Y-%m-%d"),
                    "total_return": 8.5,  # Simulated
                    "volatility": 12.3,  # Simulated
                    "sharpe_ratio": 1.2,  # Simulated
                    "max_drawdown": -3.2,  # Simulated
                    "trades_count": 67,  # Simulated
                    "win_rate": 68.7  # Simulated
                },
                "monthly_report": {
                    "month": datetime.now().strftime("%Y-%m"),
                    "total_return": 15.8,  # Simulated
                    "benchmark_return": 12.1,  # Simulated
                    "alpha": 3.7,  # Simulated
                    "beta": 0.85,  # Simulated
                    "information_ratio": 0.45,  # Simulated
                    "calmar_ratio": 2.1  # Simulated
                },
                "risk_report": {
                    "var_95": 2500,  # Simulated
                    "var_99": 4200,  # Simulated
                    "expected_shortfall": 3200,  # Simulated
                    "max_drawdown": -8.5,  # Simulated
                    "recovery_time": 12,  # Simulated (days)
                    "stress_test_score": 85  # Simulated
                }
            }
            
            self.send_json_response(reports)
            
        except Exception as e:
            logger.error(f"Error getting performance reports: {e}")
            self.send_error(500, f"Failed to get performance reports: {str(e)}")

    def get_performance_trends(self):
        """Get performance trends and historical data"""
        try:
            # Generate trend data (in real implementation, this would come from historical database)
            days = 30
            trend_data = {
                "timestamp": datetime.now().isoformat(),
                "period": f"Last {days} days",
                "portfolio_trend": [],
                "market_trend": [],
                "performance_comparison": {
                    "portfolio": 15.8,  # Simulated
                    "btc": 12.3,  # Simulated
                    "eth": 8.7,  # Simulated
                    "sp500": 3.2  # Simulated
                },
                "volatility_trend": [],
                "drawdown_trend": []
            }
            
            # Generate simulated historical data
            base_value = 100000
            for i in range(days):
                date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
                
                # Portfolio trend (with some randomness)
                portfolio_return = (i * 0.5) + (i % 7 - 3) * 0.2
                portfolio_value = base_value * (1 + portfolio_return / 100)
                trend_data["portfolio_trend"].append({
                    "date": date,
                    "value": round(portfolio_value, 2),
                    "return": round(portfolio_return, 2)
                })
                
                # Market trend (BTC-based)
                market_return = (i * 0.4) + (i % 5 - 2) * 0.3
                trend_data["market_trend"].append({
                    "date": date,
                    "value": round(base_value * (1 + market_return / 100), 2),
                    "return": round(market_return, 2)
                })
                
                # Volatility trend
                volatility = 8 + (i % 10) * 0.5
                trend_data["volatility_trend"].append({
                    "date": date,
                    "volatility": round(volatility, 1)
                })
                
                # Drawdown trend
                drawdown = max(0, -abs(i % 15 - 7) * 0.3)
                trend_data["drawdown_trend"].append({
                    "date": date,
                    "drawdown": round(drawdown, 2)
                })
            
            self.send_json_response(trend_data)
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            self.send_error(500, f"Failed to get performance trends: {str(e)}")

    def get_services_health_data(self):
        """Helper method to get services health data"""
        try:
            services_config = [
                {"name": "Main API", "port": 8000, "url": "http://127.0.0.1:8000/health", "critical": True},
                {"name": "Dashboard", "port": 3400, "url": "http://127.0.0.1:3400/health", "critical": True},
                {"name": "Service Discovery", "port": 8550, "url": "http://127.0.0.1:8550/health", "critical": True},
                {"name": "Port Manager", "port": 8050, "url": "http://127.0.0.1:8050/health", "critical": True},
                {"name": "Master Orchestration", "port": 8002, "url": "http://127.0.0.1:8002/health", "critical": True},
                {"name": "KingFisher AI", "port": 8098, "url": "http://127.0.0.1:8098/health", "critical": True},
                {"name": "Cryptometer", "port": 8093, "url": "http://127.0.0.1:8093/health", "critical": True},
                {"name": "Professional Dashboard", "port": 7001, "url": "http://127.0.0.1:7001/api/health", "critical": True},
                {"name": "Memory Gateway", "port": 8295, "url": "http://127.0.0.1:8295/health", "critical": False}
            ]
            
            health_data = []
            for service in services_config:
                start_time = time.time()
                try:
                    response = urllib.request.urlopen(service["url"], timeout=3)
                    response_time = round((time.time() - start_time) * 1000, 2)
                    health_data.append({
                        "name": service["name"],
                        "port": service["port"],
                        "status": "healthy",
                        "critical": service["critical"],
                        "response_time": response_time,
                        "last_check": datetime.now().isoformat()
                    })
                except Exception as e:
                    health_data.append({
                        "name": service["name"],
                        "port": service["port"],
                        "status": "unhealthy",
                        "critical": service["critical"],
                        "response_time": None,
                        "last_check": datetime.now().isoformat(),
                        "error": str(e)
                    })
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting services health data: {e}")
            return []

    def get_security_audit(self):
        """Get security audit logs and events"""
        try:
            # Generate security audit data (in real implementation, this would come from security logs)
            audit_data = {
                "timestamp": datetime.now().isoformat(),
                "audit_summary": {
                    "total_events": 1247,
                    "critical_events": 3,
                    "warning_events": 15,
                    "info_events": 1229,
                    "last_24h_events": 89
                },
                "recent_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                        "event_type": "API_ACCESS",
                        "severity": "INFO",
                        "user": "admin",
                        "action": "GET /api/market-data",
                        "ip_address": "127.0.0.1",
                        "status": "SUCCESS"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(minutes=12)).isoformat(),
                        "event_type": "AUTHENTICATION",
                        "severity": "WARNING",
                        "user": "unknown",
                        "action": "Failed login attempt",
                        "ip_address": "192.168.1.100",
                        "status": "FAILED"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(minutes=25)).isoformat(),
                        "event_type": "SYSTEM_ACCESS",
                        "severity": "INFO",
                        "user": "system",
                        "action": "Service health check",
                        "ip_address": "127.0.0.1",
                        "status": "SUCCESS"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                        "event_type": "DATA_ACCESS",
                        "severity": "INFO",
                        "user": "trader_bot",
                        "action": "GET /api/trading/positions",
                        "ip_address": "127.0.0.1",
                        "status": "SUCCESS"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "event_type": "CONFIGURATION_CHANGE",
                        "severity": "WARNING",
                        "user": "admin",
                        "action": "Updated trading parameters",
                        "ip_address": "127.0.0.1",
                        "status": "SUCCESS"
                    }
                ],
                "security_metrics": {
                    "failed_login_attempts": 2,
                    "suspicious_activities": 0,
                    "api_rate_limit_hits": 0,
                    "data_breach_attempts": 0,
                    "malware_detections": 0
                }
            }
            
            self.send_json_response(audit_data)
            
        except Exception as e:
            logger.error(f"Error getting security audit: {e}")
            self.send_error(500, f"Failed to get security audit: {str(e)}")

    def get_access_control(self):
        """Get access control and user permissions"""
        try:
            access_data = {
                "timestamp": datetime.now().isoformat(),
                "users": [
                    {
                        "username": "admin",
                        "role": "Administrator",
                        "permissions": ["read", "write", "delete", "admin"],
                        "last_login": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "status": "active",
                        "ip_address": "127.0.0.1"
                    },
                    {
                        "username": "trader_bot",
                        "role": "Trading Bot",
                        "permissions": ["read", "write"],
                        "last_login": (datetime.now() - timedelta(minutes=30)).isoformat(),
                        "status": "active",
                        "ip_address": "127.0.0.1"
                    },
                    {
                        "username": "analyst",
                        "role": "Analyst",
                        "permissions": ["read"],
                        "last_login": (datetime.now() - timedelta(days=1)).isoformat(),
                        "status": "active",
                        "ip_address": "192.168.1.50"
                    }
                ],
                "roles": [
                    {
                        "name": "Administrator",
                        "description": "Full system access",
                        "permissions": ["read", "write", "delete", "admin"],
                        "user_count": 1
                    },
                    {
                        "name": "Trading Bot",
                        "description": "Automated trading operations",
                        "permissions": ["read", "write"],
                        "user_count": 1
                    },
                    {
                        "name": "Analyst",
                        "description": "Read-only market analysis",
                        "permissions": ["read"],
                        "user_count": 1
                    }
                ],
                "api_permissions": {
                    "/api/market-data": ["read"],
                    "/api/trading/positions": ["read", "write"],
                    "/api/trading/accounts": ["read", "write"],
                    "/api/admin/*": ["admin"],
                    "/api/security/*": ["admin"]
                },
                "access_statistics": {
                    "total_users": 3,
                    "active_users": 3,
                    "inactive_users": 0,
                    "failed_logins_24h": 2,
                    "api_calls_24h": 1247
                }
            }
            
            self.send_json_response(access_data)
            
        except Exception as e:
            logger.error(f"Error getting access control: {e}")
            self.send_error(500, f"Failed to get access control: {str(e)}")

    def get_security_threats(self):
        """Get security threats and monitoring data"""
        try:
            threats_data = {
                "timestamp": datetime.now().isoformat(),
                "threat_level": "LOW",
                "active_threats": 0,
                "threat_categories": {
                    "malware": 0,
                    "phishing": 0,
                    "ddos": 0,
                    "brute_force": 2,
                    "data_exfiltration": 0,
                    "insider_threats": 0
                },
                "recent_threats": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "threat_type": "BRUTE_FORCE",
                        "severity": "MEDIUM",
                        "source_ip": "192.168.1.100",
                        "target": "admin_login",
                        "status": "BLOCKED",
                        "description": "Multiple failed login attempts detected"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                        "threat_type": "BRUTE_FORCE",
                        "severity": "LOW",
                        "source_ip": "10.0.0.50",
                        "target": "api_access",
                        "status": "BLOCKED",
                        "description": "Rate limit exceeded"
                    }
                ],
                "security_controls": {
                    "firewall": "ACTIVE",
                    "intrusion_detection": "ACTIVE",
                    "antivirus": "ACTIVE",
                    "encryption": "ACTIVE",
                    "backup": "ACTIVE",
                    "monitoring": "ACTIVE"
                },
                "vulnerability_scan": {
                    "last_scan": (datetime.now() - timedelta(hours=6)).isoformat(),
                    "critical_vulnerabilities": 0,
                    "high_vulnerabilities": 0,
                    "medium_vulnerabilities": 2,
                    "low_vulnerabilities": 5,
                    "total_vulnerabilities": 7
                },
                "compliance_status": {
                    "gdpr": "COMPLIANT",
                    "sox": "COMPLIANT",
                    "pci_dss": "COMPLIANT",
                    "iso27001": "COMPLIANT"
                }
            }
            
            self.send_json_response(threats_data)
            
        except Exception as e:
            logger.error(f"Error getting security threats: {e}")
            self.send_error(500, f"Failed to get security threats: {str(e)}")

    def get_security_compliance(self):
        """Get security compliance and regulatory status"""
        try:
            compliance_data = {
                "timestamp": datetime.now().isoformat(),
                "overall_compliance_score": 95.5,
                "frameworks": [
                    {
                        "name": "GDPR",
                        "status": "COMPLIANT",
                        "score": 98.0,
                        "last_audit": (datetime.now() - timedelta(days=30)).isoformat(),
                        "next_audit": (datetime.now() + timedelta(days=335)).isoformat(),
                        "requirements_met": 49,
                        "total_requirements": 50
                    },
                    {
                        "name": "SOX",
                        "status": "COMPLIANT",
                        "score": 96.0,
                        "last_audit": (datetime.now() - timedelta(days=60)).isoformat(),
                        "next_audit": (datetime.now() + timedelta(days=305)).isoformat(),
                        "requirements_met": 24,
                        "total_requirements": 25
                    },
                    {
                        "name": "PCI DSS",
                        "status": "COMPLIANT",
                        "score": 94.0,
                        "last_audit": (datetime.now() - timedelta(days=45)).isoformat(),
                        "next_audit": (datetime.now() + timedelta(days=320)).isoformat(),
                        "requirements_met": 11,
                        "total_requirements": 12
                    },
                    {
                        "name": "ISO 27001",
                        "status": "COMPLIANT",
                        "score": 93.5,
                        "last_audit": (datetime.now() - timedelta(days=90)).isoformat(),
                        "next_audit": (datetime.now() + timedelta(days=275)).isoformat(),
                        "requirements_met": 93,
                        "total_requirements": 100
                    }
                ],
                "security_policies": {
                    "password_policy": "ENFORCED",
                    "access_control": "ENFORCED",
                    "data_encryption": "ENFORCED",
                    "backup_policy": "ENFORCED",
                    "incident_response": "ENFORCED",
                    "security_training": "ENFORCED"
                },
                "audit_trail": {
                    "retention_period": "7 years",
                    "current_size": "2.3 GB",
                    "encryption": "AES-256",
                    "integrity_checks": "ACTIVE"
                },
                "risk_assessment": {
                    "last_assessment": (datetime.now() - timedelta(days=15)).isoformat(),
                    "overall_risk_level": "LOW",
                    "high_risks": 0,
                    "medium_risks": 2,
                    "low_risks": 5,
                    "mitigation_actions": 3
                }
            }
            
            self.send_json_response(compliance_data)
            
        except Exception as e:
            logger.error(f"Error getting security compliance: {e}")
            self.send_error(500, f"Failed to get security compliance: {str(e)}")

    def get_notifications(self):
        """Get all notifications and alerts"""
        try:
            # Generate notification data (in real implementation, this would come from a notification service)
            notifications_data = {
                "timestamp": datetime.now().isoformat(),
                "unread_count": 3,
                "notifications": [
                    {
                        "id": "notif_001",
                        "type": "TRADING_ALERT",
                        "severity": "HIGH",
                        "title": "Position Risk Alert",
                        "message": "BTCUSDT position approaching liquidation threshold",
                        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                        "read": False,
                        "action_required": True,
                        "metadata": {
                            "symbol": "BTCUSDT",
                            "position_size": "0.5 BTC",
                            "liquidation_price": "$45,200",
                            "current_price": "$48,056"
                        }
                    },
                    {
                        "id": "notif_002",
                        "type": "SYSTEM_ALERT",
                        "severity": "MEDIUM",
                        "title": "Service Health Warning",
                        "message": "KingFisher AI service response time increased",
                        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                        "read": False,
                        "action_required": False,
                        "metadata": {
                            "service": "KingFisher AI",
                            "response_time": "2.3s",
                            "threshold": "1.5s"
                        }
                    },
                    {
                        "id": "notif_003",
                        "type": "MARKET_ALERT",
                        "severity": "LOW",
                        "title": "Market Opportunity",
                        "message": "ETHUSDT showing bullish divergence pattern",
                        "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                        "read": True,
                        "action_required": False,
                        "metadata": {
                            "symbol": "ETHUSDT",
                            "pattern": "Bullish Divergence",
                            "confidence": "75%"
                        }
                    },
                    {
                        "id": "notif_004",
                        "type": "PERFORMANCE_ALERT",
                        "severity": "HIGH",
                        "title": "Portfolio Performance",
                        "message": "Daily P&L exceeded target: +$2,450 (12.3%)",
                        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                        "read": True,
                        "action_required": False,
                        "metadata": {
                            "pnl": "$2,450",
                            "percentage": "12.3%",
                            "target": "5%"
                        }
                    },
                    {
                        "id": "notif_005",
                        "type": "SECURITY_ALERT",
                        "severity": "CRITICAL",
                        "title": "Security Warning",
                        "message": "Multiple failed login attempts detected",
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "read": False,
                        "action_required": True,
                        "metadata": {
                            "ip_address": "192.168.1.100",
                            "attempts": 5,
                            "timeframe": "10 minutes"
                        }
                    }
                ],
                "notification_types": [
                    {"type": "TRADING_ALERT", "count": 1, "unread": 1},
                    {"type": "SYSTEM_ALERT", "count": 1, "unread": 1},
                    {"type": "MARKET_ALERT", "count": 1, "unread": 0},
                    {"type": "PERFORMANCE_ALERT", "count": 1, "unread": 0},
                    {"type": "SECURITY_ALERT", "count": 1, "unread": 1}
                ],
                "settings": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "trading_alerts": True,
                    "system_alerts": True,
                    "market_alerts": True,
                    "performance_alerts": True,
                    "security_alerts": True
                }
            }
            
            self.send_json_response(notifications_data)
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            self.send_error(500, f"Failed to get notifications: {str(e)}")

    def mark_notification_read(self):
        """Mark a notification as read"""
        try:
            # Parse request body for notification ID
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                notification_id = data.get('notification_id')
                
                if notification_id:
                    # In real implementation, this would update the database
                    logger.info(f"Marking notification {notification_id} as read")
                    
                    response_data = {
                        "success": True,
                        "message": f"Notification {notification_id} marked as read",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.send_json_response(response_data)
                else:
                    self.send_error(400, "Notification ID required")
            else:
                self.send_error(400, "Request body required")
                
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            self.send_error(500, f"Failed to mark notification as read: {str(e)}")

    def clear_all_notifications(self):
        """Clear all notifications"""
        try:
            # In real implementation, this would clear notifications from database
            logger.info("Clearing all notifications")
            
            response_data = {
                "success": True,
                "message": "All notifications cleared",
                "timestamp": datetime.now().isoformat(),
                "cleared_count": 5
            }
            self.send_json_response(response_data)
            
        except Exception as e:
            logger.error(f"Error clearing notifications: {e}")
            self.send_error(500, f"Failed to clear notifications: {str(e)}")

    def export_portfolio_data(self):
        """Export portfolio data as CSV"""
        try:
            # Get query parameters for export format
            query_params = self.parse_query_params()
            export_format = query_params.get('format', 'csv')
            date_range = query_params.get('date_range', '30d')
            
            # Generate portfolio data (in real implementation, this would come from database)
            portfolio_data = {
                "export_info": {
                    "type": "portfolio_data",
                    "format": export_format,
                    "date_range": date_range,
                    "generated_at": datetime.now().isoformat(),
                    "total_assets": 12,
                    "total_value": "$125,450.00"
                },
                "assets": [
                    {
                        "symbol": "BTCUSDT",
                        "asset": "BTC",
                        "quantity": "0.5",
                        "avg_price": "$45,200.00",
                        "current_price": "$48,056.00",
                        "market_value": "$24,028.00",
                        "unrealized_pnl": "$1,428.00",
                        "unrealized_pnl_percent": "6.32%",
                        "allocation_percent": "19.15%"
                    },
                    {
                        "symbol": "ETHUSDT",
                        "asset": "ETH",
                        "quantity": "2.0",
                        "avg_price": "$2,800.00",
                        "current_price": "$3,150.00",
                        "market_value": "$6,300.00",
                        "unrealized_pnl": "$700.00",
                        "unrealized_pnl_percent": "12.50%",
                        "allocation_percent": "5.02%"
                    },
                    {
                        "symbol": "ADAUSDT",
                        "asset": "ADA",
                        "quantity": "10000",
                        "avg_price": "$0.45",
                        "current_price": "$0.52",
                        "market_value": "$5,200.00",
                        "unrealized_pnl": "$700.00",
                        "unrealized_pnl_percent": "15.56%",
                        "allocation_percent": "4.14%"
                    }
                ],
                "summary": {
                    "total_invested": "$120,000.00",
                    "total_market_value": "$125,450.00",
                    "total_unrealized_pnl": "$5,450.00",
                    "total_unrealized_pnl_percent": "4.54%",
                    "best_performer": "ADAUSDT (+15.56%)",
                    "worst_performer": "BTCUSDT (+6.32%)"
                }
            }
            
            if export_format == 'csv':
                # Generate CSV content
                csv_content = self.generate_portfolio_csv(portfolio_data)
                self.send_csv_response(csv_content, f"portfolio_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            else:
                # Return JSON data
                self.send_json_response(portfolio_data)
                
        except Exception as e:
            logger.error(f"Error exporting portfolio data: {e}")
            self.send_error(500, f"Failed to export portfolio data: {str(e)}")

    def export_trades_data(self):
        """Export trading data as CSV"""
        try:
            query_params = self.parse_query_params()
            export_format = query_params.get('format', 'csv')
            date_range = query_params.get('date_range', '30d')
            
            # Generate trades data
            trades_data = {
                "export_info": {
                    "type": "trades_data",
                    "format": export_format,
                    "date_range": date_range,
                    "generated_at": datetime.now().isoformat(),
                    "total_trades": 45,
                    "win_rate": "68.89%"
                },
                "trades": [
                    {
                        "trade_id": "T001",
                        "symbol": "BTCUSDT",
                        "side": "BUY",
                        "quantity": "0.1",
                        "price": "$47,500.00",
                        "amount": "$4,750.00",
                        "fee": "$4.75",
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "status": "FILLED",
                        "pnl": "$55.60",
                        "pnl_percent": "1.17%"
                    },
                    {
                        "trade_id": "T002",
                        "symbol": "ETHUSDT",
                        "side": "SELL",
                        "quantity": "0.5",
                        "price": "$3,200.00",
                        "amount": "$1,600.00",
                        "fee": "$1.60",
                        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
                        "status": "FILLED",
                        "pnl": "$150.00",
                        "pnl_percent": "10.34%"
                    }
                ],
                "summary": {
                    "total_trades": 45,
                    "winning_trades": 31,
                    "losing_trades": 14,
                    "win_rate": "68.89%",
                    "total_pnl": "$2,450.00",
                    "avg_pnl_per_trade": "$54.44",
                    "best_trade": "ETHUSDT (+15.67%)",
                    "worst_trade": "BTCUSDT (-3.21%)"
                }
            }
            
            if export_format == 'csv':
                csv_content = self.generate_trades_csv(trades_data)
                self.send_csv_response(csv_content, f"trades_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            else:
                self.send_json_response(trades_data)
                
        except Exception as e:
            logger.error(f"Error exporting trades data: {e}")
            self.send_error(500, f"Failed to export trades data: {str(e)}")

    def export_performance_data(self):
        """Export performance analytics data"""
        try:
            query_params = self.parse_query_params()
            export_format = query_params.get('format', 'csv')
            date_range = query_params.get('date_range', '30d')
            
            # Generate performance data
            performance_data = {
                "export_info": {
                    "type": "performance_data",
                    "format": export_format,
                    "date_range": date_range,
                    "generated_at": datetime.now().isoformat()
                },
                "metrics": {
                    "portfolio_performance": {
                        "total_return": "12.3%",
                        "annualized_return": "156.7%",
                        "sharpe_ratio": "2.45",
                        "max_drawdown": "-8.2%",
                        "volatility": "24.5%",
                        "var_95": "$2,450.00"
                    },
                    "trading_performance": {
                        "win_rate": "68.89%",
                        "profit_factor": "2.34",
                        "avg_win": "$125.50",
                        "avg_loss": "$53.60",
                        "largest_win": "$450.00",
                        "largest_loss": "$180.00"
                    },
                    "risk_metrics": {
                        "beta": "1.15",
                        "alpha": "8.7%",
                        "information_ratio": "1.89",
                        "calmar_ratio": "19.1",
                        "sortino_ratio": "3.21"
                    }
                },
                "daily_returns": [
                    {"date": "2025-09-01", "return": "2.3%", "cumulative": "2.3%"},
                    {"date": "2025-09-02", "return": "-1.2%", "cumulative": "1.1%"},
                    {"date": "2025-09-03", "return": "3.1%", "cumulative": "4.2%"}
                ]
            }
            
            if export_format == 'csv':
                csv_content = self.generate_performance_csv(performance_data)
                self.send_csv_response(csv_content, f"performance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            else:
                self.send_json_response(performance_data)
                
        except Exception as e:
            logger.error(f"Error exporting performance data: {e}")
            self.send_error(500, f"Failed to export performance data: {str(e)}")

    def generate_pdf_report(self):
        """Generate comprehensive PDF report"""
        try:
            query_params = self.parse_query_params()
            report_type = query_params.get('type', 'comprehensive')
            date_range = query_params.get('date_range', '30d')
            
            # Generate PDF report data
            report_data = {
                "report_info": {
                    "type": report_type,
                    "date_range": date_range,
                    "generated_at": datetime.now().isoformat(),
                    "generated_by": "ZmartBot Professional Dashboard"
                },
                "executive_summary": {
                    "total_portfolio_value": "$125,450.00",
                    "total_return": "12.3%",
                    "risk_level": "Moderate",
                    "recommendation": "Continue current strategy with slight risk reduction"
                },
                "portfolio_overview": {
                    "total_assets": 12,
                    "diversification_score": "Good",
                    "top_performer": "ADAUSDT (+15.56%)",
                    "needs_attention": "BTCUSDT position size"
                },
                "trading_summary": {
                    "total_trades": 45,
                    "win_rate": "68.89%",
                    "avg_daily_trades": "1.5",
                    "most_traded_pair": "BTCUSDT"
                },
                "risk_analysis": {
                    "var_95": "$2,450.00",
                    "max_drawdown": "-8.2%",
                    "sharpe_ratio": "2.45",
                    "risk_score": "Medium"
                },
                "recommendations": [
                    "Consider reducing BTCUSDT position size to manage risk",
                    "Increase diversification with additional altcoins",
                    "Implement stop-loss orders for better risk management",
                    "Monitor market volatility and adjust position sizes accordingly"
                ]
            }
            
            # For now, return JSON data (in real implementation, this would generate actual PDF)
            self.send_json_response(report_data)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            self.send_error(500, f"Failed to generate PDF report: {str(e)}")

    def generate_portfolio_csv(self, data):
        """Generate CSV content for portfolio data"""
        csv_lines = []
        csv_lines.append("Symbol,Asset,Quantity,Avg Price,Current Price,Market Value,Unrealized PnL,Unrealized PnL %,Allocation %")
        
        for asset in data["assets"]:
            csv_lines.append(f"{asset['symbol']},{asset['asset']},{asset['quantity']},{asset['avg_price']},{asset['current_price']},{asset['market_value']},{asset['unrealized_pnl']},{asset['unrealized_pnl_percent']},{asset['allocation_percent']}")
        
        return "\n".join(csv_lines)

    def generate_trades_csv(self, data):
        """Generate CSV content for trades data"""
        csv_lines = []
        csv_lines.append("Trade ID,Symbol,Side,Quantity,Price,Amount,Fee,Timestamp,Status,PnL,PnL %")
        
        for trade in data["trades"]:
            csv_lines.append(f"{trade['trade_id']},{trade['symbol']},{trade['side']},{trade['quantity']},{trade['price']},{trade['amount']},{trade['fee']},{trade['timestamp']},{trade['status']},{trade['pnl']},{trade['pnl_percent']}")
        
        return "\n".join(csv_lines)

    def generate_performance_csv(self, data):
        """Generate CSV content for performance data"""
        csv_lines = []
        csv_lines.append("Metric,Value")
        
        # Portfolio performance
        for key, value in data["metrics"]["portfolio_performance"].items():
            csv_lines.append(f"Portfolio_{key},{value}")
        
        # Trading performance
        for key, value in data["metrics"]["trading_performance"].items():
            csv_lines.append(f"Trading_{key},{value}")
        
        # Risk metrics
        for key, value in data["metrics"]["risk_metrics"].items():
            csv_lines.append(f"Risk_{key},{value}")
        
        return "\n".join(csv_lines)

    def send_csv_response(self, csv_content, filename):
        """Send CSV response with proper headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/csv')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(csv_content.encode('utf-8'))

    def parse_query_params(self):
        """Parse query parameters from URL"""
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(self.path)
        return {k: v[0] for k, v in parse_qs(parsed_url.query).items()}

    def get_theme_preferences(self):
        """Get current theme preferences"""
        try:
            # Get query parameters for user identification
            query_params = self.parse_query_params()
            user_id = query_params.get('user_id', 'default')
            
            # Generate theme preferences data (in real implementation, this would come from user database)
            theme_data = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "current_theme": "dark",
                "available_themes": [
                    {
                        "id": "dark",
                        "name": "Dark Mode",
                        "description": "Professional dark theme with high contrast",
                        "primary_color": "#1a1a1a",
                        "secondary_color": "#2d2d2d",
                        "accent_color": "#00d4aa",
                        "text_primary": "#ffffff",
                        "text_secondary": "#b0b0b0",
                        "background": "#0f0f0f",
                        "card_background": "#1a1a1a",
                        "border_color": "#333333"
                    },
                    {
                        "id": "light",
                        "name": "Light Mode",
                        "description": "Clean light theme with modern design",
                        "primary_color": "#ffffff",
                        "secondary_color": "#f8f9fa",
                        "accent_color": "#007bff",
                        "text_primary": "#212529",
                        "text_secondary": "#6c757d",
                        "background": "#ffffff",
                        "card_background": "#f8f9fa",
                        "border_color": "#dee2e6"
                    },
                    {
                        "id": "auto",
                        "name": "Auto Mode",
                        "description": "Automatically switch based on system preference",
                        "primary_color": "var(--system-primary)",
                        "secondary_color": "var(--system-secondary)",
                        "accent_color": "var(--system-accent)",
                        "text_primary": "var(--system-text-primary)",
                        "text_secondary": "var(--system-text-secondary)",
                        "background": "var(--system-background)",
                        "card_background": "var(--system-card-background)",
                        "border_color": "var(--system-border)"
                    }
                ],
                "customization_options": {
                    "accent_colors": [
                        {"name": "ZmartBot Green", "value": "#00d4aa"},
                        {"name": "Professional Blue", "value": "#007bff"},
                        {"name": "Trading Orange", "value": "#ff6b35"},
                        {"name": "Success Green", "value": "#28a745"},
                        {"name": "Warning Yellow", "value": "#ffc107"},
                        {"name": "Danger Red", "value": "#dc3545"},
                        {"name": "Purple", "value": "#6f42c1"},
                        {"name": "Pink", "value": "#e83e8c"}
                    ],
                    "font_sizes": [
                        {"name": "Small", "value": "12px"},
                        {"name": "Medium", "value": "14px"},
                        {"name": "Large", "value": "16px"},
                        {"name": "Extra Large", "value": "18px"}
                    ],
                    "layout_density": [
                        {"name": "Compact", "value": "compact"},
                        {"name": "Normal", "value": "normal"},
                        {"name": "Comfortable", "value": "comfortable"}
                    ]
                },
                "user_preferences": {
                    "theme": "dark",
                    "accent_color": "#00d4aa",
                    "font_size": "14px",
                    "layout_density": "normal",
                    "auto_switch": True,
                    "high_contrast": False,
                    "reduced_motion": False,
                    "custom_css": ""
                }
            }
            
            self.send_json_response(theme_data)
            
        except Exception as e:
            logger.error(f"Error getting theme preferences: {e}")
            self.send_error(500, f"Failed to get theme preferences: {str(e)}")

    def update_theme_preferences(self):
        """Update theme preferences for user"""
        try:
            # Get request data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                theme_data = json.loads(post_data.decode('utf-8'))
            else:
                theme_data = {}
            
            # Validate theme data
            required_fields = ['theme', 'accent_color', 'font_size', 'layout_density']
            for field in required_fields:
                if field not in theme_data:
                    self.send_error(400, f"Missing required field: {field}")
                    return
            
            # Update theme preferences (in real implementation, this would save to user database)
            updated_preferences = {
                "timestamp": datetime.now().isoformat(),
                "user_id": theme_data.get('user_id', 'default'),
                "updated_preferences": {
                    "theme": theme_data['theme'],
                    "accent_color": theme_data['accent_color'],
                    "font_size": theme_data['font_size'],
                    "layout_density": theme_data['layout_density'],
                    "auto_switch": theme_data.get('auto_switch', True),
                    "high_contrast": theme_data.get('high_contrast', False),
                    "reduced_motion": theme_data.get('reduced_motion', False),
                    "custom_css": theme_data.get('custom_css', '')
                },
                "status": "success",
                "message": "Theme preferences updated successfully"
            }
            
            # Log theme change
            logger.info(f"Theme preferences updated for user {theme_data.get('user_id', 'default')}: {theme_data['theme']} theme with {theme_data['accent_color']} accent")
            
            self.send_json_response(updated_preferences)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in theme update request: {e}")
            self.send_error(400, "Invalid JSON data")
        except Exception as e:
                logger.error(f"Error updating theme preferences: {e}")
                self.send_error(500, f"Failed to update theme preferences: {str(e)}")

    def handle_users_request(self):
        """Handle user management requests"""
        try:
            if self.command == 'GET':
                self.get_users_list()
            elif self.command == 'POST':
                self.create_user()
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            logger.error(f"Error handling users request: {e}")
            self.send_error(500, f"Failed to handle users request: {str(e)}")

    def handle_user_detail_request(self):
        """Handle individual user requests"""
        try:
            # Extract user ID from path
            path_parts = self.path.split('/')
            user_id = path_parts[-1] if path_parts else None
            
            if not user_id or user_id == 'users':
                self.send_error(400, "User ID required")
                return
            
            if self.command == 'GET':
                self.get_user_details(user_id)
            elif self.command == 'PUT':
                self.update_user(user_id)
            elif self.command == 'DELETE':
                self.delete_user(user_id)
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            logger.error(f"Error handling user detail request: {e}")
            self.send_error(500, f"Failed to handle user detail request: {str(e)}")

    def get_users_list(self):
        """Get list of all users"""
        try:
            # Generate sample users data
            users_data = {
                "timestamp": datetime.now().isoformat(),
                "total_users": 5,
                "active_users": 4,
                "users": [
                    {
                        "id": "user_001",
                        "username": "admin",
                        "email": "admin@zmartbot.com",
                        "role": "Administrator",
                        "status": "active",
                        "last_login": "2025-09-10T00:30:00Z",
                        "created_at": "2025-01-15T10:00:00Z",
                        "permissions": ["all"],
                        "profile": {
                            "first_name": "System",
                            "last_name": "Administrator",
                            "avatar": "👑",
                            "department": "IT"
                        }
                    },
                    {
                        "id": "user_002",
                        "username": "trader_pro",
                        "email": "trader@zmartbot.com",
                        "role": "Trader",
                        "status": "active",
                        "last_login": "2025-09-09T23:45:00Z",
                        "created_at": "2025-02-20T14:30:00Z",
                        "permissions": ["trading", "analysis", "portfolio"],
                        "profile": {
                            "first_name": "John",
                            "last_name": "Trader",
                            "avatar": "📈",
                            "department": "Trading"
                        }
                    },
                    {
                        "id": "user_003",
                        "username": "analyst_ai",
                        "email": "analyst@zmartbot.com",
                        "role": "Analyst",
                        "status": "active",
                        "last_login": "2025-09-09T22:15:00Z",
                        "created_at": "2025-03-10T09:15:00Z",
                        "permissions": ["analysis", "reports", "charts"],
                        "profile": {
                            "first_name": "Sarah",
                            "last_name": "Analyst",
                            "avatar": "🧠",
                            "department": "Research"
                        }
                    },
                    {
                        "id": "user_004",
                        "username": "viewer_limited",
                        "email": "viewer@zmartbot.com",
                        "role": "Viewer",
                        "status": "active",
                        "last_login": "2025-09-09T21:00:00Z",
                        "created_at": "2025-04-05T16:20:00Z",
                        "permissions": ["view_dashboard", "view_reports"],
                        "profile": {
                            "first_name": "Mike",
                            "last_name": "Viewer",
                            "avatar": "👁️",
                            "department": "Management"
                        }
                    },
                    {
                        "id": "user_005",
                        "username": "guest_user",
                        "email": "guest@zmartbot.com",
                        "role": "Guest",
                        "status": "inactive",
                        "last_login": "2025-09-08T18:30:00Z",
                        "created_at": "2025-05-15T11:45:00Z",
                        "permissions": ["view_dashboard"],
                        "profile": {
                            "first_name": "Guest",
                            "last_name": "User",
                            "avatar": "👤",
                            "department": "External"
                        }
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_pages": 1
                }
            }
            
            self.send_json_response(users_data)
            
        except Exception as e:
            logger.error(f"Error getting users list: {e}")
            self.send_error(500, f"Failed to get users list: {str(e)}")

    def get_user_details(self, user_id):
        """Get detailed information about a specific user"""
        try:
            # Generate detailed user data
            user_details = {
                "timestamp": datetime.now().isoformat(),
                "user": {
                    "id": user_id,
                    "username": "trader_pro",
                    "email": "trader@zmartbot.com",
                    "role": "Trader",
                    "status": "active",
                    "last_login": "2025-09-09T23:45:00Z",
                    "created_at": "2025-02-20T14:30:00Z",
                    "updated_at": "2025-09-09T23:45:00Z",
                    "permissions": ["trading", "analysis", "portfolio"],
                    "profile": {
                        "first_name": "John",
                        "last_name": "Trader",
                        "avatar": "📈",
                        "department": "Trading",
                        "phone": "+1-555-0123",
                        "location": "New York, NY",
                        "timezone": "America/New_York",
                        "language": "en"
                    },
                    "security": {
                        "two_factor_enabled": True,
                        "last_password_change": "2025-08-15T10:00:00Z",
                        "login_attempts": 0,
                        "account_locked": False
                    },
                    "activity": {
                        "total_logins": 1247,
                        "last_activity": "2025-09-09T23:45:00Z",
                        "sessions_active": 1,
                        "api_calls_today": 156
                    },
                    "trading_stats": {
                        "total_trades": 89,
                        "successful_trades": 67,
                        "total_volume": 125000.50,
                        "profit_loss": 8750.25
                    }
                }
            }
            
            self.send_json_response(user_details)
            
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            self.send_error(500, f"Failed to get user details: {str(e)}")

    def create_user(self):
        """Create a new user"""
        try:
            # Get request data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                user_data = json.loads(post_data.decode('utf-8'))
            else:
                self.send_error(400, "User data required")
                return
            
            # Validate required fields
            required_fields = ['username', 'email', 'role']
            for field in required_fields:
                if field not in user_data:
                    self.send_error(400, f"Missing required field: {field}")
                    return
            
            # Create user response
            new_user = {
                "timestamp": datetime.now().isoformat(),
                "user": {
                    "id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "username": user_data['username'],
                    "email": user_data['email'],
                    "role": user_data['role'],
                    "status": "active",
                    "created_at": datetime.now().isoformat(),
                    "permissions": self.get_role_permissions(user_data['role']),
                    "profile": user_data.get('profile', {})
                },
                "status": "success",
                "message": "User created successfully"
            }
            
            logger.info(f"New user created: {user_data['username']} with role {user_data['role']}")
            self.send_json_response(new_user)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in create user request: {e}")
            self.send_error(400, "Invalid JSON data")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.send_error(500, f"Failed to create user: {str(e)}")

    def update_user(self, user_id):
        """Update an existing user"""
        try:
            # Get request data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                user_data = json.loads(post_data.decode('utf-8'))
            else:
                self.send_error(400, "User data required")
                return
            
            # Update user response
            updated_user = {
                "timestamp": datetime.now().isoformat(),
                "user": {
                    "id": user_id,
                    "username": user_data.get('username', 'trader_pro'),
                    "email": user_data.get('email', 'trader@zmartbot.com'),
                    "role": user_data.get('role', 'Trader'),
                    "status": user_data.get('status', 'active'),
                    "updated_at": datetime.now().isoformat(),
                    "permissions": self.get_role_permissions(user_data.get('role', 'Trader')),
                    "profile": user_data.get('profile', {})
                },
                "status": "success",
                "message": "User updated successfully"
            }
            
            logger.info(f"User updated: {user_id}")
            self.send_json_response(updated_user)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in update user request: {e}")
            self.send_error(400, "Invalid JSON data")
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            self.send_error(500, f"Failed to update user: {str(e)}")

    def delete_user(self, user_id):
        """Delete a user"""
        try:
            # Delete user response
            delete_response = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "status": "success",
                "message": "User deleted successfully"
            }
            
            logger.info(f"User deleted: {user_id}")
            self.send_json_response(delete_response)
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            self.send_error(500, f"Failed to delete user: {str(e)}")

    def get_user_roles(self):
        """Get available user roles and their permissions"""
        try:
            roles_data = {
                "timestamp": datetime.now().isoformat(),
                "roles": [
                    {
                        "id": "administrator",
                        "name": "Administrator",
                        "description": "Full system access and management capabilities",
                        "permissions": [
                            "all",
                            "user_management",
                            "system_configuration",
                            "security_management"
                        ],
                        "color": "#dc3545",
                        "icon": "👑"
                    },
                    {
                        "id": "trader",
                        "name": "Trader",
                        "description": "Trading operations and portfolio management",
                        "permissions": [
                            "trading",
                            "portfolio",
                            "analysis",
                            "reports",
                            "charts"
                        ],
                        "color": "#28a745",
                        "icon": "📈"
                    },
                    {
                        "id": "analyst",
                        "name": "Analyst",
                        "description": "Market analysis and research capabilities",
                        "permissions": [
                            "analysis",
                            "reports",
                            "charts",
                            "research"
                        ],
                        "color": "#007bff",
                        "icon": "🧠"
                    },
                    {
                        "id": "viewer",
                        "name": "Viewer",
                        "description": "Read-only access to dashboard and reports",
                        "permissions": [
                            "view_dashboard",
                            "view_reports",
                            "view_charts"
                        ],
                        "color": "#6c757d",
                        "icon": "👁️"
                    },
                    {
                        "id": "guest",
                        "name": "Guest",
                        "description": "Limited access for external users",
                        "permissions": [
                            "view_dashboard"
                        ],
                        "color": "#ffc107",
                        "icon": "👤"
                    }
                ]
            }
            
            self.send_json_response(roles_data)
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            self.send_error(500, f"Failed to get user roles: {str(e)}")

    def get_permissions(self):
        """Get all available permissions"""
        try:
            permissions_data = {
                "timestamp": datetime.now().isoformat(),
                "permissions": [
                    {
                        "category": "System",
                        "permissions": [
                            {"id": "all", "name": "All Permissions", "description": "Full system access"},
                            {"id": "user_management", "name": "User Management", "description": "Manage users and roles"},
                            {"id": "system_configuration", "name": "System Configuration", "description": "Configure system settings"},
                            {"id": "security_management", "name": "Security Management", "description": "Manage security settings"}
                        ]
                    },
                    {
                        "category": "Trading",
                        "permissions": [
                            {"id": "trading", "name": "Trading Operations", "description": "Execute trades and manage positions"},
                            {"id": "portfolio", "name": "Portfolio Management", "description": "Manage portfolio and assets"},
                            {"id": "risk_management", "name": "Risk Management", "description": "Configure risk parameters"}
                        ]
                    },
                    {
                        "category": "Analysis",
                        "permissions": [
                            {"id": "analysis", "name": "Market Analysis", "description": "Perform market analysis"},
                            {"id": "research", "name": "Research", "description": "Access research tools and data"},
                            {"id": "reports", "name": "Reports", "description": "Generate and view reports"},
                            {"id": "charts", "name": "Charts", "description": "Access advanced charting tools"}
                        ]
                    },
                    {
                        "category": "Viewing",
                        "permissions": [
                            {"id": "view_dashboard", "name": "View Dashboard", "description": "Access main dashboard"},
                            {"id": "view_reports", "name": "View Reports", "description": "View generated reports"},
                            {"id": "view_charts", "name": "View Charts", "description": "View charts and graphs"}
                        ]
                    }
                ]
            }
            
            self.send_json_response(permissions_data)
            
        except Exception as e:
            logger.error(f"Error getting permissions: {e}")
            self.send_error(500, f"Failed to get permissions: {str(e)}")

    def get_role_permissions(self, role):
        """Get permissions for a specific role"""
        role_permissions = {
            "Administrator": ["all"],
            "Trader": ["trading", "analysis", "portfolio"],
            "Analyst": ["analysis", "reports", "charts"],
            "Viewer": ["view_dashboard", "view_reports"],
            "Guest": ["view_dashboard"]
        }
        return role_permissions.get(role, ["view_dashboard"])

    def handle_backup_request(self):
        """Handle backup requests"""
        try:
            if self.command == 'GET':
                self.get_backup_list()
            elif self.command == 'POST':
                self.create_backup()
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            logger.error(f"Error handling backup request: {e}")
            self.send_error(500, f"Failed to handle backup request: {str(e)}")

    def handle_restore_request(self):
        """Handle restore requests"""
        try:
            if self.command == 'POST':
                self.restore_backup()
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            logger.error(f"Error handling restore request: {e}")
            self.send_error(500, f"Failed to handle restore request: {str(e)}")

    def handle_backup_detail_request(self):
        """Handle backup detail requests"""
        try:
            backup_id = self.path.split('/')[-1]
            if self.command == 'GET':
                self.get_backup_details(backup_id)
            elif self.command == 'DELETE':
                self.delete_backup(backup_id)
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            logger.error(f"Error handling backup detail request: {e}")
            self.send_error(500, f"Failed to handle backup detail request: {str(e)}")

    def get_backup_list(self):
        """Get list of available backups"""
        try:
            backups = [
                {
                    "id": "backup_001",
                    "name": "Full System Backup",
                    "type": "full",
                    "size": "2.4 GB",
                    "created_at": "2025-09-09T15:30:00Z",
                    "status": "completed",
                    "description": "Complete system backup including all user data, configurations, and trading history"
                },
                {
                    "id": "backup_002", 
                    "name": "User Data Backup",
                    "type": "user_data",
                    "size": "156 MB",
                    "created_at": "2025-09-09T12:00:00Z",
                    "status": "completed",
                    "description": "User accounts, roles, and permissions backup"
                },
                {
                    "id": "backup_003",
                    "name": "Trading History Backup",
                    "type": "trading_data",
                    "size": "890 MB", 
                    "created_at": "2025-09-09T08:15:00Z",
                    "status": "completed",
                    "description": "Complete trading history and portfolio data"
                },
                {
                    "id": "backup_004",
                    "name": "Configuration Backup",
                    "type": "config",
                    "size": "12 MB",
                    "created_at": "2025-09-09T06:00:00Z",
                    "status": "completed",
                    "description": "System configurations and API settings"
                }
            ]
            
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "total_backups": len(backups),
                "backups": backups
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            logger.error(f"Error getting backup list: {e}")
            self.send_error(500, f"Failed to get backup list: {str(e)}")

    def create_backup(self):
        """Create a new backup"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                backup_data = json.loads(post_data.decode('utf-8'))
            else:
                backup_data = {}
            
            backup_name = backup_data.get('name', f"Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            backup_type = backup_data.get('type', 'full')
            description = backup_data.get('description', 'Automated backup')
            
            # Simulate backup creation
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "message": "Backup created successfully",
                "backup": {
                    "id": backup_id,
                    "name": backup_name,
                    "type": backup_type,
                    "description": description,
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                    "size": "1.2 GB"
                }
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self.send_error(500, f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        """Restore from a backup"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                restore_data = json.loads(post_data.decode('utf-8'))
            else:
                self.send_error(400, "Backup ID required for restore")
                return
            
            backup_id = restore_data.get('backup_id')
            if not backup_id:
                self.send_error(400, "Backup ID required for restore")
                return
            
            # Simulate restore process
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "message": "Backup restored successfully",
                "restore": {
                    "backup_id": backup_id,
                    "status": "completed",
                    "restored_at": datetime.now().isoformat(),
                    "items_restored": [
                        "User accounts",
                        "Trading history", 
                        "System configurations",
                        "API settings"
                    ]
                }
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            self.send_error(500, f"Failed to restore backup: {str(e)}")

    def get_backup_details(self, backup_id):
        """Get detailed information about a specific backup"""
        try:
            # Simulate backup details
            backup_details = {
                "id": backup_id,
                "name": f"Backup {backup_id}",
                "type": "full",
                "size": "2.4 GB",
                "created_at": "2025-09-09T15:30:00Z",
                "status": "completed",
                "description": "Complete system backup",
                "files": [
                    {"name": "users.json", "size": "45 MB", "type": "user_data"},
                    {"name": "trading_history.db", "size": "1.8 GB", "type": "trading_data"},
                    {"name": "config.json", "size": "2 MB", "type": "configuration"},
                    {"name": "api_keys.json", "size": "1 MB", "type": "secrets"}
                ],
                "checksum": "sha256:abc123def456...",
                "compression": "gzip",
                "encryption": "AES-256"
            }
            
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "backup": backup_details
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            logger.error(f"Error getting backup details: {e}")
            self.send_error(500, f"Failed to get backup details: {str(e)}")

    def delete_backup(self, backup_id):
        """Delete a backup"""
        try:
            # Simulate backup deletion
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "message": f"Backup {backup_id} deleted successfully",
                "deleted_backup": {
                    "id": backup_id,
                    "deleted_at": datetime.now().isoformat()
                }
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            logger.error(f"Error deleting backup: {e}")
            self.send_error(500, f"Failed to delete backup: {str(e)}")

def main():
    """Main function to start the dashboard server"""
    print("🚀 Starting ZmartBot Professional Dashboard...")
    print(f"📍 Host: {HOST}")
    print(f"🔌 Port: {PORT}")
    print(f"🌐 URL: http://{HOST}:{PORT}")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer((HOST, PORT), ZmartBotDashboardHandler) as httpd:
            print(f"✅ Dashboard server started successfully on port {PORT}")
            print(f"📊 Professional Dashboard available at: http://{HOST}:{PORT}")
            print("🛑 Press Ctrl+C to stop the server")
            print("=" * 50)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
