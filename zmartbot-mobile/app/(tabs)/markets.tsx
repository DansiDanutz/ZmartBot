import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, RefreshControl, Alert, ActivityIndicator, TouchableOpacity } from 'react-native';
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

  useEffect(() => {
    initializeZmartBotConnection();
  }, []);

  const initializeZmartBotConnection = async () => {
    try {
      const healthStatus = await mobileTradingService.getHealthStatus();
      setIsConnected(true);
      console.log('✅ Connected to ZmartBot ecosystem:', healthStatus);
      
      // Load initial market data
      await loadMarketData();
    } catch (error) {
      console.error('❌ Failed to connect to ZmartBot:', error);
      setIsConnected(false);
      // Load mock data as fallback
      loadMockMarketData();
    }
  };

  const loadMarketData = async () => {
    try {
      const data = await mobileTradingService.getMarketData();
      setMarketData(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('❌ Failed to load market data:', error);
      loadMockMarketData();
    }
  };

  const loadMockMarketData = () => {
    const mockData: MarketData[] = [
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
      },
      {
        symbol: 'ADAUSDT',
        price: 0.3892,
        change24h: 0.0121,
        changePercent24h: 3.21,
        volume24h: 892000000,
        high24h: 0.4012,
        low24h: 0.3834,
        lastUpdated: new Date().toISOString()
      },
      {
        symbol: 'SOLUSDT',
        price: 98.45,
        change24h: 4.25,
        changePercent24h: 4.51,
        volume24h: 650000000,
        high24h: 99.80,
        low24h: 94.20,
        lastUpdated: new Date().toISOString()
      },
      {
        symbol: 'DOTUSDT',
        price: 6.85,
        change24h: 0.35,
        changePercent24h: 5.38,
        volume24h: 320000000,
        high24h: 6.95,
        low24h: 6.50,
        lastUpdated: new Date().toISOString()
      }
    ];
    setMarketData(mockData);
    setLastUpdate(new Date());
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await loadMarketData();
    } catch (error) {
      console.error('❌ Refresh failed:', error);
      Alert.alert('Refresh Failed', 'Could not update market data');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-950">
      <StatusBar style="light" />
      
      {/* Header */}
      <View className="px-4 py-4 bg-gray-900 border-b border-gray-800">
        <View className="flex-row items-center justify-between">
          <View>
            <Text className="text-2xl font-bold text-white">Markets</Text>
            <Text className="text-gray-400 text-sm">
              {isConnected ? 'Connected to ZmartBot' : 'Offline Mode'}
            </Text>
          </View>
          <View className="flex-row items-center space-x-3">
            <TouchableOpacity 
              className="w-10 h-10 bg-blue-600 rounded-full items-center justify-center"
              onPress={onRefresh}
            >
              <Ionicons name="refresh" size={20} color="white" />
            </TouchableOpacity>
            <TouchableOpacity className="w-10 h-10 bg-gray-700 rounded-full items-center justify-center">
              <Ionicons name="search" size={20} color="white" />
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Connection Status */}
        <View className="mt-3 flex-row items-center">
          <View className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <Text className={`text-sm ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            {isConnected ? 'Live Data' : 'Mock Data'}
          </Text>
          {lastUpdate && (
            <Text className="text-gray-500 text-sm ml-auto">
              Last: {lastUpdate.toLocaleTimeString()}
            </Text>
          )}
        </View>
      </View>

      {/* Market Data */}
      <ScrollView 
        className="flex-1 px-4"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {marketData.length > 0 ? (
          <View className="py-4">
            <Text className="text-lg font-semibold text-white mb-4">
              Live Market Data ({marketData.length} pairs)
            </Text>
            <MarketDataGrid data={marketData} />
          </View>
        ) : (
          <View className="flex-1 items-center justify-center py-20">
            <ActivityIndicator size="large" color="#3B82F6" />
            <Text className="text-white text-lg mt-4">Loading market data...</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
