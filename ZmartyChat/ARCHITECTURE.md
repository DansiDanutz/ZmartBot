# 🚀 ZmartTrade App Architecture

## Overview
ZmartTrade is a WhatsApp-style trading application with AI-powered chat, featuring a comprehensive onboarding process, dual theme support (dark/light), and full MCP integration with Claude.

## 🎨 Design System

### Brand Colors
- **Primary Orange**: #FF6B35 (Vibrant Trading Orange)
- **Primary Green**: #00D084 (Success/Profit Green)
- **Dark Mode Background**: #0B0E11
- **Light Mode Background**: #FFFFFF
- **Chat Bubbles**:
  - User: Orange gradient
  - Zmarty: Green gradient

### Typography
- Font Family: Inter, -apple-system, system-ui
- Sizes: 12px, 14px, 16px, 20px, 24px, 32px

## 📱 App Structure

```
ZmartTrade/
├── index.html                 # Main entry point
├── package.json              # Dependencies
├── mcp.json                  # MCP configuration
├── src/
│   ├── app.js               # Main application logic
│   ├── onboarding.js        # Onboarding flow
│   ├── chat.js              # Chat functionality
│   └── auth.js              # Authentication
├── components/
│   ├── Onboarding/
│   │   ├── Welcome.js       # Welcome screen
│   │   ├── NameInput.js     # Name collection
│   │   ├── PhoneEmail.js    # Phone/Email input
│   │   └── Verification.js  # OTP verification
│   ├── Chat/
│   │   ├── Header.js        # WhatsApp-style header
│   │   ├── MessageList.js   # Message container
│   │   ├── MessageBubble.js # Individual messages
│   │   ├── InputBar.js      # Message input
│   │   └── Menu.js          # Three-dot menu
│   └── Common/
│       ├── ThemeToggle.js   # Dark/Light mode
│       └── Loader.js        # Loading states
├── styles/
│   ├── main.css            # Main styles
│   ├── themes.css          # Theme definitions
│   └── animations.css      # Animations
├── services/
│   ├── api.js              # API client
│   ├── websocket.js        # Real-time connection
│   └── storage.js          # Local storage
├── mcp/
│   ├── server.js           # MCP server
│   └── tools.js            # MCP tool definitions
└── utils/
    ├── validators.js       # Input validation
    └── formatters.js       # Data formatting
```

## 🔄 User Flow

### 1. Onboarding Flow
```
Start → Welcome Screen → Name Input → Phone/Email → Verification → Main Chat
```

### 2. Features by Screen

#### Welcome Screen
- App logo animation
- "Get Started" button
- Theme toggle (top-right)

#### Name Input
- "What should Zmarty call you?"
- Personalized greeting preview
- Continue button

#### Phone/Email Registration
- Toggle between phone/email
- Country code selector (for phone)
- Real-time validation
- Send OTP button

#### Verification
- 6-digit OTP input
- Resend timer (60s)
- Auto-verify on complete

#### Main Chat (WhatsApp Clone)
- **Header**: Profile pic, "Zmarty", status, video call, voice call, menu
- **Chat Area**: Message bubbles with timestamps, read receipts
- **Input Bar**: Attachment, message input, emoji, voice note, send
- **Menu**: New chat, Settings, Theme, Help, Logout

## 💬 Chat Features

### Message Types
1. Text messages
2. Trading cards (price updates)
3. Charts/graphs
4. Voice notes
5. Documents (reports)
6. Quick action buttons

### WhatsApp Features to Implement
- Double tick read receipts
- "Typing..." indicator
- Message timestamps
- Date separators
- Swipe to reply
- Long press to select
- Search in chat
- Star messages

## 🔌 MCP Integration

### Available Tools
1. `get_market_data` - Real-time prices
2. `analyze_trading_signal` - AI signals
3. `get_portfolio_status` - Portfolio overview
4. `execute_trade` - Place orders
5. `get_risk_analysis` - Risk metrics
6. `get_news` - Market news
7. `set_alerts` - Price alerts
8. `get_chart` - Price charts

### Claude Integration Flow
```
User Message → MCP Server → Claude API → Tool Execution → Response → Chat UI
```

## 🗄️ Data Models

### User Model
```javascript
{
  id: "uuid",
  name: "John Doe",
  phone: "+1234567890",
  email: "john@example.com",
  avatar: "url",
  preferences: {
    theme: "dark",
    language: "en",
    notifications: true
  },
  createdAt: "timestamp"
}
```

### Message Model
```javascript
{
  id: "uuid",
  sender: "user|zmarty",
  type: "text|card|chart|voice|document",
  content: "...",
  timestamp: "ISO 8601",
  status: "sending|sent|delivered|read",
  replyTo: "messageId",
  metadata: {}
}
```

## 🔐 Security Features

1. **Authentication**: JWT tokens
2. **Encryption**: End-to-end for sensitive data
3. **Session Management**: Auto-logout after inactivity
4. **Input Validation**: XSS protection
5. **Rate Limiting**: API call limits
6. **2FA**: Optional two-factor auth

## 📱 Responsive Design

### Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

### Mobile-First Approach
- Touch-friendly buttons (min 44px)
- Swipe gestures
- Bottom navigation
- Keyboard-aware input

## ⚡ Performance Optimizations

1. **Lazy Loading**: Components load on demand
2. **Virtual Scrolling**: For long message lists
3. **Image Optimization**: WebP format, lazy load
4. **Code Splitting**: Separate bundles
5. **Service Worker**: Offline capability
6. **WebSocket**: Real-time updates

## 🚀 Deployment

### Tech Stack
- Frontend: Vanilla JS / React (optional)
- Backend: Node.js + Express
- Database: Supabase
- Real-time: WebSocket
- AI: Claude API via MCP
- Hosting: Vercel/Netlify

### Environment Variables
```env
ANTHROPIC_API_KEY=xxx
SUPABASE_URL=xxx
SUPABASE_ANON_KEY=xxx
JWT_SECRET=xxx
TWILIO_SID=xxx (for SMS)
TWILIO_TOKEN=xxx
```

## 📊 Analytics & Monitoring

1. User engagement metrics
2. Message volume tracking
3. API performance monitoring
4. Error tracking (Sentry)
5. User feedback collection

## 🔄 Next Steps

1. Set up project structure ✅
2. Create onboarding screens
3. Build WhatsApp UI clone
4. Implement theme system
5. Set up MCP server
6. Create backend API
7. Add real-time messaging
8. Integrate Claude AI
9. Test & deploy

---

This architecture provides a solid foundation for building a professional trading app with WhatsApp-like UX and powerful AI capabilities.