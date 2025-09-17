import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, RefreshControl, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { Card, CardContent, CardHeader } from '../../src/components/ui/Card';
import { MarketDataCard, MarketDataGrid } from '../../src/components/MarketDataCard';
import { mobileTradingService } from '../../src/services/MobileTradingService';
import { MarketData } from '../../src/services/ZmartBotAPIGateway';

export default function MarketsScreen() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');

  // Initialize connection to ZmartBot ecosystem
  useEffect(() => {
    initializeZmartBotConnection();
  }, []);

  const initializeZmartBotConnection = async () => {
    try {
      setIsLoading(true);
      const isConnected = await mobileTradingService.testConnection();
      setIsConnected(isConnected);
      
      if (isConnected) {
        await loadMarketData();
      } else {
        Alert.alert(
          'Connection Failed',
          'Unable to connect to ZmartBot ecosystem. Please check your connection and try again.',
          [{ text: 'Retry', onPress: initializeZmartBotConnection }]
        );
      }
    } catch (error) {
      console.error('Connection error:', error);
      Alert.alert('Error', 'Failed to connect to ZmartBot ecosystem');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMarketData = async () => {
    try {
      const data = await mobileTradingService.getMarketData();
      setMarketData(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load market data:', error);
      Alert.alert('Error', 'Failed to load market data');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadMarketData();
    setRefreshing(false);
  };

  const filteredData = marketData.filter(item =>
    item.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const topGainers = filteredData
    .filter(item => parseFloat(item.priceChangePercent) > 0)
    .sort((a, b) => parseFloat(b.priceChangePercent) - parseFloat(a.priceChangePercent))
    .slice(0, 5);

  const topLosers = filteredData
    .filter(item => parseFloat(item.priceChangePercent) < 0)
    .sort((a, b) => parseFloat(a.priceChangePercent) - parseFloat(b.priceChangePercent))
    .slice(0, 5);

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-gray-950">
        <StatusBar style="light" />
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#3B82F6" />
          <Text className="text-white text-lg mt-4">Connecting to ZmartBot...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-gray-950">
      <StatusBar style="light" />
      
      {/* Header */}
      <View className="px-4 py-4 border-b border-gray-800">
        <View className="flex-row items-center justify-between mb-4">
          <View>
            <Text className="text-white text-2xl font-bold">Markets</Text>
            <Text className="text-gray-400 text-sm">
              {isConnected ? 'Connected to ZmartBot' : 'Disconnected'}
            </Text>
          </View>
          
          <View className="flex-row items-center space-x-2">
            <View className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <Text className="text-gray-400 text-sm">
              {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Never'}
            </Text>
          </View>
        </View>

        {/* Search Bar */}
        <View className="bg-gray-900 rounded-xl p-3 flex-row items-center space-x-3">
          <Ionicons name="search" size={20} color="#6B7280" />
          <Text className="text-white flex-1 text-base">
            Search markets...
          </Text>
        </View>
      </View>

      <ScrollView 
        className="flex-1 px-4"
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#3B82F6"
            colors={['#3B82F6']}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Connection Status Card */}
        {!isConnected && (
          <Card variant="outlined" className="mb-4 border-red-500">
            <CardContent>
              <View className="flex-row items-center space-x-3">
                <Ionicons name="warning" size={24} color="#EF4444" />
                <View className="flex-1">
                  <Text className="text-red-400 font-semibold text-lg">Connection Lost</Text>
                  <Text className="text-gray-400 text-sm">
                    Unable to connect to ZmartBot ecosystem. Please check your connection.
                  </Text>
                </View>
              </View>
            </CardContent>
          </Card>
        )}

        {/* Market Overview */}
        <Card variant="elevated" className="mb-6">
          <CardHeader>
            <View className="flex-row items-center space-x-3">
              <View className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 items-center justify-center">
                <Ionicons name="trending-up" size={20} color="white" />
              </View>
              <View>
                <Text className="text-white font-bold text-xl">Market Overview</Text>
                <Text className="text-gray-400 text-sm">
                  {filteredData.length} markets • Real-time data
                </Text>
              </View>
            </View>
          </CardHeader>
          
          <CardContent>
            <View className="flex-row space-x-4">
              <View className="flex-1 bg-gray-800/50 rounded-xl p-4">
                <Text className="text-gray-400 text-sm mb-1">Total Markets</Text>
                <Text className="text-white font-bold text-2xl">{filteredData.length}</Text>
              </View>
              
              <View className="flex-1 bg-gray-800/50 rounded-xl p-4">
                <Text className="text-gray-400 text-sm mb-1">24h Volume</Text>
                <Text className="text-white font-bold text-2xl">
                  ${(filteredData.reduce((sum, item) => sum + parseFloat(item.volume), 0) / 1000000).toFixed(1)}M
                </Text>
              </View>
            </View>
          </CardContent>
        </Card>

        {/* Top Gainers */}
        <View className="mb-6">
          <View className="flex-row items-center justify-between mb-4">
            <Text className="text-white text-xl font-bold">Top Gainers</Text>
            <Text className="text-green-400 text-sm font-medium">+{topGainers.length} markets</Text>
          </View>
          <MarketDataGrid data={topGainers} />
        </View>

        {/* Top Losers */}
        <View className="mb-6">
          <View className="flex-row items-center justify-between mb-4">
            <Text className="text-white text-xl font-bold">Top Losers</Text>
            <Text className="text-red-400 text-sm font-medium">{topLosers.length} markets</Text>
          </View>
          <MarketDataGrid data={topLosers} />
        </View>

        {/* All Markets */}
        <View className="mb-8">
          <View className="flex-row items-center justify-between mb-4">
            <Text className="text-white text-xl font-bold">All Markets</Text>
            <Text className="text-gray-400 text-sm">{filteredData.length} markets</Text>
          </View>
          <MarketDataGrid data={filteredData} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
