import React, { useState, useRef, useEffect } from 'react';
import { View, Text, ScrollView, Pressable, Animated, Dimensions, TextInput } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface HistoryItem {
  id: string;
  type: 'portfolio_change' | 'ai_analysis' | 'alert_triggered' | 'credit_usage' | 'system_event';
  title: string;
  description: string;
  timestamp: Date;
  impact: 'positive' | 'negative' | 'neutral';
  category: 'portfolio' | 'trading' | 'analysis' | 'system' | 'credits';
  value?: string;
  change?: string;
  metadata?: any;
}

const mockHistory: HistoryItem[] = [
  {
    id: '1',
    type: 'portfolio_change',
    title: 'Portfolio Value Increased',
    description: 'Your portfolio gained 5.2% due to strong BTC performance',
    timestamp: new Date(Date.now() - 3600000),
    impact: 'positive',
    category: 'portfolio',
    value: '$12,450.75',
    change: '+$612.30',
  },
  {
    id: '2',
    type: 'ai_analysis',
    title: 'AI Market Analysis Completed',
    description: 'Advanced technical analysis for ETH/USDT pair completed',
    timestamp: new Date(Date.now() - 7200000),
    impact: 'neutral',
    category: 'analysis',
    value: '25 credits',
    change: '-25',
  },
  {
    id: '3',
    type: 'alert_triggered',
    title: 'Price Alert: BTC Above $43,000',
    description: 'Your price alert for BTC has been triggered',
    timestamp: new Date(Date.now() - 10800000),
    impact: 'positive',
    category: 'trading',
    value: '$43,250',
  },
  {
    id: '4',
    type: 'credit_usage',
    title: 'Credits Purchased',
    description: 'Successfully purchased 500 AI credits',
    timestamp: new Date(Date.now() - 86400000),
    impact: 'positive',
    category: 'credits',
    value: '500 credits',
    change: '+500',
  },
  {
    id: '5',
    type: 'system_event',
    title: 'Portfolio Rebalancing',
    description: 'AI suggested portfolio rebalancing based on market conditions',
    timestamp: new Date(Date.now() - 172800000),
    impact: 'neutral',
    category: 'portfolio',
  },
  {
    id: '6',
    type: 'ai_analysis',
    title: 'Risk Assessment',
    description: 'Portfolio risk level increased from Low to Medium',
    timestamp: new Date(Date.now() - 259200000),
    impact: 'negative',
    category: 'analysis',
    value: 'Medium Risk',
  },
];

const HistoryCard: React.FC<{ item: HistoryItem; index: number }> = ({ item, index }) => {
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'portfolio_change': return 'trending-up';
      case 'ai_analysis': return 'analytics';
      case 'alert_triggered': return 'notifications';
      case 'credit_usage': return 'card';
      case 'system_event': return 'settings';
      default: return 'time';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'portfolio': return '#00C896';
      case 'trading': return '#F0B90B';
      case 'analysis': return '#FF8E53';
      case 'system': return '#848E9C';
      case 'credits': return '#6BCF7F';
      default: return '#848E9C';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'positive': return '#00C896';
      case 'negative': return '#FF6B6B';
      case 'neutral': return '#848E9C';
      default: return '#848E9C';
    }
  };

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diffInMs = now.getTime() - timestamp.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return `${diffInDays}d ago`;
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
      className="mb-3"
    >
      <LinearGradient
        colors={['#1E2026', '#2A2D35']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        className="rounded-lg p-4 border border-binance-border"
      >
        <View className="flex-row items-start justify-between mb-3">
          <View className="flex-row items-start flex-1">
            <View 
              className="w-10 h-10 rounded-full items-center justify-center mr-3 mt-1"
              style={{ backgroundColor: getCategoryColor(item.category) + '20' }}
            >
              <Ionicons 
                name={getTypeIcon(item.type) as any} 
                size={20} 
                color={getCategoryColor(item.category)} 
              />
            </View>
            <View className="flex-1">
              <Text className="text-binance-text-primary font-semibold text-base mb-1">
                {item.title}
              </Text>
              <Text className="text-binance-text-secondary text-sm leading-5">
                {item.description}
              </Text>
            </View>
          </View>
          <View className="items-end">
            <Text className="text-binance-text-tertiary text-xs mb-2">
              {formatTimeAgo(item.timestamp)}
            </Text>
            {item.value && (
              <Text className="text-binance-text-primary text-sm font-medium">
                {item.value}
              </Text>
            )}
          </View>
        </View>

        {item.change && (
          <View className="flex-row items-center justify-between mb-3">
            <View className="flex-row items-center">
              <View 
                className="w-2 h-2 rounded-full mr-2"
                style={{ backgroundColor: getImpactColor(item.impact) }}
              />
              <Text className="text-binance-text-secondary text-xs capitalize">
                {item.category}
              </Text>
            </View>
            <Text 
              className={`text-sm font-bold ${
                item.change.startsWith('+') ? 'text-binance-green' : 'text-red-400'
              }`}
            >
              {item.change}
            </Text>
          </View>
        )}

        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center">
            <View 
              className={`px-2 py-1 rounded-full mr-2 ${
                item.impact === 'positive' ? 'bg-binance-green/20' : 
                item.impact === 'negative' ? 'bg-red-500/20' : 'bg-gray-500/20'
              }`}
            >
              <Text 
                className={`text-xs font-medium capitalize ${
                  item.impact === 'positive' ? 'text-binance-green' : 
                  item.impact === 'negative' ? 'text-red-500' : 'text-gray-400'
                }`}
              >
                {item.impact}
              </Text>
            </View>
          </View>
          
          <View className="flex-row space-x-2">
            <Pressable className="bg-binance-bg-tertiary px-3 py-2 rounded-md">
              <Text className="text-binance-text-secondary text-xs">Details</Text>
            </Pressable>
            <Pressable className="bg-binance-bg-tertiary px-3 py-2 rounded-md">
              <Text className="text-binance-text-secondary text-xs">Share</Text>
            </Pressable>
          </View>
        </View>
      </LinearGradient>
    </Animated.View>
  );
};

const HistoryScreen = () => {
  const [activeFilter, setActiveFilter] = useState('All');
  const [timeRange, setTimeRange] = useState('24h');
  const [searchQuery, setSearchQuery] = useState('');
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim]);

  const filters = ['All', 'Portfolio', 'Trading', 'Analysis', 'System', 'Credits'];
  const timeRanges = ['1h', '24h', '7d', '30d', 'All'];
  
  const filteredHistory = mockHistory.filter(item => {
    const matchesFilter = activeFilter === 'All' || item.category === activeFilter.toLowerCase();
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getHistoryStats = () => {
    const total = mockHistory.length;
    const positive = mockHistory.filter(item => item.impact === 'positive').length;
    const negative = mockHistory.filter(item => item.impact === 'negative').length;
    const neutral = mockHistory.filter(item => item.impact === 'neutral').length;
    
    return { total, positive, negative, neutral };
  };

  const stats = getHistoryStats();

  return (
    <View className="flex-1 bg-binance-bg-primary">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="px-4 py-6 bg-binance-bg-secondary border-b border-binance-border">
          <Text className="text-binance-text-primary text-2xl font-bold mb-2">
            Activity History
          </Text>
          <Text className="text-binance-text-secondary text-base">
            Track your portfolio performance and AI interactions
          </Text>
        </View>

        {/* Stats Cards */}
        <View className="px-4 py-4">
          <View className="flex-row space-x-3">
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Total Activities</Text>
              <Text className="text-binance-text-primary text-2xl font-bold">{stats.total}</Text>
            </View>
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Positive</Text>
              <Text className="text-binance-green text-2xl font-bold">{stats.positive}</Text>
            </View>
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Neutral</Text>
              <Text className="text-binance-text-primary text-2xl font-bold">{stats.neutral}</Text>
            </View>
          </View>
        </View>

        {/* Search and Filters */}
        <View className="px-4 py-3 border-b border-binance-border">
          <View className="bg-binance-bg-secondary rounded-lg px-3 py-2 flex-row items-center mb-3">
            <Ionicons name="search" size={20} color="#848E9C" />
            <TextInput
              className="flex-1 text-binance-text-primary ml-2 text-base"
              placeholder="Search activities..."
              placeholderTextColor="#848E9C"
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>

          {/* Time Range */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} className="mb-3">
            <View className="flex-row space-x-2">
              {timeRanges.map(range => (
                <Pressable
                  key={range}
                  onPress={() => setTimeRange(range)}
                  className={`px-3 py-2 rounded-full border ${
                    timeRange === range 
                      ? 'bg-binance-green border-binance-green' 
                      : 'border-binance-border'
                  }`}
                >
                  <Text className={`text-xs font-medium ${
                    timeRange === range 
                      ? 'text-white' 
                      : 'text-binance-text-secondary'
                  }`}>
                    {range}
                  </Text>
                </Pressable>
              ))}
            </View>
          </ScrollView>

          {/* Category Filters */}
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

        {/* History List */}
        <View className="px-4 py-4">
          <Animated.View style={{ opacity: fadeAnim }}>
            {filteredHistory.length > 0 ? (
              filteredHistory.map((item, index) => (
                <HistoryCard key={item.id} item={item} index={index} />
              ))
            ) : (
              <View className="items-center py-12">
                <Ionicons name="time-outline" size={64} color="#848E9C" />
                <Text className="text-binance-text-secondary text-lg mt-4">
                  No activities found
                </Text>
                <Text className="text-binance-text-tertiary text-center mt-2">
                  {searchQuery ? 'Try adjusting your search or filters' : 'Your activity history will appear here'}
                </Text>
              </View>
            )}
          </Animated.View>
        </View>

        {/* AI Insights */}
        <View className="px-4 py-4">
          <View className="bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
            <View className="flex-row items-center mb-3">
              <Ionicons name="sparkles" size={20} color="#00C896" />
              <Text className="text-binance-green font-semibold text-lg ml-2">
                AI Insights
              </Text>
            </View>
            <Text className="text-binance-text-primary text-sm leading-6 mb-3">
              Based on your activity patterns, you're most active during market hours (9 AM - 5 PM EST). 
              Consider setting up automated alerts for better portfolio monitoring.
            </Text>
            <View className="flex-row space-x-2">
              <Pressable className="bg-binance-green px-4 py-2 rounded-md">
                <Text className="text-white text-sm font-medium">Set Alerts</Text>
              </Pressable>
              <Pressable className="bg-binance-bg-tertiary px-4 py-2 rounded-md">
                <Text className="text-binance-text-secondary text-sm">Learn More</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

export default HistoryScreen;