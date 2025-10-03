import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface TradingSignalCardProps {
  signal: {
    id: string;
    symbol: string;
    signal: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    price: number;
    targetPrice?: number;
    stopLoss?: number;
    reasoning?: string;
    timestamp: string;
  };
  onPress?: () => void;
}

export const TradingSignalCard: React.FC<TradingSignalCardProps> = ({ signal, onPress }) => {
  const signalColor = signal.signal === 'BUY' ? '#10B981' : signal.signal === 'SELL' ? '#EF4444' : '#6B7280';

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.symbol}>{signal.symbol}</Text>
        <View style={[styles.signalBadge, { backgroundColor: signalColor }]}>
          <Text style={styles.signalText}>{signal.signal}</Text>
        </View>
      </View>

      <View style={styles.details}>
        <View style={styles.detailRow}>
          <Text style={styles.label}>Confidence:</Text>
          <Text style={styles.value}>{(signal.confidence * 100).toFixed(0)}%</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.label}>Price:</Text>
          <Text style={styles.value}>${signal.price.toLocaleString()}</Text>
        </View>
        {signal.targetPrice && (
          <View style={styles.detailRow}>
            <Text style={styles.label}>Target:</Text>
            <Text style={styles.value}>${signal.targetPrice.toLocaleString()}</Text>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(30, 41, 59, 0.8)',
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(71, 85, 105, 0.3)',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  symbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E0F2FE',
  },
  signalBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  signalText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  details: {
    gap: 8,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  label: {
    fontSize: 14,
    color: '#94A3B8',
  },
  value: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
