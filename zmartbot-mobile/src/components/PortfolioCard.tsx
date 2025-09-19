import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface PortfolioCardProps {
  position: {
    symbol: string;
    amount: number;
    value: number;
    profit?: number;
  };
}

export const PortfolioCard: React.FC<PortfolioCardProps> = ({ position }) => {
  const profitPercent = position.profit || 0;
  const isPositive = profitPercent >= 0;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.symbol}>{position.symbol}</Text>
        <Text style={styles.amount}>{position.amount} units</Text>
      </View>

      <Text style={styles.value}>${position.value.toLocaleString()}</Text>

      {position.profit !== undefined && (
        <View style={[styles.profitBadge, isPositive ? styles.positive : styles.negative]}>
          <Text style={styles.profitText}>
            {isPositive ? '↑' : '↓'} {Math.abs(profitPercent).toFixed(2)}%
          </Text>
        </View>
      )}
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
    marginBottom: 8,
  },
  symbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E0F2FE',
  },
  amount: {
    fontSize: 14,
    color: '#94A3B8',
  },
  value: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  profitBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  positive: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.4)',
  },
  negative: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.4)',
  },
  profitText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});