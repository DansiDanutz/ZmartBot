#!/usr/bin/env python3
"""
MDC Orchestration Dashboard
Real-time dashboard for monitoring and controlling the MDC Orchestration Agent
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import threading

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDC Orchestration Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1419; color: #fff; }
        .header { background: #1a2332; padding: 20px; border-bottom: 1px solid #2d3748; }
        .header h1 { color: #4fd1c7; font-size: 28px; margin-bottom: 5px; }
        .header p { color: #a0aec0; font-size: 14px; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: #1a2332; border: 1px solid #2d3748; border-radius: 8px; padding: 20px; }
        .card h3 { color: #4fd1c7; margin-bottom: 15px; font-size: 18px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-healthy { background: #48bb78; }
        .status-warning { background: #ed8936; }
        .status-error { background: #f56565; }
        .status-unknown { background: #718096; }
        .metric { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #2d3748; }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #a0aec0; font-size: 14px; }
        .metric-value { color: #fff; font-weight: 600; font-size: 14px; }
        .btn { background: #4fd1c7; color: #0f1419; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #38b2ac; }
        .btn-secondary { background: #2d3748; color: #fff; }
        .btn-secondary:hover { background: #4a5568; }
        .btn-danger { background: #f56565; color: #fff; }
        .btn-danger:hover { background: #e53e3e; }
        .controls { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .log-container { background: #0d1117; border: 1px solid #2d3748; border-radius: 6px; padding: 15px; max-height: 400px; overflow-y: auto; font-family: 'SF Mono', Monaco, monospace; font-size: 13px; }
        .log-line { margin-bottom: 2px; }
        .log-timestamp { color: #4fd1c7; }
        .log-level { font-weight: 600; }
        .log-info { color: #68d391; }
        .log-warning { color: #f6ad55; }
        .log-error { color: #fc8181; }
        .task-item { background: #2d3748; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
        .task-status { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .task-pending { background: #2d3748; color: #a0aec0; }
        .task-running { background: #3182ce; color: #fff; }
        .task-completed { background: #38a169; color: #fff; }
        .task-failed { background: #e53e3e; color: #fff; }
        .refresh-indicator { animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .connection-graph { background: #0d1117; border: 1px solid #2d3748; border-radius: 6px; padding: 15px; min-height: 200px; }
        .service-node { background: #2d3748; border: 1px solid #4fd1c7; border-radius: 4px; padding: 8px; margin: 5px; display: inline-block; font-size: 12px; }
        .auto-refresh { position: fixed; top: 20px; right: 20px; z-index: 1000; }
        .notification { position: fixed; top: 80px; right: 20px; background: #38a169; color: #fff; padding: 12px 16px; border-radius: 6px; z-index: 1000; display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 MDC Orchestration Dashboard</h1>
        <p>Real-time monitoring and control for the MDC management system</p>
    </div>
    
    <div class="auto-refresh">
        <button class="btn btn-secondary" onclick="toggleAutoRefresh()" id="autoRefreshBtn">Auto Refresh: ON</button>
    </div>
    
    <div class="notification" id="notification"></div>
    
    <div class="container">
        <!-- System Status -->
        <div class="grid">
            <div class="card">
                <h3>System Health</h3>
                <div id="systemHealth">
                    <div class="metric">
                        <span class="metric-label">Overall Status</span>
                        <span class="metric-value"><span class="status-indicator status-unknown"></span>Loading...</span>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn" onclick="triggerOrchestration('full')">Full Orchestration</button>
                    <button class="btn btn-secondary" onclick="triggerOrchestration('incremental')">Incremental Update</button>
                </div>
            </div>
            
            <div class="card">
                <h3>Subsystem Status</h3>
                <div id="subsystemStatus">
                    <div class="metric">
                        <span class="metric-label">MDC Agent</span>
                        <span class="metric-value"><span class="status-indicator status-unknown"></span>Unknown</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Connection Agent</span>
                        <span class="metric-value"><span class="status-indicator status-unknown"></span>Unknown</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Context Optimizer</span>
                        <span class="metric-value"><span class="status-indicator status-unknown"></span>Unknown</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>System Metrics</h3>
                <div id="systemMetrics">
                    <div class="metric">
                        <span class="metric-label">Total Services</span>
                        <span class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Connections</span>
                        <span class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CLAUDE.md Size</span>
                        <span class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Full Orchestration</span>
                        <span class="metric-value">-</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Active Tasks -->
        <div class="grid">
            <div class="card">
                <h3>Active Tasks</h3>
                <div id="activeTasks">
                    <p style="color: #a0aec0; text-align: center; padding: 20px;">No active tasks</p>
                </div>
            </div>
            
            <div class="card">
                <h3>Connection Discovery</h3>
                <div id="connectionStats">
                    <div class="metric">
                        <span class="metric-label">Services with Connections</span>
                        <span class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Average Connections</span>
                        <span class="metric-value">-</span>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn btn-secondary" onclick="discoverAllConnections()">Discover All</button>
                    <button class="btn btn-secondary" onclick="optimizeContext()">Optimize Context</button>
                </div>
            </div>
            
            <div class="card">
                <h3>Recent Activity</h3>
                <div id="recentActivity">
                    <p style="color: #a0aec0; text-align: center; padding: 20px;">No recent activity</p>
                </div>
            </div>
        </div>
        
        <!-- Logs and Details -->
        <div class="grid">
            <div class="card" style="grid-column: 1 / -1;">
                <h3>System Logs</h3>
                <div class="log-container" id="systemLogs">
                    <div class="log-line">
                        <span class="log-timestamp">[Loading...]</span>
                        <span class="log-level log-info">INFO</span>
                        Connecting to MDC Orchestration Agent...
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefresh = true;
        let refreshInterval;
        const API_BASE = 'http://localhost:8615';
        const DASHBOARD_API_BASE = '/api';
        
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.style.background = type === 'error' ? '#e53e3e' : '#38a169';
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
        
        async function fetchSystemStatus() {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/system-status`);
                const data = await response.json();
                updateSystemHealth(data.health);
                updateSystemMetrics(data.metrics);
                updateSubsystemStatus(data.subsystems);
            } catch (error) {
                console.error('Error fetching system status:', error);
            }
        }
        
        async function fetchActiveTasks() {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/tasks`);
                const data = await response.json();
                updateActiveTasks(data.active_tasks);
                updateRecentActivity(data.recent_completed);
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }
        }
        
        async function fetchConnectionStats() {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/connection-stats`);
                const data = await response.json();
                updateConnectionStats(data);
            } catch (error) {
                console.error('Error fetching connection stats:', error);
            }
        }
        
        async function fetchSystemLogs() {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/logs`);
                const data = await response.json();
                updateSystemLogs(data.logs);
            } catch (error) {
                console.error('Error fetching logs:', error);
            }
        }
        
        function updateSystemHealth(health) {
            const container = document.getElementById('systemHealth');
            const statusClass = health.overall_status === 'healthy' ? 'status-healthy' : 
                               health.overall_status === 'warning' ? 'status-warning' : 'status-error';
            
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">Overall Status</span>
                    <span class="metric-value"><span class="status-indicator ${statusClass}"></span>${health.overall_status}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Errors (Last Hour)</span>
                    <span class="metric-value">${health.errors_last_hour}</span>
                </div>
            `;
        }
        
        function updateSubsystemStatus(subsystems) {
            const container = document.getElementById('subsystemStatus');
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">MDC Agent</span>
                    <span class="metric-value"><span class="status-indicator ${getStatusClass(subsystems.mdc_agent_status)}"></span>${subsystems.mdc_agent_status}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Connection Agent</span>
                    <span class="metric-value"><span class="status-indicator ${getStatusClass(subsystems.connection_agent_status)}"></span>${subsystems.connection_agent_status}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Context Optimizer</span>
                    <span class="metric-value"><span class="status-indicator ${getStatusClass(subsystems.context_optimizer_status)}"></span>${subsystems.context_optimizer_status}</span>
                </div>
            `;
        }
        
        function updateSystemMetrics(metrics) {
            const container = document.getElementById('systemMetrics');
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">Total Services</span>
                    <span class="metric-value">${metrics.total_services}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Connections</span>
                    <span class="metric-value">${metrics.total_connections}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">CLAUDE.md Size</span>
                    <span class="metric-value">${formatBytes(metrics.claude_md_size)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Full Orchestration</span>
                    <span class="metric-value">${formatTimestamp(metrics.last_full_orchestration)}</span>
                </div>
            `;
        }
        
        function updateActiveTasks(tasks) {
            const container = document.getElementById('activeTasks');
            if (tasks.length === 0) {
                container.innerHTML = '<p style="color: #a0aec0; text-align: center; padding: 20px;">No active tasks</p>';
                return;
            }
            
            container.innerHTML = tasks.map(task => `
                <div class="task-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>${task.task_type}</span>
                        <span class="task-status task-${task.status}">${task.status.toUpperCase()}</span>
                    </div>
                    ${task.service_name ? `<div style="color: #a0aec0; font-size: 12px; margin-top: 4px;">Service: ${task.service_name}</div>` : ''}
                </div>
            `).join('');
        }
        
        function updateConnectionStats(stats) {
            const container = document.getElementById('connectionStats');
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">Services with Connections</span>
                    <span class="metric-value">${stats.services_with_connections || 0}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Average Connections</span>
                    <span class="metric-value">${(stats.average_connections || 0).toFixed(1)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Connection Types</span>
                    <span class="metric-value">${Object.keys(stats.connection_types || {}).length}</span>
                </div>
            `;
        }
        
        function updateRecentActivity(activities) {
            const container = document.getElementById('recentActivity');
            if (!activities || activities.length === 0) {
                container.innerHTML = '<p style="color: #a0aec0; text-align: center; padding: 20px;">No recent activity</p>';
                return;
            }
            
            container.innerHTML = activities.slice(0, 5).map(activity => `
                <div class="task-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>${activity.task_type}</span>
                        <span class="task-status task-${activity.status}">${activity.status.toUpperCase()}</span>
                    </div>
                    <div style="color: #a0aec0; font-size: 12px; margin-top: 4px;">${formatTimestamp(activity.completed_at)}</div>
                </div>
            `).join('');
        }
        
        function updateSystemLogs(logs) {
            const container = document.getElementById('systemLogs');
            if (!logs || logs.length === 0) {
                container.innerHTML = '<div class="log-line"><span class="log-timestamp">[No logs]</span></div>';
                return;
            }
            
            container.innerHTML = logs.slice(-50).map(log => `
                <div class="log-line">
                    <span class="log-timestamp">[${log.timestamp}]</span>
                    <span class="log-level log-${log.level.toLowerCase()}">${log.level}</span>
                    ${log.message}
                </div>
            `).join('');
            container.scrollTop = container.scrollHeight;
        }
        
        async function triggerOrchestration(type) {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/trigger-orchestration`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type })
                });
                
                const data = await response.json();
                if (data.success) {
                    showNotification(`${type} orchestration triggered successfully`);
                    setTimeout(refreshAll, 1000);
                } else {
                    showNotification(`Failed to trigger ${type} orchestration: ${data.error}`, 'error');
                }
            } catch (error) {
                showNotification(`Error: ${error.message}`, 'error');
            }
        }
        
        async function discoverAllConnections() {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/discover-connections`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'discover_all' })
                });
                
                const data = await response.json();
                if (data.success) {
                    showNotification('Connection discovery started');
                    setTimeout(refreshAll, 2000);
                } else {
                    showNotification(`Failed to start connection discovery: ${data.error}`, 'error');
                }
            } catch (error) {
                showNotification(`Error: ${error.message}`, 'error');
            }
        }
        
        async function optimizeContext() {
            try {
                const response = await fetch(`${DASHBOARD_API_BASE}/optimize-context`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (data.success) {
                    showNotification('Context optimization started');
                    setTimeout(refreshAll, 1000);
                } else {
                    showNotification(`Failed to optimize context: ${data.error}`, 'error');
                }
            } catch (error) {
                showNotification(`Error: ${error.message}`, 'error');
            }
        }
        
        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const btn = document.getElementById('autoRefreshBtn');
            btn.textContent = `Auto Refresh: ${autoRefresh ? 'ON' : 'OFF'}`;
            
            if (autoRefresh) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        }
        
        function startAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            refreshInterval = setInterval(refreshAll, 5000); // Refresh every 5 seconds
        }
        
        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }
        
        function refreshAll() {
            fetchSystemStatus();
            fetchActiveTasks();
            fetchConnectionStats();
            fetchSystemLogs();
        }
        
        function getStatusClass(status) {
            if (status === 'healthy' || status === 'running' || status === 'available') return 'status-healthy';
            if (status === 'warning' || status === 'degraded') return 'status-warning';
            if (status === 'error' || status === 'failed' || status === 'unavailable') return 'status-error';
            return 'status-unknown';
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function formatTimestamp(timestamp) {
            if (!timestamp) return 'Never';
            try {
                const date = new Date(timestamp);
                const now = new Date();
                const diff = now - date;
                
                if (diff < 60000) return 'Just now';
                if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
                if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
                return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
            } catch (e) {
                return timestamp;
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshAll();
            startAutoRefresh();
        });
    </script>
</body>
</html>
"""

class MDCOrchestrationDashboard:
    """
    Real-time dashboard for monitoring and controlling the MDC Orchestration Agent
    """
    
    def __init__(self, orchestration_agent_url: str = "http://localhost:8615", port: int = 8616):
        self.orchestration_agent_url = orchestration_agent_url
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Setup routes
        self.setup_routes()
        
        print(f"MDC Orchestration Dashboard initialized - Port: {self.port}")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template_string(DASHBOARD_HTML)
        
        @self.app.route('/api/system-status')
        def system_status():
            """Get system status from orchestration agent"""
            try:
                response = requests.get(f"{self.orchestration_agent_url}/status", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    return jsonify({
                        "health": health_data,
                        "metrics": {
                            "total_services": health_data.get("total_services", 0),
                            "total_connections": health_data.get("total_connections", 0),
                            "claude_md_size": health_data.get("claude_md_size", 0),
                            "last_full_orchestration": health_data.get("last_full_orchestration")
                        },
                        "subsystems": {
                            "mdc_agent_status": health_data.get("mdc_agent_status", "unknown"),
                            "connection_agent_status": health_data.get("connection_agent_status", "unknown"),
                            "context_optimizer_status": health_data.get("context_optimizer_status", "unknown")
                        }
                    })
                else:
                    return jsonify({"error": "Orchestration agent unavailable"}), 503
            except Exception as e:
                return jsonify({"error": str(e)}), 503
        
        @self.app.route('/api/tasks')
        def tasks():
            """Get tasks from orchestration agent"""
            try:
                response = requests.get(f"{self.orchestration_agent_url}/tasks", timeout=5)
                if response.status_code == 200:
                    return jsonify(response.json())
                else:
                    return jsonify({"active_tasks": [], "recent_completed": []})
            except Exception as e:
                return jsonify({"active_tasks": [], "recent_completed": [], "error": str(e)})
        
        @self.app.route('/api/connection-stats')
        def connection_stats():
            """Get connection statistics"""
            try:
                response = requests.get(f"{self.orchestration_agent_url}/connections/stats", timeout=5)
                if response.status_code == 200:
                    return jsonify(response.json())
                else:
                    return jsonify({"error": "Connection stats unavailable"}), 503
            except Exception as e:
                return jsonify({"error": str(e)}), 503
        
        @self.app.route('/api/logs')
        def logs():
            """Get system logs (mock implementation)"""
            # This would integrate with actual log files
            mock_logs = [
                {"timestamp": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": "MDC Orchestration Agent running"},
                {"timestamp": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": "Connection discovery completed"},
                {"timestamp": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": "Context optimization successful"}
            ]
            return jsonify({"logs": mock_logs})
        
        @self.app.route('/api/trigger-orchestration', methods=['POST'])
        def trigger_orchestration():
            """Trigger orchestration"""
            try:
                data = request.get_json()
                orchestration_type = data.get('type', 'full')
                
                endpoint = "/orchestrate" if orchestration_type == "full" else "/orchestrate/incremental"
                response = requests.post(f"{self.orchestration_agent_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    return jsonify({"success": True, "data": response.json()})
                else:
                    return jsonify({"success": False, "error": f"HTTP {response.status_code}"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/api/discover-connections', methods=['POST'])
        def discover_connections():
            """Trigger connection discovery"""
            try:
                response = requests.post(f"{self.orchestration_agent_url}/connections/discover/all", timeout=10)
                
                if response.status_code == 200:
                    return jsonify({"success": True, "data": response.json()})
                else:
                    return jsonify({"success": False, "error": f"HTTP {response.status_code}"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/api/optimize-context', methods=['POST'])
        def optimize_context():
            """Trigger context optimization"""
            try:
                response = requests.post(f"{self.orchestration_agent_url}/context/optimize", timeout=10)
                
                if response.status_code == 200:
                    return jsonify({"success": True, "data": response.json()})
                else:
                    return jsonify({"success": False, "error": f"HTTP {response.status_code}"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
    
    def run(self):
        """Run the dashboard"""
        print(f"Starting MDC Orchestration Dashboard on http://localhost:{self.port}")
        self.app.run(host='localhost', port=self.port, debug=False)

def main():
    """Main entry point"""
    orchestration_url = os.getenv('MDC_ORCHESTRATION_URL', 'http://localhost:8615')
    dashboard_port = int(os.getenv('MDC_DASHBOARD_PORT', 8616))
    
    dashboard = MDCOrchestrationDashboard(orchestration_url, dashboard_port)
    dashboard.run()

if __name__ == "__main__":
    main()