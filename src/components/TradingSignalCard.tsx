import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Card, CardContent, CardHeader } from './ui/Card';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

interface TradingSignal {
  id: string;
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  price: string;
  targetPrice: string;
  stopLoss: string;
  timeframe: string;
  reasoning: string;
  timestamp: number;
}

interface TradingSignalCardProps {
  signal: TradingSignal;
  onPress?: () => void;
}

export function TradingSignalCard({ signal, onPress }: TradingSignalCardProps) {
  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case 'BUY': return '#10B981';
      case 'SELL': return '#EF4444';
      case 'HOLD': return '#F59E0B';
      default: return '#6B7280';
    }
  };

  const getSignalIcon = (signalType: string) => {
    switch (signalType) {
      case 'BUY': return 'trending-up';
      case 'SELL': return 'trending-down';
      case 'HOLD': return 'pause';
      default: return 'help';
    }
  };

  const signalColor = getSignalColor(signal.signal);
  const signalIcon = getSignalIcon(signal.signal);

  const formatPrice = (price: string) => {
    const num = parseFloat(price);
    if (num >= 1) return num.toFixed(2);
    if (num >= 0.01) return num.toFixed(4);
    return num.toFixed(8);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return '#10B981';
    if (confidence >= 60) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.8}>
      <Card variant="elevated" className="mb-3">
        <LinearGradient
          colors={['#1F2937', '#111827']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          className="rounded-2xl"
        >
          <CardHeader>
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center space-x-3">
                <View 
                  className="w-12 h-12 rounded-full items-center justify-center"
                  style={{ backgroundColor: signalColor }}
                >
                  <Ionicons name={signalIcon as any} size={24} color="white" />
                </View>
                <View>
                  <Text className="text-white font-bold text-xl">{signal.symbol}</Text>
                  <Text className="text-gray-400 text-sm">AI Trading Signal</Text>
                </View>
              </View>
              
              <View className="items-end">
                <View 
                  className="px-3 py-1 rounded-full"
                  style={{ backgroundColor: `${signalColor}20` }}
                >
                  <Text 
                    className="font-bold text-sm"
                    style={{ color: signalColor }}
                  >
                    {signal.signal}
                  </Text>
                </View>
                <Text className="text-white font-bold text-lg mt-1">
                  ${formatPrice(signal.price)}
                </Text>
              </View>
            </View>
          </CardHeader>

          <CardContent>
            <View className="space-y-4">
              {/* Confidence Bar */}
              <View className="space-y-2">
                <View className="flex-row justify-between items-center">
                  <Text className="text-gray-400 text-sm">AI Confidence</Text>
                  <Text 
                    className="font-semibold text-sm"
                    style={{ color: getConfidenceColor(signal.confidence) }}
                  >
                    {signal.confidence}%
                  </Text>
                </View>
                <View className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <View 
                    className="h-full rounded-full"
                    style={{ 
                      width: `${signal.confidence}%`,
                      backgroundColor: getConfidenceColor(signal.confidence)
                    }}
                  />
                </View>
              </View>

              {/* Price Targets */}
              <View className="flex-row space-x-3">
                <View className="flex-1 bg-gray-800/50 rounded-xl p-3">
                  <Text className="text-gray-400 text-xs mb-1">Target</Text>
                  <Text className="text-green-400 font-semibold">
                    ${formatPrice(signal.targetPrice)}
                  </Text>
                </View>
                
                <View className="flex-1 bg-gray-800/50 rounded-xl p-3">
                  <Text className="text-gray-400 text-xs mb-1">Stop Loss</Text>
                  <Text className="text-red-400 font-semibold">
                    ${formatPrice(signal.stopLoss)}
                  </Text>
                </View>
              </View>

              {/* Reasoning */}
              <View className="bg-gray-800/50 rounded-xl p-3">
                <Text className="text-gray-400 text-xs mb-2">AI Reasoning</Text>
                <Text className="text-white text-sm leading-5">
                  {signal.reasoning}
                </Text>
              </View>

              {/* Footer */}
              <View className="flex-row justify-between items-center">
                <Text className="text-gray-400 text-xs">
                  {signal.timeframe} • {new Date(signal.timestamp).toLocaleTimeString()}
                </Text>
                <View className="flex-row items-center space-x-1">
                  <Ionicons name="flash" size={14} color="#F59E0B" />
                  <Text className="text-yellow-500 text-xs font-medium">Live Signal</Text>
                </View>
              </View>
            </View>
          </CardContent>
        </LinearGradient>
      </Card>
    </TouchableOpacity>
  );
}
