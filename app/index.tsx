import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { Card, CardContent, CardHeader } from '../src/components/ui/Card';
import { PortfolioCard } from '../src/components/PortfolioCard';

export default function IndexScreen() {
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
            <Text style={styles.subtitle}>Professional Trading Assistant</Text>
          </View>
          <TouchableOpacity style={styles.notificationButton}>
            <Ionicons name="notifications" size={24} color="#fff" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Main Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        
        {/* Portfolio Summary Card */}
        <Card variant="elevated" style={styles.portfolioCard}>
          <CardHeader>
            <Text style={styles.cardTitle}>Portfolio Overview</Text>
            <TouchableOpacity>
              <Ionicons name="refresh" size={20} color="#10B981" />
            </TouchableOpacity>
          </CardHeader>
          <CardContent>
            <PortfolioCard
              totalValue={125000}
              totalPnL={8750}
              totalPnLPercent={7.5}
              availableBalance={45000}
              marginUsed={80000}
            />
          </CardContent>
        </Card>

        {/* Market Data Section */}
        <Card variant="elevated" style={styles.marketCard}>
          <CardHeader>
            <Text style={styles.cardTitle}>Live Markets</Text>
            <TouchableOpacity>
              <Ionicons name="trending-up" size={20} color="#10B981" />
            </TouchableOpacity>
          </CardHeader>
          <CardContent>
            <View style={styles.marketGrid}>
              {[
                { symbol: 'BTC/USDT', price: '43,250', change: '+2.45%', volume: '2.1B' },
                { symbol: 'ETH/USDT', price: '2,680', change: '+1.87%', volume: '1.8B' },
                { symbol: 'BNB/USDT', price: '312', change: '+3.12%', volume: '890M' },
                { symbol: 'ADA/USDT', price: '0.48', change: '-0.85%', volume: '450M' }
              ].map((market, index) => (
                <TouchableOpacity key={index} style={styles.marketItem}>
                  <View style={styles.marketItemHeader}>
                    <Text style={styles.marketSymbol}>{market.symbol}</Text>
                    <Text style={[styles.marketChange, { color: market.change.startsWith('+') ? '#10B981' : '#EF4444' }]}>
                      {market.change}
                    </Text>
                  </View>
                  <Text style={styles.marketPrice}>${market.price}</Text>
                  <Text style={styles.marketVolume}>Vol: {market.volume}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </CardContent>
        </Card>

        {/* Trading Signals */}
        <Card variant="elevated" style={styles.signalsCard}>
          <CardHeader>
            <Text style={styles.cardTitle}>AI Trading Signals</Text>
            <TouchableOpacity>
              <Ionicons name="flash" size={20} color="#F59E0B" />
            </TouchableOpacity>
          </CardHeader>
          <CardContent>
            <View style={styles.signalsList}>
              {[
                { symbol: 'BTC/USDT', signal: 'BUY', confidence: 95, price: '43,250', target: '45,000' },
                { symbol: 'ETH/USDT', signal: 'HOLD', confidence: 78, price: '2,680', target: '2,750' },
                { symbol: 'BNB/USDT', signal: 'SELL', confidence: 82, price: '312', target: '298' }
              ].map((signal, index) => (
                <View key={index} style={styles.signalItem}>
                  <View style={styles.signalHeader}>
                    <Text style={styles.signalSymbol}>{signal.symbol}</Text>
                    <View style={[styles.signalBadge, { backgroundColor: signal.signal === 'BUY' ? '#10B981' : signal.signal === 'SELL' ? '#EF4444' : '#F59E0B' }]}>
                      <Text style={styles.signalText}>{signal.signal}</Text>
                    </View>
                  </View>
                  <View style={styles.signalDetails}>
                    <Text style={styles.signalPrice}>${signal.price}</Text>
                    <Text style={styles.signalTarget}>Target: ${signal.target}</Text>
                    <Text style={styles.signalConfidence}>{signal.confidence}% Confidence</Text>
                  </View>
                </View>
              ))}
            </View>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card variant="elevated" style={styles.actionsCard}>
          <CardHeader>
            <Text style={styles.cardTitle}>Quick Actions</Text>
          </CardHeader>
          <CardContent>
            <View style={styles.actionsGrid}>
              <TouchableOpacity style={styles.actionButton}>
                <LinearGradient colors={['#10B981', '#059669']} style={styles.actionGradient}>
                  <Ionicons name="add-circle" size={32} color="#fff" />
                  <Text style={styles.actionText}>New Trade</Text>
                </LinearGradient>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.actionButton}>
                <LinearGradient colors={['#3B82F6', '#2563EB']} style={styles.actionGradient}>
                  <Ionicons name="analytics" size={32} color="#fff" />
                  <Text style={styles.actionText}>Analytics</Text>
                </LinearGradient>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.actionButton}>
                <LinearGradient colors={['#8B5CF6', '#7C3AED']} style={styles.actionGradient}>
                  <Ionicons name="settings" size={32} color="#fff" />
                  <Text style={styles.actionText}>Settings</Text>
                </LinearGradient>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.actionButton}>
                <LinearGradient colors={['#F59E0B', '#D97706']} style={styles.actionGradient}>
                  <Ionicons name="help-circle" size={32} color="#fff" />
                  <Text style={styles.actionText}>Support</Text>
                </LinearGradient>
              </TouchableOpacity>
            </View>
          </CardContent>
        </Card>
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
    paddingTop: 60,
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
    color: '#9CA3AF',
  },
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  portfolioCard: {
    marginTop: 20,
    marginBottom: 16,
  },
  marketCard: {
    marginBottom: 16,
  },
  signalsCard: {
    marginBottom: 16,
  },
  actionsCard: {
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  marketGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  marketItem: {
    width: '48%',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  marketItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  marketSymbol: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  marketChange: {
    fontSize: 14,
    fontWeight: '500',
  },
  marketPrice: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  marketVolume: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  signalsList: {
    gap: 16,
  },
  signalItem: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
  },
  signalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  signalSymbol: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  signalBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  signalText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#fff',
  },
  signalDetails: {
    gap: 4,
  },
  signalPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  signalTarget: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  signalConfidence: {
    fontSize: 12,
    color: '#10B981',
    fontWeight: '500',
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 12,
  },
  actionButton: {
    width: '48%',
    borderRadius: 16,
    overflow: 'hidden',
  },
  actionGradient: {
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 100,
  },
  actionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
  },
});
