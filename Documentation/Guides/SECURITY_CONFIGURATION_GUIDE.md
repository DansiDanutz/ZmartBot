# 🔐 ZmartBot Security Configuration Guide

## 🛡️ **Environment Variables Setup**

For security reasons, all API keys and sensitive configuration must be set as environment variables, **NOT** hardcoded in the source code.

### **Required Environment Variables**

#### **OpenAI Configuration (Required for AI Analysis)**
```bash
export OPENAI_API_KEY="sk-proj-your-openai-api-key-here"
export OPENAI_API_KEY_TRADING="sk-proj-your-openai-trading-api-key-here"
```

#### **Cryptometer API Configuration (Required for Market Data)**
```bash
export CRYPTOMETER_API_KEY="your-cryptometer-api-key-here"
```

#### **KuCoin API Configuration (Required for Trading)**
```bash
export KUCOIN_API_KEY="your-kucoin-api-key-here"
export KUCOIN_API_SECRET="your-kucoin-api-secret-here"
export KUCOIN_API_PASSPHRASE="your-kucoin-passphrase-here"
```

#### **Database Configuration**
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/zmartbot"
export REDIS_URL="redis://localhost:6379/0"
```

#### **Server Configuration**
```bash
export DEBUG="false"
export LOG_LEVEL="INFO"
export PORT="8000"
```

#### **Security Configuration**
```bash
export SECRET_KEY="your-secret-key-here"
export JWT_SECRET="your-jwt-secret-here"
```

### **Setup Methods**

#### **Method 1: Shell Environment (Recommended for Development)**
```bash
# Add to your ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="your-actual-key-here"
export OPENAI_API_KEY_TRADING="your-actual-trading-key-here"
export CRYPTOMETER_API_KEY="k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"

# Reload your shell
source ~/.bashrc  # or source ~/.zshrc
```

#### **Method 2: .env File (Local Development)**
Create a `.env` file in the project root:
```bash
# .env file (DO NOT COMMIT TO GIT)
OPENAI_API_KEY=your-actual-key-here
OPENAI_API_KEY_TRADING=your-actual-trading-key-here
CRYPTOMETER_API_KEY=k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2
```

#### **Method 3: Docker Environment (Production)**
```bash
docker run -e OPENAI_API_KEY="your-key" -e CRYPTOMETER_API_KEY="your-key" zmartbot
```

### **🚨 Security Best Practices**

#### **✅ DO:**
- Store API keys in environment variables
- Use different keys for development/production
- Rotate API keys regularly
- Use `.env` files for local development (add to `.gitignore`)
- Use secrets management in production (AWS Secrets Manager, etc.)

#### **❌ DON'T:**
- Hardcode API keys in source code
- Commit `.env` files to Git
- Share API keys in chat/email
- Use production keys in development
- Store keys in plain text files

### **🔧 Configuration Verification**

To verify your configuration is working:

```bash
# Check if environment variables are set
echo $OPENAI_API_KEY
echo $CRYPTOMETER_API_KEY

# Run the configuration test
cd backend/zmart-api
python -c "from src.config.settings import settings; print('✅ Configuration loaded successfully')"
```

### **🎯 API Key Sources**

#### **OpenAI API Keys**
- Get from: https://platform.openai.com/api-keys
- Format: `sk-proj-...`
- Required for: AI analysis, report generation

#### **Cryptometer API Key**
- Get from: https://cryptometer.io
- Current key: `k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2`
- Required for: Market data analysis

#### **KuCoin API Keys**
- Get from: https://www.kucoin.com/account/api
- Required for: Trading operations
- Use 'Zmart' or 'ZmartBot' sub-accounts only

### **🛠️ Troubleshooting**

#### **Common Issues:**

1. **"API key not found" error:**
   ```bash
   # Check if environment variable is set
   echo $OPENAI_API_KEY
   
   # If empty, set it:
   export OPENAI_API_KEY="your-key-here"
   ```

2. **"Invalid API key" error:**
   - Verify the key format is correct
   - Check if the key has proper permissions
   - Ensure no extra spaces or characters

3. **Configuration not loading:**
   ```bash
   # Restart your terminal/shell
   # Or reload the environment
   source ~/.bashrc
   ```

### **🔒 Production Deployment**

For production environments:

1. **Use Secrets Management:**
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager
   - HashiCorp Vault

2. **Container Secrets:**
   ```yaml
   # docker-compose.yml
   services:
     zmartbot:
       environment:
         - OPENAI_API_KEY_FILE=/run/secrets/openai_key
       secrets:
         - openai_key
   
   secrets:
     openai_key:
       external: true
   ```

3. **Kubernetes Secrets:**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: zmartbot-secrets
   data:
     openai-api-key: <base64-encoded-key>
   ```

### **📋 Security Checklist**

- [ ] All API keys removed from source code
- [ ] Environment variables configured
- [ ] `.env` file added to `.gitignore`
- [ ] API keys tested and working
- [ ] Different keys for dev/prod environments
- [ ] Regular key rotation scheduled
- [ ] Access logging enabled
- [ ] Rate limiting configured

---

**🚨 CRITICAL: Never commit API keys to version control. Always use environment variables or secrets management systems.**

*Last Updated: January 31, 2025*