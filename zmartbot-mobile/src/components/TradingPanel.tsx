import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, Alert } from 'react-native';

interface TradingPanelProps {
  symbol: string;
  currentPrice: number;
  onPlaceOrder: (order: OrderData) => void;
}

export interface OrderData {
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop';
  amount: number;
  price?: number;
  stopPrice?: number;
}

export const TradingPanel: React.FC<TradingPanelProps> = ({
  symbol,
  currentPrice,
  onPlaceOrder
}) => {
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'stop'>('market');
  const [amount, setAmount] = useState('');
  const [price, setPrice] = useState('');
  const [stopPrice, setStopPrice] = useState('');

  const handleSubmit = () => {
    if (!amount || parseFloat(amount) <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }

    if (orderType === 'limit' && (!price || parseFloat(price) <= 0)) {
      Alert.alert('Error', 'Please enter a valid limit price');
      return;
    }

    if (orderType === 'stop' && (!stopPrice || parseFloat(stopPrice) <= 0)) {
      Alert.alert('Error', 'Please enter a valid stop price');
      return;
    }

    const order: OrderData = {
      symbol,
      side: orderSide,
      type: orderType,
      amount: parseFloat(amount),
      price: orderType === 'limit' ? parseFloat(price) : undefined,
      stopPrice: orderType === 'stop' ? parseFloat(stopPrice) : undefined,
    };

    onPlaceOrder(order);

    setAmount('');
    setPrice('');
    setStopPrice('');
  };

  const estimatedTotal = () => {
    const qty = parseFloat(amount) || 0;
    const prc = orderType === 'limit' ? parseFloat(price) || 0 : currentPrice;
    return (qty * prc).toFixed(2);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Trade {symbol}</Text>
      <Text style={styles.currentPrice}>Current: ${currentPrice.toLocaleString()}</Text>

      <View style={styles.sideSelector}>
        <Pressable
          style={[styles.sideButton, orderSide === 'buy' && styles.buyActive]}
          onPress={() => setOrderSide('buy')}
        >
          <Text style={[styles.sideButtonText, orderSide === 'buy' && styles.activeText]}>
            BUY
          </Text>
        </Pressable>
        <Pressable
          style={[styles.sideButton, orderSide === 'sell' && styles.sellActive]}
          onPress={() => setOrderSide('sell')}
        >
          <Text style={[styles.sideButtonText, orderSide === 'sell' && styles.activeText]}>
            SELL
          </Text>
        </Pressable>
      </View>

      <View style={styles.typeSelector}>
        {(['market', 'limit', 'stop'] as const).map((type) => (
          <Pressable
            key={type}
            style={[styles.typeButton, orderType === type && styles.typeActive]}
            onPress={() => setOrderType(type)}
          >
            <Text style={[styles.typeButtonText, orderType === type && styles.activeText]}>
              {type.toUpperCase()}
            </Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Amount</Text>
        <TextInput
          style={styles.input}
          value={amount}
          onChangeText={setAmount}
          placeholder="0.00"
          placeholderTextColor="#64748B"
          keyboardType="decimal-pad"
        />
      </View>

      {orderType === 'limit' && (
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Limit Price</Text>
          <TextInput
            style={styles.input}
            value={price}
            onChangeText={setPrice}
            placeholder="0.00"
            placeholderTextColor="#64748B"
            keyboardType="decimal-pad"
          />
        </View>
      )}

      {orderType === 'stop' && (
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Stop Price</Text>
          <TextInput
            style={styles.input}
            value={stopPrice}
            onChangeText={setStopPrice}
            placeholder="0.00"
            placeholderTextColor="#64748B"
            keyboardType="decimal-pad"
          />
        </View>
      )}

      <View style={styles.summary}>
        <Text style={styles.summaryLabel}>Estimated Total</Text>
        <Text style={styles.summaryValue}>${estimatedTotal()}</Text>
      </View>

      <Pressable
        style={[
          styles.submitButton,
          orderSide === 'buy' ? styles.buyButton : styles.sellButton
        ]}
        onPress={handleSubmit}
      >
        <Text style={styles.submitButtonText}>
          {orderSide === 'buy' ? 'Place Buy Order' : 'Place Sell Order'}
        </Text>
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'rgba(30, 41, 59, 0.95)',
    borderRadius: 24,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(71, 85, 105, 0.3)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 6,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E0F2FE',
    marginBottom: 8,
  },
  currentPrice: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 16,
  },
  sideSelector: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  sideButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: 'rgba(71, 85, 105, 0.3)',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  buyActive: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    borderColor: 'rgba(16, 185, 129, 0.4)',
  },
  sellActive: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderColor: 'rgba(239, 68, 68, 0.4)',
  },
  sideButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  typeSelector: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 20,
  },
  typeButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: 'rgba(71, 85, 105, 0.2)',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  typeActive: {
    backgroundColor: 'rgba(14, 165, 233, 0.15)',
    borderColor: 'rgba(14, 165, 233, 0.3)',
  },
  typeButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748B',
  },
  activeText: {
    color: '#FFFFFF',
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 13,
    color: '#94A3B8',
    marginBottom: 6,
    fontWeight: '500',
  },
  input: {
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: '#FFFFFF',
    fontSize: 16,
    borderWidth: 1,
    borderColor: 'rgba(71, 85, 105, 0.3)',
  },
  summary: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(71, 85, 105, 0.3)',
    marginBottom: 16,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#94A3B8',
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  submitButton: {
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 4,
  },
  buyButton: {
    backgroundColor: '#10B981',
  },
  sellButton: {
    backgroundColor: '#EF4444',
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});