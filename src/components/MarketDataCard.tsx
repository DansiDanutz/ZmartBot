import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Card, CardContent, CardHeader } from './ui/Card';
import { MarketData } from '../services/ZmartBotAPIGateway';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

interface MarketDataCardProps {
  data: MarketData;
  onPress?: () => void;
  isSelected?: boolean;
}

export function MarketDataCard({ data, onPress, isSelected }: MarketDataCardProps) {
  const isPositive = parseFloat(data.priceChangePercent) >= 0;
  const changeColor = isPositive ? '#10B981' : '#EF4444';
  
  const formatPrice = (price: string) => {
    const num = parseFloat(price);
    if (num >= 1) return num.toFixed(2);
    if (num >= 0.01) return num.toFixed(4);
    return num.toFixed(8);
  };

  const formatVolume = (volume: string) => {
    const num = parseFloat(volume);
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toFixed(0);
  };

  return (
    <TouchableOpacity 
      onPress={onPress}
      activeOpacity={0.7}
      className={`mb-3 ${isSelected ? 'scale-105' : ''}`}
    >
      <Card 
        variant={isSelected ? 'elevated' : 'default'}
        className="border-l-4"
        style={{
          borderLeftColor: changeColor,
          borderLeftWidth: 4,
        }}
      >
        <CardHeader>
          <View className="flex-row items-center space-x-3">
            <View className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 items-center justify-center">
              <Text className="text-white font-bold text-sm">
                {data.symbol.substring(0, 2)}
              </Text>
            </View>
            <View>
              <Text className="text-white font-bold text-lg">{data.symbol}</Text>
              <Text className="text-gray-400 text-sm">24h Change</Text>
            </View>
          </View>
          
          <View className="items-end">
            <Text className="text-white font-bold text-xl">
              ${formatPrice(data.price)}
            </Text>
            <View className="flex-row items-center space-x-1">
              <Ionicons 
                name={isPositive ? 'trending-up' : 'trending-down'} 
                size={16} 
                color={changeColor} 
              />
              <Text 
                className="font-semibold text-sm"
                style={{ color: changeColor }}
              >
                {isPositive ? '+' : ''}{data.priceChangePercent}%
              </Text>
            </View>
          </View>
        </CardHeader>

        <CardContent>
          <View className="flex-row justify-between items-center">
            <View className="space-y-2">
              <View className="flex-row items-center space-x-2">
                <Text className="text-gray-400 text-sm">Volume:</Text>
                <Text className="text-white font-medium">
                  {formatVolume(data.volume)}
                </Text>
              </View>
              
              <View className="flex-row items-center space-x-2">
                <Text className="text-gray-400 text-sm">High:</Text>
                <Text className="text-green-400 font-medium">
                  ${formatPrice(data.high)}
                </Text>
              </View>
            </View>
            
            <View className="space-y-2 items-end">
              <View className="flex-row items-center space-x-2">
                <Text className="text-gray-400 text-sm">Change:</Text>
                <Text 
                  className="font-medium"
                  style={{ color: changeColor }}
                >
                  ${formatPrice(data.priceChange)}
                </Text>
              </View>
              
              <View className="flex-row items-center space-x-2">
                <Text className="text-gray-400 text-sm">Low:</Text>
                <Text className="text-red-400 font-medium">
                  ${formatPrice(data.low)}
                </Text>
              </View>
            </View>
          </View>
        </CardContent>
      </Card>
    </TouchableOpacity>
  );
}

export function MarketDataGrid({ data }: { data: MarketData[] }) {
  return (
    <View className="space-y-3">
      {data.map((item, index) => (
        <MarketDataCard 
          key={`${item.symbol}-${index}`} 
          data={item} 
        />
      ))}
    </View>
  );
}
