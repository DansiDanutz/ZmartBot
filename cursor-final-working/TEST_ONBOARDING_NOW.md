# 🚀 TEST YOUR ONBOARDING - STEP BY STEP

## ✅ Chrome DevTools MCP Installed!
- **Version**: 0.4.0
- **Location**: /usr/local/lib (globally installed)
- **Status**: Ready to use

## 📋 How to Test Your Onboarding

### 1. Open Chrome & Navigate
```bash
# Open your deployed site
open https://vermillion-paprenjak-67497b.netlify.app/
```

### 2. Open Developer Console (F12)

### 3. Paste Test Script
Copy and paste the entire contents of `browser-test-script.js` into the console

### 4. Run Commands

**Quick Diagnostic:**
```javascript
diagnoseOnboarding()
```

**Check Current Step:**
```javascript
checkCurrentStep()
```

**See What's Visible:**
```javascript
getVisibleElements()
```

**Force Navigation (if stuck):**
```javascript
// Go to specific step (1-9)
state.goToStep(6, 'forward', true)  // Example: go to tier selection
```

## 🧪 Manual Test Flow

### Step 1: Welcome
- ✅ Should see: "Welcome to ZmartyBrain"
- ✅ Click: "Get Started"
- ❓ If stuck: `state.goToStep(2, 'forward', true)`

### Step 2: Authentication
- ✅ Register with new email
- ✅ Or use Google Sign-in
- ❓ If stuck after registration: Check console for errors

### Step 3: Confirmation
- ✅ Should show briefly
- ✅ Auto-progress to Step 4

### Step 4: Email Verification
- ✅ Check email for 6-digit code
- ✅ Enter code in boxes
- ❓ Skip if needed: `state.goToStep(6, 'forward', true)`

### Step 5: Password Reset (Optional)
- ⏭️ Usually skipped

### Step 6: Choose Tier
- ✅ Select: Starter/Professional/Enterprise
- ✅ Should save and progress

### Step 7: Complete Profile
- ✅ Fill: Name, Country, Industry
- ✅ Click: Complete

### Step 8: Success!
- ✅ See: Confetti animation
- ✅ Complete message

## 🔧 If Something Breaks

### Reset Everything:
```javascript
sessionStorage.clear();
localStorage.clear();
supabaseClient.auth.signOut();
location.reload();
```

### Check for Errors:
```javascript
// See all console errors
diagnoseOnboarding();

// Check Supabase connection
supabaseClient.auth.getSession().then(console.log);

// Check database
supabaseClient.from('zmartychat_users').select('*').then(console.log);
```

### Force Complete Flow (Testing):
```javascript
// Skip through all steps quickly
async function skipToEnd() {
    for(let i = 1; i <= 8; i++) {
        state.goToStep(i, 'forward', true);
        await new Promise(r => setTimeout(r, 1000));
        console.log(`Step ${i} completed`);
    }
}
skipToEnd();
```

## 📊 Expected Results

✅ **PASS**: Can navigate from Step 1 to Step 8
✅ **PASS**: Data saves to Supabase
✅ **PASS**: No console errors
✅ **PASS**: Mobile responsive
✅ **PASS**: Auth works (Email or Google)

## 🚨 Current Known Issues

1. **Leaked Password Protection**: Not visible in dashboard (using client-side validation instead)
2. **Email Verification**: Requires real email - use test mode to skip
3. **Google OAuth**: Must be tested with real Google account

## 💡 Quick Test (No Email Required)

```javascript
// Bypass email verification for testing
async function quickTest() {
    // Start
    state.goToStep(1, 'forward', true);
    await new Promise(r => setTimeout(r, 1000));

    // Skip auth
    state.goToStep(6, 'forward', true);
    await new Promise(r => setTimeout(r, 1000));

    // Select tier
    document.querySelector('.tier-card').click();
    await new Promise(r => setTimeout(r, 1000));

    // Skip to profile
    state.goToStep(7, 'forward', true);
    await new Promise(r => setTimeout(r, 1000));

    // Fill profile
    document.querySelector('#fullName').value = 'Test User';
    document.querySelector('#country').value = 'USA';
    document.querySelector('#industry').value = 'Tech';

    // Complete
    document.querySelector('#completeBtn').click();
}

// Run it
quickTest();
```

---

**Ready to test!** Open Chrome, go to your site, and use these commands in the console.