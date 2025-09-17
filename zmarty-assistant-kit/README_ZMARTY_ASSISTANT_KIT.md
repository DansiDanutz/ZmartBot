# Zmarty Assistant Kit (Expo / React Native)

Drop-in bundle to add **Smart Mode** to your Expo app:
- City-level location (opt-in) for local greetings.
- Voice (TTS) replies (opt-in).
- Chat screen calling your Foundation API with evidence chips and credit spend.
- Smart Mode settings screen with toggles.
- Minimal, privacy-first approach.

## 1) Install dependencies (in your Expo project root)
```bash
npx expo install expo-location expo-speech
npm i axios @tanstack/react-query zustand react-native-uuid
# If you don't have NativeWind (Tailwind) yet:
npm i nativewind tailwindcss
npx tailwindcss init
# Add to tailwind.config.js:
#   content: ["./App.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"]
```

## 2) Copy these folders into your project
Copy the `src/assistant` directory into your app's `src` directory.
If you don't have `src`, create it and then paste.

```
your-app/
  src/
    assistant/
      api/client.ts
      store/prefs.ts
      utils/greet.ts
      utils/location.ts
      utils/voice.ts
      screens/Chat.tsx
      screens/SettingsSmart.tsx
      components/EvidenceChips.tsx
```

## 3) Navigation
Add the two screens to your navigator (example with React Navigation tabs):
```tsx
// Example in src/navigation/AppNavigator.tsx
import Chat from '@/assistant/screens/Chat';
import SettingsSmart from '@/assistant/screens/SettingsSmart';

<Tab.Screen name="Chat" component={Chat} />
<Tab.Screen name="Smart" component={SettingsSmart} options={{ title: 'Smart Mode' }} />
```

> If you already have a Chat and Settings screen, either replace or mount these temporarily to test.

## 4) Environment
Expose your backend URL for the app:
- Expo (best): add to `app.config.js` or `app.json` as **extra** or use Expo public env:
  - `process.env.EXPO_PUBLIC_FOUNDATION_API_URL`
- For local dev, default is `http://127.0.0.1:8000`

## 5) Run
```bash
npx expo start
```

Open **Chat** tab and press **Win rate now (1 ⓒ)** to see a real response and TTS (if enabled).

## Notes
- All personalization is **opt-in** in the Settings Smart screen.
- We do **not** read photos or other apps; no background location; no always-on mic.
- You can later add STT (speech-to-text) via Whisper API or react-native-voice (bare config).

Enjoy!
