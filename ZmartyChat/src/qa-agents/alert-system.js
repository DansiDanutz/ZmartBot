// QA Alert System
// Comprehensive alert management for all QA agents

import { zmartyDB } from '../supabase-client.js';

export class QAAlertSystem {
    constructor() {
        this.alertLevels = {
            CRITICAL: { priority: 1, color: '#FF0000', notify: true, autoEscalate: true },
            ERROR: { priority: 2, color: '#FF6600', notify: true, autoEscalate: false },
            WARNING: { priority: 3, color: '#FFAA00', notify: true, autoEscalate: false },
            INFO: { priority: 4, color: '#0099FF', notify: false, autoEscalate: false },
            SUCCESS: { priority: 5, color: '#00CC00', notify: false, autoEscalate: false }
        };

        this.alertChannels = {
            database: true,
            websocket: true,
            voice: true,
            email: false,
            sms: false,
            webhook: true
        };

        this.activeAlerts = new Map();
        this.alertHistory = [];
        this.subscribers = new Set();
        this.escalationRules = new Map();
        this.alertThrottles = new Map();
    }

    // Create a new alert
    async createAlert(alertData) {
        const alert = {
            id: this.generateAlertId(),
            timestamp: new Date().toISOString(),
            level: alertData.level || 'INFO',
            component: alertData.component,
            title: alertData.title,
            message: alertData.message,
            details: alertData.details || {},
            metrics: alertData.metrics || {},
            actions: alertData.actions || [],
            status: 'ACTIVE',
            acknowledged: false,
            resolvedAt: null,
            resolvedBy: null,
            ttl: alertData.ttl || 3600000, // 1 hour default
            tags: alertData.tags || [],
            correlationId: alertData.correlationId || null
        };

        // Check throttling
        if (this.isThrottled(alert)) {
            console.log(`Alert throttled: ${alert.component}:${alert.title}`);
            return null;
        }

        // Store alert
        this.activeAlerts.set(alert.id, alert);
        this.alertHistory.push(alert);

        // Distribute alert
        await this.distributeAlert(alert);

        // Check for escalation
        if (this.alertLevels[alert.level].autoEscalate) {
            this.scheduleEscalation(alert);
        }

        // Auto-expire if TTL is set
        if (alert.ttl > 0) {
            setTimeout(() => this.expireAlert(alert.id), alert.ttl);
        }

        return alert;
    }

    // Distribute alert to various channels
    async distributeAlert(alert) {
        const promises = [];

        // Save to database
        if (this.alertChannels.database) {
            promises.push(this.saveAlertToDatabase(alert));
        }

        // Broadcast via WebSocket
        if (this.alertChannels.websocket) {
            promises.push(this.broadcastAlert(alert));
        }

        // Send to voice system
        if (this.alertChannels.voice && this.shouldNotifyVoice(alert)) {
            promises.push(this.sendToVoiceSystem(alert));
        }

        // Send to webhook
        if (this.alertChannels.webhook) {
            promises.push(this.sendToWebhook(alert));
        }

        // Notify subscribers
        promises.push(this.notifySubscribers(alert));

        await Promise.allSettled(promises);
    }

    // Save alert to database
    async saveAlertToDatabase(alert) {
        try {
            await zmartyDB.supabase
                .from('qa_alerts')
                .insert({
                    alert_id: alert.id,
                    level: alert.level,
                    component: alert.component,
                    title: alert.title,
                    message: alert.message,
                    details: alert.details,
                    metrics: alert.metrics,
                    status: alert.status,
                    created_at: alert.timestamp
                });
        } catch (error) {
            console.error('Failed to save alert to database:', error);
        }
    }

    // Broadcast alert via WebSocket
    async broadcastAlert(alert) {
        // This would connect to the Socket.IO instance
        if (global.io) {
            global.io.emit('qa_alert', {
                ...alert,
                formattedMessage: this.formatAlertMessage(alert)
            });
        }
    }

    // Send alert to voice system (ElevenLabs)
    async sendToVoiceSystem(alert) {
        const voiceMessage = this.formatVoiceAlert(alert);

        try {
            // Send to Zmarty voice agent
            const response = await fetch('http://localhost:3001/api/voice-alert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    alert: voiceMessage,
                    priority: this.alertLevels[alert.level].priority,
                    interrupt: alert.level === 'CRITICAL'
                })
            });

            if (!response.ok) {
                console.error('Failed to send voice alert');
            }
        } catch (error) {
            console.error('Voice alert error:', error);
        }
    }

    // Send to webhook (ZmartBot API)
    async sendToWebhook(alert) {
        try {
            await fetch('http://localhost:8000/api/qa/alerts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer zmart-api-key-2024'
                },
                body: JSON.stringify(alert)
            });
        } catch (error) {
            console.error('Webhook alert error:', error);
        }
    }

    // Format alert for voice
    formatVoiceAlert(alert) {
        const levelDescriptions = {
            CRITICAL: 'Critical alert!',
            ERROR: 'Error detected.',
            WARNING: 'Warning.',
            INFO: 'Information.',
            SUCCESS: 'Success notification.'
        };

        let message = `${levelDescriptions[alert.level]} ${alert.component} system: ${alert.message}`;

        if (alert.actions && alert.actions.length > 0) {
            message += ` Recommended action: ${alert.actions[0]}`;
        }

        if (alert.metrics && alert.level === 'CRITICAL') {
            if (alert.metrics.score !== undefined) {
                message += ` System score: ${(alert.metrics.score * 100).toFixed(0)} percent.`;
            }
        }

        return message;
    }

    // Format alert message
    formatAlertMessage(alert) {
        return `[${alert.level}] ${alert.component}: ${alert.title}\n${alert.message}`;
    }

    // Check if voice notification should be sent
    shouldNotifyVoice(alert) {
        return this.alertLevels[alert.level].notify &&
               (alert.level === 'CRITICAL' || alert.level === 'ERROR');
    }

    // Subscribe to alerts
    subscribe(callback) {
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    // Notify all subscribers
    async notifySubscribers(alert) {
        const promises = Array.from(this.subscribers).map(callback =>
            Promise.resolve(callback(alert)).catch(error =>
                console.error('Subscriber notification error:', error)
            )
        );

        await Promise.allSettled(promises);
    }

    // Acknowledge alert
    async acknowledgeAlert(alertId, acknowledgedBy = 'system') {
        const alert = this.activeAlerts.get(alertId);
        if (!alert) return false;

        alert.acknowledged = true;
        alert.acknowledgedAt = new Date().toISOString();
        alert.acknowledgedBy = acknowledgedBy;

        await this.updateAlertInDatabase(alertId, {
            acknowledged: true,
            acknowledged_at: alert.acknowledgedAt,
            acknowledged_by: acknowledgedBy
        });

        return true;
    }

    // Resolve alert
    async resolveAlert(alertId, resolvedBy = 'system', resolution = null) {
        const alert = this.activeAlerts.get(alertId);
        if (!alert) return false;

        alert.status = 'RESOLVED';
        alert.resolvedAt = new Date().toISOString();
        alert.resolvedBy = resolvedBy;
        alert.resolution = resolution;

        this.activeAlerts.delete(alertId);

        await this.updateAlertInDatabase(alertId, {
            status: 'RESOLVED',
            resolved_at: alert.resolvedAt,
            resolved_by: resolvedBy,
            resolution: resolution
        });

        // Create resolution notification
        if (alert.level === 'CRITICAL' || alert.level === 'ERROR') {
            await this.createAlert({
                level: 'SUCCESS',
                component: alert.component,
                title: `${alert.title} - Resolved`,
                message: `Previous ${alert.level} alert has been resolved`,
                correlationId: alertId
            });
        }

        return true;
    }

    // Update alert in database
    async updateAlertInDatabase(alertId, updates) {
        try {
            await zmartyDB.supabase
                .from('qa_alerts')
                .update(updates)
                .eq('alert_id', alertId);
        } catch (error) {
            console.error('Failed to update alert in database:', error);
        }
    }

    // Expire alert
    expireAlert(alertId) {
        const alert = this.activeAlerts.get(alertId);
        if (alert && !alert.acknowledged) {
            alert.status = 'EXPIRED';
            this.activeAlerts.delete(alertId);
        }
    }

    // Schedule escalation
    scheduleEscalation(alert) {
        const escalationDelay = 300000; // 5 minutes

        setTimeout(() => {
            if (this.activeAlerts.has(alert.id) && !alert.acknowledged) {
                this.escalateAlert(alert);
            }
        }, escalationDelay);
    }

    // Escalate alert
    async escalateAlert(alert) {
        const escalatedAlert = {
            ...alert,
            level: 'CRITICAL',
            title: `[ESCALATED] ${alert.title}`,
            message: `Unacknowledged alert escalated: ${alert.message}`,
            escalatedFrom: alert.id,
            escalatedAt: new Date().toISOString()
        };

        await this.createAlert(escalatedAlert);
    }

    // Check throttling
    isThrottled(alert) {
        const key = `${alert.component}:${alert.title}`;
        const now = Date.now();
        const lastAlert = this.alertThrottles.get(key);

        if (lastAlert && (now - lastAlert) < 60000) { // 1 minute throttle
            return true;
        }

        this.alertThrottles.set(key, now);
        return false;
    }

    // Get active alerts
    getActiveAlerts(filter = {}) {
        let alerts = Array.from(this.activeAlerts.values());

        if (filter.level) {
            alerts = alerts.filter(a => a.level === filter.level);
        }

        if (filter.component) {
            alerts = alerts.filter(a => a.component === filter.component);
        }

        if (filter.unacknowledged) {
            alerts = alerts.filter(a => !a.acknowledged);
        }

        return alerts.sort((a, b) =>
            this.alertLevels[a.level].priority - this.alertLevels[b.level].priority
        );
    }

    // Get alert statistics
    getAlertStatistics() {
        const stats = {
            active: this.activeAlerts.size,
            total: this.alertHistory.length,
            byLevel: {},
            byComponent: {},
            unacknowledged: 0,
            criticalActive: 0
        };

        this.activeAlerts.forEach(alert => {
            stats.byLevel[alert.level] = (stats.byLevel[alert.level] || 0) + 1;
            stats.byComponent[alert.component] = (stats.byComponent[alert.component] || 0) + 1;

            if (!alert.acknowledged) stats.unacknowledged++;
            if (alert.level === 'CRITICAL') stats.criticalActive++;
        });

        return stats;
    }

    // Create bulk alerts from QA results
    async createAlertsFromQAResults(qaResults) {
        const alerts = [];

        // Check overall system status
        if (qaResults.overall?.systemStatus === 'CRITICAL') {
            alerts.push(await this.createAlert({
                level: 'CRITICAL',
                component: 'SYSTEM',
                title: 'System Critical Failure',
                message: 'QA detected critical system failures requiring immediate attention',
                details: qaResults.overall,
                metrics: { score: qaResults.overall.score },
                actions: ['Pause trading operations', 'Review failed components', 'Contact support']
            }));
        }

        // Check individual components
        for (const [component, results] of Object.entries(qaResults.components || {})) {
            if (results.status === 'FAIL') {
                alerts.push(await this.createAlert({
                    level: results.overallScore < 0.5 ? 'CRITICAL' : 'ERROR',
                    component: component.toUpperCase(),
                    title: `${component} QA Failure`,
                    message: `Component failed quality assurance with score ${(results.overallScore * 100).toFixed(1)}%`,
                    details: results,
                    metrics: {
                        score: results.overallScore,
                        failedTests: results.tests?.filter(t => t.status === 'FAIL').length || 0
                    },
                    actions: results.report?.recommendations || []
                }));
            }

            // Check for risk alerts
            if (component === 'riskAssessment' && results.riskLevel === 'CRITICAL') {
                alerts.push(await this.createAlert({
                    level: 'CRITICAL',
                    component: 'RISK',
                    title: 'Critical Risk Level Detected',
                    message: 'Risk assessment indicates critical exposure levels',
                    details: results,
                    actions: ['Reduce all positions immediately', 'Review risk parameters']
                }));
            }
        }

        return alerts.filter(a => a !== null);
    }

    // Generate alert ID
    generateAlertId() {
        return `ALERT-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    // Clear expired alerts
    clearExpiredAlerts() {
        const now = Date.now();
        let cleared = 0;

        this.activeAlerts.forEach((alert, id) => {
            const alertAge = now - new Date(alert.timestamp).getTime();
            if (alertAge > alert.ttl && alert.status === 'ACTIVE' && !alert.acknowledged) {
                this.activeAlerts.delete(id);
                cleared++;
            }
        });

        return cleared;
    }

    // Get alert summary for voice
    getVoiceAlertSummary() {
        const stats = this.getAlertStatistics();

        if (stats.criticalActive > 0) {
            return `Critical alert! You have ${stats.criticalActive} critical alerts requiring immediate attention.`;
        } else if (stats.unacknowledged > 0) {
            return `You have ${stats.unacknowledged} unacknowledged alerts in the system.`;
        } else if (stats.active > 0) {
            return `System has ${stats.active} active alerts, all under control.`;
        } else {
            return 'All systems operating normally. No active alerts.';
        }
    }
}

export const qaAlertSystem = new QAAlertSystem();