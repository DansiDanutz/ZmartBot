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
    <View style={{flex: 1, backgroundColor: '#000'}}>
      {/* Header Section with Cards */}
      <View style={{padding: 16, paddingBottom: 8}}>
        <View style={{flexDirection: 'row', gap: 12, marginBottom: 16}}>
          <Pressable 
            style={{
              flex: 1, 
              backgroundColor: '#0EA5E9', 
              borderRadius: 16, 
              padding: 16,
              alignItems: 'center'
            }}
            onPress={winrateNow} 
            disabled={loading}
          >
            <Text style={{color: 'white', fontWeight: 'bold', fontSize: 14}}>
              {loading ? 'Working…' : '📊 Win Rate Now'}
            </Text>
            <Text style={{color: '#E0F2FE', fontSize: 12, marginTop: 4}}>1 ⓒ</Text>
          </Pressable>
          
          <Pressable 
            style={{
              flex: 1, 
              backgroundColor: '#10B981', 
              borderRadius: 16, 
              padding: 16,
              alignItems: 'center'
            }}
            onPress={bestEntry} 
            disabled={loading}
          >
            <Text style={{color: 'white', fontWeight: 'bold', fontSize: 14}}>🎯 Best Entry</Text>
            <Text style={{color: '#D1FAE5', fontSize: 12, marginTop: 4}}>2 ⓒ</Text>
          </Pressable>
        </View>

        {loading && (
          <View style={{
            backgroundColor: 'rgba(51, 65, 85, 0.6)', 
            borderRadius: 16, 
            padding: 16, 
            marginBottom: 12,
            flexDirection: 'row', 
            alignItems: 'center', 
            justifyContent: 'center'
          }}>
            <ActivityIndicator size="small" color="#0EA5E9" />
            <Text style={{color: '#CBD5E1', marginLeft: 12, fontWeight: '500'}}>
              Processing your request...
            </Text>
          </View>
        )}
      </View>

      {/* Chat Messages */}
      <ScrollView 
        style={{flex: 1, paddingHorizontal: 16}}
        contentContainerStyle={{paddingBottom: 40}}
        showsVerticalScrollIndicator={false}
      >
        {bubbles.map((b, i) => (
          <View 
            key={i} 
            style={{
              backgroundColor: 'rgba(51, 65, 85, 0.8)', 
              borderRadius: 16, 
              padding: 16, 
              marginBottom: 12,
              borderWidth: 1,
              borderColor: 'rgba(71, 85, 105, 0.5)'
            }}
          >
            <Text style={{color: '#F1F5F9', lineHeight: 24, fontWeight: '500'}}>{b.text}</Text>
            {b.evidence && (
              <View style={{
                marginTop: 12, 
                paddingTop: 12, 
                borderTopWidth: 1, 
                borderTopColor: 'rgba(71, 85, 105, 0.5)'
              }}>
                <EvidenceChips evidence={b.evidence} />
              </View>
            )}
          </View>
        ))}
      </ScrollView>
    </View>
  );
}
