# 🚨 URGENT SECURITY MIGRATION GUIDE

## IMMEDIATE ACTIONS REQUIRED

### ⚠️ CRITICAL: Your API Keys Have Been Compromised

All API keys that were hardcoded in your source code are now compromised and must be rotated immediately.

## Step 1: Rotate All API Keys (DO THIS NOW!)

### 1.1 KuCoin API Keys
1. Log into [KuCoin](https://www.kucoin.com)
2. Go to Settings → API Management
3. **DELETE** the compromised API key: `6888904828335c0001f5e7ea`
4. Create a NEW API key with appropriate permissions
5. Save the new credentials securely

### 1.2 Cryptometer API Key
1. Log into [Cryptometer](https://cryptometer.io)
2. Go to API Settings
3. **REVOKE** the compromised key: `k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2`
4. Generate a NEW API key
5. Save the new key securely

### 1.3 Binance API Keys
1. Log into [Binance](https://www.binance.com)
2. Go to Settings → API Management
3. **DELETE** the compromised API key starting with: `sXVeaqbRPBuFli69OSMTtkImE8LNfTL2Do...`
4. Create a NEW API key pair
5. Save the new credentials securely

### 1.4 OpenAI API Keys
1. Log into [OpenAI Platform](https://platform.openai.com)
2. Go to API Keys section
3. **REVOKE** both compromised keys:
   - Main key: `sk-proj-2WsROzNA0NrN531jsXDcwP8Gim...`
   - Trading key: `sk-proj-yPoiZiV5d6vdzouOkEQs64JU8u...`
4. Generate NEW API keys
5. Save the new keys securely

## Step 2: Set Up Environment Variables

### 2.1 Create your .env file
```bash
cd backend/zmart-api
cp .env.example .env
```

### 2.2 Edit the .env file with your NEW credentials
```bash
nano .env  # or use your preferred editor
```

Fill in all the required values with your NEW API keys:
```env
# Example (use your actual NEW keys)
KUCOIN_API_KEY=your_new_kucoin_api_key_here
KUCOIN_SECRET=your_new_kucoin_secret_here
KUCOIN_PASSPHRASE=your_new_kucoin_passphrase_here
CRYPTOMETER_API_KEY=your_new_cryptometer_key_here
BINANCE_API_KEY=your_new_binance_key_here
BINANCE_SECRET=your_new_binance_secret_here
OPENAI_API_KEY=your_new_openai_key_here
```

## Step 3: Verify Configuration

### 3.1 Test that environment variables are loading correctly
```bash
cd backend/zmart-api
python -c "from src.config.settings import settings; print('Config loaded successfully' if settings.CRYPTOMETER_API_KEY else 'ERROR: API keys not loading')"
```

### 3.2 Verify .gitignore is working
```bash
git status
# The .env file should NOT appear in the list
# If it does appear, run: git rm --cached .env
```

## Step 4: Clean Git History (IMPORTANT!)

Your git history still contains the compromised keys. You need to clean it:

### Option A: If repository is private and not shared
```bash
# This is destructive - make a backup first!
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/zmart-api/src/config/settings.py" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to remote
git push origin --force --all
git push origin --force --tags
```

### Option B: Start fresh (RECOMMENDED)
1. Archive current repository
2. Create new repository
3. Copy only necessary files (excluding .git folder)
4. Initialize new git repository
5. Commit clean code without keys

## Step 5: Security Best Practices Going Forward

### 5.1 Never hardcode credentials
- Always use environment variables
- Use `.env` files for local development
- Use secure secret management in production (AWS Secrets Manager, Azure Key Vault, etc.)

### 5.2 Use different keys for different environments
```env
# Development
KUCOIN_API_KEY=dev_key_with_limited_permissions

# Production (use secret manager)
KUCOIN_API_KEY=${SECRET_MANAGER_KUCOIN_KEY}
```

### 5.3 Implement API key rotation schedule
- Rotate keys every 90 days
- Keep track of key creation dates
- Use monitoring to detect unauthorized usage

### 5.4 Set up pre-commit hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Install and configure:
```bash
pip install pre-commit
pre-commit install
```

## Step 6: Monitor for Unauthorized Usage

### Check your API usage immediately:
1. **KuCoin**: Check API usage logs for any unauthorized trades
2. **Binance**: Review API access history
3. **OpenAI**: Check usage dashboard for unexpected charges
4. **Cryptometer**: Monitor API call logs

## Step 7: Update Your Team

If you're working with others:
1. Notify all team members about the security breach
2. Ensure everyone updates their local `.env` files
3. Review access permissions for all services
4. Consider implementing 2FA on all exchange accounts

## Verification Checklist

- [ ] All API keys rotated on respective platforms
- [ ] New keys added to `.env` file
- [ ] `.env` file is NOT tracked by git
- [ ] Old keys removed from all source files
- [ ] Git history cleaned or repository recreated
- [ ] Pre-commit hooks installed
- [ ] Team members notified
- [ ] API usage monitored for unauthorized access

## Emergency Contacts

If you detect unauthorized usage:
- **KuCoin Support**: https://www.kucoin.com/support
- **Binance Support**: https://www.binance.com/en/support
- **OpenAI Support**: support@openai.com

## Summary of Changes Made

1. ✅ Removed hardcoded API keys from `src/config/settings.py`
2. ✅ Updated `src/services/kucoin_service.py` to use environment variables
3. ✅ Created `.env.example` template file
4. ✅ Updated `.gitignore` to exclude all sensitive files
5. ✅ Created this security migration guide

## Next Steps

After completing the security migration:
1. Review the `PROJECT_AUDIT_DEEP_DIVE.md` for other critical issues
2. Implement proper error handling for missing API keys
3. Add validation to ensure all required environment variables are set
4. Consider implementing a secret management service for production

---

**Remember**: Security is not a one-time fix. Implement these practices as part of your development workflow to prevent future incidents.