import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface MarketDataCardProps {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: string;
}

export const MarketDataCard: React.FC<MarketDataCardProps> = ({
  symbol,
  price,
  change,
  changePercent,
  volume
}) => {
  const isPositive = change >= 0;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.symbol}>{symbol}</Text>
        <View style={[styles.changeBadge, isPositive ? styles.positive : styles.negative]}>
          <Text style={styles.changeText}>
            {isPositive ? '↑' : '↓'} {Math.abs(changePercent).toFixed(2)}%
          </Text>
        </View>
      </View>

      <Text style={styles.price}>${price.toLocaleString()}</Text>

      <View style={styles.footer}>
        <Text style={[styles.change, isPositive ? styles.positiveText : styles.negativeText]}>
          {isPositive ? '+' : ''}{change.toFixed(2)}
        </Text>
        {volume && (
          <Text style={styles.volume}>Vol: {volume}</Text>
        )}
      </View>
    </View>
  );
};

interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  lastUpdated: string;
}

interface MarketDataGridProps {
  data: MarketData[];
}

export const MarketDataGrid: React.FC<MarketDataGridProps> = ({ data }) => {
  return (
    <View style={styles.grid}>
      {data.map((item, index) => (
        <MarketDataCard
          key={index}
          symbol={item.symbol}
          price={item.price}
          change={item.change24h}
          changePercent={item.changePercent24h}
          volume={item.volume24h.toLocaleString()}
        />
      ))}
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  symbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E0F2FE',
    letterSpacing: 0.5,
  },
  price: {
    fontSize: 28,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  changeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
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
  changeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  change: {
    fontSize: 14,
    fontWeight: '500',
  },
  positiveText: {
    color: '#10B981',
  },
  negativeText: {
    color: '#EF4444',
  },
  volume: {
    fontSize: 12,
    color: '#94A3B8',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
  },
});