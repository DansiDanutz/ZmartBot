# 📱 ZmartBot Mobile - Testing Guide

## Quick Start (5 minutes)

### Prerequisites
- iPhone/Android with Expo Go app installed
- Same WiFi network as your laptop

### Step 1: Start Servers
```bash
# Terminal 1 - Backend API
cd /Users/dansidanutz/Desktop/ZmartBot/zmart-foundation
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Mobile App
cd /Users/dansidanutz/Desktop/ZmartBot/zmartbot-mobile
npx expo start
```

### Step 2: Connect Phone
1. Download "Expo Go" from App Store/Google Play
2. Scan QR code from terminal with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

### Step 3: Test Features ✅

#### 🎯 Chat Screen
- Type "ETH" or "BTC" to request trading signals
- Watch credits get deducted (10 per signal)
- See AI-powered trading analysis with evidence

#### 💰 Credits Screen  
- View current balance and transaction history
- See credit spending from signal requests
- Mock purchase/earn flows

#### 🎪 Pools Screen
- Create new funding pools for specific topics
- Contribute credits to existing pools
- Track funding progress to goals

#### 🔔 Alerts Screen
- Toggle push notifications on/off
- Select symbols to watch (ETH, BTC, SOL, etc.)
- Configure alert rules (price changes, signals, pools)
- Choose notification plan (Basic/Premium)

#### 📜 History Screen
- Filter activity by type (All, Signals, Pools, Credits)
- View detailed transaction history
- Tap items for full details

## 🚀 Production Deployment

### Build Android APK
```bash
npx expo build:android
# or with EAS
eas build --platform android
```

### Build iOS IPA  
```bash
npx expo build:ios
# or with EAS
eas build --platform ios
```

## 🔧 Troubleshooting

### Can't Connect to API?
- Backend must be running on `http://127.0.0.1:8000`
- Check network connectivity
- Try restarting Metro bundler

### App Won't Load?
- Clear Expo cache: `npx expo start --clear`
- Restart Expo Go app
- Check for TypeScript errors in terminal

### Missing Features?
- Ensure all dependencies installed: `npm install`
- Check backend API status: `curl http://127.0.0.1:8000/v1/health`

## 📊 Backend API Status
- ✅ Health: http://127.0.0.1:8000/v1/health  
- ✅ Docs: http://127.0.0.1:8000/docs
- ✅ All endpoints working with mock data
- ✅ Database and caching operational

## 🎯 User Journey Test
1. Open app → Chat tab
2. Type "Show me ETH analysis" 
3. Credits deducted, signal shown with evidence
4. Go to Pools → Create "ETH Long Setup" pool
5. Contribute 25 credits to pool
6. Set up alerts for ETH price changes
7. Check history for all activities

**Expected Result**: Smooth, professional mobile trading experience! 🚀