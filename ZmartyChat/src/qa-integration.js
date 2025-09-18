// QA Integration Module for ZmartyChat
// Connects QA agents with the main server and ElevenLabs

import { MarketAnalysisQA } from './qa-agents/market-analysis-qa.js';
import { RiskAssessmentQA } from './qa-agents/risk-assessment-qa.js';
import { TradingIntelligenceQA } from './qa-agents/trading-intelligence-qa.js';
import { MasterQAOrchestrator } from './qa-agents/master-qa-orchestrator.js';
import { QAAlertSystem } from './qa-agents/alert-system.js';

// Initialize QA components
export const qaSystem = {
    marketAnalysis: new MarketAnalysisQA(),
    riskAssessment: new RiskAssessmentQA(),
    tradingIntelligence: new TradingIntelligenceQA(),
    master: new MasterQAOrchestrator(),
    alerts: new QAAlertSystem()
};

// QA API endpoints for Express
export function createQARoutes() {
    const express = require('express');
    const router = express.Router();

    // Run full system QA
    router.post('/run-full', async (req, res) => {
        try {
            const results = await qaSystem.master.runSystemQA();
            const report = qaSystem.master.generateSystemReport(results);

            // Create alerts for any issues
            const alerts = await qaSystem.alerts.createAlertsFromQAResults(results);

            res.json({
                status: 'success',
                results,
                report,
                alerts,
                summary: {
                    systemStatus: results.overall.systemStatus,
                    score: results.overall.scorePercentage,
                    criticalAlerts: alerts.filter(a => a?.level === 'CRITICAL').length
                }
            });
        } catch (error) {
            res.status(500).json({
                status: 'error',
                error: error.message
            });
        }
    });

    // Run specific component QA
    router.post('/run/:component', async (req, res) => {
        const { component } = req.params;

        try {
            let results;
            let report;

            switch (component) {
                case 'market':
                    results = await qaSystem.marketAnalysis.runFullQA();
                    report = qaSystem.marketAnalysis.generateReport(results);
                    break;
                case 'risk':
                    results = await qaSystem.riskAssessment.runFullQA();
                    report = qaSystem.riskAssessment.generateReport(results);
                    break;
                case 'intelligence':
                    results = await qaSystem.tradingIntelligence.runFullQA();
                    report = qaSystem.tradingIntelligence.generateReport(results);
                    break;
                default:
                    return res.status(400).json({
                        status: 'error',
                        error: 'Invalid component'
                    });
            }

            res.json({
                status: 'success',
                component,
                results,
                report
            });
        } catch (error) {
            res.status(500).json({
                status: 'error',
                error: error.message
            });
        }
    });

    // Get active alerts
    router.get('/alerts', (req, res) => {
        const alerts = qaSystem.alerts.getActiveAlerts();
        const stats = qaSystem.alerts.getAlertStatistics();

        res.json({
            alerts,
            statistics: stats,
            voiceSummary: qaSystem.alerts.getVoiceAlertSummary()
        });
    });

    // Acknowledge alert
    router.post('/alerts/:alertId/acknowledge', async (req, res) => {
        const { alertId } = req.params;
        const { acknowledgedBy } = req.body;

        const success = await qaSystem.alerts.acknowledgeAlert(alertId, acknowledgedBy);

        res.json({
            status: success ? 'success' : 'error',
            acknowledged: success
        });
    });

    // Resolve alert
    router.post('/alerts/:alertId/resolve', async (req, res) => {
        const { alertId } = req.params;
        const { resolvedBy, resolution } = req.body;

        const success = await qaSystem.alerts.resolveAlert(alertId, resolvedBy, resolution);

        res.json({
            status: success ? 'success' : 'error',
            resolved: success
        });
    });

    // Voice alert endpoint
    router.post('/voice-alert', (req, res) => {
        const { alert, priority, interrupt } = req.body;

        // Store for voice system to pick up
        global.voiceAlertQueue = global.voiceAlertQueue || [];
        global.voiceAlertQueue.push({
            message: alert,
            priority,
            interrupt,
            timestamp: new Date().toISOString()
        });

        res.json({
            status: 'queued',
            queueLength: global.voiceAlertQueue.length
        });
    });

    // Get QA status summary
    router.get('/status', async (req, res) => {
        const alertStats = qaSystem.alerts.getAlertStatistics();
        const history = qaSystem.master.getTestHistory(5);

        res.json({
            status: 'operational',
            alerts: {
                active: alertStats.active,
                critical: alertStats.criticalActive,
                unacknowledged: alertStats.unacknowledged
            },
            lastTests: history.map(h => ({
                timestamp: h.timestamp,
                status: h.overall?.systemStatus,
                score: h.overall?.scorePercentage
            })),
            components: {
                marketAnalysis: 'ready',
                riskAssessment: 'ready',
                tradingIntelligence: 'ready',
                alertSystem: 'active'
            }
        });
    });

    return router;
}

// ElevenLabs voice tool handlers for QA
export async function handleQATool(toolName, parameters, userId) {
    let result;
    let creditsUsed = 0;

    try {
        switch (toolName) {
            case 'run_qa_test':
                creditsUsed = 3;
                const component = parameters?.component || 'all';

                if (component === 'all') {
                    const results = await qaSystem.master.runSystemQA();
                    const alerts = await qaSystem.alerts.createAlertsFromQAResults(results);

                    result = `QA test complete. System status: ${results.overall.systemStatus}. Score: ${results.overall.scorePercentage}. `;

                    if (alerts.filter(a => a?.level === 'CRITICAL').length > 0) {
                        result += `Critical alerts detected! Immediate action required. `;
                    }

                    result += `${creditsUsed} credits used.`;
                } else {
                    let componentResults;
                    switch (component.toLowerCase()) {
                        case 'market':
                            componentResults = await qaSystem.marketAnalysis.runFullQA();
                            break;
                        case 'risk':
                            componentResults = await qaSystem.riskAssessment.runFullQA();
                            break;
                        case 'intelligence':
                            componentResults = await qaSystem.tradingIntelligence.runFullQA();
                            break;
                        default:
                            result = `Unknown component: ${component}. Available: market, risk, intelligence, or all.`;
                            return { result, creditsUsed: 0 };
                    }

                    result = `${component} QA complete. Status: ${componentResults.status}. Score: ${(componentResults.overallScore * 100).toFixed(1)}%. ${creditsUsed} credits used.`;
                }
                break;

            case 'check_alerts':
                creditsUsed = 1;
                const alertSummary = qaSystem.alerts.getVoiceAlertSummary();
                const stats = qaSystem.alerts.getAlertStatistics();

                result = alertSummary;
                if (stats.active > 0) {
                    result += ` Active alerts breakdown: `;
                    Object.entries(stats.byLevel).forEach(([level, count]) => {
                        result += `${count} ${level.toLowerCase()}, `;
                    });
                }
                result += ` ${creditsUsed} credit used.`;
                break;

            case 'acknowledge_alerts':
                creditsUsed = 1;
                const activeAlerts = qaSystem.alerts.getActiveAlerts({ unacknowledged: true });
                let acknowledged = 0;

                for (const alert of activeAlerts) {
                    await qaSystem.alerts.acknowledgeAlert(alert.id, `voice_user_${userId}`);
                    acknowledged++;
                }

                result = `Acknowledged ${acknowledged} alerts. ${creditsUsed} credit used.`;
                break;

            case 'system_health':
                creditsUsed = 1;
                const lastTest = qaSystem.master.getTestHistory(1)[0];

                if (lastTest) {
                    result = `Last system QA: ${lastTest.overall?.systemStatus || 'unknown'}. Score: ${lastTest.overall?.scorePercentage || 'N/A'}. `;

                    if (lastTest.overall?.hasRiskIssues) {
                        result += `Warning: Risk issues detected. `;
                    }
                } else {
                    result = `No recent QA tests available. Run a test to check system health. `;
                }

                const alertStats = qaSystem.alerts.getAlertStatistics();
                if (alertStats.criticalActive > 0) {
                    result += `Alert: ${alertStats.criticalActive} critical alerts active! `;
                }

                result += `${creditsUsed} credit used.`;
                break;

            default:
                result = `Unknown QA tool: ${toolName}`;
                creditsUsed = 0;
        }
    } catch (error) {
        console.error('QA tool error:', error);
        result = `QA system error: ${error.message}`;
        creditsUsed = 0;
    }

    return { result, creditsUsed };
}

// WebSocket integration for real-time alerts
export function setupQAWebSocket(io) {
    // Store io instance globally for alert system
    global.io = io;

    // Subscribe to QA alerts
    qaSystem.alerts.subscribe((alert) => {
        io.emit('qa_alert', {
            ...alert,
            formattedMessage: qaSystem.alerts.formatAlertMessage(alert)
        });
    });

    // Handle WebSocket connections
    io.on('connection', (socket) => {
        // Send current alert status on connect
        socket.emit('qa_status', {
            alerts: qaSystem.alerts.getActiveAlerts(),
            statistics: qaSystem.alerts.getAlertStatistics()
        });

        // Subscribe to QA updates
        socket.on('subscribe_qa', () => {
            socket.join('qa_subscribers');
        });

        // Handle alert acknowledgment
        socket.on('acknowledge_alert', async (data) => {
            const { alertId, userId } = data;
            const success = await qaSystem.alerts.acknowledgeAlert(alertId, userId);

            socket.emit('alert_acknowledged', {
                alertId,
                success
            });

            // Broadcast update to all subscribers
            io.to('qa_subscribers').emit('alerts_updated', {
                alerts: qaSystem.alerts.getActiveAlerts()
            });
        });
    });
}

// Schedule periodic QA tests
export function scheduleQATests() {
    // Run full system QA every hour
    setInterval(async () => {
        console.log('Running scheduled QA test...');
        try {
            const results = await qaSystem.master.runSystemQA();
            await qaSystem.alerts.createAlertsFromQAResults(results);

            console.log(`Scheduled QA complete: ${results.overall.systemStatus}`);
        } catch (error) {
            console.error('Scheduled QA failed:', error);
        }
    }, 3600000); // 1 hour

    // Clear expired alerts every 15 minutes
    setInterval(() => {
        const cleared = qaSystem.alerts.clearExpiredAlerts();
        if (cleared > 0) {
            console.log(`Cleared ${cleared} expired alerts`);
        }
    }, 900000); // 15 minutes
}

export default qaSystem;