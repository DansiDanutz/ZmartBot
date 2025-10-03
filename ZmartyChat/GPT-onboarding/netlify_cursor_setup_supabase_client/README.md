# 🚀 Netlify + Cursor Setup Guide

This package contains everything needed to get your project deployed with **Netlify**, **Supabase**, **GitHub Actions**, and managed by **Cursor**.

---

## 📂 Included Files
- **netlify.toml** → Build & deploy configuration for Netlify.
- **Netlify_Deploy_Rules.mdc** → Cursor rules to handle Netlify builds automatically.
- **.env.example** → Example environment variables (Supabase, Resend, Google Cloud, Netlify).
- **package.json** → Starter scaffold with build script.
- **index.html** + **src/** → Minimal Vite app scaffold.
- **src/lib/supabase.js** → Supabase client boilerplate.
- **.github/workflows/deploy.yml** → GitHub Actions workflow for automatic deploys.

---

## ⚙️ Step 1: Environment Variables

Configure in **Netlify → Project configuration → Environment variables** and in **GitHub → Repo → Settings → Secrets → Actions**.

### 🔑 Supabase
- `VITE_SUPABASE_URL` → your Supabase project URL (public).
- `VITE_SUPABASE_ANON_KEY` → your Supabase anon key (public).  
- `SUPABASE_SERVICE_ROLE_KEY` → private, full-access key. Only for backend/server functions. **Never expose in frontend.**

### 🔑 SMTP (Resend)
- `RESEND_API_KEY` → API key for Resend.

### 🔑 Google Cloud
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`

### 🔑 Netlify
- `NETLIFY_AUTH_TOKEN` → personal token (for GitHub Actions).
- `NETLIFY_SITE_ID` → your site ID (e.g. `vermillion-paprenjak-67497b`).

### Optional
- `NODE_ENV=production`
- `PORT=3000`

---

## ⚙️ Step 2: Supabase Client Usage

In your code you can now import the preconfigured Supabase client:

```js
import { supabase } from './src/lib/supabase.js'

async function loadData() {
  const { data, error } = await supabase.from('profiles').select('*')
  console.log(data, error)
}
```

---

✅ Done! You can now use Supabase + Netlify + Cursor with minimal setup.
