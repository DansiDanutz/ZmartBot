# 🧪 ZmartyBrain Onboarding Flow - Complete Testing Guide

## 📍 Live URL: https://vermillion-paprenjak-67497b.netlify.app/

## ✅ Expected Flow (9 Steps)

### Step 1: Welcome
- **What to see**: Welcome screen with "Get Started" button
- **Action**: Click "Get Started"
- **Expected**: Move to Step 2

### Step 2: Authentication
- **What to see**: Email/Google tabs
- **Test Email Registration**:
  1. Enter email: test@example.com
  2. Enter password: TestPass123!
  3. Click "Register"
  4. **Expected**: Move to Step 4 (Email Verification)
- **Test Google OAuth**:
  1. Click "Continue with Google"
  2. Complete Google auth
  3. **Expected**: Move to Step 3 or 6 based on user state

### Step 3: Account Confirmation
- **What to see**: "Account created successfully"
- **Action**: Automatic progression or click Continue
- **Expected**: Move to Step 4 or 6

### Step 4: Email Verification
- **What to see**: 6-digit code input field
- **Actions**:
  1. Check email for code
  2. Enter 6-digit code
  3. Or click magic link in email
- **Expected**: Move to Step 6 (Tier Selection)

### Step 5: Password Reset (Optional)
- **What to see**: Password reset form
- **Action**: Only if user needs password reset
- **Expected**: Return to authentication

### Step 6: Choose Your Plan
- **What to see**: 3 tier cards (Starter/Professional/Enterprise)
- **Action**: Select a tier
- **Expected**: Move to Step 7

### Step 7: Complete Your Profile
- **What to see**: Profile form (Name, Country, Industry)
- **Action**: Fill form and click Complete
- **Expected**: Move to Step 8

### Step 8: Welcome Complete
- **What to see**: Success message, confetti animation
- **Action**: Click "Go to Dashboard"
- **Expected**: Complete onboarding

### Step 9: Final (Hidden)
- **What to see**: Should not be visible
- **Expected**: Redirect or completion

## 🔍 Common Issues & Fixes

### Issue 1: Stuck on Step 2 After Registration
**Symptom**: After registering, redirected back to Step 2
**Fix Applied**: Updated routing logic to detect new registrations
**Status**: ✅ FIXED in latest deployment

### Issue 2: Google OAuth Redirect Loop
**Symptom**: After Google auth, sent back to Step 2
**Fix Applied**: Proper user state detection for OAuth returns
**Status**: ✅ FIXED in latest deployment

### Issue 3: Email Verification Not Progressing
**Symptom**: Enter code but doesn't move forward
**Possible Causes**:
- Invalid code
- Session expired
- Network issue
**Debug**: Check browser console for errors

### Issue 4: Tier Selection Not Saving
**Symptom**: Select tier but not saved to database
**Fix**: Ensure `selected_tier` column exists in database
**Status**: ✅ Column added via SQL script

## 🛠️ Debugging Steps

### 1. Open Browser Console (F12)
```javascript
// Check current step
console.log('Current Step:', state.currentStep);

// Check user session
supabaseClient.auth.getSession().then(({data}) => console.log('Session:', data));

// Check user profile
supabaseClient.from('zmartychat_users').select('*').then(({data}) => console.log('Profile:', data));
```

### 2. Manual Navigation (Console)
```javascript
// Force navigation to specific step
state.goToStep(6, 'forward', true); // Go to tier selection

// Check navigation state
console.log('Can navigate:', state.canNavigateToStep(7));
```

### 3. Clear Session & Restart
```javascript
// Clear all data and restart
sessionStorage.clear();
localStorage.clear();
supabaseClient.auth.signOut();
location.reload();
```

## 📋 Test Checklist

- [ ] **New User - Email Registration**
  - [ ] Can register with email
  - [ ] Receive verification email
  - [ ] Enter 6-digit code
  - [ ] Select tier
  - [ ] Complete profile
  - [ ] Reach completion screen

- [ ] **New User - Google OAuth**
  - [ ] Can sign in with Google
  - [ ] Automatic email verification
  - [ ] Select tier
  - [ ] Complete profile
  - [ ] Reach completion screen

- [ ] **Returning User - Email**
  - [ ] Can sign in
  - [ ] Skip to appropriate step
  - [ ] Continue from last position

- [ ] **Returning User - Google**
  - [ ] Can sign in
  - [ ] Skip to appropriate step
  - [ ] Continue from last position

## 🚨 Critical Validations

1. **Email Format**: Must be valid email
2. **Password Strength**: Min 8 chars, mix of upper/lower/number
3. **Verification Code**: 6 digits only
4. **Profile Fields**: Name required, Country required

## 🔧 Quick Fixes

### If Navigation Broken:
1. Check browser console for errors
2. Clear cache and cookies
3. Try incognito mode
4. Check network tab for failed requests

### If Authentication Fails:
1. Verify Supabase project is running
2. Check redirect URLs in Supabase dashboard
3. Ensure cookies are enabled
4. Try different browser

### If Stuck on Any Step:
1. Open console and run:
   ```javascript
   state.goToStep(state.currentStep + 1, 'forward', true);
   ```
2. Check for JavaScript errors
3. Verify network connectivity

## 📊 Success Metrics

✅ **Working**: User can complete full flow from Step 1-8
✅ **Smooth**: No console errors during flow
✅ **Persistent**: Data saved to Supabase
✅ **Responsive**: Works on mobile and desktop
✅ **Secure**: Passwords validated, data encrypted

## 🎯 Final Test

1. Open: https://vermillion-paprenjak-67497b.netlify.app/
2. Complete registration with new email
3. Verify email
4. Select tier
5. Complete profile
6. Reach success screen
7. **All steps complete = SUCCESS!**

---

**Last Updated**: September 27, 2025
**Status**: Ready for Testing
**Deployment**: Live on Netlify