import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import Chat from '../assistant/screens/Chat';
import { TradingPanel } from '../components/TradingPanel';
import { MarketDataCard } from '../components/MarketDataCard';
import { PortfolioCard } from '../components/PortfolioCard';
import { SignalAnalysisDashboard } from '../components/SignalAnalysisDashboard';

type Tab = 'chat' | 'trade' | 'market' | 'portfolio' | 'signals';

export default function MainApp() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  const mockSignals = [
    {
      id: '1',
      timestamp: new Date(),
      symbol: 'ETH',
      type: 'BUY' as const,
      strength: 4,
      confidence: 87,
      price: 3456.78,
      target: 3812.45,
      stopLoss: 3234.56,
      riskReward: 2.3,
      source: 'AI' as const
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 3600000),
      symbol: 'BTC',
      type: 'HOLD' as const,
      strength: 3,
      confidence: 72,
      price: 67890.12,
      target: 72000,
      stopLoss: 65000,
      riskReward: 1.8,
      source: 'Technical' as const
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <Chat />;

      case 'trade':
        return (
          <View style={styles.contentContainer}>
            <TradingPanel
              symbol="ETH/USDT"
              currentPrice={3456.78}
              onPlaceOrder={(order) => console.log('Order placed:', order)}
            />
          </View>
        );

      case 'market':
        return (
          <View style={styles.contentContainer}>
            <Text style={styles.sectionTitle}>Market Overview</Text>
            <MarketDataCard
              symbol="ETH/USDT"
              price={3456.78}
              change={156.32}
              changePercent={5.23}
              volume="234.5M"
            />
            <MarketDataCard
              symbol="BTC/USDT"
              price={67890.12}
              change={-890.45}
              changePercent={-1.29}
              volume="1.2B"
            />
            <MarketDataCard
              symbol="SOL/USDT"
              price={145.67}
              change={12.34}
              changePercent={9.25}
              volume="89.3M"
            />
          </View>
        );

      case 'portfolio':
        return (
          <View style={styles.contentContainer}>
            <Text style={styles.sectionTitle}>Your Portfolio</Text>
            <View style={styles.portfolioSummary}>
              <Text style={styles.totalLabel}>Total Value</Text>
              <Text style={styles.totalValue}>$45,678.90</Text>
              <Text style={styles.totalChange}>+$2,345.67 (+5.42%)</Text>
            </View>
            <PortfolioCard
              position={{
                symbol: 'BTC',
                amount: 0.5,
                value: 33945.06,
                profit: 12.5
              }}
            />
            <PortfolioCard
              position={{
                symbol: 'ETH',
                amount: 3.2,
                value: 11061.70,
                profit: -2.3
              }}
            />
          </View>
        );

      case 'signals':
        return <SignalAnalysisDashboard signals={mockSignals} />;

      default:
        return null;
    }
  };

  const TabButton = ({
    tab,
    icon,
    label
  }: {
    tab: Tab;
    icon: string;
    label: string;
  }) => (
    <Pressable
      style={[styles.tabButton, activeTab === tab && styles.activeTab]}
      onPress={() => setActiveTab(tab)}
    >
      <Text style={[styles.tabIcon, activeTab === tab && styles.activeTabText]}>
        {icon}
      </Text>
      <Text style={[styles.tabLabel, activeTab === tab && styles.activeTabText]}>
        {label}
      </Text>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>ZmartyChat</Text>
        <View style={styles.headerRight}>
          <Text style={styles.credits}>100 Credits</Text>
          <Pressable style={styles.profileButton}>
            <Text style={styles.profileIcon}>👤</Text>
          </Pressable>
        </View>
      </View>

      <View style={styles.content}>
        {renderContent()}
      </View>

      <View style={styles.tabBar}>
        <TabButton tab="chat" icon="💬" label="Chat" />
        <TabButton tab="trade" icon="📊" label="Trade" />
        <TabButton tab="market" icon="📈" label="Market" />
        <TabButton tab="portfolio" icon="💼" label="Portfolio" />
        <TabButton tab="signals" icon="🎯" label="Signals" />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E1B',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 16,
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 255, 204, 0.1)',
  },
  logo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00FFCC',
    letterSpacing: 1,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  credits: {
    fontSize: 14,
    color: '#94A3B8',
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 204, 0.2)',
  },
  profileButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(71, 85, 105, 0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  profileIcon: {
    fontSize: 20,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E0F2FE',
    marginBottom: 20,
  },
  portfolioSummary: {
    backgroundColor: 'rgba(14, 165, 233, 0.1)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 204, 0.2)',
    alignItems: 'center',
  },
  totalLabel: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 8,
  },
  totalValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  totalChange: {
    fontSize: 16,
    color: '#10B981',
    fontWeight: '600',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(71, 85, 105, 0.3)',
    paddingBottom: 20,
    paddingTop: 8,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeTab: {
    borderTopWidth: 2,
    borderTopColor: '#00FFCC',
    marginTop: -1,
  },
  tabIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 11,
    color: '#64748B',
  },
  activeTabText: {
    color: '#00FFCC',
  },
});