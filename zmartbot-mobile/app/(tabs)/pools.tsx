import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, RefreshControl, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { Card, CardContent, CardHeader } from '../../src/components/ui/Card';
import { PortfolioCard } from '../../src/components/PortfolioCard';
import { mobileTradingService } from '../../src/services/MobileTradingService';
import { PortfolioPosition } from '../../src/services/ZmartBotAPIGateway';
import { formatCurrency, formatPercentage } from '../../src/lib/utils';

export default function PortfolioScreen() {
  const [portfolio, setPortfolio] = useState({
    totalValue: 0,
    totalPnL: 0,
    totalPnLPercent: 0,
    availableBalance: 0,
    marginUsed: 0
  });
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    initializePortfolio();
  }, []);

  const initializePortfolio = async () => {
    try {
      const healthStatus = await mobileTradingService.getHealthStatus();
      setIsConnected(true);
      console.log('✅ Connected to ZmartBot ecosystem:', healthStatus);
      
      await loadPortfolioData();
    } catch (error) {
      console.error('❌ Failed to connect to ZmartBot:', error);
      setIsConnected(false);
      loadMockPortfolioData();
    }
  };

  const loadPortfolioData = async () => {
    try {
      const portfolioData = await mobileTradingService.getPortfolio();
      setPortfolio({
        totalValue: portfolioData.totalValue || 0,
        totalPnL: portfolioData.totalPnL || 0,
        totalPnLPercent: portfolioData.totalPnLPercent || 0,
        availableBalance: portfolioData.availableBalance || 0,
        marginUsed: portfolioData.marginUsed || 0
      });
      setPositions(portfolioData.positions || []);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('❌ Failed to load portfolio data:', error);
      loadMockPortfolioData();
    }
  };

  const loadMockPortfolioData = () => {
    const mockPortfolio = {
      totalValue: 125000,
      totalPnL: 8750,
      totalPnLPercent: 7.5,
      availableBalance: 25000,
      marginUsed: 100000
    };
    
    const mockPositions: PortfolioPosition[] = [
      {
        symbol: 'BTCUSDT',
        quantity: 2.5,
        entryPrice: 42000,
        currentPrice: 43250,
        pnl: 3125,
        pnlPercent: 7.44,
        margin: 50000,
        leverage: 20,
        side: 'LONG'
      },
      {
        symbol: 'ETHUSDT',
        quantity: 15.8,
        entryPrice: 2580,
        currentPrice: 2650,
        pnl: 1106,
        pnlPercent: 4.29,
        margin: 30000,
        leverage: 15,
        side: 'LONG'
      },
      {
        symbol: 'BNBUSDT',
        quantity: 120,
        entryPrice: 305,
        currentPrice: 312.75,
        pnl: 930,
        pnlPercent: 3.05,
        margin: 20000,
        leverage: 10,
        side: 'LONG'
      }
    ];
    
    setPortfolio(mockPortfolio);
    setPositions(mockPositions);
    setLastUpdate(new Date());
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await loadPortfolioData();
    } catch (error) {
      console.error('❌ Refresh failed:', error);
      Alert.alert('Refresh Failed', 'Could not update portfolio data');
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
            <Text className="text-2xl font-bold text-white">Portfolio</Text>
            <Text className="text-gray-400 text-sm">
              {isConnected ? 'Live Portfolio Data' : 'Demo Portfolio'}
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
              <Ionicons name="add" size={20} color="white" />
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Connection Status */}
        <View className="mt-3 flex-row items-center">
          <View className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`} />
          <Text className={`text-sm ${isConnected ? 'text-green-400' : 'text-yellow-400'}`}>
            {isConnected ? 'Live Data' : 'Demo Mode'}
          </Text>
          {lastUpdate && (
            <Text className="text-gray-500 text-sm ml-auto">
              Last: {lastUpdate.toLocaleTimeString()}
            </Text>
          )}
        </View>
      </View>

      <ScrollView 
        className="flex-1 px-4"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Portfolio Overview Card */}
        <View className="py-4">
          <PortfolioCard
            totalValue={portfolio.totalValue}
            totalPnL={portfolio.totalPnL}
            totalPnLPercent={portfolio.totalPnLPercent}
            availableBalance={portfolio.availableBalance}
            marginUsed={portfolio.marginUsed}
            onPress={() => Alert.alert('Portfolio', 'Portfolio details')}
          />
        </View>

        {/* Active Positions */}
        <View className="pb-4">
          <Text className="text-lg font-semibold text-white mb-4">
            Active Positions ({positions.length})
          </Text>
          
          {positions.length > 0 ? (
            positions.map((position, index) => (
              <Card key={index} variant="elevated" className="mb-3">
                <CardHeader>
                  <View className="flex-row items-center justify-between">
                    <Text className="text-lg font-bold text-white">{position.symbol}</Text>
                    <View className={`px-3 py-1 rounded-full ${position.side === 'LONG' ? 'bg-green-900' : 'bg-red-900'}`}>
                      <Text className={`text-sm font-medium ${position.side === 'LONG' ? 'text-green-300' : 'text-red-300'}`}>
                        {position.side}
                      </Text>
                    </View>
                  </View>
                </CardHeader>
                <CardContent>
                  <View className="space-y-2">
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">Quantity</Text>
                      <Text className="text-white font-medium">{position.quantity}</Text>
                    </View>
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">Entry Price</Text>
                      <Text className="text-white font-medium">${position.entryPrice.toFixed(2)}</Text>
                    </View>
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">Current Price</Text>
                      <Text className="text-white font-medium">${position.currentPrice.toFixed(2)}</Text>
                    </View>
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">P&L</Text>
                      <Text className={`font-bold ${position.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {position.pnl >= 0 ? '+' : ''}{formatCurrency(position.pnl)}
                      </Text>
                    </View>
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">P&L %</Text>
                      <Text className={`font-bold ${position.pnlPercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {formatPercentage(position.pnlPercent)}
                      </Text>
                    </View>
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">Margin</Text>
                      <Text className="text-white font-medium">{formatCurrency(position.margin)}</Text>
                    </View>
                    <View className="flex-row justify-between">
                      <Text className="text-gray-400">Leverage</Text>
                      <Text className="text-white font-medium">{position.leverage}x</Text>
                    </View>
                  </View>
                </CardContent>
              </Card>
            ))
          ) : (
            <View className="items-center justify-center py-20">
              <Ionicons name="wallet-outline" size={64} color="#6B7280" />
              <Text className="text-gray-400 text-lg mt-4">No active positions</Text>
              <Text className="text-gray-500 text-sm text-center mt-2">
                Start trading to see your positions here
              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

