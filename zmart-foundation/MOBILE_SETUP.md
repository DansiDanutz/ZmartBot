# ZmartBot Mobile - Quick Start Guide

## API Backend Status: ✅ READY
- Server: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- All endpoints tested and working

## Mobile App Setup

### Option A: Expo/React Native (Recommended for MVP)
```bash
# Create new Expo app
npx create-expo-app zmart-mobile --template tabs
cd zmart-mobile

# Install API client dependencies  
npm install axios @react-native-async-storage/async-storage
npm install @expo/vector-icons expo-notifications

# Environment setup
echo "FOUNDATION_API_URL=http://127.0.0.1:8000" > .env.local
```

### Option B: Flutter
```bash
flutter create zmart_mobile
cd zmart_mobile

# Add dependencies to pubspec.yaml:
# http: ^1.1.0
# shared_preferences: ^2.2.2
# flutter_local_notifications: ^17.2.1
```

## App Architecture
```
zmart-mobile/
├── src/
│   ├── screens/
│   │   ├── ChatScreen.tsx      # /v1/signals/snapshot
│   │   ├── PoolsScreen.tsx     # /v1/pools
│   │   ├── AlertsScreen.tsx    # /v1/alerts  
│   │   ├── CreditsScreen.tsx   # /v1/credits
│   │   └── HistoryScreen.tsx   # User activity
│   ├── services/
│   │   └── api.ts              # Foundation API client
│   ├── components/
│   │   ├── SignalBubble.tsx    # Chat UI for signals
│   │   ├── PoolProgress.tsx    # Pool funding progress
│   │   └── CreditBalance.tsx   # Credits display
│   └── types/
│       └── api.ts              # TypeScript interfaces
```

## API Integration Checklist
- [ ] Chat: GET /v1/signals/snapshot?symbol=ETH
- [ ] Credits: GET /v1/credits?user_id={id}
- [ ] Spend: POST /v1/credits/spend (with X-Request-ID)
- [ ] Pools: POST /v1/pools, GET /v1/pools/{id}
- [ ] Alerts: POST /v1/alerts

## Next Milestone: Working Mobile App
1. Basic tab navigation ✅
2. API client setup ✅  
3. Chat screen with signal bubbles
4. Credits management
5. Pool participation UI
6. Push notifications setup

**Goal**: User can request ETH signal → spend credits → see evidence → join pools