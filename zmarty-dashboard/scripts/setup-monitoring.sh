#!/bin/bash

# Monitoring Stack Setup Script for Zmarty Dashboard
# Sets up Prometheus, Grafana, and related monitoring components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
MONITORING_DIR="$PROJECT_ROOT/monitoring"
GRAFANA_ADMIN_PASSWORD="admin123"
ENABLE_ALERTMANAGER=false
ENABLE_NODE_EXPORTER=true
ENABLE_CADVISOR=true
DATA_RETENTION="15d"

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

show_help() {
    cat << EOF
📊 Monitoring Stack Setup Script for Zmarty Dashboard

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -p, --password PASSWORD     Grafana admin password (default: admin123)
    -r, --retention PERIOD      Prometheus data retention period (default: 15d)
    -a, --alertmanager          Enable Alertmanager for alerts
    -n, --no-node-exporter      Disable Node Exporter
    -c, --no-cadvisor          Disable cAdvisor
    -h, --help                  Show this help message

EXAMPLES:
    # Basic monitoring setup
    $0

    # Custom Grafana password and retention
    $0 -p mysecretpassword -r 30d

    # Full monitoring with alerting
    $0 -a -p mysecretpassword

COMPONENTS:
    Prometheus    - Metrics collection and storage
    Grafana       - Visualization and dashboards
    Node Exporter - System metrics (optional)
    cAdvisor      - Container metrics (optional)
    Alertmanager  - Alert handling (optional)

EOF
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is required but not installed."
        exit 1
    fi
    
    # Create monitoring directory
    mkdir -p "$MONITORING_DIR"/{prometheus,grafana,alertmanager}
    
    print_status "Prerequisites check completed"
}

create_prometheus_config() {
    print_step "Creating Prometheus configuration..."
    
    cat > "$MONITORING_DIR/prometheus/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
$(if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
  cat << 'ALERT_EOF'
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
ALERT_EOF
fi)

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s

  # Zmarty Backend
  - job_name: 'zmarty-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    scrape_interval: 30s
    scrape_timeout: 10s

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 60s

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 60s

$(if [[ "$ENABLE_NODE_EXPORTER" == true ]]; then
  cat << 'NODE_EOF'
  # Node Exporter (System metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 60s
NODE_EOF
fi)

$(if [[ "$ENABLE_CADVISOR" == true ]]; then
  cat << 'CADVISOR_EOF'
  # cAdvisor (Container metrics)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 60s
CADVISOR_EOF
fi)

  # Nginx (if metrics are enabled)
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: /metrics
    scrape_interval: 60s
EOF
    
    print_status "Prometheus configuration created"
}

create_alert_rules() {
    print_step "Creating Prometheus alert rules..."
    
    cat > "$MONITORING_DIR/prometheus/alert_rules.yml" << 'EOF'
groups:
  - name: zmarty_alerts
    rules:
      # High CPU Usage
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes on {{ $labels.instance }}"

      # High Memory Usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes on {{ $labels.instance }}"

      # Service Down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Service {{ $labels.job }} on {{ $labels.instance }} has been down for more than 1 minute"

      # High HTTP Error Rate
      - alert: HighHTTPErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High HTTP error rate"
          description: "HTTP 5xx error rate is above 10% for more than 5 minutes"

      # Database Connection Issues
      - alert: DatabaseConnectionHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "PostgreSQL connection count is above 80 for more than 5 minutes"

      # Redis Memory Usage
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
          description: "Redis memory usage is above 90% for more than 5 minutes"

      # Disk Space Low
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space is low"
          description: "Available disk space is below 10% on {{ $labels.instance }}"

      # API Response Time High
      - alert: APIResponseTimeHigh
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API response time is high"
          description: "95th percentile response time is above 2 seconds for more than 10 minutes"
EOF
    
    print_status "Prometheus alert rules created"
}

create_grafana_config() {
    print_step "Creating Grafana configuration..."
    
    # Create Grafana directories
    mkdir -p "$MONITORING_DIR/grafana"/{provisioning,dashboards}/{datasources,dashboards}
    
    # Grafana datasource configuration
    cat > "$MONITORING_DIR/grafana/provisioning/datasources/prometheus.yml" << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
EOF
    
    # Grafana dashboard provisioning
    cat > "$MONITORING_DIR/grafana/provisioning/dashboards/dashboards.yml" << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    updateIntervalSeconds: 10
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
    
    print_status "Grafana configuration created"
}

create_dashboards() {
    print_step "Creating Grafana dashboards..."
    
    # Main Zmarty Dashboard
    cat > "$MONITORING_DIR/grafana/dashboards/zmarty-main.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Zmarty Dashboard - Main Overview",
    "tags": ["zmarty"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Response Time (95th percentile)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Active Users",
        "type": "singlestat",
        "targets": [
          {
            "expr": "active_users_total",
            "legendFormat": "Active Users"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Credit Transactions",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(credit_transactions_total[1h])",
            "legendFormat": "Transactions/hour"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "5s"
  }
}
EOF
    
    # System Resources Dashboard
    cat > "$MONITORING_DIR/grafana/dashboards/system-resources.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "System Resources",
    "tags": ["system", "resources"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_filesystem_avail_bytes{mountpoint=\"/\"} / node_filesystem_size_bytes{mountpoint=\"/\"})) * 100",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Network I/O",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total[5m])",
            "legendFormat": "Received {{device}}"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total[5m])",
            "legendFormat": "Transmitted {{device}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "5s"
  }
}
EOF
    
    print_status "Grafana dashboards created"
}

create_alertmanager_config() {
    if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
        print_step "Creating Alertmanager configuration..."
        
        cat > "$MONITORING_DIR/alertmanager/alertmanager.yml" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@yourdomain.com'
        subject: 'Zmarty Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF
        
        print_status "Alertmanager configuration created"
    fi
}

create_docker_compose_monitoring() {
    print_step "Creating Docker Compose monitoring configuration..."
    
    cat > "$PROJECT_ROOT/docker-compose.monitoring.yml" << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: zmarty-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=${DATA_RETENTION}'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring
      - default

  grafana:
    image: grafana/grafana:latest
    container_name: zmarty-grafana
    ports:
      - "3001:3000"
    volumes:
      - ./monitoring/grafana:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped
    networks:
      - monitoring
      - default

$(if [[ "$ENABLE_NODE_EXPORTER" == true ]]; then
  cat << 'NODE_EOF'
  node-exporter:
    image: prom/node-exporter:latest
    container_name: zmarty-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring
NODE_EOF
fi)

$(if [[ "$ENABLE_CADVISOR" == true ]]; then
  cat << 'CADVISOR_EOF'
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: zmarty-cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    restart: unless-stopped
    networks:
      - monitoring
CADVISOR_EOF
fi)

$(if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
  cat << 'ALERT_EOF'
  alertmanager:
    image: prom/alertmanager:latest
    container_name: zmarty-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped
    networks:
      - monitoring
ALERT_EOF
fi)

  # Log aggregation with Loki
  loki:
    image: grafana/loki:latest
    container_name: zmarty-loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/loki.yml
    restart: unless-stopped
    networks:
      - monitoring

  # Log shipping with Promtail
  promtail:
    image: grafana/promtail:latest
    container_name: zmarty-promtail
    volumes:
      - ./logs:/var/log/app
      - ./monitoring/promtail:/etc/promtail
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/promtail.yml
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
$(if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
  echo "  alertmanager_data:"
fi)

networks:
  monitoring:
    driver: bridge
EOF
    
    print_status "Docker Compose monitoring configuration created"
}

create_loki_config() {
    print_step "Creating Loki configuration..."
    
    mkdir -p "$MONITORING_DIR/loki"
    
    cat > "$MONITORING_DIR/loki/loki.yml" << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093
EOF
    
    # Create Promtail configuration
    mkdir -p "$MONITORING_DIR/promtail"
    
    cat > "$MONITORING_DIR/promtail/promtail.yml" << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs:
      - json:
          expressions:
            tag:
          source: attrs
      - regex:
          expression: (?P<container_name>(?:[^|]*))\|
          source: tag
      - timestamp:
          format: RFC3339Nano
          source: time
      - labels:
          stream:
          container_name:
      - output:
          source: output

  - job_name: app_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: app
          __path__: /var/log/app/*.log
EOF
    
    print_status "Loki and Promtail configuration created"
}

update_backend_metrics() {
    print_step "Adding metrics endpoint to backend..."
    
    local metrics_file="$PROJECT_ROOT/backend/core/metrics.py"
    
    cat > "$metrics_file" << 'EOF'
"""
Prometheus metrics for Zmarty Dashboard backend
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from typing import Callable

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_users_total = Gauge(
    'active_users_total',
    'Total number of active users'
)

credit_transactions_total = Counter(
    'credit_transactions_total',
    'Total number of credit transactions',
    ['type', 'status']
)

zmarty_requests_total = Counter(
    'zmarty_requests_total',
    'Total number of Zmarty AI requests',
    ['status']
)

database_connections = Gauge(
    'database_connections',
    'Number of active database connections'
)


def metrics_middleware(request, call_next: Callable):
    """Middleware to collect HTTP metrics"""
    start_time = time.time()
    
    response = call_next(request)
    
    # Record metrics
    method = request.method
    endpoint = request.url.path
    status = response.status_code
    duration = time.time() - start_time
    
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)
    
    return response


def get_metrics():
    """Get Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Utility functions for custom metrics
def record_credit_transaction(transaction_type: str, status: str):
    """Record a credit transaction"""
    credit_transactions_total.labels(
        type=transaction_type,
        status=status
    ).inc()


def record_zmarty_request(status: str):
    """Record a Zmarty AI request"""
    zmarty_requests_total.labels(status=status).inc()


def update_active_users(count: int):
    """Update active users count"""
    active_users_total.set(count)


def update_database_connections(count: int):
    """Update database connections count"""
    database_connections.set(count)
EOF
    
    print_status "Backend metrics module created"
}

create_monitoring_scripts() {
    print_step "Creating monitoring management scripts..."
    
    # Monitoring start/stop script
    cat > "$PROJECT_ROOT/scripts/monitoring.sh" << EOF
#!/bin/bash

# Monitoring Stack Management Script

PROJECT_ROOT="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)"

case \$1 in
    start)
        echo "🚀 Starting monitoring stack..."
        docker-compose -f "\$PROJECT_ROOT/docker-compose.yml" -f "\$PROJECT_ROOT/docker-compose.monitoring.yml" up -d
        echo "✅ Monitoring stack started!"
        echo
        echo "📊 Access URLs:"
        echo "  Prometheus: http://localhost:9090"
        echo "  Grafana:    http://localhost:3001 (admin/${GRAFANA_ADMIN_PASSWORD})"
        $(if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
        echo "  Alertmanager: http://localhost:9093"
        fi)
        echo "  Loki:       http://localhost:3100"
        ;;
    stop)
        echo "🛑 Stopping monitoring stack..."
        docker-compose -f "\$PROJECT_ROOT/docker-compose.yml" -f "\$PROJECT_ROOT/docker-compose.monitoring.yml" down
        echo "✅ Monitoring stack stopped!"
        ;;
    restart)
        echo "🔄 Restarting monitoring stack..."
        \$0 stop
        sleep 5
        \$0 start
        ;;
    status)
        echo "📊 Monitoring Stack Status:"
        echo "=========================="
        docker-compose -f "\$PROJECT_ROOT/docker-compose.yml" -f "\$PROJECT_ROOT/docker-compose.monitoring.yml" ps
        ;;
    logs)
        service=\${2:-""}
        if [[ -n "\$service" ]]; then
            docker-compose -f "\$PROJECT_ROOT/docker-compose.yml" -f "\$PROJECT_ROOT/docker-compose.monitoring.yml" logs -f \$service
        else
            docker-compose -f "\$PROJECT_ROOT/docker-compose.yml" -f "\$PROJECT_ROOT/docker-compose.monitoring.yml" logs -f
        fi
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs [service]}"
        echo
        echo "Examples:"
        echo "  \$0 start              # Start all monitoring services"
        echo "  \$0 stop               # Stop all monitoring services"
        echo "  \$0 status             # Show service status"
        echo "  \$0 logs prometheus    # Show Prometheus logs"
        exit 1
        ;;
esac
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/monitoring.sh"
    
    # Health check script
    cat > "$PROJECT_ROOT/scripts/monitoring-health.sh" << EOF
#!/bin/bash

# Monitoring Health Check Script

echo "🏥 Checking Monitoring Stack Health..."
echo "====================================="

# Check Prometheus
echo -n "Prometheus: "
if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check Grafana
echo -n "Grafana: "
if curl -f http://localhost:3001/api/health >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check Loki
echo -n "Loki: "
if curl -f http://localhost:3100/ready >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

$(if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
cat << 'ALERT_HEALTH_EOF'
# Check Alertmanager
echo -n "Alertmanager: "
if curl -f http://localhost:9093/-/healthy >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi
ALERT_HEALTH_EOF
fi)

echo
echo "📊 Quick Stats:"
echo "Prometheus targets: \$(curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length' 2>/dev/null || echo 'N/A')"
echo "Grafana dashboards: \$(curl -s -u admin:${GRAFANA_ADMIN_PASSWORD} http://localhost:3001/api/search | jq '. | length' 2>/dev/null || echo 'N/A')"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/monitoring-health.sh"
    
    print_status "Monitoring management scripts created"
}

main() {
    echo "📊 Monitoring Stack Setup for Zmarty Dashboard"
    echo "==============================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--password)
                GRAFANA_ADMIN_PASSWORD="$2"
                shift 2
                ;;
            -r|--retention)
                DATA_RETENTION="$2"
                shift 2
                ;;
            -a|--alertmanager)
                ENABLE_ALERTMANAGER=true
                shift
                ;;
            -n|--no-node-exporter)
                ENABLE_NODE_EXPORTER=false
                shift
                ;;
            -c|--no-cadvisor)
                ENABLE_CADVISOR=false
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Show configuration
    print_status "Configuration:"
    print_status "  Grafana Password: ${GRAFANA_ADMIN_PASSWORD//?/*}"
    print_status "  Data Retention: $DATA_RETENTION"
    print_status "  Alertmanager: $([ "$ENABLE_ALERTMANAGER" == true ] && echo "Enabled" || echo "Disabled")"
    print_status "  Node Exporter: $([ "$ENABLE_NODE_EXPORTER" == true ] && echo "Enabled" || echo "Disabled")"
    print_status "  cAdvisor: $([ "$ENABLE_CADVISOR" == true ] && echo "Enabled" || echo "Disabled")"
    
    # Check prerequisites
    check_prerequisites
    
    # Create configurations
    create_prometheus_config
    create_alert_rules
    create_grafana_config
    create_dashboards
    create_loki_config
    
    if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
        create_alertmanager_config
    fi
    
    # Create Docker Compose configuration
    create_docker_compose_monitoring
    
    # Update backend with metrics
    update_backend_metrics
    
    # Create management scripts
    create_monitoring_scripts
    
    print_status "🎉 Monitoring stack setup completed successfully!"
    echo
    echo "📋 Next steps:"
    echo "1. Start monitoring stack: ./scripts/monitoring.sh start"
    echo "2. Access Grafana: http://localhost:3001 (admin/${GRAFANA_ADMIN_PASSWORD})"
    echo "3. Access Prometheus: http://localhost:9090"
    echo "4. Check health: ./scripts/monitoring-health.sh"
    echo
    echo "🔧 Management Commands:"
    echo "  Start:   ./scripts/monitoring.sh start"
    echo "  Stop:    ./scripts/monitoring.sh stop"
    echo "  Status:  ./scripts/monitoring.sh status"
    echo "  Health:  ./scripts/monitoring-health.sh"
    echo
    echo "📊 Monitoring Components:"
    echo "  ✅ Prometheus - Metrics collection"
    echo "  ✅ Grafana - Visualization dashboards"
    echo "  ✅ Loki - Log aggregation"
    echo "  ✅ Promtail - Log shipping"
    if [[ "$ENABLE_NODE_EXPORTER" == true ]]; then
        echo "  ✅ Node Exporter - System metrics"
    fi
    if [[ "$ENABLE_CADVISOR" == true ]]; then
        echo "  ✅ cAdvisor - Container metrics"
    fi
    if [[ "$ENABLE_ALERTMANAGER" == true ]]; then
        echo "  ✅ Alertmanager - Alert handling"
    fi
    echo
    echo "⚠️  Remember to:"
    echo "  - Configure email settings in Alertmanager (if enabled)"
    echo "  - Set up proper retention policies for production"
    echo "  - Configure firewall rules for monitoring ports"
    echo "  - Set up backup for monitoring data"
}

# Run main function
main "$@"