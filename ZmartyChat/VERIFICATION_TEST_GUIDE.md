# 🧪 Email Verification Testing Guide

## ✅ Quick Test Checklist

### 1. New User Registration Test
```
Email: test[timestamp]@example.com (e.g., test1737297600@example.com)
Password: TestPass123!
```

**Expected Flow:**
1. Enter email → Continue button appears
2. Enter password → Confirm password field appears
3. Passwords match → Register button appears
4. Click Register → Loading state → Slide 5 (6-digit code)
5. Email arrives with ONLY 6-digit code (no clickable link)
6. Enter code → Verify → Slide 6 (Tier selection)

### 2. Verification Points

#### ✅ What SHOULD happen:
- [ ] Email contains only 6-digit code (e.g., `123456`)
- [ ] No clickable "Verify Email" button in email
- [ ] No magic link URL in email
- [ ] User stays on Slide 5 until code is entered
- [ ] Wrong code shows error "Invalid verification code"
- [ ] Correct code → proceeds to Slide 6

#### ❌ What should NOT happen:
- [ ] Auto-redirect to tier selection (bypassing code entry)
- [ ] Magic link in email that skips verification
- [ ] Login happening before verification
- [ ] White overlay appearing after registration

### 3. Test Commands

Open test dashboard:
```
http://localhost:9000/test-onboarding-complete.html
```

Watch console for verification code (test mode):
```
// Console will show: "Verification code (for testing): 123456"
```

### 4. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Still getting magic link | Check email template - remove ALL `{{ .ConfirmationURL }}` references |
| Auto-redirect happening | Clear browser cache and sessionStorage |
| Code not working | Check if using test code from console vs real Supabase code |
| Rate limited | Wait 60 seconds between registration attempts |

### 5. Manual Test Flow

1. **Clear everything:**
   ```javascript
   sessionStorage.clear();
   localStorage.clear();
   ```

2. **Register new user:**
   - Use unique email each time
   - Watch console for test code
   - Check email for production code

3. **Verify behavior:**
   - Should stay on Slide 5
   - No auto-navigation
   - Code entry required

## 📊 Success Metrics

✅ **Working Correctly If:**
- User must enter 6-digit code
- No bypassing verification step
- Email only contains code (no links)
- 100% test suite passes

## 🔍 Debug Info

Check current slide:
```javascript
console.log('Current slide:', window.currentSlide);
```

Check session storage:
```javascript
console.log('Pending verification:', sessionStorage.getItem('pending_verification'));
console.log('Test code:', sessionStorage.getItem('verification_code'));
```

Check auth state:
```javascript
const { data: { session } } = await supabase.auth.getSession();
console.log('Session:', session);
```

---

**Updated**: 2025-01-19
**Status**: Ready for testing with updated email template