import axios, { AxiosInstance } from 'axios';

export interface TradingDecision {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD' | 'MONITOR';
  confidence: number;
  reasoning: string;
  supporting_indicators: string[];
  risk_assessment: string;
  expected_outcome: string;
  timestamp: string;
}

export interface ServiceMetrics {
  service_name: string;
  response_time: number;
  success_rate: number;
  error_count: number;
  last_update: string;
  data_quality_score: number;
  reliability_score: number;
  integration_score: number;
}

export interface TradingOrchestrationStatus {
  status: string;
  timestamp: string;
  active_services: number;
  total_decisions: number;
  learning_cycles_completed: number;
  uptime_hours: number;
  port: number;
  version: string;
}

export interface ServiceHealth {
  [serviceName: string]: {
    url: string;
    type: string;
    priority: string;
    certification?: string;
    features?: string[];
    status: 'healthy' | 'unhealthy' | 'unknown';
    response_time?: number;
  };
}

export interface TradingAnalysis {
  market_sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  top_opportunities: TradingDecision[];
  risk_alerts: string[];
  portfolio_recommendations: string[];
  market_summary: string;
}

class TradingOrchestrationServiceClient {
  private api: AxiosInstance;
  private baseURL: string;
  private isConnected: boolean = false;

  constructor() {
    this.baseURL = 'http://localhost:8200';
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.api.interceptors.response.use(
      (response) => {
        this.isConnected = true;
        return response;
      },
      (error) => {
        console.error('Trading Orchestration API Error:', error.message);
        this.isConnected = false;
        throw error;
      }
    );
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      this.isConnected = response.status === 200;
      return this.isConnected;
    } catch (error) {
      console.error('Trading Orchestration health check failed:', error);
      this.isConnected = false;
      return false;
    }
  }

  async getStatus(): Promise<TradingOrchestrationStatus> {
    try {
      const response = await this.api.get('/status');
      return response.data;
    } catch (error) {
      console.error('Error getting trading orchestration status:', error);
      throw error;
    }
  }

  async getTradingDecisions(symbol?: string, limit: number = 10): Promise<TradingDecision[]> {
    try {
      const params = new URLSearchParams();
      if (symbol) params.append('symbol', symbol);
      params.append('limit', limit.toString());

      const response = await this.api.get(`/api/v1/decisions?${params.toString()}`);
      return response.data.decisions || [];
    } catch (error) {
      console.error('Error getting trading decisions:', error);
      throw error;
    }
  }

  async getLatestDecision(symbol: string): Promise<TradingDecision | null> {
    try {
      const response = await this.api.get(`/api/v1/decision/${symbol}`);
      return response.data.decision || null;
    } catch (error) {
      console.error(`Error getting latest decision for ${symbol}:`, error);
      return null;
    }
  }

  async requestAnalysis(symbol: string, timeframe: string = '1h'): Promise<TradingDecision> {
    try {
      const response = await this.api.post('/api/v1/analyze', {
        symbol,
        timeframe
      });
      return response.data.decision;
    } catch (error) {
      console.error(`Error requesting analysis for ${symbol}:`, error);
      throw error;
    }
  }

  async getServiceHealth(): Promise<ServiceHealth> {
    try {
      const response = await this.api.get('/api/v1/services/health');
      return response.data.services || {};
    } catch (error) {
      console.error('Error getting service health:', error);
      throw error;
    }
  }

  async getServiceMetrics(): Promise<ServiceMetrics[]> {
    try {
      const response = await this.api.get('/api/v1/metrics');
      return response.data.metrics || [];
    } catch (error) {
      console.error('Error getting service metrics:', error);
      throw error;
    }
  }

  async startLearningCycle(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.api.post('/api/v1/learning/start');
      return response.data;
    } catch (error) {
      console.error('Error starting learning cycle:', error);
      throw error;
    }
  }

  async getLearningStatus(): Promise<{
    active: boolean;
    cycles_completed: number;
    current_phase: string;
    progress: number;
    last_update: string;
  }> {
    try {
      const response = await this.api.get('/api/v1/learning/status');
      return response.data;
    } catch (error) {
      console.error('Error getting learning status:', error);
      throw error;
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getServiceInfo(): { name: string; port: number; baseURL: string; connected: boolean } {
    return {
      name: 'Trading Orchestration Service',
      port: 8200,
      baseURL: this.baseURL,
      connected: this.isConnected
    };
  }

  // High-level analysis methods for Zmarty AI
  async getComprehensiveAnalysis(): Promise<TradingAnalysis> {
    try {
      const [decisions, serviceHealth, metrics] = await Promise.all([
        this.getTradingDecisions(undefined, 20),
        this.getServiceHealth(),
        this.getServiceMetrics()
      ]);

      // Analyze market sentiment from recent decisions
      const buyDecisions = decisions.filter(d => d.action === 'BUY').length;
      const sellDecisions = decisions.filter(d => d.action === 'SELL').length;
      const holdDecisions = decisions.filter(d => d.action === 'HOLD').length;

      let market_sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL' = 'NEUTRAL';
      if (buyDecisions > sellDecisions * 1.5) market_sentiment = 'BULLISH';
      else if (sellDecisions > buyDecisions * 1.5) market_sentiment = 'BEARISH';

      // Get top opportunities (high confidence decisions)
      const top_opportunities = decisions
        .filter(d => d.confidence > 0.7 && d.action !== 'HOLD')
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 5);

      // Generate risk alerts from low confidence or negative decisions
      const risk_alerts = decisions
        .filter(d => d.confidence < 0.4 || d.action === 'SELL')
        .map(d => `${d.symbol}: ${d.reasoning} (Confidence: ${(d.confidence * 100).toFixed(1)}%)`)
        .slice(0, 3);

      // Generate portfolio recommendations
      const portfolio_recommendations = [
        `Market sentiment is ${market_sentiment.toLowerCase()}`,
        `${top_opportunities.length} high-confidence opportunities identified`,
        `${decisions.filter(d => d.action === 'MONITOR').length} symbols under monitoring`,
        `Average decision confidence: ${(decisions.reduce((sum, d) => sum + d.confidence, 0) / decisions.length * 100).toFixed(1)}%`
      ];

      // Service health summary
      const healthyServices = Object.values(serviceHealth).filter(s => s.status === 'healthy').length;
      const totalServices = Object.keys(serviceHealth).length;
      
      const market_summary = `
Trading Orchestration Analysis:
• Market Sentiment: ${market_sentiment}
• Service Health: ${healthyServices}/${totalServices} services online
• Recent Decisions: ${buyDecisions} BUY, ${sellDecisions} SELL, ${holdDecisions} HOLD
• Learning Status: ${metrics.length > 0 ? 'Active' : 'Inactive'}
• Risk Level: ${risk_alerts.length > 2 ? 'High' : risk_alerts.length > 0 ? 'Medium' : 'Low'}
      `.trim();

      return {
        market_sentiment,
        top_opportunities,
        risk_alerts,
        portfolio_recommendations,
        market_summary
      };
    } catch (error) {
      console.error('Error getting comprehensive trading analysis:', error);
      throw error;
    }
  }

  async getPortfolioInsights(): Promise<{
    active_symbols: string[];
    decision_distribution: Record<string, number>;
    confidence_analysis: {
      high_confidence: TradingDecision[];
      medium_confidence: TradingDecision[];
      low_confidence: TradingDecision[];
    };
    recommendations: string[];
  }> {
    try {
      const decisions = await this.getTradingDecisions(undefined, 50);
      
      const active_symbols = [...new Set(decisions.map(d => d.symbol))];
      
      const decision_distribution = decisions.reduce((acc, d) => {
        acc[d.action] = (acc[d.action] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const confidence_analysis = {
        high_confidence: decisions.filter(d => d.confidence >= 0.8),
        medium_confidence: decisions.filter(d => d.confidence >= 0.5 && d.confidence < 0.8),
        low_confidence: decisions.filter(d => d.confidence < 0.5)
      };

      const recommendations = [
        `Tracking ${active_symbols.length} unique symbols`,
        `${confidence_analysis.high_confidence.length} high-confidence decisions available`,
        `${confidence_analysis.low_confidence.length} low-confidence decisions require review`,
        `Most common action: ${Object.entries(decision_distribution).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A'}`
      ];

      return {
        active_symbols,
        decision_distribution,
        confidence_analysis,
        recommendations
      };
    } catch (error) {
      console.error('Error getting portfolio insights:', error);
      throw error;
    }
  }

  async getSystemPerformance(): Promise<{
    orchestration_health: 'excellent' | 'good' | 'poor';
    service_availability: number;
    decision_quality: number;
    learning_progress: number;
    recommendations: string[];
  }> {
    try {
      const [status, serviceHealth, learningStatus] = await Promise.all([
        this.getStatus(),
        this.getServiceHealth(),
        this.getLearningStatus()
      ]);

      const healthyServices = Object.values(serviceHealth).filter(s => s.status === 'healthy').length;
      const totalServices = Object.keys(serviceHealth).length;
      const service_availability = totalServices > 0 ? (healthyServices / totalServices) * 100 : 0;

      const recentDecisions = await this.getTradingDecisions(undefined, 20);
      const decision_quality = recentDecisions.length > 0 ? 
        (recentDecisions.reduce((sum, d) => sum + d.confidence, 0) / recentDecisions.length) * 100 : 0;

      const learning_progress = learningStatus.cycles_completed * 10; // Arbitrary scoring

      let orchestration_health: 'excellent' | 'good' | 'poor' = 'poor';
      if (service_availability > 90 && decision_quality > 70) orchestration_health = 'excellent';
      else if (service_availability > 70 && decision_quality > 50) orchestration_health = 'good';

      const recommendations = [
        `System health: ${orchestration_health.toUpperCase()}`,
        `Service availability: ${service_availability.toFixed(1)}%`,
        `Decision quality score: ${decision_quality.toFixed(1)}%`,
        `Learning cycles completed: ${learningStatus.cycles_completed}`,
        learningStatus.active ? 'Learning system is active' : 'Consider starting learning cycle'
      ];

      return {
        orchestration_health,
        service_availability,
        decision_quality,
        learning_progress,
        recommendations
      };
    } catch (error) {
      console.error('Error getting system performance:', error);
      throw error;
    }
  }
}

export const tradingOrchestrationService = new TradingOrchestrationServiceClient();
export default tradingOrchestrationService;