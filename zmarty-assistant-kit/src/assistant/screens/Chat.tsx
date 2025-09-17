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
    <View className="flex-1 bg-black p-4">
      <View className="flex-row gap-2 mb-3">
        <Pressable className="bg-sky-500 rounded-2xl px-4 py-3" onPress={winrateNow} disabled={loading}>
          <Text className="text-white font-semibold">{loading ? 'Working…' : 'Win rate now (1 ⓒ)'}</Text>
        </Pressable>
        <Pressable className="bg-sky-700 rounded-2xl px-4 py-3" onPress={bestEntry} disabled={loading}>
          <Text className="text-white font-semibold">Best entry (2 ⓒ)</Text>
        </Pressable>
      </View>

      {loading && <ActivityIndicator />}

      <ScrollView className="flex-1" contentContainerStyle={{ paddingBottom: 40 }}>
        {bubbles.map((b, i) => (
          <View key={i} className="bg-zinc-900 rounded-2xl p-4 mb-3">
            <Text className="text-zinc-100">{b.text}</Text>
            {b.evidence && <EvidenceChips evidence={b.evidence} />}
          </View>
        ))}
      </ScrollView>
    </View>
  );
}
