import React, { useState, useRef, useEffect } from 'react';
import { View, Text, ScrollView, Pressable, Animated, Dimensions, TextInput } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface Alert {
  id: string;
  title: string;
  message: string;
  type: 'portfolio' | 'market' | 'risk' | 'opportunity' | 'system';
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  status: 'Active' | 'Triggered' | 'Resolved' | 'Dismissed';
  timestamp: Date;
  symbol?: string;
  threshold?: string;
  currentValue?: string;
  actionRequired: boolean;
  aiInsight?: string;
}

const mockAlerts: Alert[] = [
  {
    id: '1',
    title: 'Portfolio Risk Alert',
    message: 'Your portfolio volatility has increased by 15% in the last 24 hours',
    type: 'risk',
    priority: 'High',
    status: 'Active',
    timestamp: new Date(Date.now() - 300000),
    actionRequired: true,
    aiInsight: 'Consider rebalancing your portfolio to reduce risk exposure',
  },
  {
    id: '2',
    title: 'Market Opportunity',
    message: 'BTC showing strong bullish signals based on technical analysis',
    type: 'opportunity',
    priority: 'Medium',
    status: 'Active',
    timestamp: new Date(Date.now() - 900000),
    symbol: 'BTC/USDT',
    actionRequired: false,
    aiInsight: 'RSI indicates oversold conditions, potential reversal ahead',
  },
  {
    id: '3',
    title: 'Portfolio Performance',
    message: 'Your portfolio has outperformed BTC by 8.5% this week',
    type: 'portfolio',
    priority: 'Low',
    status: 'Active',
    timestamp: new Date(Date.now() - 1800000),
    actionRequired: false,
    aiInsight: 'Your diversification strategy is working well',
  },
  {
    id: '4',
    title: 'System Maintenance',
    message: 'Scheduled maintenance in 2 hours - some features may be unavailable',
    type: 'system',
    priority: 'Medium',
    status: 'Active',
    timestamp: new Date(Date.now() - 3600000),
    actionRequired: false,
  },
];

const AlertCard: React.FC<{ alert: Alert; index: number }> = ({ alert, index }) => {
  const slideAnim = useRef(new Animated.Value(width)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        delay: index * 100,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 100,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, [slideAnim, scaleAnim, index]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical': return '#FF6B6B';
      case 'High': return '#FF8E53';
      case 'Medium': return '#FFD93D';
      case 'Low': return '#6BCF7F';
      default: return '#848E9C';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'portfolio': return 'pie-chart';
      case 'market': return 'trending-up';
      case 'risk': return 'warning';
      case 'opportunity': return 'bulb';
      case 'system': return 'settings';
      default: return 'notifications';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return '#00C896';
      case 'Triggered': return '#FF6B6B';
      case 'Resolved': return '#6BCF7F';
      case 'Dismissed': return '#848E9C';
      default: return '#848E9C';
    }
  };

  return (
    <Animated.View
      style={{
        transform: [
          { translateX: slideAnim },
          { scale: scaleAnim },
        ],
      }}
      className="mb-4"
    >
      <LinearGradient
        colors={['#1E2026', '#2A2D35']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        className="rounded-lg p-4 border border-binance-border"
      >
        <View className="flex-row items-start justify-between mb-3">
          <View className="flex-row items-center flex-1">
            <View 
              className="w-10 h-10 rounded-full items-center justify-center mr-3"
              style={{ backgroundColor: getPriorityColor(alert.priority) + '20' }}
            >
              <Ionicons 
                name={getTypeIcon(alert.type) as any} 
                size={20} 
                color={getPriorityColor(alert.priority)} 
              />
            </View>
            <View className="flex-1">
              <Text className="text-binance-text-primary font-semibold text-base mb-1">
                {alert.title}
              </Text>
              <Text className="text-binance-text-secondary text-sm">
                {alert.message}
              </Text>
            </View>
          </View>
          <View className="items-end">
            <View 
              className="px-2 py-1 rounded-full mb-2"
              style={{ backgroundColor: getStatusColor(alert.status) + '20' }}
            >
              <Text 
                className="text-xs font-medium"
                style={{ color: getStatusColor(alert.status) }}
              >
                {alert.status}
              </Text>
            </View>
            <Text className="text-binance-text-tertiary text-xs">
              {alert.timestamp.toLocaleTimeString()}
            </Text>
          </View>
        </View>

        {alert.symbol && (
          <View className="flex-row items-center mb-3">
            <Ionicons name="pricetag" size={16} color="#848E9C" />
            <Text className="text-binance-text-secondary text-sm ml-2">
              {alert.symbol}
            </Text>
          </View>
        )}

        {alert.aiInsight && (
          <View className="bg-binance-green/10 border border-binance-green/20 rounded-md p-3 mb-3">
            <View className="flex-row items-center mb-2">
              <Ionicons name="sparkles" size={16} color="#00C896" />
              <Text className="text-binance-green font-medium text-sm ml-2">
                AI Insight
              </Text>
            </View>
            <Text className="text-binance-text-primary text-sm">
              {alert.aiInsight}
            </Text>
          </View>
        )}

        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center">
            <View 
              className="w-2 h-2 rounded-full mr-2"
              style={{ backgroundColor: getPriorityColor(alert.priority) }}
            />
            <Text 
              className="text-xs font-medium"
              style={{ color: getPriorityColor(alert.priority) }}
            >
              {alert.priority} Priority
            </Text>
          </View>
          
          <View className="flex-row">
            {alert.actionRequired && (
              <Pressable className="bg-binance-green px-3 py-2 rounded-md mr-2">
                <Text className="text-white text-xs font-medium">Take Action</Text>
              </Pressable>
            )}
            <Pressable className="bg-binance-bg-tertiary px-3 py-2 rounded-md">
              <Text className="text-binance-text-secondary text-xs">Dismiss</Text>
            </Pressable>
          </View>
        </View>
      </LinearGradient>
    </Animated.View>
  );
};

const AlertsScreen = () => {
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim]);

  const filters = ['All', 'Portfolio', 'Market', 'Risk', 'Opportunity', 'System'];
  
  const filteredAlerts = mockAlerts.filter(alert => {
    const matchesFilter = activeFilter === 'All' || alert.type === activeFilter.toLowerCase();
    const matchesSearch = alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         alert.message.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getAlertStats = () => {
    const total = mockAlerts.length;
    const active = mockAlerts.filter(a => a.status === 'Active').length;
    const critical = mockAlerts.filter(a => a.priority === 'Critical').length;
    const high = mockAlerts.filter(a => a.priority === 'High').length;
    
    return { total, active, critical, high };
  };

  const stats = getAlertStats();

  return (
    <View className="flex-1 bg-binance-bg-primary">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="px-4 py-6 bg-binance-bg-secondary border-b border-binance-border">
          <Text className="text-binance-text-primary text-2xl font-bold mb-2">
            Alerts & Notifications
          </Text>
          <Text className="text-binance-text-secondary text-base">
            Stay informed with AI-powered insights and portfolio alerts
          </Text>
        </View>

        {/* Stats Cards */}
        <View className="px-4 py-4">
          <View className="flex-row space-x-3">
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Total Alerts</Text>
              <Text className="text-binance-text-primary text-2xl font-bold">{stats.total}</Text>
            </View>
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Active</Text>
              <Text className="text-binance-text-primary text-2xl font-bold">{stats.active}</Text>
            </View>
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Critical</Text>
              <Text className="text-red-400 text-2xl font-bold">{stats.critical}</Text>
            </View>
          </View>
        </View>

        {/* Search */}
        <View className="px-4 py-3 border-b border-binance-border">
          <View className="bg-binance-bg-secondary rounded-lg px-3 py-2 flex-row items-center">
            <Ionicons name="search" size={20} color="#848E9C" />
            <TextInput
              className="flex-1 text-binance-text-primary ml-2 text-base"
              placeholder="Search alerts..."
              placeholderTextColor="#848E9C"
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>
        </View>

        {/* Filters */}
        <View className="px-4 py-3 border-b border-binance-border">
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View className="flex-row space-x-2">
              {filters.map(filter => (
                <Pressable
                  key={filter}
                  onPress={() => setActiveFilter(filter)}
                  className={`px-4 py-2 rounded-full border ${
                    activeFilter === filter 
                      ? 'bg-binance-green border-binance-green' 
                      : 'border-binance-border'
                  }`}
                >
                  <Text className={`text-sm font-medium ${
                    activeFilter === filter 
                      ? 'text-white' 
                      : 'text-binance-text-secondary'
                  }`}>
                    {filter}
                  </Text>
                </Pressable>
              ))}
            </View>
          </ScrollView>
        </View>

        {/* Alerts List */}
        <View className="px-4 py-4">
          <Animated.View style={{ opacity: fadeAnim }}>
            {filteredAlerts.length > 0 ? (
              filteredAlerts.map((alert, index) => (
                <AlertCard key={alert.id} alert={alert} index={index} />
              ))
            ) : (
              <View className="items-center py-12">
                <Ionicons name="notifications-off" size={64} color="#848E9C" />
                <Text className="text-binance-text-secondary text-lg mt-4">
                  No alerts found
                </Text>
                <Text className="text-binance-text-tertiary text-center mt-2">
                  {searchQuery ? 'Try adjusting your search or filters' : 'You\'re all caught up!'}
                </Text>
              </View>
            )}
          </Animated.View>
        </View>
      </ScrollView>
    </View>
  );
};

export default AlertsScreen;