import React from 'react';
import { View, Text } from 'react-native';

type Evidence = { source: string; text: string };

export default function EvidenceChips({ evidence }: { evidence: Evidence[] }) {
  if (!evidence?.length) return null;
  return (
    <View className="flex-row flex-wrap gap-2 mt-2">
      {evidence.slice(0,3).map((e, idx) => (
        <View key={idx} className="bg-sky-600/20 border border-sky-700 rounded-full px-3 py-1 mr-2 mb-2">
          <Text className="text-sky-300 text-xs">[{e.source}] {e.text}</Text>
        </View>
      ))}
    </View>
  );
}
