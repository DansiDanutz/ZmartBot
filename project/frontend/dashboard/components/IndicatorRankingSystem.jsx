/**
 * 🏆 INDICATOR RANKING SYSTEM
 * Complete ranking and management system for 21 technical indicators
 * Based on trading importance, computational cost, and system impact
 */

export const INDICATOR_RANKINGS = {
  
  // 🔥 RANK S (SUPER CRITICAL) - Priority 1-2 - Load INSTANTLY
  RANK_S: {
    tier: 1,
    priority_range: [1, 2],
    update_frequency: 'immediate', // Every update cycle
    description: 'Mission-critical indicators - always load first',
    max_queue_load: 3, // Maximum indicators to load at once
    color: '#dc2626', // Red
    indicators: [
      {
        id: 'rsi',
        name: 'RSI (Relative Strength Index)',
        rank: 'S',
        priority: 1,
        weight: 0.25,
        reason: 'Most widely used momentum indicator, crucial for overbought/oversold levels'
      },
      {
        id: 'macd',
        name: 'MACD (Moving Average Convergence Divergence)',
        rank: 'S', 
        priority: 1,
        weight: 0.25,
        reason: 'Essential trend and momentum indicator, used in most trading strategies'
      },
      {
        id: 'support_resistance',
        name: 'Support/Resistance Levels',
        rank: 'S',
        priority: 2,
        weight: 0.30,
        reason: 'Core price action analysis, critical for entry/exit points'
      },
      {
        id: 'volume',
        name: 'Volume Analysis',
        rank: 'S',
        priority: 2,
        weight: 0.20,
        reason: 'Confirms price movements, essential for trade validation'
      }
    ]
  },

  // ⚡ RANK A (HIGH CRITICAL) - Priority 3-4 - Load SECOND
  RANK_A: {
    tier: 2,
    priority_range: [3, 4],
    update_frequency: 'high', // Load after 2 seconds delay
    description: 'High-importance indicators - core technical analysis',
    max_queue_load: 4,
    color: '#ea580c', // Orange-red
    indicators: [
      {
        id: 'ema_cross',
        name: 'EMA Crossover (9/21)',
        rank: 'A',
        priority: 3,
        weight: 0.20,
        reason: 'Trend identification and signal generation'
      },
      {
        id: 'bollinger',
        name: 'Bollinger Bands',
        rank: 'A',
        priority: 3,
        weight: 0.20,
        reason: 'Volatility and price target analysis'
      },
      {
        id: 'adx',
        name: 'ADX (Average Directional Index)',
        rank: 'A',
        priority: 4,
        weight: 0.15,
        reason: 'Trend strength measurement'
      },
      {
        id: 'atr',
        name: 'ATR (Average True Range)',
        rank: 'A',
        priority: 4,
        weight: 0.15,
        reason: 'Volatility measurement for position sizing'
      }
    ]
  },

  // 📊 RANK B (MEDIUM IMPORTANT) - Priority 5-6 - Load THIRD  
  RANK_B: {
    tier: 3,
    priority_range: [5, 6],
    update_frequency: 'medium', // Load after 5 seconds delay
    description: 'Medium-importance indicators - supplementary analysis',
    max_queue_load: 5,
    color: '#f59e0b', // Amber
    indicators: [
      {
        id: 'stochastic',
        name: 'Stochastic Oscillator',
        rank: 'B',
        priority: 5,
        weight: 0.12,
        reason: 'Momentum oscillator for overbought/oversold conditions'
      },
      {
        id: 'ichimoku',
        name: 'Ichimoku Cloud',
        rank: 'B',
        priority: 5,
        weight: 0.15,
        reason: 'Comprehensive trend analysis system'
      },
      {
        id: 'ma_convergence',
        name: 'Moving Average Convergence',
        rank: 'B',
        priority: 6,
        weight: 0.12,
        reason: 'Trend confirmation through MA alignment'
      },
      {
        id: 'fibonacci',
        name: 'Fibonacci Retracements',
        rank: 'B',
        priority: 6,
        weight: 0.15,
        reason: 'Key support/resistance levels identification'
      },
      {
        id: 'cci',
        name: 'CCI (Commodity Channel Index)',
        rank: 'B',
        priority: 6,
        weight: 0.10,
        reason: 'Cyclical turns and momentum measurement'
      }
    ]
  },

  // 🔍 RANK C (LOWER PRIORITY) - Priority 7-8 - Load FOURTH
  RANK_C: {
    tier: 4,
    priority_range: [7, 8], 
    update_frequency: 'low', // Load after 10 seconds delay
    description: 'Lower-priority indicators - advanced analysis',
    max_queue_load: 6,
    color: '#3b82f6', // Blue
    indicators: [
      {
        id: 'williams_r',
        name: 'Williams %R',
        rank: 'C',
        priority: 7,
        weight: 0.08,
        reason: 'Alternative momentum oscillator'
      },
      {
        id: 'parabolic_sar',
        name: 'Parabolic SAR',
        rank: 'C',
        priority: 7,
        weight: 0.10,
        reason: 'Trailing stop and trend reversal signals'
      },
      {
        id: 'obv',
        name: 'OBV (On-Balance Volume)',
        rank: 'C',
        priority: 7,
        weight: 0.08,
        reason: 'Volume-price relationship analysis'
      },
      {
        id: 'momentum',
        name: 'Price Momentum',
        rank: 'C',
        priority: 8,
        weight: 0.08,
        reason: 'Rate of price change measurement'
      },
      {
        id: 'roc',
        name: 'ROC (Rate of Change)',
        rank: 'C',
        priority: 8,
        weight: 0.07,
        reason: 'Momentum measurement over time periods'
      }
    ]
  },

  // 📈 RANK D (OPTIONAL) - Priority 9-10 - Load LAST (if system resources allow)
  RANK_D: {
    tier: 5,
    priority_range: [9, 10],
    update_frequency: 'optional', // Load only if queue < 5
    description: 'Optional indicators - specialized analysis',
    max_queue_load: 3,
    color: '#6b7280', // Gray
    indicators: [
      {
        id: 'price_channels',
        name: 'Price Channels',
        rank: 'D',
        priority: 9,
        weight: 0.05,
        reason: 'Channel breakout analysis'
      },
      {
        id: 'bollinger_squeeze',
        name: 'Bollinger Band Squeeze',
        rank: 'D',
        priority: 9,
        weight: 0.06,
        reason: 'Low volatility breakout prediction'
      },
      {
        id: 'macd_histogram',
        name: 'MACD Histogram',
        rank: 'D',
        priority: 10,
        weight: 0.05,
        reason: 'MACD momentum divergence analysis'
      }
    ]
  }
};

// 🛠️ MANAGEMENT FUNCTIONS
export class IndicatorManager {
  
  static getAllIndicators() {
    return Object.values(INDICATOR_RANKINGS)
      .flatMap(rank => rank.indicators)
      .sort((a, b) => a.priority - b.priority);
  }
  
  static getIndicatorsByRank(rank) {
    return INDICATOR_RANKINGS[`RANK_${rank}`]?.indicators || [];
  }
  
  static getIndicatorsByTier(tier) {
    return Object.values(INDICATOR_RANKINGS)
      .filter(rank => rank.tier === tier)
      .flatMap(rank => rank.indicators);
  }
  
  static getCriticalIndicators() {
    return [...this.getIndicatorsByRank('S'), ...this.getIndicatorsByRank('A')];
  }
  
  static getOptionalIndicators() {
    return [...this.getIndicatorsByRank('C'), ...this.getIndicatorsByRank('D')];
  }
  
  static getLoadingStrategy(systemHealth) {
    const { queue_length, status } = systemHealth;
    
    if (status === 'critical' || queue_length > 15) {
      return {
        strategy: 'minimal',
        ranks: ['S'],
        description: 'System overloaded - only critical indicators'
      };
    } else if (status === 'warning' || queue_length > 10) {
      return {
        strategy: 'conservative', 
        ranks: ['S', 'A'],
        description: 'System stressed - critical and high-importance only'
      };
    } else if (queue_length > 5) {
      return {
        strategy: 'balanced',
        ranks: ['S', 'A', 'B'],
        description: 'Normal load - skip optional indicators'
      };
    } else {
      return {
        strategy: 'full',
        ranks: ['S', 'A', 'B', 'C', 'D'],
        description: 'System healthy - load all indicators progressively'
      };
    }
  }
  
  static getUpdateTimings(strategy) {
    const timings = {
      'minimal': { S: 0 },
      'conservative': { S: 0, A: 3000 },
      'balanced': { S: 0, A: 2000, B: 5000 },
      'full': { S: 0, A: 2000, B: 5000, C: 10000, D: 15000 }
    };
    
    return timings[strategy] || timings.minimal;
  }
  
  static getIndicatorInfo(indicatorId) {
    for (const rankData of Object.values(INDICATOR_RANKINGS)) {
      const indicator = rankData.indicators.find(ind => ind.id === indicatorId);
      if (indicator) {
        return {
          ...indicator,
          tier: rankData.tier,
          color: rankData.color,
          update_frequency: rankData.update_frequency
        };
      }
    }
    return null;
  }
  
  static getTotalWeight() {
    return this.getAllIndicators().reduce((sum, ind) => sum + ind.weight, 0);
  }
  
  static getSystemStats() {
    const all = this.getAllIndicators();
    return {
      total_indicators: all.length,
      by_rank: {
        S: this.getIndicatorsByRank('S').length,
        A: this.getIndicatorsByRank('A').length, 
        B: this.getIndicatorsByRank('B').length,
        C: this.getIndicatorsByRank('C').length,
        D: this.getIndicatorsByRank('D').length
      },
      total_weight: this.getTotalWeight(),
      critical_count: this.getCriticalIndicators().length,
      optional_count: this.getOptionalIndicators().length
    };
  }
}

// 🎨 VISUAL HELPERS
export const RANK_COLORS = {
  S: '#dc2626', // Red - Critical
  A: '#ea580c', // Orange-red - High
  B: '#f59e0b', // Amber - Medium  
  C: '#3b82f6', // Blue - Low
  D: '#6b7280'  // Gray - Optional
};

export const TIER_DESCRIPTIONS = {
  1: '🔥 Critical - Load immediately',
  2: '⚡ High - Load after 2s delay',
  3: '📊 Medium - Load after 5s delay', 
  4: '🔍 Low - Load after 10s delay',
  5: '📈 Optional - Load only if system healthy'
};

export default IndicatorManager;