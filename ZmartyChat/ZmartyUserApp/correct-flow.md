# CORRECT ONBOARDING FLOW

## Current Issues:
- Slides 3 & 4 both show tier selection (duplicate!)
- Slide 5 is email registration (should be slide 3)
- Slide 6 & "Slide 6" are both verification (duplicate!)
- Slide 7 is "Quick Login" (not needed in main flow)
- Slide 8 is profile completion

## CORRECT ORDER SHOULD BE:
1. **Welcome** - Introduction to Zmarty
2. **AI Features** - Show what we offer
3. **Email Registration** - Create account FIRST
4. **Email Verification** - Verify the email
5. **Choose Tier** - Select plan (Free highlighted, paid goes to Stripe)
6. **Complete Profile** - Name and country
→ **Dashboard**

## The Fix:
- Remove duplicate slides
- Move email registration to slide 3
- Move verification to slide 4
- Move tier selection to slide 5 (AFTER account exists!)
- Profile completion is slide 6

This way:
- User has account BEFORE choosing paid tier
- Stripe payment can be linked to existing verified account
- Free users skip Stripe completely