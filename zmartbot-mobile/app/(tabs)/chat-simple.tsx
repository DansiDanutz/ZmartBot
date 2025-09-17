import React, { useState } from 'react';
import { View, Text, ScrollView, TextInput, Pressable } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  type: 'text' | 'trade_suggestion' | 'market_analysis' | 'portfolio_insight' | 'risk_alert';
}

const mockMessages: Message[] = [
  {
    id: '1',
    text: 'Welcome to ZmartBot! I can help you with trading strategies, market analysis, and portfolio management.',
    isUser: false,
    timestamp: new Date(),
    type: 'text'
  }
];

const MessageCard: React.FC<{ message: Message }> = ({ message }) => {
  return (
    <View style={{ 
      backgroundColor: message.isUser ? '#F0B90B' : '#1E1E1E',
      margin: 8,
      padding: 16,
      borderRadius: 12,
      alignSelf: message.isUser ? 'flex-end' : 'flex-start',
      maxWidth: '80%'
    }}>
      <Text style={{ color: message.isUser ? '#000' : '#FFF' }}>
        {message.text}
      </Text>
    </View>
  );
};

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [inputText, setInputText] = useState('');

  const sendMessage = () => {
    if (!inputText.trim()) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
      type: 'text'
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInputText('');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#0B0E11' }}>
      <LinearGradient
        colors={['#0B0E11', '#1A1A1A', '#0B0E11']}
        style={{ flex: 1 }}
      >
        {/* Header */}
        <View style={{ 
          flexDirection: 'row', 
          alignItems: 'center', 
          padding: 20,
          borderBottomWidth: 1,
          borderBottomColor: '#F0B90B20'
        }}>
          <Ionicons name="chatbubble-ellipses" size={24} color="#F0B90B" />
          <Text style={{ 
            color: '#FFF', 
            fontSize: 20, 
            fontWeight: 'bold', 
            marginLeft: 12 
          }}>
            AI Trading Assistant
          </Text>
        </View>

        {/* Messages */}
        <ScrollView style={{ flex: 1, padding: 16 }}>
          {messages.map((message) => (
            <MessageCard key={message.id} message={message} />
          ))}
        </ScrollView>

        {/* Input */}
        <View style={{
          flexDirection: 'row',
          padding: 16,
          alignItems: 'center',
          borderTopWidth: 1,
          borderTopColor: '#F0B90B20'
        }}>
          <TextInput
            style={{
              flex: 1,
              backgroundColor: '#1E1E1E',
              color: '#FFF',
              padding: 12,
              borderRadius: 20,
              marginRight: 12
            }}
            placeholder="Ask ZmartBot anything..."
            placeholderTextColor="#666"
            value={inputText}
            onChangeText={setInputText}
          />
          <Pressable
            onPress={sendMessage}
            style={{
              backgroundColor: '#F0B90B',
              padding: 12,
              borderRadius: 20
            }}
          >
            <Ionicons name="send" size={20} color="#000" />
          </Pressable>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}