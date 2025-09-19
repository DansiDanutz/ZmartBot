# 🎯 EXACT STEP-BY-STEP PLAN TO COMPLETE ONBOARDING

## CURRENT STATE (What We Have Working NOW)
✅ **Slide 1**: Welcome - WORKING
✅ **Slide 2**: Multi LLM - WORKING
✅ **Slide 3**: Crypto Portfolio - WORKING
✅ **Slide 4**: Registration with Progressive Reveal - WORKING (fields appear when typing)
✅ **Slide 5**: Email Verification UI - WORKING (but no OTP codes arriving)
❌ **Slide 6**: Tier Selection - NOT IMPLEMENTED
❌ **Slide 7**: Profile Setup - NOT IMPLEMENTED

## THE PROBLEM
- Supabase is sending MAGIC LINKS instead of 6-DIGIT CODES
- We have the UI ready for 6-digit codes but Supabase isn't configured properly

## EXACT STEPS TO FIX (DO IN THIS ORDER)

### STEP 1: Configure Supabase Email Template (5 minutes)
1. Go to https://asjtxrmftmutcsnqgidy.supabase.co/dashboard
2. Navigate to: **Authentication** → **Email Templates**
3. Select template type: **Magic Link**
4. Replace the ENTIRE template with:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
    .container { background: white; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 10px; }
    .logo { text-align: center; font-size: 32px; color: #0066ff; margin-bottom: 20px; }
    .code-box { background: #f0f0f0; padding: 25px; text-align: center; border-radius: 8px; margin: 20px 0; }
    .code { font-size: 36px; letter-spacing: 10px; font-weight: bold; color: #333; }
    .footer { text-align: center; color: #666; font-size: 14px; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">🤖 Zmarty</div>
    <h2>Your Verification Code</h2>
    <p>Hi there! Please enter this code in the Zmarty app to complete your registration:</p>
    <div class="code-box">
      <div class="code">{{ .Token }}</div>
    </div>
    <p>This code will expire in 60 minutes.</p>
    <div class="footer">
      If you didn't request this code, please ignore this email.
    </div>
  </div>
</body>
</html>
```
5. Click **Save**

### STEP 2: Update Supabase Auth Settings (2 minutes)
1. Still in Supabase Dashboard
2. Go to: **Authentication** → **Providers** → **Email**
3. Make sure these are ENABLED:
   - ✅ Enable Email provider
   - ✅ Enable email confirmations
4. Under **Email OTP Settings**:
   - Set expiry to: 3600 (60 minutes)
   - Max attempts: 5

### STEP 3: Test Registration Flow (3 minutes)
1. Open: http://localhost:3000/ZmartyUserApp/index.html
2. Click through to Slide 4
3. Register with a REAL email (not test@example.com):
   - Type email → password field appears ✓
   - Type password → confirm field appears ✓
   - Type confirm → register button appears ✓
4. Click Register
5. Check email for 6-DIGIT CODE (not magic link)
6. Enter code on Slide 5
7. Should proceed to Slide 6

### STEP 4: Implement Slide 6 - Tier Selection (10 minutes)
Update `/ZmartyUserApp/index.html` - Add this after slide-5:

```html
<!-- Slide 6: Choose Your Tier -->
<div class="slide" id="slide-6">
    <div class="slide-content">
        <h1 class="slide-title">Choose Your Tier</h1>
        <p class="slide-subtitle">Select the plan that fits you</p>

        <div class="tier-options">
            <div class="tier-card" onclick="selectTier('free')">
                <div class="tier-header">
                    <h3>Free</h3>
                    <p class="tier-price">$0/month</p>
                </div>
                <ul class="tier-features">
                    <li>✓ Basic AI insights</li>
                    <li>✓ 5 trades per day</li>
                    <li>✓ Community support</li>
                </ul>
            </div>

            <div class="tier-card featured" onclick="selectTier('pro')">
                <div class="tier-badge">POPULAR</div>
                <div class="tier-header">
                    <h3>Pro</h3>
                    <p class="tier-price">$29/month</p>
                </div>
                <ul class="tier-features">
                    <li>✓ Advanced AI analysis</li>
                    <li>✓ Unlimited trades</li>
                    <li>✓ Priority support</li>
                    <li>✓ Custom alerts</li>
                </ul>
            </div>

            <div class="tier-card" onclick="selectTier('premium')">
                <div class="tier-header">
                    <h3>Premium</h3>
                    <p class="tier-price">$99/month</p>
                </div>
                <ul class="tier-features">
                    <li>✓ All AI models</li>
                    <li>✓ API access</li>
                    <li>✓ White-glove support</li>
                    <li>✓ Custom strategies</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

Add to `onboarding-slides.js`:
```javascript
window.selectTier = async function(tier) {
    // Save tier selection
    sessionStorage.setItem('selected_tier', tier);

    // Update user profile
    const result = await UserService.updateTier(tier);

    if (result.success) {
        // Move to profile setup
        nextSlide();
    }
};
```

### STEP 5: Implement Slide 7 - Profile Setup (10 minutes)
Update `/ZmartyUserApp/index.html` - Add this after slide-6:

```html
<!-- Slide 7: Complete Your Profile -->
<div class="slide" id="slide-7">
    <div class="slide-content">
        <h1 class="slide-title">Complete Your Profile</h1>
        <p class="slide-subtitle">Tell us about yourself</p>

        <div class="profile-form">
            <div class="input-group">
                <label>Your Name</label>
                <input type="text"
                       id="profile-name"
                       placeholder="Enter your name"
                       class="profile-input">
            </div>

            <div class="input-group">
                <label>Country</label>
                <select id="profile-country" class="profile-input">
                    <option value="">Select your country</option>
                    <option value="US">United States</option>
                    <option value="UK">United Kingdom</option>
                    <option value="CA">Canada</option>
                    <option value="AU">Australia</option>
                    <option value="DE">Germany</option>
                    <option value="FR">France</option>
                    <option value="ES">Spain</option>
                    <option value="IT">Italy</option>
                    <option value="JP">Japan</option>
                    <option value="CN">China</option>
                    <option value="IN">India</option>
                    <option value="BR">Brazil</option>
                    <option value="OTHER">Other</option>
                </select>
            </div>

            <button class="complete-btn" onclick="completeProfile()">
                Start Trading →
            </button>
        </div>
    </div>
</div>
```

Add to `onboarding-slides.js`:
```javascript
window.completeProfile = async function() {
    const name = document.getElementById('profile-name').value;
    const country = document.getElementById('profile-country').value;

    if (!name || !country) {
        alert('Please fill in all fields');
        return;
    }

    // Save profile
    const result = await UserService.updateProfile(name, country);

    if (result.success) {
        // Redirect to dashboard
        window.location.href = 'dashboard.html';
    }
};
```

### STEP 6: Add Required CSS (5 minutes)
Add to `onboarding-slides.css`:

```css
/* Tier Selection Styles */
.tier-options {
    display: flex;
    gap: 20px;
    margin-top: 30px;
}

.tier-card {
    flex: 1;
    background: rgba(255,255,255,0.05);
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    position: relative;
    transition: all 0.3s;
}

.tier-card:hover {
    background: rgba(255,255,255,0.08);
    border-color: #0066ff;
    transform: translateY(-2px);
}

.tier-card.featured {
    border-color: #0066ff;
    background: rgba(0,102,255,0.1);
}

.tier-badge {
    position: absolute;
    top: -10px;
    right: 20px;
    background: #0066ff;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}

.tier-header h3 {
    color: white;
    font-size: 20px;
    margin-bottom: 5px;
}

.tier-price {
    color: #0066ff;
    font-size: 24px;
    font-weight: bold;
}

.tier-features {
    list-style: none;
    padding: 0;
    margin-top: 20px;
}

.tier-features li {
    color: rgba(255,255,255,0.8);
    padding: 8px 0;
    font-size: 14px;
}

/* Profile Form Styles */
.profile-form {
    max-width: 400px;
    margin: 30px auto 0;
}

.input-group {
    margin-bottom: 20px;
}

.input-group label {
    display: block;
    color: rgba(255,255,255,0.7);
    margin-bottom: 8px;
    font-size: 14px;
}

.profile-input {
    width: 100%;
    padding: 14px;
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    color: white;
    font-size: 16px;
}

.profile-input:focus {
    border-color: #0066ff;
    outline: none;
}

.complete-btn {
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, #0066ff, #00b4d8);
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 20px;
}
```

### STEP 7: Final Testing Checklist (5 minutes)
Run through this EXACT sequence:

1. **Clear browser data** (localStorage, sessionStorage, cookies)
2. Go to: http://localhost:3000/ZmartyUserApp/index.html
3. Test each slide:
   - [ ] Slide 1: Welcome → Click "Get Started"
   - [ ] Slide 2: Multi LLM → Click "Next"
   - [ ] Slide 3: Crypto → Click "Next"
   - [ ] Slide 4: Registration
     - [ ] Type email → password field appears
     - [ ] Type password → confirm field appears
     - [ ] Type confirm → register button appears
     - [ ] Click Register → moves to slide 5
   - [ ] Slide 5: Verification
     - [ ] Check email for 6-DIGIT CODE
     - [ ] Enter code → moves to slide 6
   - [ ] Slide 6: Tier Selection
     - [ ] Select a tier → moves to slide 7
   - [ ] Slide 7: Profile
     - [ ] Fill name & country
     - [ ] Click "Start Trading" → redirects to dashboard

## ⚠️ IF EMAIL STILL SHOWS MAGIC LINK

This means Supabase didn't save the template properly. Try:

1. **Alternative Template Location**:
   - Go to: Authentication → Email Templates → **Confirm signup**
   - Paste the same template there too

2. **Check Email Provider**:
   - Go to: Project Settings → Auth
   - Check if using Custom SMTP or Supabase default
   - If custom SMTP, might need different template format

3. **Force Token in URL**:
   - As last resort, we can extract token from magic link URL
   - The link contains: `...token=123456&...`
   - We parse and use that

## 🎯 SUCCESS CRITERIA

✅ User can register with progressive reveal
✅ User receives 6-digit code (not magic link)
✅ User can verify with the code
✅ User can select tier
✅ User can complete profile
✅ User lands on dashboard.html

## TIME ESTIMATE
- Total time: ~40 minutes
- Supabase config: 7 minutes
- Implementation: 20 minutes
- Testing: 10 minutes
- Buffer: 3 minutes

## IMPORTANT NOTES
1. Use REAL email addresses for testing
2. Check SPAM folder if email doesn't arrive
3. Supabase free tier = 3 emails per hour limit
4. If rate limited, wait 60 seconds between attempts

---

**THIS PLAN IS COMPLETE AND READY TO EXECUTE**
Start with STEP 1 and follow sequentially.