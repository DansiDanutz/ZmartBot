import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Card, CardContent, CardHeader } from './ui/Card';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { formatCurrency, formatPercentage } from '../lib/utils';

interface PortfolioCardProps {
  totalValue: number;
  totalPnL: number;
  totalPnLPercent: number;
  availableBalance: number;
  marginUsed: number;
  onPress?: () => void;
}

export function PortfolioCard({ 
  totalValue, 
  totalPnL, 
  totalPnLPercent, 
  availableBalance, 
  marginUsed, 
  onPress 
}: PortfolioCardProps) {
  const isPositive = totalPnL >= 0;
  const pnlColor = isPositive ? '#10B981' : '#EF4444';
  
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.8}>
      <Card variant="elevated" className="mb-4">
        <LinearGradient
          colors={['#1F2937', '#111827']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          className="rounded-2xl"
        >
          <CardHeader>
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center space-x-3">
                <View className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 items-center justify-center">
                  <Ionicons name="wallet" size={24} color="white" />
                </View>
                <View>
                  <Text className="text-white font-bold text-xl">Portfolio</Text>
                  <Text className="text-gray-400 text-sm">Total Balance</Text>
                </View>
              </View>
              
              <View className="items-end">
                <Text className="text-white font-bold text-2xl">
                  {formatCurrency(totalValue)}
                </Text>
                <View className="flex-row items-center space-x-1">
                  <Ionicons 
                    name={isPositive ? 'trending-up' : 'trending-down'} 
                    size={16} 
                    color={pnlColor} 
                  />
                  <Text 
                    className="font-semibold text-sm"
                    style={{ color: pnlColor }}
                  >
                    {formatPercentage(totalPnLPercent)}
                  </Text>
                </View>
              </View>
            </View>
          </CardHeader>

          <CardContent>
            <View className="space-y-4">
              {/* PnL Section */}
              <View className="bg-gray-800/50 rounded-xl p-4">
                <View className="flex-row justify-between items-center mb-2">
                  <Text className="text-gray-400 text-sm">Total P&L</Text>
                  <Text className="text-gray-400 text-sm">24h Change</Text>
                </View>
                <View className="flex-row justify-between items-center">
                  <Text 
                    className="font-bold text-lg"
                    style={{ color: pnlColor }}
                  >
                    {formatCurrency(totalPnL)}
                  </Text>
                  <Text 
                    className="font-semibold text-lg"
                    style={{ color: pnlColor }}
                  >
                    {formatPercentage(totalPnLPercent)}
                  </Text>
                </View>
              </View>

              {/* Balance Details */}
              <View className="flex-row space-x-3">
                <View className="flex-1 bg-gray-800/50 rounded-xl p-3">
                  <Text className="text-gray-400 text-xs mb-1">Available</Text>
                  <Text className="text-white font-semibold">
                    {formatCurrency(availableBalance)}
                  </Text>
                </View>
                
                <View className="flex-1 bg-gray-800/50 rounded-xl p-3">
                  <Text className="text-gray-400 text-xs mb-1">Margin Used</Text>
                  <Text className="text-white font-semibold">
                    {formatCurrency(marginUsed)}
                  </Text>
                </View>
              </View>
            </View>
          </CardContent>
        </LinearGradient>
      </Card>
    </TouchableOpacity>
  );
}
