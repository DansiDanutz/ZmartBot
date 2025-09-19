import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface Signal {
  id: string;
  timestamp: Date;
  symbol: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  strength: number;
  confidence: number;
  price: number;
  target: number;
  stopLoss: number;
  riskReward: number;
  source: 'AI' | 'Technical' | 'Fundamental' | 'Mixed';
}

interface SignalAnalysisDashboardProps {
  signals: Signal[];
  onSignalSelect?: (signal: Signal) => void;
}

export const SignalAnalysisDashboard: React.FC<SignalAnalysisDashboardProps> = ({
  signals,
  onSignalSelect
}) => {
  const getSignalColor = (type: Signal['type']) => {
    switch (type) {
      case 'BUY': return '#10B981';
      case 'SELL': return '#EF4444';
      case 'HOLD': return '#F59E0B';
    }
  };

  const getStrengthBars = (strength: number) => {
    const bars = [];
    for (let i = 1; i <= 5; i++) {
      bars.push(
        <View
          key={i}
          style={[
            styles.strengthBar,
            { opacity: i <= strength ? 1 : 0.3 }
          ]}
        />
      );
    }
    return bars;
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>Signal Analysis</Text>
        <Text style={styles.subtitle}>AI-Powered Trading Signals</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{signals.length}</Text>
          <Text style={styles.statLabel}>Active Signals</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {signals.filter(s => s.type === 'BUY').length}
          </Text>
          <Text style={styles.statLabel}>Buy Signals</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {Math.round(signals.reduce((acc, s) => acc + s.confidence, 0) / signals.length)}%
          </Text>
          <Text style={styles.statLabel}>Avg Confidence</Text>
        </View>
      </View>

      {signals.map((signal) => (
        <View key={signal.id} style={styles.signalCard}>
          <View style={styles.signalHeader}>
            <View style={styles.signalSymbol}>
              <Text style={styles.symbolText}>{signal.symbol}</Text>
              <View
                style={[
                  styles.typeBadge,
                  { backgroundColor: getSignalColor(signal.type) }
                ]}
              >
                <Text style={styles.typeText}>{signal.type}</Text>
              </View>
            </View>
            <View style={styles.signalMeta}>
              <Text style={styles.sourceText}>{signal.source}</Text>
              <Text style={styles.timeText}>
                {new Date(signal.timestamp).toLocaleTimeString()}
              </Text>
            </View>
          </View>

          <View style={styles.signalBody}>
            <View style={styles.priceInfo}>
              <View style={styles.priceRow}>
                <Text style={styles.priceLabel}>Entry</Text>
                <Text style={styles.priceValue}>${signal.price.toFixed(2)}</Text>
              </View>
              <View style={styles.priceRow}>
                <Text style={styles.priceLabel}>Target</Text>
                <Text style={[styles.priceValue, styles.targetPrice]}>
                  ${signal.target.toFixed(2)}
                </Text>
              </View>
              <View style={styles.priceRow}>
                <Text style={styles.priceLabel}>Stop Loss</Text>
                <Text style={[styles.priceValue, styles.stopLossPrice]}>
                  ${signal.stopLoss.toFixed(2)}
                </Text>
              </View>
            </View>

            <View style={styles.metricsContainer}>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Strength</Text>
                <View style={styles.strengthBars}>
                  {getStrengthBars(signal.strength)}
                </View>
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Confidence</Text>
                <View style={styles.confidenceBar}>
                  <View
                    style={[
                      styles.confidenceFill,
                      { width: `${signal.confidence}%` }
                    ]}
                  />
                </View>
                <Text style={styles.confidenceText}>{signal.confidence}%</Text>
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Risk/Reward</Text>
                <Text style={styles.riskRewardValue}>1:{signal.riskReward.toFixed(1)}</Text>
              </View>
            </View>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E1B',
  },
  header: {
    padding: 20,
    paddingBottom: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#E0F2FE',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#94A3B8',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 12,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'rgba(30, 41, 59, 0.8)',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(71, 85, 105, 0.3)',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00FFCC',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 11,
    color: '#94A3B8',
    textTransform: 'uppercase',
  },
  signalCard: {
    marginHorizontal: 20,
    marginBottom: 16,
    backgroundColor: 'rgba(30, 41, 59, 0.95)',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(71, 85, 105, 0.3)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 6,
  },
  signalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  signalSymbol: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  symbolText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  typeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  typeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  signalMeta: {
    alignItems: 'flex-end',
  },
  sourceText: {
    fontSize: 12,
    color: '#00FFCC',
    marginBottom: 2,
  },
  timeText: {
    fontSize: 11,
    color: '#64748B',
  },
  signalBody: {
    gap: 16,
  },
  priceInfo: {
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    borderRadius: 12,
    padding: 12,
    gap: 8,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 13,
    color: '#94A3B8',
  },
  priceValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  targetPrice: {
    color: '#10B981',
  },
  stopLossPrice: {
    color: '#EF4444',
  },
  metricsContainer: {
    gap: 12,
  },
  metric: {
    gap: 4,
  },
  metricLabel: {
    fontSize: 11,
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  strengthBars: {
    flexDirection: 'row',
    gap: 4,
  },
  strengthBar: {
    width: 20,
    height: 8,
    backgroundColor: '#00FFCC',
    borderRadius: 4,
  },
  confidenceBar: {
    height: 8,
    backgroundColor: 'rgba(71, 85, 105, 0.3)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#0EA5E9',
    borderRadius: 4,
  },
  confidenceText: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 2,
  },
  riskRewardValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F59E0B',
  },
});