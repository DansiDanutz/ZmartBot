import React from 'react';
import { View, Text, Switch, Pressable, Alert } from 'react-native';
import { usePrefs } from '../store/prefs';
import { enableCityLevelLocation } from '../utils/location';

export default function SettingsSmart() {
  const { smartMode, allowLocation, allowVoice, city, set } = usePrefs();

  async function toggleLocation(v: boolean) {
    if (v) {
      const res = await enableCityLevelLocation();
      if (!res.ok) {
        Alert.alert('Permission denied', 'We need location permission to personalize your tips.');
        return;
      }
    }
    set({ allowLocation: v });
  }

  return (
    <View className="flex-1 bg-black p-4 gap-4">
      <View className="bg-zinc-900 p-4 rounded-2xl">
        <Text className="text-white font-semibold mb-2">Smart Mode</Text>
        <View className="flex-row items-center justify-between">
          <Text className="text-zinc-300">Personalized tips</Text>
          <Switch value={smartMode} onValueChange={(v)=>set({ smartMode: v })} />
        </View>
      </View>

      <View className="bg-zinc-900 p-4 rounded-2xl">
        <View className="flex-row items-center justify-between mb-2">
          <Text className="text-white font-semibold">Location (city-level)</Text>
          <Switch value={allowLocation} onValueChange={toggleLocation} />
        </View>
        <Text className="text-zinc-400">{city ? `Using: ${city}` : 'Off'}</Text>
      </View>

      <View className="bg-zinc-900 p-4 rounded-2xl">
        <View className="flex-row items-center justify-between">
          <Text className="text-white font-semibold">Voice replies (TTS)</Text>
          <Switch value={allowVoice} onValueChange={(v)=>set({ allowVoice: v })} />
        </View>
      </View>

      <View className="bg-zinc-900 p-4 rounded-2xl">
        <Text className="text-zinc-300">
          Zmarty personalizes tips only with your consent. No background tracking, no photos or other apps are accessed.
        </Text>
      </View>

      <Pressable className="bg-sky-500 p-4 rounded-2xl">
        <Text className="text-white text-center">Save</Text>
      </Pressable>
    </View>
  );
}
