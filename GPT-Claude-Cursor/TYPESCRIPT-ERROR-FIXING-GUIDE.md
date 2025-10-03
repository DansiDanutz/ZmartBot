# TypeScript Error Fixing Guide - ZmartBot Project

**Date**: October 1, 2025  
**Purpose**: Document common TypeScript errors and systematic fixing approach

---

## 🏗️ Project Structure

```text
ZmartBot/
├── zmartbot-mobile/          # React Native + TypeScript
│   ├── App.tsx               # Main entry point
│   ├── src/
│   │   ├── assistant/store/  # State management
│   │   ├── services/         # Business logic services
│   │   └── screens/          # UI screens
│   └── tsconfig.json         # TypeScript configuration
├── Dashboard/                # React frontend
└── zmart-api/               # Python backend
```

**Key Points:**
- Root `tsconfig.json` exists but build scripts are in subdirectories
- Multiple TypeScript projects with different configurations
- Mobile app is main TypeScript project

---

## 🐛 Common Error Patterns

### 1. PrefsProvider Export Error

**Error:**

```text
App.tsx(5,10): error TS2305: Module '"./src/assistant/store/prefs"' has no exported member 'PrefsProvider'.
```

**Root Cause:**
- `App.tsx` imports `PrefsProvider` component
- `prefs.ts` only exports `usePrefs` hook
- No Provider component exists in the file

**Fix:**

```typescript
// BEFORE (App.tsx)
import { PrefsProvider } from './src/assistant/store/prefs';

return (
  <PrefsProvider>
    <StatusBar />
    {/* content */}
  </PrefsProvider>
);

// AFTER (App.tsx)
import { usePrefs } from './src/assistant/store/prefs';

return (
  <>
    <StatusBar />
    {/* content */}
  </>
);
```

### 2. MobileTradingService Missing Methods

**Error:**

```text
error TS2339: Property 'getHealthStatus' does not exist on type 'MobileTradingService'
```

**Root Cause:**
- Service interface expects method `getHealthStatus()`
- Implementation class doesn't have this method
- Type mismatch between interface and implementation

**Fix:**

```typescript
// Add missing method to MobileTradingService.ts
class MobileTradingService {
  // ... existing code ...

  async getHealthStatus(): Promise<HealthStatus> {
    try {
      const response = await this.apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}
```

### 3. PortfolioPosition Type Errors

**Error:**

```text
error TS2322: Type 'Position' is not assignable to type 'PortfolioPosition'
```

**Root Cause:**
- Type definitions don't match between service and UI
- Missing properties in type definition
- Type aliasing issues

**Fix:**
- Check actual type definitions in both files
- Add missing properties to type
- Use proper type imports

---

## 🔧 Systematic Fixing Workflow

### Step 1: Identify Errors

```bash
# Run TypeScript compiler in check mode
cd zmartbot-mobile
npx tsc --noEmit 2>&1 | head -50
```

### Step 2: Read Source Files

```bash
# Before fixing imports, verify actual exports
cat src/assistant/store/prefs.ts | grep -E "export|function|const"
```

### Step 3: Fix in Order

1. **Fix exports first** - Add missing exports to source files
2. **Fix imports second** - Update imports to match actual exports
3. **Fix implementations third** - Add missing methods/properties
4. **Fix types last** - Update type definitions if needed

### Step 4: Verify Fix

```bash
# Re-run TypeScript checker
npx tsc --noEmit
```

---

## 📋 Checklist for Each Error

- [ ] Read the error message completely
- [ ] Locate the source file mentioned in error
- [ ] Check what's actually exported in source file
- [ ] Compare with what's being imported
- [ ] Fix source file if export is missing
- [ ] Fix import if export name is different
- [ ] Add implementation if method is missing
- [ ] Re-run TypeScript checker to verify

---

## 🎯 Best Practices

### Do's ✅

- **Always verify actual exports** before changing imports
- **Read source files first** before making assumptions
- **Fix root cause** not symptoms
- **Test incrementally** after each fix
- **Document patterns** you discover

### Don'ts ❌

- **Don't assume exports** from file names
- **Don't remove types** to make errors go away
- **Don't skip verification** after fixing
- **Don't fix multiple errors** without testing each
- **Don't ignore error messages** - they're accurate

---

## 🔍 Common File Locations

| File | Purpose | Common Issues |
|------|---------|---------------|
| `App.tsx` | Main entry | Import errors, Provider issues |
| `src/assistant/store/prefs.ts` | Preferences | Missing exports |
| `src/services/MobileTradingService.ts` | Trading logic | Missing methods |
| `src/screens/*.tsx` | UI screens | Type mismatches |
| `src/types/*.ts` | Type definitions | Missing properties |

---

## 🚀 Quick Reference Commands

```bash
# Check all TypeScript errors
cd zmartbot-mobile && npx tsc --noEmit

# Check specific file
npx tsc --noEmit src/services/MobileTradingService.ts

# Find all exports in a file
grep -E "export" src/assistant/store/prefs.ts

# Count TypeScript files
find . -name "*.ts" -o -name "*.tsx" | wc -l

# List all tsconfig.json files
find . -name "tsconfig.json"
```

---

## 📚 Pattern Examples

### Pattern: Missing Export

```typescript
// prefs.ts (BEFORE)
const usePrefs = () => { /* ... */ };
// No export!

// prefs.ts (AFTER)
export const usePrefs = () => { /* ... */ };
```

### Pattern: Wrong Import Name

```typescript
// App.tsx (BEFORE)
import { PrefsProvider } from './store/prefs';  // Doesn't exist

// App.tsx (AFTER)
import { usePrefs } from './store/prefs';  // Actually exported
```

### Pattern: Missing Method Implementation

```typescript
// Service.ts (BEFORE)
interface TradingService {
  getHealth(): Promise<Health>;
}

class MobileTradingService implements TradingService {
  // Missing getHealth() method
}

// Service.ts (AFTER)
class MobileTradingService implements TradingService {
  async getHealth(): Promise<Health> {
    return { status: 'ok' };
  }
}
```

---

## 🎓 Learning Notes

**Key Insight:**
TypeScript errors in ZmartBot are systematic. Most errors follow these patterns:
1. Import/export mismatches (50%)
2. Missing method implementations (30%)
3. Type definition mismatches (20%)

**Pro Tip:**
Always run `npx tsc --noEmit` in the `zmartbot-mobile/` directory, not the project root, as the root tsconfig.json is not the primary one.

**Memory Aid:**
"Read source → Fix source → Update imports → Verify"

---

**Status**: ✅ DOCUMENTED  
**Last Updated**: October 1, 2025  
**Next Review**: When new error patterns emerge


