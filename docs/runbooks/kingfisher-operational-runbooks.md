# KingFisher Operational Runbooks v1.1.0

## Overview

This document provides operational runbooks for common KingFisher service failure scenarios and maintenance procedures. Each runbook includes symptoms, diagnosis steps, resolution procedures, and prevention strategies.

**Service**: zmart-kingfisher  
**Version**: 1.1.0  
**Last Updated**: 2025-08-25  
**On-call Team**: trading-ai  

---

## 🚨 Critical Alerts

### A) Service Down (KingfisherServiceDown)

**Symptoms:**
- Prometheus alert: `KingfisherServiceDown`
- No metrics being scraped from service
- HTTP endpoints returning 503/connection refused
- Dashboard shows service as DOWN

**Diagnosis:**
```bash
# Check service process
ps aux | grep -i kingfisher

# Check port binding
lsof -i :8201  # Replace with actual assigned port

# Check logs
tail -50 /var/log/kingfisher/service.log

# Check system resources
free -h
df -h
```

**Resolution:**

1. **Immediate Action:**
   ```bash
   # Attempt service restart
   systemctl restart kingfisher
   # OR if running manually:
   cd /path/to/kingfisher-module/backend
   python run_dev.py
   ```

2. **If restart fails:**
   ```bash
   # Check configuration
   python -c "import sys; sys.path.append('.'); from src.config import settings; print('Config OK')"
   
   # Check database connectivity
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;"
   
   # Check dependencies
   redis-cli ping
   curl -s http://localhost:15672/api/overview  # RabbitMQ
   ```

3. **Escalation:** If service won't start after 10 minutes, page senior engineer.

**Prevention:**
- Monitor system resources (disk space, memory)
- Set up log rotation
- Regular dependency health checks

---

### B) High Pipeline Failures (KingfisherPipelineFailuresHigh)

**Symptoms:**
- Alert: `KingfisherPipelineFailuresHigh`
- Error rate > 5 failures/5min
- Users report missing or incomplete analysis

**Diagnosis:**
```bash
# Check recent errors in logs
grep -i error /var/log/kingfisher/service.log | tail -20

# Check specific pipeline steps
curl -s http://localhost:8201/metrics | grep kingfisher_pipeline_failures_total

# Check plugin execution status
curl -s http://localhost:8201/api/v1/master-summary/statistics
```

**Common Causes & Resolutions:**

1. **OpenAI API Rate Limiting:**
   ```bash
   # Reduce OpenAI QPS in config
   python scripts/seed_config.py --service zmart-kingfisher --env prod
   # Edit config to reduce openai.max_qps from 8 to 4
   ```

2. **Image Processing Failures:**
   ```bash
   # Check image directory permissions
   ls -la data/images/
   
   # Check for corrupted images
   find data/images/ -name "*.jpg" -exec file {} \; | grep -v "JPEG image"
   ```

3. **Database Connection Issues:**
   ```bash
   # Check connection pool
   curl -s http://localhost:8201/metrics | grep db_connections
   
   # Restart database connection pool
   systemctl restart kingfisher
   ```

4. **Plugin-Specific Failures:**
   ```bash
   # Check individual plugin logs
   grep "plugin.*error" /var/log/kingfisher/service.log | tail -10
   
   # Test plugins individually
   cd kingfisher-module/backend
   python King-Scripts/step5_runner.py --plugin symbol_update --symbol BTCUSDT
   ```

**Resolution Priority:**
1. Stop further damage (pause automation if needed)
2. Fix immediate cause (rate limits, permissions)
3. Clear error backlog
4. Resume normal operation

---

### C) Security Violations High (KingfisherSecurityViolationsHigh)

**Symptoms:**
- Alert: `KingfisherSecurityViolationsHigh`
- > 10 violations in 5 minutes
- Possible attack or misconfiguration

**Immediate Response:**
```bash
# Check violation types
curl -s http://localhost:8201/metrics | grep kingfisher_security_violations_total

# Check recent access logs
grep "40[13]" /var/log/kingfisher/access.log | tail -20

# Identify source IPs
grep "40[13]" /var/log/kingfisher/access.log | awk '{print $1}' | sort | uniq -c | sort -nr
```

**Resolution:**

1. **Rate Limit Violations (most common):**
   ```bash
   # Check Redis rate limit keys
   redis-cli keys "ratelimit:*" | head -10
   
   # Increase rate limits temporarily if legitimate traffic
   # Update config with higher limits for specific endpoints
   ```

2. **Authentication Failures:**
   ```bash
   # Check for expired tokens
   grep "401" /var/log/kingfisher/access.log | tail -10
   
   # Generate fresh tokens for affected clients
   python scripts/gen_jwt.py --roles analysis.write --expires 24
   ```

3. **Potential Attack:**
   ```bash
   # Block suspicious IPs at firewall level
   iptables -A INPUT -s <suspicious_ip> -j DROP
   
   # Notify security team
   # Review access patterns for last 24h
   ```

---

## ⚠️ Warning Alerts

### D) Analysis Latency High (KingfisherAnalysisLatencyHigh)

**Symptoms:**
- P95 latency > 30 seconds for 10+ minutes
- Users report slow response times
- Processing backlog building up

**Diagnosis:**
```bash
# Check current latency
curl -s http://localhost:8201/metrics | grep kingfisher_analysis_duration_seconds

# Check system load
uptime
iostat 1 5

# Check process CPU/memory usage
ps aux | grep kingfisher | grep -v grep
```

**Resolution:**

1. **High CPU Usage:**
   ```bash
   # Temporarily reduce concurrent workers
   # Edit config: orchestrator.max_workers from 8 to 4
   systemctl reload kingfisher
   ```

2. **I/O Bottleneck:**
   ```bash
   # Check disk usage and speed
   df -h
   iostat -x 1 5
   
   # Move temporary files to faster disk if available
   # Clean up old temporary files
   find data/images/temp -mtime +1 -delete
   ```

3. **Database Slowness:**
   ```bash
   # Check slow query log
   sudo -u postgres psql -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
   
   # Add missing indices if needed
   # Check connection pool status
   ```

4. **OpenAI API Slowness:**
   ```bash
   # Check OpenAI response times
   curl -w "@curl-format.txt" -s -o /dev/null https://api.openai.com/v1/models
   
   # Reduce OpenAI dependency temporarily
   # Enable fallback processing mode
   ```

---

### E) Image Processing Stalled (KingfisherImageProcessingStalled)

**Symptoms:**
- No images downloaded for 15+ minutes during business hours
- Telegram bot appears inactive
- Users report missing analysis

**Diagnosis:**
```bash
# Check Telegram bot status
curl -s http://localhost:8201/api/v1/telegram/status

# Check recent image downloads
ls -la data/images/$(date +%Y)/$(date +%m)/$(date +%d)/ | head -10

# Check Telegram API connectivity
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

**Resolution:**

1. **Telegram Rate Limiting:**
   ```bash
   # Check for 429 responses
   grep "429" /var/log/kingfisher/service.log | tail -5
   
   # Implement backoff if not already active
   # Wait 60 seconds, then resume
   ```

2. **Network Connectivity:**
   ```bash
   # Test external connectivity
   ping -c 3 api.telegram.org
   curl -s https://httpbin.org/ip
   
   # Check DNS resolution
   nslookup api.telegram.org
   ```

3. **Bot Configuration:**
   ```bash
   # Verify bot token
   echo $TELEGRAM_BOT_TOKEN | head -c 10
   
   # Test bot commands
   curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates"
   ```

4. **Source Channel Issues:**
   ```bash
   # Check if source channel is active
   # Verify bot has access to channel
   # Check for channel restrictions or deletions
   ```

---

### F) Events Stuck in Outbox (KingfisherOutboxEventsStuck)

**Symptoms:**
- Alert: `KingfisherOutboxEventsStuck`
- > 100 pending events for 10+ minutes
- RabbitMQ may be down or unreachable

**Diagnosis:**
```bash
# Check outbox status
curl -s http://localhost:8201/api/v1/outbox/stats

# Check RabbitMQ status
systemctl status rabbitmq-server
curl -s http://localhost:15672/api/overview -u guest:guest

# Check network connectivity to RabbitMQ
telnet localhost 5672
```

**Resolution:**

1. **RabbitMQ Down:**
   ```bash
   # Restart RabbitMQ
   systemctl restart rabbitmq-server
   
   # Verify exchanges exist
   rabbitmqctl list_exchanges
   
   # Events will automatically resume publishing
   ```

2. **Network Issues:**
   ```bash
   # Check firewall rules
   iptables -L | grep 5672
   
   # Test AMQP connection
   python -c "import pika; pika.BlockingConnection(pika.URLParameters('$RABBIT_URL'))"
   ```

3. **Outbox Publisher Issues:**
   ```bash
   # Check publisher logs
   grep "outbox.*publisher" /var/log/kingfisher/service.log | tail -10
   
   # Restart outbox publisher
   # (This happens automatically with service restart)
   systemctl restart kingfisher
   ```

---

## 🔧 Maintenance Procedures

### G) Routine Maintenance

**Weekly Tasks:**
```bash
# 1. Check log sizes and rotate if needed
du -sh /var/log/kingfisher/
logrotate -f /etc/logrotate.d/kingfisher

# 2. Clean up old processed images
find data/images/ -name "*.jpg" -mtime +7 -delete

# 3. Vacuum database tables
sudo -u postgres psql zmart_core -c "VACUUM ANALYZE kingfisher.liquidation_clusters;"

# 4. Check and update dependencies
pip list --outdated

# 5. Review security violations
curl -s http://localhost:8201/metrics | grep security_violations
```

**Monthly Tasks:**
```bash
# 1. Update monitoring dashboard
# 2. Review and update runbooks
# 3. Capacity planning review
# 4. Security audit
# 5. Performance optimization review
```

---

### H) Emergency Procedures

**Complete Service Recovery:**
```bash
#!/bin/bash
# emergency-recovery.sh

echo "🚨 KingFisher Emergency Recovery Procedure"

# 1. Stop all processes
pkill -f kingfisher
pkill -f "King-Scripts"

# 2. Backup current state
mkdir -p /tmp/kingfisher-backup-$(date +%Y%m%d-%H%M%S)
cp -r data/images/$(date +%Y)/$(date +%m)/$(date +%d) /tmp/kingfisher-backup-*/

# 3. Check and fix permissions
chown -R kingfisher:kingfisher data/
chmod -R 755 data/

# 4. Clear temporary files
rm -rf data/temp/*
rm -rf /tmp/kingfisher-*

# 5. Reset Redis rate limits
redis-cli flushdb 1

# 6. Restart dependencies
systemctl restart postgresql
systemctl restart redis
systemctl restart rabbitmq-server

# 7. Wait for dependencies
sleep 30

# 8. Start service
systemctl start kingfisher

# 9. Verify health
sleep 10
curl -s http://localhost:8201/health
curl -s http://localhost:8201/ready

echo "✅ Recovery procedure completed"
```

---

## 📞 Escalation Procedures

### Primary On-Call: Trading AI Team
- **Slack**: #trading-ai-alerts
- **PagerDuty**: trading-ai-primary

### Secondary On-Call: Platform Team  
- **Slack**: #platform-alerts
- **PagerDuty**: platform-secondary

### Escalation Matrix:
1. **0-15 minutes**: Attempt automated recovery
2. **15-30 minutes**: Page primary on-call
3. **30-60 minutes**: Page secondary on-call  
4. **60+ minutes**: Page engineering manager

### Critical Business Hours:
- **Primary**: 8 AM - 10 PM UTC (trading hours)
- **Secondary**: 10 PM - 8 AM UTC (maintenance window)

---

## 🔍 Useful Commands Reference

```bash
# Service status
systemctl status kingfisher
curl -s http://localhost:8201/health | jq .

# Logs
tail -f /var/log/kingfisher/service.log
journalctl -u kingfisher -f

# Metrics
curl -s http://localhost:8201/metrics | grep kingfisher_

# Database queries
sudo -u postgres psql zmart_core -c "SELECT COUNT(*) FROM kingfisher.liquidation_clusters WHERE created_at > NOW() - INTERVAL '1 hour';"

# Redis inspection  
redis-cli info
redis-cli keys "kingfisher:*"

# RabbitMQ status
rabbitmqctl status
rabbitmqctl list_queues

# Process monitoring
ps aux | grep -E "(kingfisher|King-Scripts)"
lsof -p $(pgrep -f kingfisher)

# Performance analysis
iostat -x 1 5
sar -u 1 5
free -h
```

---

## 📋 Post-Incident Checklist

After resolving any incident:

- [ ] Document root cause in incident report
- [ ] Update monitoring thresholds if needed
- [ ] Update runbooks with new procedures
- [ ] Schedule post-mortem meeting
- [ ] Implement prevention measures
- [ ] Test recovery procedures
- [ ] Update team knowledge base
- [ ] Review escalation effectiveness

---

**Document Version**: 1.1.0  
**Last Updated**: 2025-08-25  
**Next Review**: 2025-09-25  
**Maintainer**: Trading AI Team