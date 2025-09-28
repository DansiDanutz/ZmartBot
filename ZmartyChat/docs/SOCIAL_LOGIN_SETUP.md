# Social Login Setup Guide for Zmarty.me

## Overview
This guide will help you set up OAuth providers (Google, GitHub, Apple) for your Supabase project using the zmarty.me domain.

## Important URLs
- **Supabase Project URL**: `https://xhskmqsgtdhehzlvtuns.supabase.co`
- **Your App Domain**: `https://zmarty.me` (or `http://localhost:3000` for development)
- **Callback URL Pattern**: `https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback`

---

## 1. Google OAuth Setup

### Step 1: Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

### Step 2: Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen first if needed:
   - User Type: External
   - App name: Zmarty
   - User support email: support@zmarty.me
   - App domain: zmarty.me
   - Authorized domains: zmarty.me
   - Developer contact: your email

### Step 3: Create OAuth Client
1. Application type: "Web application"
2. Name: "Zmarty Web App"
3. Authorized JavaScript origins:
   ```
   https://zmarty.me
   http://localhost:3000
   http://localhost:3001
   ```
4. Authorized redirect URIs:
   ```
   https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback
   http://localhost:3000/auth/callback
   https://zmarty.me/auth/callback
   ```
5. Click "Create"
6. Save the Client ID and Client Secret

---

## 2. GitHub OAuth Setup

### Step 1: GitHub OAuth App
1. Go to GitHub Settings → [Developer settings](https://github.com/settings/developers)
2. Click "OAuth Apps" → "New OAuth App"

### Step 2: Configure OAuth App
- **Application name**: Zmarty
- **Homepage URL**: https://zmarty.me
- **Application description**: AI-Powered Trading Assistant
- **Authorization callback URL**:
  ```
  https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback
  ```
3. Click "Register application"
4. Generate a new client secret
5. Save the Client ID and Client Secret

---

## 3. Apple OAuth Setup (Optional)

### Prerequisites
- Apple Developer Account ($99/year)
- App ID configured for Sign in with Apple

### Step 1: Apple Developer Console
1. Go to [Apple Developer](https://developer.apple.com/)
2. Certificates, Identifiers & Profiles
3. Create an App ID with Sign in with Apple capability

### Step 2: Create Service ID
1. Create a Service ID for web authentication
2. Configure domains and return URLs:
   - Domain: zmarty.me
   - Return URL: https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback

### Step 3: Create Private Key
1. Keys → Create a key
2. Enable Sign in with Apple
3. Download the .p8 file

---

## 4. Configure Supabase

### Step 1: Access Auth Settings
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project (ZmartyBrain)
3. Go to Authentication → Providers

### Step 2: Enable Google Provider
1. Toggle "Google" to enabled
2. Add credentials:
   - **Client ID**: (from Google Cloud Console)
   - **Client Secret**: (from Google Cloud Console)
3. Click "Save"

### Step 3: Enable GitHub Provider
1. Toggle "GitHub" to enabled
2. Add credentials:
   - **Client ID**: (from GitHub OAuth App)
   - **Client Secret**: (from GitHub OAuth App)
3. Click "Save"

### Step 4: Configure Redirect URLs
1. Go to Authentication → URL Configuration
2. Add site URL: `https://zmarty.me`
3. Add redirect URLs:
   ```
   https://zmarty.me/auth/callback
   https://zmarty.me/dashboard
   http://localhost:3000/auth/callback
   http://localhost:3000/dashboard
   ```

---

## 5. Update Environment Variables

Add to your `.env.local`:

```bash
# OAuth Providers (Public Keys Only)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id

# Supabase Auth Redirect URL
NEXT_PUBLIC_AUTH_REDIRECT_URL=https://zmarty.me/auth/callback
```

---

## 6. Implementation Code

### Frontend (Next.js)

```typescript
// lib/supabase/auth.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Google Sign In
export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      },
    },
  })
  return { data, error }
}

// GitHub Sign In
export async function signInWithGitHub() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'github',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
      scopes: 'read:user user:email',
    },
  })
  return { data, error }
}

// Apple Sign In
export async function signInWithApple() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'apple',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  })
  return { data, error }
}
```

### Auth Callback Page

```typescript
// app/auth/callback/route.ts
import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )

    await supabase.auth.exchangeCodeForSession(code)
  }

  // Redirect to dashboard after successful login
  return NextResponse.redirect(`${requestUrl.origin}/dashboard`)
}
```

---

## 7. Testing

### Local Testing
1. Update your `/etc/hosts` file (optional):
   ```
   127.0.0.1 local.zmarty.me
   ```
2. Use `http://localhost:3000` for development
3. Test each provider login

### Production Testing
1. Deploy to your hosting (Vercel/Netlify/etc)
2. Ensure domain points to your app
3. Test with real accounts

---

## 8. Troubleshooting

### Common Issues

1. **"Redirect URI mismatch"**
   - Ensure callback URLs match exactly in provider settings
   - Check for trailing slashes
   - Verify http vs https

2. **"Invalid client"**
   - Double-check Client ID and Secret
   - Ensure credentials are in correct Supabase fields

3. **"User already registered"**
   - Check Supabase → Authentication → Users
   - User might have signed up with different provider

4. **CORS errors**
   - Add domain to Supabase allowed URLs
   - Check browser console for specific CORS policy

---

## 9. Security Notes

1. **Never expose** provider secret keys in frontend code
2. **Always use HTTPS** in production
3. **Restrict redirect URLs** to your domains only
4. **Enable 2FA** on provider accounts (Google, GitHub)
5. **Rotate secrets** periodically

---

## 10. Next Steps

After setup:
1. Customize the login UI
2. Add social login buttons to your app
3. Handle user profile data from providers
4. Set up user roles and permissions
5. Implement logout functionality
6. Add account linking (connect multiple providers)

---

## Support Resources

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Sign in with Apple](https://developer.apple.com/sign-in-with-apple/)

---

Last Updated: January 2025