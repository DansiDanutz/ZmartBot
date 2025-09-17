import React, { useState, useRef, useEffect } from 'react';
import { View, Text, ScrollView, Pressable, Animated, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface CreditTransaction {
  id: string;
  type: 'purchase' | 'usage' | 'bonus' | 'refund';
  amount: number;
  description: string;
  timestamp: Date;
  status: 'completed' | 'pending' | 'failed';
  category: 'chat' | 'analysis' | 'portfolio' | 'alerts' | 'premium';
}

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  savings?: number;
  popular?: boolean;
  features: string[];
}

const mockTransactions: CreditTransaction[] = [
  {
    id: '1',
    type: 'purchase',
    amount: 1000,
    description: 'Premium Package Purchase',
    timestamp: new Date(Date.now() - 86400000),
    status: 'completed',
    category: 'premium',
  },
  {
    id: '2',
    type: 'usage',
    amount: -50,
    description: 'Advanced Portfolio Analysis',
    timestamp: new Date(Date.now() - 3600000),
    status: 'completed',
    category: 'portfolio',
  },
  {
    id: '3',
    type: 'usage',
    amount: -25,
    description: 'AI Market Prediction',
    timestamp: new Date(Date.now() - 1800000),
    status: 'completed',
    category: 'analysis',
  },
  {
    id: '4',
    type: 'bonus',
    amount: 100,
    description: 'Welcome Bonus',
    timestamp: new Date(Date.now() - 604800000),
    status: 'completed',
    category: 'premium',
  },
];

const creditPackages: CreditPackage[] = [
  {
    id: '1',
    name: 'Starter',
    credits: 100,
    price: 9.99,
    features: ['Basic AI Chat', 'Portfolio Tracking', 'Market Alerts'],
  },
  {
    id: '2',
    name: 'Pro',
    credits: 500,
    price: 39.99,
    savings: 20,
    popular: true,
    features: ['Advanced AI Analysis', 'Risk Assessment', 'Priority Support'],
  },
  {
    id: '3',
    name: 'Premium',
    credits: 1000,
    price: 69.99,
    savings: 30,
    features: ['Unlimited AI Chat', 'Custom Alerts', 'API Access'],
  },
];

const TransactionCard: React.FC<{ transaction: CreditTransaction; index: number }> = ({ transaction, index }) => {
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

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'purchase': return '#00C896';
      case 'usage': return '#FF6B6B';
      case 'bonus': return '#FFD93D';
      case 'refund': return '#6BCF7F';
      default: return '#848E9C';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'purchase': return 'add-circle';
      case 'usage': return 'remove-circle';
      case 'bonus': return 'gift';
      case 'refund': return 'refresh';
      default: return 'card';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'chat': return 'chatbubble';
      case 'analysis': return 'analytics';
      case 'portfolio': return 'pie-chart';
      case 'alerts': return 'notifications';
      case 'premium': return 'star';
      default: return 'settings';
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
        <View className="flex-row items-center justify-between mb-3">
          <View className="flex-row items-center flex-1">
            <View 
              className="w-10 h-10 rounded-full items-center justify-center mr-3"
              style={{ backgroundColor: getTypeColor(transaction.type) + '20' }}
            >
              <Ionicons 
                name={getTypeIcon(transaction.type) as any} 
                size={20} 
                color={getTypeColor(transaction.type)} 
              />
            </View>
            <View className="flex-1">
              <Text className="text-binance-text-primary font-semibold text-base mb-1">
                {transaction.description}
              </Text>
              <View className="flex-row items-center">
                <Ionicons name={getCategoryIcon(transaction.category) as any} size={14} color="#848E9C" />
                <Text className="text-binance-text-secondary text-sm ml-2 capitalize">
                  {transaction.category}
                </Text>
              </View>
            </View>
          </View>
          <View className="items-end">
            <Text 
              className={`text-lg font-bold ${
                transaction.amount > 0 ? 'text-binance-green' : 'text-red-400'
              }`}
            >
              {transaction.amount > 0 ? '+' : ''}{transaction.amount} credits
            </Text>
            <Text className="text-binance-text-tertiary text-xs">
              {transaction.timestamp.toLocaleDateString()}
            </Text>
          </View>
        </View>

        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center">
            <View 
              className={`px-2 py-1 rounded-full mr-2 ${
                transaction.status === 'completed' ? 'bg-binance-green/20' : 
                transaction.status === 'pending' ? 'bg-yellow-500/20' : 'bg-red-500/20'
              }`}
            >
              <Text 
                className={`text-xs font-medium capitalize ${
                  transaction.status === 'completed' ? 'text-binance-green' : 
                  transaction.status === 'pending' ? 'text-yellow-500' : 'text-red-500'
                }`}
              >
                {transaction.status}
              </Text>
            </View>
          </View>
          
          <Pressable className="bg-binance-bg-tertiary px-3 py-2 rounded-md">
            <Text className="text-binance-text-secondary text-xs">Details</Text>
          </Pressable>
        </View>
      </LinearGradient>
    </Animated.View>
  );
};

const PackageCard: React.FC<{ pkg: CreditPackage; onSelect: (pkg: CreditPackage) => void }> = ({ pkg, onSelect }) => {
  const scaleAnim = useRef(new Animated.Value(0.9)).current;

  useEffect(() => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      tension: 100,
      friction: 8,
      useNativeDriver: true,
    }).start();
  }, [scaleAnim]);

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <Pressable
        onPress={() => onSelect(pkg)}
        className={`rounded-lg p-4 border-2 mb-3 ${
          pkg.popular 
            ? 'border-binance-green bg-binance-green/5' 
            : 'border-binance-border bg-binance-bg-secondary'
        }`}
      >
        {pkg.popular && (
          <View className="absolute -top-2 left-4 bg-binance-green px-3 py-1 rounded-full">
            <Text className="text-white text-xs font-bold">MOST POPULAR</Text>
          </View>
        )}
        
        <View className="flex-row items-center justify-between mb-3">
          <Text className="text-binance-text-primary text-xl font-bold">
            {pkg.name}
          </Text>
          <View className="items-end">
            <Text className="text-binance-text-primary text-2xl font-bold">
              ${pkg.price}
            </Text>
            {pkg.savings && (
              <Text className="text-binance-green text-sm font-medium">
                Save {pkg.savings}%
              </Text>
            )}
          </View>
        </View>

        <View className="mb-4">
          <Text className="text-3xl font-bold text-binance-green mb-1">
            {pkg.credits.toLocaleString()}
          </Text>
          <Text className="text-binance-text-secondary text-sm">
            AI Credits
          </Text>
        </View>

        <View className="mb-4">
          {pkg.features.map((feature, index) => (
            <View key={index} className="flex-row items-center mb-2">
              <Ionicons name="checkmark-circle" size={16} color="#00C896" />
              <Text className="text-binance-text-primary text-sm ml-2">
                {feature}
              </Text>
            </View>
          ))}
        </View>

        <Pressable 
          className={`py-3 rounded-lg ${
            pkg.popular ? 'bg-binance-green' : 'bg-binance-accent'
          }`}
        >
          <Text className="text-center font-semibold text-white">
            Select Package
          </Text>
        </Pressable>
      </Pressable>
    </Animated.View>
  );
};

const CreditsScreen = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, [fadeAnim]);

  const currentCredits = 875;
  const totalSpent = 69.99;
  const usageThisMonth = 125;

  const handlePackageSelect = (pkg: CreditPackage) => {
    setShowPurchaseModal(true);
    // Handle package selection
  };

  return (
    <View className="flex-1 bg-binance-bg-primary">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="px-4 py-6 bg-binance-bg-secondary border-b border-binance-border">
          <Text className="text-binance-text-primary text-2xl font-bold mb-2">
            Credits & Premium
          </Text>
          <Text className="text-binance-text-secondary text-base">
            Manage your AI credits and unlock premium features
          </Text>
        </View>

        {/* Credits Overview */}
        <View className="px-4 py-4">
          <LinearGradient
            colors={['#00C896', '#00A884']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            className="rounded-lg p-6 mb-4"
          >
            <View className="flex-row items-center justify-between mb-4">
              <View>
                <Text className="text-white text-sm mb-1">Available Credits</Text>
                <Text className="text-white text-3xl font-bold">
                  {currentCredits.toLocaleString()}
                </Text>
              </View>
              <View className="items-end">
                <Text className="text-white text-sm mb-1">Total Spent</Text>
                <Text className="text-white text-xl font-bold">
                  ${totalSpent}
                </Text>
              </View>
            </View>
            
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center">
                <Ionicons name="trending-up" size={20} color="white" />
                <Text className="text-white text-sm ml-2">
                  {usageThisMonth} credits used this month
                </Text>
              </View>
              <Pressable 
                onPress={() => setShowPurchaseModal(true)}
                className="bg-white/20 px-4 py-2 rounded-full"
              >
                <Text className="text-white font-medium">Buy More</Text>
              </Pressable>
            </View>
          </LinearGradient>
        </View>

        {/* Quick Stats */}
        <View className="px-4 py-3 border-b border-binance-border">
          <View className="flex-row space-x-3">
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Daily Usage</Text>
              <Text className="text-binance-text-primary text-xl font-bold">8.3</Text>
              <Text className="text-binance-text-secondary text-xs">avg credits/day</Text>
            </View>
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Credits Left</Text>
              <Text className="text-binance-text-primary text-xl font-bold">35</Text>
              <Text className="text-binance-text-secondary text-xs">days remaining</Text>
            </View>
            <View className="flex-1 bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
              <Text className="text-binance-text-tertiary text-sm mb-1">Efficiency</Text>
              <Text className="text-binance-green text-xl font-bold">92%</Text>
              <Text className="text-binance-text-secondary text-xs">usage rate</Text>
            </View>
          </View>
        </View>

        {/* Tabs */}
        <View className="px-4 py-3 border-b border-binance-border">
          <View className="flex-row space-x-2">
            {['overview', 'packages', 'history'].map(tab => (
              <Pressable
                key={tab}
                onPress={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-full border ${
                  activeTab === tab 
                    ? 'bg-binance-green border-binance-green' 
                    : 'border-binance-border'
                }`}
              >
                <Text className={`text-sm font-medium capitalize ${
                  activeTab === tab 
                    ? 'text-white' 
                    : 'text-binance-text-secondary'
                }`}>
                  {tab}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        {/* Tab Content */}
        <Animated.View style={{ opacity: fadeAnim }} className="px-4 py-4">
          {activeTab === 'overview' && (
            <View>
              <Text className="text-binance-text-primary text-lg font-semibold mb-4">
                AI Usage Analytics
              </Text>
              
              <View className="bg-binance-bg-secondary rounded-lg p-4 border border-binance-border mb-4">
                <Text className="text-binance-text-primary font-semibold mb-3">Top Features Used</Text>
                <View className="space-y-3">
                  <View className="flex-row items-center justify-between">
                    <View className="flex-row items-center">
                      <Ionicons name="chatbubble" size={20} color="#00C896" />
                      <Text className="text-binance-text-primary ml-2">AI Chat</Text>
                    </View>
                    <Text className="text-binance-text-secondary">45%</Text>
                  </View>
                  <View className="flex-row items-center justify-between">
                    <View className="flex-row items-center">
                      <Ionicons name="analytics" size={20} color="#FFD93D" />
                      <Text className="text-binance-text-primary ml-2">Portfolio Analysis</Text>
                    </View>
                    <Text className="text-binance-text-secondary">32%</Text>
                  </View>
                  <View className="flex-row items-center justify-between">
                    <View className="flex-row items-center">
                      <Ionicons name="notifications" size={20} color="#FF8E53" />
                      <Text className="text-binance-text-primary ml-2">Market Alerts</Text>
                    </View>
                    <Text className="text-binance-text-secondary">23%</Text>
                  </View>
                </View>
              </View>

              <View className="bg-binance-bg-secondary rounded-lg p-4 border border-binance-border">
                <Text className="text-binance-text-primary font-semibold mb-3">AI Insights</Text>
                <Text className="text-binance-text-secondary text-sm leading-6">
                  Based on your usage patterns, you're most active during market hours. 
                  Consider upgrading to Premium for unlimited AI chat and advanced portfolio insights.
                </Text>
              </View>
            </View>
          )}

          {activeTab === 'packages' && (
            <View>
              <Text className="text-binance-text-primary text-lg font-semibold mb-4">
                Choose Your Plan
              </Text>
              {creditPackages.map(pkg => (
                <PackageCard key={pkg.id} pkg={pkg} onSelect={handlePackageSelect} />
              ))}
            </View>
          )}

          {activeTab === 'history' && (
            <View>
              <Text className="text-binance-text-primary text-lg font-semibold mb-4">
                Transaction History
              </Text>
              {mockTransactions.map((transaction, index) => (
                <TransactionCard key={transaction.id} transaction={transaction} index={index} />
              ))}
            </View>
          )}
        </Animated.View>
      </ScrollView>
    </View>
  );
};

export default CreditsScreen;

