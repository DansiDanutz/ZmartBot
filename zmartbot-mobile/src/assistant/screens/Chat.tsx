import React, { useState } from 'react';
import { View, Text, Pressable, ActivityIndicator, ScrollView } from 'react-native';
import uuid from 'react-native-uuid';
import { API } from '../api/client';
import EvidenceChips from '../components/EvidenceChips';
import { usePrefs } from '../store/prefs';
import { smartGreeting } from '../utils/greet';
import { speak } from '../utils/voice';

type Snapshot = {
  symbol: string;
  long_prob: number;
  short_prob: number;
  stance: 'long'|'short'|'wait';
  evidence: { source: string; text: string }[];
};

type Bubble = { text: string; evidence?: Snapshot['evidence'] };

export default function Chat() {
  const { allowVoice } = usePrefs();
  const [loading, setLoading] = useState(false);
  const [bubbles, setBubbles] = useState<Bubble[]>([
    { text: smartGreeting() + " I’m Zmarty — want a quick win-rate snapshot?" }
  ]);

  async function winrateNow() {
    setLoading(true);
    try {
      await API.post(`/v1/credits/spend?user_id=demo&amount=1&reason=snapshot`, {}, {
        headers: { 'X-Request-ID': String(uuid.v4()) }
      });
      const { data } = await API.get<Snapshot>(`/v1/signals/snapshot`, { params: { symbol: 'ETH' }});
      const prob = Math.floor(Math.max(data.long_prob, data.short_prob) * 100);
      const stance = data.stance.toUpperCase();
      const text = `ETH now: ${stance} (${prob}%).\nEducational only — not financial advice.`;
      const bubble: Bubble = { text, evidence: data.evidence };
      setBubbles((b) => [bubble, ...b]);
      if (allowVoice) speak(text.replace(/\n/g, ' '));
    } catch (e: any) {
      setBubbles((b) => [{ text: "Couldn’t fetch right now—try again shortly." }, ...b]);
    } finally {
      setLoading(false);
    }
  }

  async function bestEntry() {
    setLoading(true);
    try {
      await API.post(`/v1/credits/spend?user_id=demo&amount=2&reason=best-entry`, {}, {
        headers: { 'X-Request-ID': String(uuid.v4()) }
      });
      const { data } = await API.post(`/v1/signals/best-entry`, { symbol: 'ETH' });
      const text = `Best entry for ETH: $${data.best_entry} (~${Math.round(data.est_prob*100)}% win-prob at that level).`;
      setBubbles((b) => [{ text, evidence: data.evidence }, ...b]);
      if (allowVoice) speak(text);
    } catch (e) {
      setBubbles((b) => [{ text: "Couldn’t fetch best entry now." }, ...b]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={{flex: 1, backgroundColor: '#0A0E1B'}}>
      {/* Header Section with Cards */}
      <View style={{
        padding: 16,
        paddingBottom: 8,
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(0, 255, 204, 0.1)'
      }}>
        <View style={{flexDirection: 'row', gap: 12, marginBottom: 16}}>
          <Pressable
            style={{
              flex: 1,
              backgroundColor: loading ? '#064E73' : '#0EA5E9',
              borderRadius: 20,
              padding: 18,
              alignItems: 'center',
              shadowColor: '#0EA5E9',
              shadowOffset: { width: 0, height: 4 },
              shadowOpacity: 0.3,
              shadowRadius: 8,
              elevation: 8,
              borderWidth: 1,
              borderColor: 'rgba(14, 165, 233, 0.3)',
              transform: [{ scale: loading ? 0.98 : 1 }]
            }}
            onPress={winrateNow} 
            disabled={loading}
          >
            <Text style={{
              color: 'white',
              fontWeight: 'bold',
              fontSize: 16,
              textShadowColor: 'rgba(0, 0, 0, 0.5)',
              textShadowOffset: { width: 0, height: 1 },
              textShadowRadius: 2
            }}>
              {loading ? '⏳ Working…' : '📊 Win Rate Now'}
            </Text>
            <Text style={{
              color: '#BAE6FD',
              fontSize: 13,
              marginTop: 6,
              fontWeight: '600',
              backgroundColor: 'rgba(0, 0, 0, 0.2)',
              paddingHorizontal: 8,
              paddingVertical: 2,
              borderRadius: 10
            }}>1 credit</Text>
          </Pressable>
          
          <Pressable
            style={{
              flex: 1,
              backgroundColor: loading ? '#065F46' : '#10B981',
              borderRadius: 20,
              padding: 18,
              alignItems: 'center',
              shadowColor: '#10B981',
              shadowOffset: { width: 0, height: 4 },
              shadowOpacity: 0.3,
              shadowRadius: 8,
              elevation: 8,
              borderWidth: 1,
              borderColor: 'rgba(16, 185, 129, 0.3)',
              transform: [{ scale: loading ? 0.98 : 1 }]
            }}
            onPress={bestEntry} 
            disabled={loading}
          >
            <Text style={{
              color: 'white',
              fontWeight: 'bold',
              fontSize: 16,
              textShadowColor: 'rgba(0, 0, 0, 0.5)',
              textShadowOffset: { width: 0, height: 1 },
              textShadowRadius: 2
            }}>🎯 Best Entry</Text>
            <Text style={{
              color: '#D1FAE5',
              fontSize: 13,
              marginTop: 6,
              fontWeight: '600',
              backgroundColor: 'rgba(0, 0, 0, 0.2)',
              paddingHorizontal: 8,
              paddingVertical: 2,
              borderRadius: 10
            }}>2 credits</Text>
          </Pressable>
        </View>

        {loading && (
          <View style={{
            backgroundColor: 'rgba(14, 165, 233, 0.1)',
            borderRadius: 20,
            padding: 18,
            marginBottom: 12,
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center',
            borderWidth: 1,
            borderColor: 'rgba(14, 165, 233, 0.2)'
          }}>
            <ActivityIndicator size="small" color="#00FFCC" />
            <Text style={{
              color: '#00FFCC',
              marginLeft: 12,
              fontWeight: '600',
              fontSize: 15,
              letterSpacing: 0.5
            }}>
              Analyzing market data...
            </Text>
          </View>
        )}
      </View>

      {/* Chat Messages */}
      <ScrollView
        style={{
          flex: 1,
          paddingHorizontal: 16,
          backgroundColor: 'linear-gradient(180deg, #0A0E1B 0%, #0F172A 100%)'
        }}
        contentContainerStyle={{paddingBottom: 40, paddingTop: 16}}
        showsVerticalScrollIndicator={false}
      >
        {bubbles.map((b, i) => (
          <View
            key={i}
            style={{
              backgroundColor: i === 0
                ? 'rgba(14, 165, 233, 0.05)'
                : 'rgba(30, 41, 59, 0.8)',
              borderRadius: 20,
              padding: 18,
              marginBottom: 16,
              borderWidth: 1,
              borderColor: i === 0
                ? 'rgba(0, 255, 204, 0.3)'
                : 'rgba(71, 85, 105, 0.3)',
              shadowColor: i === 0 ? '#00FFCC' : '#000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: i === 0 ? 0.2 : 0.1,
              shadowRadius: 8,
              elevation: 4
            }}
          >
            <View style={{flexDirection: 'row', alignItems: 'flex-start'}}>
              <View style={{
                width: 8,
                height: 8,
                borderRadius: 4,
                backgroundColor: i === 0 ? '#00FFCC' : '#64748B',
                marginTop: 8,
                marginRight: 12
              }} />
              <Text style={{
                color: i === 0 ? '#E0F2FE' : '#CBD5E1',
                lineHeight: 26,
                fontWeight: i === 0 ? '600' : '500',
                fontSize: 15,
                flex: 1,
                letterSpacing: 0.3
              }}>{b.text}</Text>
            </View>
            {b.evidence && (
              <View style={{
                marginTop: 16,
                paddingTop: 16,
                borderTopWidth: 1,
                borderTopColor: i === 0
                  ? 'rgba(0, 255, 204, 0.2)'
                  : 'rgba(71, 85, 105, 0.3)'
              }}>
                <Text style={{
                  color: '#94A3B8',
                  fontSize: 12,
                  fontWeight: '600',
                  letterSpacing: 1,
                  textTransform: 'uppercase',
                  marginBottom: 8
                }}>📍 EVIDENCE</Text>
                <EvidenceChips evidence={b.evidence} />
              </View>
            )}
          </View>
        ))}
      </ScrollView>
    </View>
  );
}
