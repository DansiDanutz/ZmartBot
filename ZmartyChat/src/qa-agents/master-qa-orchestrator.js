// Master QA Orchestrator
// Coordinates all QA agents and provides comprehensive system quality assurance

import { marketAnalysisQA } from './market-analysis-qa.js';
import { riskAssessmentQA } from './risk-assessment-qa.js';
import { tradingIntelligenceQA } from './trading-intelligence-qa.js';

export class MasterQAOrchestrator {
    constructor() {
        this.qaAgents = {
            marketAnalysis: marketAnalysisQA,
            riskAssessment: riskAssessmentQA,
            tradingIntelligence: tradingIntelligenceQA
        };

        this.systemThresholds = {
            criticalScore: 0.60, // Below this is critical failure
            warningScore: 0.75,  // Below this triggers warnings
            optimalScore: 0.85,  // Above this is optimal performance
            excellentScore: 0.95 // Above this is excellent
        };

        this.testHistory = [];
        this.alertSubscribers = [];
    }

    // Run comprehensive system QA
    async runSystemQA(options = {}) {
        const startTime = Date.now();
        const results = {
            timestamp: new Date().toISOString(),
            sessionId: this.generateSessionId(),
            type: options.type || 'comprehensive',
            components: {},
            overall: {},
            alerts: [],
            duration: 0
        };

        try {
            // Run all QA suites in parallel for efficiency
            const qaPromises = [];

            if (options.components?.marketAnalysis !== false) {
                qaPromises.push(this.runComponentQA('marketAnalysis'));
            }

            if (options.components?.riskAssessment !== false) {
                qaPromises.push(this.runComponentQA('riskAssessment'));
            }

            if (options.components?.tradingIntelligence !== false) {
                qaPromises.push(this.runComponentQA('tradingIntelligence'));
            }

            // Wait for all QA tests to complete
            const componentResults = await Promise.allSettled(qaPromises);

            // Process results
            componentResults.forEach((result, index) => {
                const componentName = Object.keys(this.qaAgents)[index];
                if (result.status === 'fulfilled') {
                    results.components[componentName] = result.value;
                } else {
                    results.components[componentName] = {
                        status: 'ERROR',
                        error: result.reason.message
                    };
                }
            });

            // Calculate overall system health
            results.overall = this.calculateSystemHealth(results.components);

            // Generate alerts based on results
            results.alerts = this.generateSystemAlerts(results);

            // Calculate execution time
            results.duration = Date.now() - startTime;

            // Store in history
            this.testHistory.push(results);

            // Notify subscribers if critical issues found
            if (results.overall.systemStatus === 'CRITICAL') {
                await this.notifyAlertSubscribers(results.alerts);
            }

        } catch (error) {
            results.overall = {
                systemStatus: 'ERROR',
                error: error.message
            };
        }

        return results;
    }

    // Run QA for specific component
    async runComponentQA(componentName) {
        const agent = this.qaAgents[componentName];
        if (!agent) {
            throw new Error(`QA agent '${componentName}' not found`);
        }

        const results = await agent.runFullQA();
        const report = agent.generateReport(results);

        return {
            ...results,
            report
        };
    }

    // Calculate overall system health
    calculateSystemHealth(components) {
        const scores = [];
        const statuses = [];

        Object.entries(components).forEach(([name, component]) => {
            if (component.overallScore !== undefined) {
                scores.push(component.overallScore);
                statuses.push(component.status);
            }
        });

        if (scores.length === 0) {
            return {
                systemStatus: 'NO_DATA',
                score: 0,
                grade: 'N/A'
            };
        }

        // Calculate weighted average (risk gets higher weight)
        const weights = {
            marketAnalysis: 1.0,
            riskAssessment: 1.5, // Higher weight for risk
            tradingIntelligence: 1.2
        };

        let weightedSum = 0;
        let totalWeight = 0;

        Object.entries(components).forEach(([name, component]) => {
            if (component.overallScore !== undefined) {
                const weight = weights[name] || 1.0;
                weightedSum += component.overallScore * weight;
                totalWeight += weight;
            }
        });

        const overallScore = weightedSum / totalWeight;

        // Determine system status
        let systemStatus;
        let grade;

        if (overallScore >= this.systemThresholds.excellentScore) {
            systemStatus = 'EXCELLENT';
            grade = 'A+';
        } else if (overallScore >= this.systemThresholds.optimalScore) {
            systemStatus = 'OPTIMAL';
            grade = 'A';
        } else if (overallScore >= this.systemThresholds.warningScore) {
            systemStatus = 'SATISFACTORY';
            grade = 'B';
        } else if (overallScore >= this.systemThresholds.criticalScore) {
            systemStatus = 'WARNING';
            grade = 'C';
        } else {
            systemStatus = 'CRITICAL';
            grade = 'F';
        }

        // Check for any critical component failures
        const hasCriticalFailure = statuses.includes('FAIL') ||
                                   components.riskAssessment?.riskLevel === 'CRITICAL';

        if (hasCriticalFailure) {
            systemStatus = 'CRITICAL';
            grade = 'F';
        }

        return {
            systemStatus,
            score: overallScore,
            grade,
            scorePercentage: `${(overallScore * 100).toFixed(1)}%`,
            componentsTotal: Object.keys(components).length,
            componentsPassed: statuses.filter(s => s === 'PASS').length,
            componentsFailed: statuses.filter(s => s === 'FAIL').length,
            hasRiskIssues: components.riskAssessment?.riskLevel === 'HIGH' ||
                          components.riskAssessment?.riskLevel === 'CRITICAL'
        };
    }

    // Generate system alerts
    generateSystemAlerts(results) {
        const alerts = [];

        // Check overall system status
        if (results.overall.systemStatus === 'CRITICAL') {
            alerts.push({
                level: 'CRITICAL',
                component: 'SYSTEM',
                message: 'System is in critical state - immediate action required',
                timestamp: new Date().toISOString(),
                actions: ['Pause all trading operations', 'Run diagnostic tests', 'Review all component failures']
            });
        } else if (results.overall.systemStatus === 'WARNING') {
            alerts.push({
                level: 'WARNING',
                component: 'SYSTEM',
                message: 'System performance is degraded',
                timestamp: new Date().toISOString(),
                actions: ['Review component warnings', 'Adjust system parameters']
            });
        }

        // Check individual components
        Object.entries(results.components).forEach(([name, component]) => {
            if (component.status === 'FAIL') {
                alerts.push({
                    level: 'ERROR',
                    component: name.toUpperCase(),
                    message: `${name} component has failed QA tests`,
                    timestamp: new Date().toISOString(),
                    score: component.overallScore,
                    recommendations: component.report?.recommendations || []
                });
            }

            // Check for risk-specific alerts
            if (name === 'riskAssessment' && component.report?.alerts) {
                alerts.push(...component.report.alerts);
            }
        });

        return alerts;
    }

    // Generate comprehensive report
    generateSystemReport(results) {
        const report = {
            title: 'ZmartBot System QA Report',
            timestamp: results.timestamp,
            sessionId: results.sessionId,
            executionTime: `${results.duration}ms`,

            executive_summary: {
                status: results.overall.systemStatus,
                grade: results.overall.grade,
                score: results.overall.scorePercentage,
                recommendation: this.getExecutiveRecommendation(results.overall.systemStatus)
            },

            system_health: {
                ...results.overall,
                trend: this.calculateTrend()
            },

            component_summaries: this.generateComponentSummaries(results.components),

            critical_findings: this.extractCriticalFindings(results),

            recommendations: this.consolidateRecommendations(results),

            alerts: results.alerts,

            test_coverage: {
                totalTests: this.countTotalTests(results.components),
                passedTests: this.countPassedTests(results.components),
                failedTests: this.countFailedTests(results.components),
                errorTests: this.countErrorTests(results.components)
            },

            next_steps: this.generateNextSteps(results)
        };

        return report;
    }

    // Get executive recommendation
    getExecutiveRecommendation(status) {
        const recommendations = {
            'EXCELLENT': 'System is performing at peak efficiency. Continue monitoring.',
            'OPTIMAL': 'System is operating well. Minor optimizations may improve performance.',
            'SATISFACTORY': 'System is functional but has room for improvement. Review warnings.',
            'WARNING': 'System requires attention. Address failing components promptly.',
            'CRITICAL': 'IMMEDIATE ACTION REQUIRED. System integrity at risk. Halt operations if necessary.',
            'ERROR': 'System QA failed to complete. Investigate infrastructure issues.',
            'NO_DATA': 'Insufficient data for assessment. Run full diagnostic suite.'
        };

        return recommendations[status] || 'Status unknown. Manual review required.';
    }

    // Generate component summaries
    generateComponentSummaries(components) {
        const summaries = {};

        Object.entries(components).forEach(([name, component]) => {
            summaries[name] = {
                status: component.status,
                score: component.overallScore ?
                    `${(component.overallScore * 100).toFixed(1)}%` : 'N/A',
                testsPassed: component.tests?.filter(t => t.status === 'PASS').length || 0,
                testsFailed: component.tests?.filter(t => t.status === 'FAIL').length || 0,
                keyFindings: this.extractKeyFindings(component)
            };

            // Add component-specific data
            if (name === 'riskAssessment') {
                summaries[name].riskLevel = component.riskLevel;
            }
            if (name === 'tradingIntelligence') {
                summaries[name].aiPerformance = component.aiPerformance;
            }
        });

        return summaries;
    }

    // Extract key findings from component
    extractKeyFindings(component) {
        const findings = [];

        if (component.tests) {
            component.tests.forEach(test => {
                if (test.status === 'FAIL') {
                    findings.push(`${test.name} failed with score ${(test.score * 100).toFixed(1)}%`);
                }
            });
        }

        return findings.length > 0 ? findings : ['All tests passed'];
    }

    // Extract critical findings
    extractCriticalFindings(results) {
        const criticalFindings = [];

        // System-level critical findings
        if (results.overall.systemStatus === 'CRITICAL') {
            criticalFindings.push({
                severity: 'CRITICAL',
                finding: 'System operating below minimum acceptable threshold',
                impact: 'Trading operations may be compromised'
            });
        }

        // Component-level critical findings
        Object.entries(results.components).forEach(([name, component]) => {
            if (component.status === 'FAIL') {
                criticalFindings.push({
                    severity: 'HIGH',
                    finding: `${name} component failure`,
                    impact: this.getComponentImpact(name)
                });
            }
        });

        return criticalFindings;
    }

    // Get component impact description
    getComponentImpact(componentName) {
        const impacts = {
            marketAnalysis: 'Market data accuracy and signal generation affected',
            riskAssessment: 'Portfolio risk exposure may exceed safe limits',
            tradingIntelligence: 'AI decision making and strategy execution compromised'
        };

        return impacts[componentName] || 'System functionality degraded';
    }

    // Consolidate recommendations
    consolidateRecommendations(results) {
        const allRecommendations = [];

        Object.values(results.components).forEach(component => {
            if (component.report?.recommendations) {
                allRecommendations.push(...component.report.recommendations);
            }
        });

        // Remove duplicates and prioritize
        const unique = [...new Set(allRecommendations)];

        return unique.map((rec, index) => ({
            priority: index < 3 ? 'HIGH' : index < 6 ? 'MEDIUM' : 'LOW',
            recommendation: rec
        }));
    }

    // Generate next steps
    generateNextSteps(results) {
        const steps = [];

        if (results.overall.systemStatus === 'CRITICAL') {
            steps.push('1. Immediately pause trading operations');
            steps.push('2. Run detailed diagnostic on failed components');
            steps.push('3. Engage technical team for emergency review');
        } else if (results.overall.systemStatus === 'WARNING') {
            steps.push('1. Review all component warnings');
            steps.push('2. Implement recommended fixes');
            steps.push('3. Schedule follow-up QA test in 1 hour');
        } else {
            steps.push('1. Continue normal operations');
            steps.push('2. Monitor system metrics');
            steps.push('3. Schedule next QA test as per routine');
        }

        return steps;
    }

    // Calculate trend from history
    calculateTrend() {
        if (this.testHistory.length < 2) return 'STABLE';

        const recent = this.testHistory.slice(-5);
        const scores = recent.map(r => r.overall.score).filter(s => s !== undefined);

        if (scores.length < 2) return 'STABLE';

        const trend = scores[scores.length - 1] - scores[0];

        if (trend > 0.05) return 'IMPROVING';
        if (trend < -0.05) return 'DEGRADING';
        return 'STABLE';
    }

    // Count tests
    countTotalTests(components) {
        return Object.values(components).reduce((total, comp) =>
            total + (comp.tests?.length || 0), 0);
    }

    countPassedTests(components) {
        return Object.values(components).reduce((total, comp) =>
            total + (comp.tests?.filter(t => t.status === 'PASS').length || 0), 0);
    }

    countFailedTests(components) {
        return Object.values(components).reduce((total, comp) =>
            total + (comp.tests?.filter(t => t.status === 'FAIL').length || 0), 0);
    }

    countErrorTests(components) {
        return Object.values(components).reduce((total, comp) =>
            total + (comp.tests?.filter(t => t.status === 'ERROR').length || 0), 0);
    }

    // Subscribe to alerts
    subscribeToAlerts(callback) {
        this.alertSubscribers.push(callback);
    }

    // Notify alert subscribers
    async notifyAlertSubscribers(alerts) {
        for (const subscriber of this.alertSubscribers) {
            try {
                await subscriber(alerts);
            } catch (error) {
                console.error('Failed to notify subscriber:', error);
            }
        }
    }

    // Generate session ID
    generateSessionId() {
        return `QA-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    // Get test history
    getTestHistory(limit = 10) {
        return this.testHistory.slice(-limit);
    }

    // Clear test history
    clearTestHistory() {
        this.testHistory = [];
    }
}

export const masterQA = new MasterQAOrchestrator();