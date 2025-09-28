# 📱 ZmartBot Onboarding - Slide Interaction & Authentication Flow Documentation

## 🎯 Overview
The ZmartBot onboarding system implements a 9-step progressive slide system with conditional navigation, authentication flows, and Supabase email management.

---

## 📊 Slide Structure & Flow

### **Step 1: Welcome**
- **Purpose**: Introduction to ZmartyBrain
- **Actions**: Get Started button
- **Conditions**: None (always accessible)
- **Navigation**: Can only go forward

### **Step 2: Choose Authentication Method**
- **Purpose**: Select login/register method
- **Options**:
  1. **Google Authentication** (OAuth)
  2. **Email Authentication** (Traditional)
- **Conditions**: Must choose a method to proceed
- **Navigation**: Can go back to Step 1

### **Step 3: Email/Password Input**
- **Purpose**: Enter credentials
- **Login Flow**:
  - Email field
  - Password field
  - "Forgot Password?" link
- **Register Flow**:
  - Email field
  - Password field (with strength indicator)
  - Confirm password field
- **Conditions**: Valid email and password required
- **Navigation**: Can go back to Step 2

### **Step 4: Email Verification (OTP)**
- **Purpose**: Verify email with 6-digit code
- **Features**:
  - 6 separate input boxes
  - Auto-advance on input
  - Paste support for full code
  - "Resend Code" button (rate-limited: 5 attempts, 60s cooldown)
- **Conditions**: Must verify email to proceed
- **Navigation**: Cannot skip, can go back to Step 3

### **Step 5: Forgot Password Flow**
- **Purpose**: Reset password via email
- **Process**:
  1. Enter email address
  2. Receive reset link
  3. Click link to reset
  4. Enter new password
- **Navigation**: Can return to login

### **Step 6: Additional Information**
- **Purpose**: Collect user preferences
- **Fields**: Industry, use case, etc.
- **Conditions**: Optional fields
- **Navigation**: Can skip or go back

### **Step 7: Choose Pricing Tier**
- **Purpose**: Select subscription plan
- **Options**:
  - Starter ($0/month)
  - Professional ($29/month)
  - Enterprise ($99/month)
- **Conditions**: Must select a plan
- **Navigation**: Cannot proceed without selection

### **Step 8: Complete Profile**
- **Purpose**: Finalize user details
- **Fields**:
  - Full name (required)
  - Job title (optional)
  - Company (optional)
  - Industry (optional)
- **Conditions**: Name required
- **Navigation**: Can go back to Step 7

### **Step 9: Welcome Complete**
- **Purpose**: Onboarding success
- **Actions**: Launch Dashboard button
- **Navigation**: End of flow

---

## 🔒 Authentication Flows

### 1. **Google OAuth Flow**
```javascript
Step 2 → Google Sign-in → Auto-redirect → Step 6 (skips email verification)
```
- Clicking "Sign in with Google" opens OAuth popup
- On success: Automatically advances to Step 6
- On failure: Shows error with retry option

### 2. **Email Registration Flow**
```javascript
Step 2 → Step 3 (Register) → Step 4 (OTP) → Step 6 → Step 7 → Step 8 → Step 9
```
- Email/password validation
- OTP verification required
- Welcome email sent via Supabase

### 3. **Email Login Flow**
```javascript
Step 2 → Step 3 (Login) → Step 6 → Step 7 → Step 8 → Step 9
```
- Existing users skip OTP verification
- Direct progression after authentication

### 4. **Forgot Password Flow**
```javascript
Step 3 → Forgot Password → Email sent → Reset link → New password → Step 3 (Login)
```
- Triggered from Step 3 login form
- Supabase sends reset email
- User returns to login after reset

---

## 📧 Supabase Email Management

### **Email Types & Triggers**

1. **Welcome Email**
   - **Trigger**: Successful registration (Step 4 completion)
   - **Content**: Welcome message, getting started guide
   - **Supabase Function**: `auth.signUp()`

2. **Email Verification (OTP)**
   - **Trigger**: New registration (Step 3 → Step 4)
   - **Content**: 6-digit verification code
   - **Supabase Function**: `auth.signUp()` with `email` confirmation

3. **Password Reset Email**
   - **Trigger**: "Forgot Password" link (Step 3)
   - **Content**: Reset link valid for 1 hour
   - **Supabase Function**: `auth.resetPasswordForEmail()`

4. **Resend Verification Email**
   - **Trigger**: "Resend Code" button (Step 4)
   - **Rate Limit**: 5 attempts, 60-second cooldown
   - **Supabase Function**: `auth.resend()`

---

## 🎮 Navigation Rules & Conditions

### **Arrow Navigation (Keyboard)**
- **Left Arrow**: Previous step (if allowed)
- **Right Arrow**: Next step (if conditions met)
- **ESC Key**: Close modals/overlays

### **Touch Navigation (Mobile)**
- **Swipe Left**: Next step
- **Swipe Right**: Previous step
- **Swipe Indicators**: Visual feedback on swipe

### **Conditional Blocks**
```javascript
// Step-specific conditions that prevent navigation:

Step 2 → Step 3: Must select auth method
Step 3 → Step 4: Must have valid email/password
Step 4 → Step 6: Must verify email (cannot skip)
Step 7 → Step 8: Must select pricing tier
Step 8 → Step 9: Must enter name
```

### **Back Navigation Restrictions**
- Cannot go back from Step 4 if email not verified
- Cannot go back to Step 1 once authenticated
- Cannot skip mandatory steps (4, 7)

---

## 🔄 State Management

### **Session Persistence**
- User progress saved in SecureStorage
- Refreshing page maintains current step
- Authentication state preserved via Supabase session

### **Rate Limiting**
- OTP resend: 5 attempts max
- 60-second cooldown between attempts
- Browser fingerprinting prevents bypass

### **Error Handling**
- Network failures: Retry with exponential backoff
- Invalid credentials: Generic error messages (security)
- Session timeout: Automatic re-authentication prompt

---

## 🧪 Testing Scenarios

### **Scenario 1: New User Registration**
1. Start at Step 1
2. Choose Email auth (Step 2)
3. Enter new email/password (Step 3)
4. Receive OTP email
5. Enter code (Step 4)
6. Skip optional info (Step 6)
7. Select pricing tier (Step 7)
8. Complete profile (Step 8)
9. Reach welcome screen (Step 9)

### **Scenario 2: Existing User Login**
1. Start at Step 1
2. Choose Email auth (Step 2)
3. Enter existing credentials (Step 3)
4. Skip to Step 6 (no OTP needed)
5. Continue through remaining steps

### **Scenario 3: Google OAuth**
1. Start at Step 1
2. Choose Google auth (Step 2)
3. Complete OAuth flow
4. Jump to Step 6 (email pre-verified)
5. Continue through remaining steps

### **Scenario 4: Password Reset**
1. Reach Step 3 (login)
2. Click "Forgot Password?"
3. Enter email
4. Check email for reset link
5. Click link and set new password
6. Return to Step 3 to login

### **Scenario 5: Navigation Testing**
1. Use arrows to navigate forward/back
2. Try to skip mandatory steps (should fail)
3. Test swipe gestures on mobile
4. Verify conditions block inappropriate navigation

---

## 🚦 Current Implementation Status

### ✅ **Fully Implemented**
- All 9 steps with proper UI
- Google OAuth integration
- Email/password authentication
- OTP verification with rate limiting
- Password reset flow
- Resend verification code
- Arrow key navigation
- Touch/swipe support
- State persistence
- Error handling

### ⚠️ **Supabase Configuration Required**
- Email templates need customization in Supabase dashboard
- SMTP settings must be configured
- OAuth redirect URLs must be set
- Rate limiting rules should be configured

### 📝 **Email Template Locations in Supabase**
1. **Dashboard** → **Authentication** → **Email Templates**
   - Confirmation email (OTP)
   - Password reset email
   - Welcome email (if using custom)

2. **Dashboard** → **Authentication** → **Providers**
   - Google OAuth settings
   - Redirect URLs configuration

3. **Dashboard** → **Authentication** → **Settings**
   - Email rate limiting
   - Password requirements
   - Session duration

---

## 🔍 Live Testing Instructions

### **To Test the Complete Flow:**

1. **Visit**: https://vermillion-paprenjak-67497b.netlify.app/

2. **Test Registration**:
   - Click "Get Started"
   - Choose "Continue with Email"
   - Enter new email/password
   - Check email for OTP code
   - Enter code and continue

3. **Test Login**:
   - Use existing account
   - Should skip OTP step

4. **Test Google OAuth**:
   - Choose "Sign in with Google"
   - Complete Google login
   - Should skip to Step 6

5. **Test Password Reset**:
   - Go to login
   - Click "Forgot Password?"
   - Enter email
   - Check for reset email

6. **Test Navigation**:
   - Use arrow keys
   - Try going back at various steps
   - Test swipe on mobile
   - Verify conditional blocks work

---

## 📊 Monitoring & Analytics

The system tracks:
- Step completion rates
- Drop-off points
- Authentication method preferences
- Time spent per step
- Error occurrences
- Email delivery success

---

*Last Updated: 2025-01-28*
*System Version: 4.7.0*
*Total Bugs Fixed: 47*