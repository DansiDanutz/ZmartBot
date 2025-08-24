# 🚀 ZmartBot Professional Trading Platform

## 📁 **Project Structure**

```
project/
├── 🏗️  backend/           # Backend services and APIs
│   ├── 🔌 api/           # Main API server and routes
│   ├── 🔧 services/      # Business logic services  
│   ├── 🤖 agents/        # Trading and analysis agents
│   ├── 💾 database/      # Database schemas and models
│   ├── ⚡ cache/         # Cache management
│   ├── 🛠️  utils/        # Utilities and helpers
│   └── 📋 requirements.txt
│
├── 🎨 frontend/           # Frontend applications
│   ├── 📊 dashboard/     # Professional React dashboard
│   ├── 🧩 components/    # Reusable UI components
│   ├── 🎯 assets/        # Static assets
│   └── 💅 styles/        # CSS and styling
│
├── 🧩 modules/            # Specialized modules
│   ├── 🎣 kingfisher/    # Liquidation analysis
│   ├── 🔔 alerts/        # Alert system
│   ├── 💰 cryptoverse/   # Crypto data integration
│   ├── 🧠 grok-x/        # AI sentiment analysis
│   └── 📈 symbols/       # Symbol management
│
├── 📚 documentation/      # All documentation
│   ├── 🔌 api/           # API documentation
│   ├── 👥 user-guides/   # User guides and tutorials
│   ├── ⚙️  technical/     # Technical documentation
│   └── 🚀 deployment/    # Deployment guides
│
├── 🔧 scripts/           # Automation scripts
├── ⚙️  configs/          # Configuration files
├── 🛠️  tools/           # Development tools
└── 🧪 tests/            # Test suites
```

## 🚀 **Quick Start**

### **Start the Platform**
```bash
cd project/scripts/
./start_zmartbot_official.sh
```

### **Access Points**
- **🎛️ Dashboard**: http://localhost:3400
- **🔌 API**: http://localhost:8000
- **📋 API Docs**: http://localhost:8000/docs

### **Stop the Platform**
```bash
cd project/scripts/
./stop_zmartbot_official.sh
```

## 🏗️ **Backend Architecture**

### **Main API Server**
- **Location**: `backend/api/main.py`
- **Port**: 8000
- **Purpose**: Core trading platform API

### **Dashboard Server**  
- **Location**: `backend/api/professional_dashboard_server.py`
- **Port**: 3400
- **Purpose**: Serves React dashboard

### **Key Services**
- **Trading Engine**: Multi-agent trading system
- **Risk Management**: Position and risk analysis
- **Data Integration**: Multiple market data sources
- **AI Analysis**: OpenAI-powered insights

## 🎨 **Frontend Architecture**

### **Professional Dashboard**
- **Location**: `frontend/dashboard/`
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS + Custom styles
- **Features**: Real-time trading dashboard

## 🧩 **Modules**

### **🎣 KingFisher**
Liquidation heat map analysis using image processing

### **🔔 Alerts**
Real-time alert system with multiple notification channels

### **💰 Cryptoverse**
Cryptocurrency market data integration

### **🧠 Grok-X**
AI-powered sentiment analysis using X (Twitter) data

### **📈 Symbols**
Advanced symbol and portfolio management

## 📋 **Development**

### **Backend Development**
```bash
cd project/backend/api/
python run_dev.py
```

### **Frontend Development**
```bash
cd project/frontend/dashboard/
npm run dev
```

## 🔒 **Security**

- JWT authentication
- Rate limiting
- CORS protection
- Environment-based secrets
- API key management

---

**📞 Support**: Check documentation or create an issue
**🔗 License**: Proprietary - ZmartBot Trading Platform