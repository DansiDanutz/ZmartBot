/**
 * HISTORY ANALYZER AGENT
 * Analyzes historical patterns, tracks knowledge evolution, and learns from past successes/failures
 * Critical for understanding what works and what doesn't over time
 */

import BaseAgent from './BaseAgent.js';
import { subDays, startOfDay, endOfDay } from 'date-fns';

export default class HistoryAnalyzerAgent extends BaseAgent {
  constructor(config) {
    super({
      ...config,
      name: 'History Analyzer Agent',
      priority: 7
    });

    // Analysis configurations
    this.analysisConfig = {
      lookbackPeriods: [1, 7, 30, 90, 365], // days
      minSampleSize: 10,
      confidenceThreshold: 0.7,
      significanceLevel: 0.05,
      trendDetectionWindow: 7
    };

    // Historical patterns storage
    this.historicalPatterns = new Map();
    this.trendData = new Map();
    this.evolutionTimeline = [];

    // Performance tracking
    this.performanceMetrics = {
      successfulPredictions: 0,
      failedPredictions: 0,
      discoveredPatterns: 0,
      evolutionEvents: 0
    };
  }

  /**
   * Initialize the history analyzer
   */
  async initialize() {
    console.log('📊 Initializing History Analyzer Agent');

    // Load historical baselines
    await this.loadHistoricalBaselines();

    // Initialize trend tracking
    await this.initializeTrendTracking();
  }

  /**
   * Execute history analysis task
   */
  async executeTask(task) {
    const { type, data } = task;

    switch (type) {
      case 'analyze_period':
        return await this.analyzePeriod(data);

      case 'track_evolution':
        return await this.trackEvolution(data);

      case 'analyze_user_history':
        return await this.analyzeUserHistory(data);

      case 'find_success_patterns':
        return await this.findSuccessPatterns(data);

      case 'analyze_failures':
        return await this.analyzeFailures(data);

      case 'generate_insights':
        return await this.generateHistoricalInsights(data);

      default:
        throw new Error(`Unknown task type: ${type}`);
    }
  }

  /**
   * Scheduled history analysis
   */
  async executeScheduledTasks() {
    console.log('🕐 Running scheduled history analysis');

    // Daily analysis
    await this.analyzeDailyHistory();

    // Track knowledge evolution
    await this.trackKnowledgeEvolution();

    // Analyze pattern performance
    await this.analyzePatternPerformance();

    // Generate trend reports
    await this.generateTrendReports();

    // Clean old history
    await this.archiveOldHistory();
  }

  /**
   * Analyze a specific time period
   */
  async analyzePeriod({ startDate, endDate, focus = 'all' }) {
    const analysis = {
      period: { start: startDate, end: endDate },
      metrics: {},
      patterns: [],
      trends: [],
      insights: []
    };

    try {
      // Gather data for the period
      const periodData = await this.gatherPeriodData(startDate, endDate);

      // Analyze different aspects based on focus
      if (focus === 'all' || focus === 'knowledge') {
        analysis.metrics.knowledge = await this.analyzeKnowledgeHistory(periodData);
      }

      if (focus === 'all' || focus === 'patterns') {
        analysis.patterns = await this.analyzePatternsInPeriod(periodData);
      }

      if (focus === 'all' || focus === 'user_behavior') {
        analysis.metrics.userBehavior = await this.analyzeUserBehaviorHistory(periodData);
      }

      if (focus === 'all' || focus === 'performance') {
        analysis.metrics.performance = await this.analyzePerformanceHistory(periodData);
      }

      // Detect trends
      analysis.trends = this.detectTrends(periodData);

      // Generate insights
      analysis.insights = await this.generateInsights(analysis);

      // Store analysis results
      await this.storeAnalysisResults(analysis);

      return analysis;

    } catch (error) {
      this.handleError('Period analysis failed', error);
      throw error;
    }
  }

  /**
   * Track knowledge evolution over time
   */
  async trackKnowledgeEvolution() {
    const evolution = {
      timestamp: Date.now(),
      changes: [],
      growth: {},
      quality: {}
    };

    // Track knowledge growth
    for (const period of this.analysisConfig.lookbackPeriods) {
      const startDate = subDays(new Date(), period);

      // Count new knowledge added
      const { count: newKnowledge } = await this.supabase
        .from('brain_knowledge')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', startDate.toISOString());

      evolution.growth[`${period}d`] = newKnowledge;

      // Track quality changes
      const { data: qualityData } = await this.supabase
        .from('brain_knowledge')
        .select('confidence_score')
        .gte('created_at', startDate.toISOString());

      if (qualityData) {
        const avgConfidence = qualityData.reduce((sum, item) =>
          sum + item.confidence_score, 0) / qualityData.length;

        evolution.quality[`${period}d`] = avgConfidence;
      }
    }

    // Detect significant changes
    evolution.changes = await this.detectSignificantChanges();

    // Track evolution timeline
    this.evolutionTimeline.push(evolution);

    // Keep timeline size manageable
    if (this.evolutionTimeline.length > 1000) {
      this.evolutionTimeline = this.evolutionTimeline.slice(-500);
    }

    this.performanceMetrics.evolutionEvents++;

    return evolution;
  }

  /**
   * Analyze user history for patterns
   */
  async analyzeUserHistory({ userId, lookbackDays = 30 }) {
    const analysis = {
      userId,
      period: lookbackDays,
      patterns: [],
      preferences: {},
      performance: {},
      recommendations: []
    };

    const startDate = subDays(new Date(), lookbackDays);

    // Get user interactions
    const { data: interactions } = await this.supabase
      .from('brain_user_interactions')
      .select('*')
      .eq('user_id', userId)
      .gte('created_at', startDate.toISOString())
      .order('created_at', { ascending: true });

    if (interactions && interactions.length > 0) {
      // Analyze question patterns
      analysis.patterns = this.analyzeQuestionPatterns(interactions);

      // Extract preferences
      analysis.preferences = this.extractUserPreferences(interactions);

      // Analyze performance
      analysis.performance = this.analyzeUserPerformance(interactions);

      // Generate personalized recommendations
      analysis.recommendations = await this.generateUserRecommendations(
        analysis.patterns,
        analysis.preferences,
        analysis.performance
      );

      // Update user memory
      await this.updateUserMemoryFromHistory(userId, analysis);
    }

    return analysis;
  }

  /**
   * Find successful patterns in history
   */
  async findSuccessPatterns({ lookbackDays = 30, minSuccessRate = 0.7 }) {
    const patterns = [];
    const startDate = subDays(new Date(), lookbackDays);

    // Query successful patterns
    const { data: successfulPatterns } = await this.supabase
      .from('brain_patterns')
      .select('*')
      .gte('success_rate', minSuccessRate * 100)
      .gte('last_seen', startDate.toISOString())
      .order('success_rate', { ascending: false });

    if (successfulPatterns) {
      for (const pattern of successfulPatterns) {
        // Analyze pattern history
        const history = await this.analyzePatternHistory(pattern);

        if (history.isConsistent) {
          patterns.push({
            pattern,
            history,
            score: this.calculatePatternScore(pattern, history)
          });
        }
      }
    }

    // Discover new success patterns
    const newPatterns = await this.discoverNewSuccessPatterns(startDate);
    patterns.push(...newPatterns);

    this.performanceMetrics.discoveredPatterns += newPatterns.length;

    return patterns.sort((a, b) => b.score - a.score);
  }

  /**
   * Analyze failures to learn from mistakes
   */
  async analyzeFailures({ lookbackDays = 30 }) {
    const failures = {
      patterns: [],
      commonCauses: {},
      preventableFai

: [],
      lessons: []
    };

    const startDate = subDays(new Date(), lookbackDays);

    // Get failed predictions
    const { data: failedItems } = await this.supabase
      .from('brain_knowledge')
      .select('*')
      .gt('failure_count', 'success_count')
      .gte('updated_at', startDate.toISOString());

    if (failedItems) {
      // Identify failure patterns
      failures.patterns = this.identifyFailurePatterns(failedItems);

      // Find common causes
      failures.commonCauses = this.findCommonFailureCauses(failedItems);

      // Identify preventable failures
      failures.preventableFailures = this.identifyPreventableFailures(failedItems);

      // Extract lessons
      failures.lessons = await this.extractLessonsFromFailures(failures);

      // Store lessons learned
      await this.storeLessonsLearned(failures.lessons);
    }

    return failures;
  }

  /**
   * Analyze daily history
   */
  async analyzeDailyHistory() {
    const today = new Date();
    const yesterday = subDays(today, 1);

    const dailyAnalysis = {
      date: yesterday,
      metrics: {},
      highlights: [],
      issues: []
    };

    // Knowledge metrics
    const { count: newKnowledge } = await this.supabase
      .from('brain_knowledge')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', startOfDay(yesterday).toISOString())
      .lte('created_at', endOfDay(yesterday).toISOString());

    dailyAnalysis.metrics.newKnowledge = newKnowledge;

    // User activity
    const { count: userInteractions } = await this.supabase
      .from('brain_user_interactions')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', startOfDay(yesterday).toISOString())
      .lte('created_at', endOfDay(yesterday).toISOString());

    dailyAnalysis.metrics.userInteractions = userInteractions;

    // Pattern discoveries
    const { data: newPatterns } = await this.supabase
      .from('brain_patterns')
      .select('*')
      .gte('first_seen', startOfDay(yesterday).toISOString())
      .lte('first_seen', endOfDay(yesterday).toISOString());

    if (newPatterns && newPatterns.length > 0) {
      dailyAnalysis.highlights.push(`Discovered ${newPatterns.length} new patterns`);
    }

    // Performance issues
    const issues = await this.detectDailyIssues(yesterday);
    dailyAnalysis.issues = issues;

    // Store daily analysis
    await this.storeDailyAnalysis(dailyAnalysis);

    // Send summary
    this.sendMessage('history:daily_analysis', dailyAnalysis);

    return dailyAnalysis;
  }

  /**
   * Analyze pattern performance over time
   */
  async analyzePatternPerformance() {
    const performanceReport = {
      topPerformers: [],
      declining: [],
      emerging: [],
      retired: []
    };

    // Get all active patterns
    const { data: patterns } = await this.supabase
      .from('brain_patterns')
      .select('*')
      .eq('status', 'active');

    if (patterns) {
      for (const pattern of patterns) {
        const performance = await this.calculatePatternPerformance(pattern);

        // Categorize by performance
        if (performance.trend === 'improving' && performance.successRate > 0.7) {
          performanceReport.topPerformers.push({ pattern, performance });
        } else if (performance.trend === 'declining') {
          performanceReport.declining.push({ pattern, performance });
        } else if (performance.isNew && performance.potential > 0.6) {
          performanceReport.emerging.push({ pattern, performance });
        } else if (performance.successRate < 0.4) {
          performanceReport.retired.push({ pattern, performance });
        }
      }
    }

    // Update pattern statuses based on performance
    await this.updatePatternStatuses(performanceReport);

    return performanceReport;
  }

  /**
   * Generate historical insights
   */
  async generateHistoricalInsights({ focus = 'general' }) {
    const insights = [];

    try {
      // Knowledge growth insights
      const growthInsight = await this.generateGrowthInsight();
      if (growthInsight) insights.push(growthInsight);

      // Pattern effectiveness insights
      const patternInsight = await this.generatePatternInsight();
      if (patternInsight) insights.push(patternInsight);

      // User behavior insights
      const behaviorInsight = await this.generateBehaviorInsight();
      if (behaviorInsight) insights.push(behaviorInsight);

      // Quality trend insights
      const qualityInsight = await this.generateQualityInsight();
      if (qualityInsight) insights.push(qualityInsight);

      // Seasonal patterns
      const seasonalInsight = await this.detectSeasonalPatterns();
      if (seasonalInsight) insights.push(seasonalInsight);

      // Store insights
      for (const insight of insights) {
        await this.storeInsight(insight);
      }

      return insights;

    } catch (error) {
      this.handleError('Failed to generate insights', error);
      return insights;
    }
  }

  /**
   * Detect trends in data
   */
  detectTrends(data) {
    const trends = [];

    // Time series analysis
    const timeSeries = this.prepareTimeSeries(data);

    // Moving average trend
    const maTrend = this.calculateMovingAverageTrend(timeSeries);
    if (maTrend.isSignificant) {
      trends.push({
        type: 'moving_average',
        direction: maTrend.direction,
        strength: maTrend.strength,
        description: maTrend.description
      });
    }

    // Linear regression trend
    const linearTrend = this.calculateLinearTrend(timeSeries);
    if (linearTrend.r2 > 0.5) {
      trends.push({
        type: 'linear',
        slope: linearTrend.slope,
        r2: linearTrend.r2,
        description: linearTrend.description
      });
    }

    // Cyclical patterns
    const cycles = this.detectCycles(timeSeries);
    if (cycles.length > 0) {
      trends.push({
        type: 'cyclical',
        cycles,
        description: `Detected ${cycles.length} cyclical patterns`
      });
    }

    return trends;
  }

  /**
   * Calculate pattern score
   */
  calculatePatternScore(pattern, history) {
    let score = 0;

    // Base score from success rate
    score += pattern.success_rate / 100 * 40;

    // Consistency bonus
    if (history.consistencyScore > 0.8) {
      score += 20;
    }

    // Recency bonus
    const daysSinceLastSeen = (Date.now() - new Date(pattern.last_seen).getTime()) / 86400000;
    if (daysSinceLastSeen < 7) {
      score += 15;
    }

    // Volume bonus
    if (pattern.occurrences > 100) {
      score += 15;
    } else if (pattern.occurrences > 50) {
      score += 10;
    }

    // Confidence bonus
    if (pattern.confidence_level > 0.8) {
      score += 10;
    }

    return Math.min(100, score);
  }

  /**
   * Identify failure patterns
   */
  identifyFailurePatterns(failedItems) {
    const patterns = new Map();

    for (const item of failedItems) {
      // Group by failure characteristics
      const key = `${item.knowledge_type}_${item.source_type}`;

      if (!patterns.has(key)) {
        patterns.set(key, {
          type: item.knowledge_type,
          source: item.source_type,
          count: 0,
          items: []
        });
      }

      const pattern = patterns.get(key);
      pattern.count++;
      pattern.items.push(item.id);
    }

    // Convert to array and sort by frequency
    return Array.from(patterns.values())
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }

  /**
   * Store analysis results
   */
  async storeAnalysisResults(analysis) {
    await this.supabase.from('brain_history_analysis').insert({
      period_start: analysis.period.start,
      period_end: analysis.period.end,
      metrics: analysis.metrics,
      patterns: analysis.patterns,
      trends: analysis.trends,
      insights: analysis.insights,
      agent_name: this.config.name
    });
  }

  /**
   * Load historical baselines
   */
  async loadHistoricalBaselines() {
    // Load recent analysis results
    const { data: recentAnalysis } = await this.supabase
      .from('brain_history_analysis')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10);

    if (recentAnalysis) {
      // Build baseline metrics
      this.baselineMetrics = this.calculateBaselines(recentAnalysis);
    }
  }

  /**
   * Archive old history
   */
  async archiveOldHistory() {
    const archiveDate = subDays(new Date(), 365); // Archive data older than 1 year

    // Archive old interactions
    const { count: archivedInteractions } = await this.supabase
      .from('brain_user_interactions')
      .delete()
      .lt('created_at', archiveDate.toISOString());

    // Archive old analysis results
    const { count: archivedAnalysis } = await this.supabase
      .from('brain_history_analysis')
      .delete()
      .lt('created_at', archiveDate.toISOString());

    console.log(`📦 Archived ${archivedInteractions} interactions and ${archivedAnalysis} analysis results`);
  }

  /**
   * Get history statistics
   */
  getStatistics() {
    return {
      ...this.performanceMetrics,
      historicalPatternsCount: this.historicalPatterns.size,
      evolutionTimelineLength: this.evolutionTimeline.length,
      trendDataPoints: this.trendData.size,
      predictionAccuracy: this.performanceMetrics.successfulPredictions /
        Math.max(1, this.performanceMetrics.successfulPredictions + this.performanceMetrics.failedPredictions)
    };
  }
}