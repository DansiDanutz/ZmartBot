#!/usr/bin/env python3
"""
Automated Performance Reporter
Generate comprehensive performance reports for ZmartBot system
"""

import json
import logging
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
import requests

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: str
    system_health: float
    api_response_times: Dict[str, float]
    service_uptime: Dict[str, float]
    error_rates: Dict[str, float]
    resource_usage: Dict[str, float]
    throughput_metrics: Dict[str, int]

class AutomatedPerformanceReporter:
    """Generate and distribute automated performance reports"""
    
    def __init__(self, config_file="performance_reporting_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.logger = self.setup_logger()
        self.reports_dir = Path("performance_reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def setup_logger(self):
        """Setup reporting logging"""
        logger = logging.getLogger('performance_reporter')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('performance_reporter.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_config(self):
        """Load reporting configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "reporting_enabled": True,
            "report_frequency": "daily",  # daily, weekly, monthly
            "report_time": "09:00",  # Time to generate report
            "email_notifications": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipients": []
            },
            "webhook_notifications": {
                "enabled": False,
                "webhook_url": "",
                "headers": {}
            },
            "metrics_to_include": [
                "system_health",
                "api_performance",
                "service_uptime",
                "error_rates",
                "resource_usage",
                "throughput"
            ],
            "retention_days": 30
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config):
        """Save reporting configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive system performance metrics"""
        self.logger.info("Collecting system performance metrics")
        
        # System health from service monitor
        system_health = self.get_system_health()
        
        # API response times
        api_response_times = self.get_api_response_times()
        
        # Service uptime
        service_uptime = self.get_service_uptime()
        
        # Error rates
        error_rates = self.get_error_rates()
        
        # Resource usage
        resource_usage = self.get_resource_usage()
        
        # Throughput metrics
        throughput_metrics = self.get_throughput_metrics()
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            system_health=system_health,
            api_response_times=api_response_times,
            service_uptime=service_uptime,
            error_rates=error_rates,
            resource_usage=resource_usage,
            throughput_metrics=throughput_metrics
        )
    
    def get_system_health(self) -> float:
        """Get overall system health percentage"""
        try:
            from expanded_service_monitor import service_monitor
            health_status = service_monitor.check_all_services()
            report = service_monitor.generate_health_report(health_status)
            return report['summary']['health_percentage']
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return 0.0
    
    def get_api_response_times(self) -> Dict[str, float]:
        """Get API response times for key endpoints"""
        api_endpoints = {
            "zmart-api": "http://localhost:8000/health",
            "kucoin": "http://localhost:8302/health",
            "binance": "http://localhost:8303/health",
            "api-keys-manager": "http://localhost:8006/health",
            "service-discovery": "http://localhost:8550/health"
        }
        
        response_times = {}
        for service, url in api_endpoints.items():
            try:
                start_time = datetime.now()
                response = requests.get(url, timeout=5)
                end_time = datetime.now()
                
                if response.status_code == 200:
                    response_times[service] = (end_time - start_time).total_seconds() * 1000
                else:
                    response_times[service] = -1  # Error indicator
            except Exception:
                response_times[service] = -1  # Error indicator
        
        return response_times
    
    def get_service_uptime(self) -> Dict[str, float]:
        """Get service uptime percentages"""
        try:
            from expanded_service_monitor import service_monitor
            health_status = service_monitor.check_all_services()
            
            uptime_percentages = {}
            for service_name, health in health_status.items():
                if health.status == "HEALTHY":
                    uptime_percentages[service_name] = 100.0
                elif health.status in ["UNHEALTHY", "WARNING"]:
                    uptime_percentages[service_name] = 75.0
                else:
                    uptime_percentages[service_name] = 0.0
            
            return uptime_percentages
        except Exception as e:
            self.logger.error(f"Error getting service uptime: {e}")
            return {}
    
    def get_error_rates(self) -> Dict[str, float]:
        """Get error rates for services"""
        try:
            from expanded_service_monitor import service_monitor
            health_status = service_monitor.check_all_services()
            
            error_rates = {}
            for service_name, health in health_status.items():
                # Calculate error rate based on error count and status
                if health.status == "HEALTHY":
                    error_rates[service_name] = 0.0
                elif health.status in ["UNHEALTHY", "WARNING"]:
                    error_rates[service_name] = min(health.error_count * 10, 50.0)
                else:
                    error_rates[service_name] = 100.0
            
            return error_rates
        except Exception as e:
            self.logger.error(f"Error getting error rates: {e}")
            return {}
    
    def get_resource_usage(self) -> Dict[str, float]:
        """Get system resource usage"""
        import psutil
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict()
            }
        except Exception as e:
            self.logger.error(f"Error getting resource usage: {e}")
            return {}
    
    def get_throughput_metrics(self) -> Dict[str, int]:
        """Get throughput metrics"""
        try:
            # This would typically come from application logs or metrics
            # For now, we'll simulate based on service health
            from expanded_service_monitor import service_monitor
            health_status = service_monitor.check_all_services()
            
            healthy_services = sum(1 for health in health_status.values() if health.status == "HEALTHY")
            total_services = len(health_status)
            
            return {
                "requests_per_minute": healthy_services * 100,  # Simulated
                "active_connections": healthy_services * 50,   # Simulated
                "data_processed_mb": healthy_services * 10,    # Simulated
                "services_operational": healthy_services,
                "total_services": total_services
            }
        except Exception as e:
            self.logger.error(f"Error getting throughput metrics: {e}")
            return {}
    
    def generate_performance_report(self, metrics: PerformanceMetrics) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "report_id": f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": metrics.timestamp,
            "report_type": "performance_summary",
            "summary": {
                "system_health": metrics.system_health,
                "overall_status": "HEALTHY" if metrics.system_health > 80 else "WARNING" if metrics.system_health > 60 else "CRITICAL",
                "total_services": len(metrics.service_uptime),
                "healthy_services": sum(1 for uptime in metrics.service_uptime.values() if uptime > 80),
                "average_response_time": sum(rt for rt in metrics.api_response_times.values() if rt > 0) / max(1, sum(1 for rt in metrics.api_response_times.values() if rt > 0)),
                "total_errors": sum(metrics.error_rates.values()),
                "resource_utilization": {
                    "cpu": metrics.resource_usage.get("cpu_percent", 0),
                    "memory": metrics.resource_usage.get("memory_percent", 0),
                    "disk": metrics.resource_usage.get("disk_percent", 0)
                }
            },
            "detailed_metrics": {
                "api_response_times": metrics.api_response_times,
                "service_uptime": metrics.service_uptime,
                "error_rates": metrics.error_rates,
                "resource_usage": metrics.resource_usage,
                "throughput_metrics": metrics.throughput_metrics
            },
            "recommendations": self.generate_recommendations(metrics),
            "alerts": self.generate_alerts(metrics)
        }
        
        return report
    
    def generate_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # System health recommendations
        if metrics.system_health < 80:
            recommendations.append("System health is below optimal. Review service configurations and restart unhealthy services.")
        
        # API response time recommendations
        slow_apis = [service for service, time in metrics.api_response_times.items() if time > 1000]
        if slow_apis:
            recommendations.append(f"Slow API response times detected for: {', '.join(slow_apis)}. Consider optimization.")
        
        # Error rate recommendations
        high_error_services = [service for service, rate in metrics.error_rates.items() if rate > 10]
        if high_error_services:
            recommendations.append(f"High error rates detected for: {', '.join(high_error_services)}. Investigate and fix issues.")
        
        # Resource usage recommendations
        if metrics.resource_usage.get("cpu_percent", 0) > 80:
            recommendations.append("High CPU usage detected. Consider scaling or optimization.")
        
        if metrics.resource_usage.get("memory_percent", 0) > 80:
            recommendations.append("High memory usage detected. Consider memory optimization or scaling.")
        
        if not recommendations:
            recommendations.append("System performance is optimal. Continue monitoring.")
        
        return recommendations
    
    def generate_alerts(self, metrics: PerformanceMetrics) -> List[Dict]:
        """Generate performance alerts"""
        alerts = []
        
        # Critical alerts
        if metrics.system_health < 50:
            alerts.append({
                "level": "CRITICAL",
                "message": f"System health critically low: {metrics.system_health:.1f}%",
                "action_required": "Immediate intervention required"
            })
        
        # Warning alerts
        if metrics.system_health < 80:
            alerts.append({
                "level": "WARNING",
                "message": f"System health below optimal: {metrics.system_health:.1f}%",
                "action_required": "Monitor closely and consider optimization"
            })
        
        # Resource alerts
        if metrics.resource_usage.get("cpu_percent", 0) > 90:
            alerts.append({
                "level": "CRITICAL",
                "message": "CPU usage critically high",
                "action_required": "Immediate scaling or optimization required"
            })
        
        return alerts
    
    def save_report(self, report: Dict):
        """Save performance report to file"""
        report_filename = f"performance_report_{report['report_id']}.json"
        report_path = self.reports_dir / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Performance report saved: {report_path}")
        return report_path
    
    def send_email_report(self, report: Dict):
        """Send performance report via email"""
        if not self.config.get("email_notifications", {}).get("enabled", False):
            return
        
        email_config = self.config["email_notifications"]
        
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = email_config["sender_email"]
            msg['To'] = ", ".join(email_config["recipients"])
            msg['Subject'] = f"ZmartBot Performance Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create email body
            body = self.format_report_for_email(report)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["sender_email"], email_config["sender_password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Performance report sent via email")
            
        except Exception as e:
            self.logger.error(f"Failed to send email report: {e}")
    
    def send_webhook_report(self, report: Dict):
        """Send performance report via webhook"""
        if not self.config.get("webhook_notifications", {}).get("enabled", False):
            return
        
        webhook_config = self.config["webhook_notifications"]
        
        try:
            response = requests.post(
                webhook_config["webhook_url"],
                json=report,
                headers=webhook_config.get("headers", {}),
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Performance report sent via webhook")
            else:
                self.logger.error(f"Webhook failed with status: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook report: {e}")
    
    def format_report_for_email(self, report: Dict) -> str:
        """Format report for email display"""
        html = f"""
        <html>
        <body>
            <h2>ZmartBot Performance Report</h2>
            <p><strong>Generated:</strong> {report['generated_at']}</p>
            
            <h3>Summary</h3>
            <ul>
                <li><strong>System Health:</strong> {report['summary']['system_health']:.1f}%</li>
                <li><strong>Overall Status:</strong> {report['summary']['overall_status']}</li>
                <li><strong>Healthy Services:</strong> {report['summary']['healthy_services']}/{report['summary']['total_services']}</li>
                <li><strong>Average Response Time:</strong> {report['summary']['average_response_time']:.1f}ms</li>
            </ul>
            
            <h3>Resource Utilization</h3>
            <ul>
                <li><strong>CPU:</strong> {report['summary']['resource_utilization']['cpu']:.1f}%</li>
                <li><strong>Memory:</strong> {report['summary']['resource_utilization']['memory']:.1f}%</li>
                <li><strong>Disk:</strong> {report['summary']['resource_utilization']['disk']:.1f}%</li>
            </ul>
            
            <h3>Recommendations</h3>
            <ul>
        """
        
        for rec in report['recommendations']:
            html += f"<li>{rec}</li>"
        
        html += "</ul>"
        
        if report['alerts']:
            html += "<h3>Alerts</h3><ul>"
            for alert in report['alerts']:
                html += f"<li><strong>{alert['level']}:</strong> {alert['message']}</li>"
            html += "</ul>"
        
        html += "</body></html>"
        return html
    
    def cleanup_old_reports(self):
        """Clean up old performance reports"""
        retention_days = self.config.get("retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        for report_file in self.reports_dir.glob("performance_report_*.json"):
            if report_file.stat().st_mtime < cutoff_date.timestamp():
                report_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old performance reports")
    
    def generate_and_distribute_report(self):
        """Generate and distribute performance report"""
        self.logger.info("Starting automated performance report generation")
        
        # Collect metrics
        metrics = self.collect_system_metrics()
        
        # Generate report
        report = self.generate_performance_report(metrics)
        
        # Save report
        report_path = self.save_report(report)
        
        # Send notifications
        self.send_email_report(report)
        self.send_webhook_report(report)
        
        # Cleanup old reports
        self.cleanup_old_reports()
        
        self.logger.info(f"Performance report generated and distributed: {report['report_id']}")
        
        return report

# Global performance reporter instance
performance_reporter = AutomatedPerformanceReporter()

if __name__ == "__main__":
    # Generate performance report
    reporter = AutomatedPerformanceReporter()
    report = reporter.generate_and_distribute_report()
    
    print("📊 Performance Report Generated:")
    print(f"   Report ID: {report['report_id']}")
    print(f"   System Health: {report['summary']['system_health']:.1f}%")
    print(f"   Overall Status: {report['summary']['overall_status']}")
    print(f"   Healthy Services: {report['summary']['healthy_services']}/{report['summary']['total_services']}")
    print(f"   Recommendations: {len(report['recommendations'])}")
    print(f"   Alerts: {len(report['alerts'])}")
