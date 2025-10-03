import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useState } from 'react';
import { RefreshControl, ScrollView, StatusBar, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { MarketDataGrid } from '../src/components/MarketDataCard';
import { PortfolioCard } from '../src/components/PortfolioCard';
import { TradingSignalCard } from '../src/components/TradingSignalCard';
import { Card, CardContent } from '../src/components/ui/Card';

export default function IndexScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 125000,
    totalPnL: 8750,
    totalPnLPercent: 7.5,
    availableBalance: 45000,
    marginUsed: 80000
  });

  const [marketData] = useState([
    {
      symbol: 'BTCUSDT',
      price: 43250.50,
      change24h: 1250.75,
      changePercent24h: 2.98,
      volume24h: 2850000000,
      high24h: 43500.00,
      low24h: 41800.00,
      lastUpdated: new Date().toISOString()
    },
    {
      symbol: 'ETHUSDT',
      price: 2650.25,
      change24h: 85.50,
      changePercent24h: 3.33,
      volume24h: 1850000000,
      high24h: 2680.00,
      low24h: 2550.00,
      lastUpdated: new Date().toISOString()
    },
    {
      symbol: 'BNBUSDT',
      price: 312.75,
      change24h: 12.25,
      changePercent24h: 4.08,
      volume24h: 850000000,
      high24h: 315.00,
      low24h: 300.00,
      lastUpdated: new Date().toISOString()
    }
  ]);

  const [tradingSignals] = useState([
    {
      id: '1',
      symbol: 'BTCUSDT',
      signal: 'BUY' as const,
      confidence: 85,
      price: 43250.50,
      targetPrice: 44500.00,
      stopLoss: 42500.00,
      timeframe: '4H',
      reasoning: 'Strong support at 42.5k, bullish momentum building',
      timestamp: new Date().toISOString()
    },
    {
      id: '2',
      symbol: 'ETHUSDT',
      signal: 'HOLD' as const,
      confidence: 65,
      price: 2650.25,
      targetPrice: 2700.00,
      stopLoss: 2600.00,
      timeframe: '1H',
      reasoning: 'Consolidating above key support, waiting for breakout',
      timestamp: new Date().toISOString()
    }
  ]);

  const onRefresh = async () => {
    setRefreshing(true);
    // Simulate data refresh
    setTimeout(() => setRefreshing(false), 2000);
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0f0f23" />
      
      {/* Header */}
      <LinearGradient
        colors={['#1a1a2e', '#16213e', '#0f3460']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.headerLeft}>
            <Text style={styles.logo}>🚀 ZmartBot</Text>
            <Text style={styles.subtitle}>Professional Trading Platform</Text>
          </View>
          <TouchableOpacity style={styles.notificationButton}>
            <Ionicons name="notifications" size={24} color="#fff" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      <ScrollView 
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Portfolio Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Portfolio Overview</Text>
          <PortfolioCard
            totalValue={portfolioData.totalValue}
            totalPnL={portfolioData.totalPnL}
            totalPnLPercent={portfolioData.totalPnLPercent}
            availableBalance={portfolioData.availableBalance}
            marginUsed={portfolioData.marginUsed}
            onPress={() => console.log('Portfolio pressed')}
          />
        </View>

        {/* Market Data */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Live Market Data</Text>
          <MarketDataGrid data={marketData} />
        </View>

        {/* Trading Signals */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI Trading Signals</Text>
          {tradingSignals.map((signal) => (
            <TradingSignalCard
              key={signal.id}
              signal={signal}
              onPress={() => console.log('Signal pressed:', signal.symbol)}
            />
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity style={styles.actionButton}>
              <LinearGradient
                colors={['#10B981', '#059669']}
                style={styles.actionGradient}
              >
                <Ionicons name="trending-up" size={24} color="#fff" />
                <Text style={styles.actionText}>New Trade</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionButton}>
              <LinearGradient
                colors={['#3B82F6', '#2563EB']}
                style={styles.actionGradient}
              >
                <Ionicons name="analytics" size={24} color="#fff" />
                <Text style={styles.actionText}>Analytics</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionButton}>
              <LinearGradient
                colors={['#8B5CF6', '#7C3AED']}
                style={styles.actionGradient}
              >
                <Ionicons name="settings" size={24} color="#fff" />
                <Text style={styles.actionText}>Settings</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionButton}>
              <LinearGradient
                colors={['#F59E0B', '#D97706']}
                style={styles.actionGradient}
              >
                <Ionicons name="help-circle" size={24} color="#fff" />
                <Text style={styles.actionText}>Support</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>

        {/* System Status */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Status</Text>
          <Card variant="glass" style={styles.statusCard}>
            <CardContent>
              <View style={styles.statusRow}>
                <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                <Text style={styles.statusText}>Mobile Service: Active (Port 7777)</Text>
              </View>
              <View style={styles.statusRow}>
                <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                <Text style={styles.statusText}>ZmartBot API: Connected (Port 8000)</Text>
              </View>
              <View style={styles.statusRow}>
                <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                <Text style={styles.statusText}>IoT Integration: Ready</Text>
              </View>
            </CardContent>
          </Card>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerLeft: {
    flex: 1,
  },
  logo: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#94A3B8',
  },
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 12,
  },
  actionButton: {
    width: '48%',
    height: 80,
    borderRadius: 12,
    overflow: 'hidden',
  },
  actionGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
  },
  statusCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 12,
  },
});