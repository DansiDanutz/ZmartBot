# 🚨 CURSOR DEVELOPMENT RULES

## ⚠️ CRITICAL RULE: ALWAYS SEARCH FIRST

### Rule #1: Search Before Implementation
**NEVER start implementing ANY feature until you have searched for existing versions.**

#### Required Search Steps:
1. **Search the codebase** for existing implementations
2. **Check for V2, V3, or enhanced versions** of the same functionality
3. **Look for similar modules** that might already exist
4. **Check documentation** for completed implementations
5. **Verify which version is currently being used** in production

#### Search Commands to Use:
```bash
# Search for existing implementations
codebase_search "feature name"

# Search for specific file types
file_search "service_name"

# Search for imports and usage
grep_search "service_name"

# Search for version numbers
grep_search "V2|V3|enhanced|complete"
```

#### What to Do When You Find Existing Versions:
1. **Use the BEST version** (usually V2, V3, or "complete" versions)
2. **Delete old/duplicate versions** to avoid confusion
3. **Update imports** to use the correct version
4. **Test the existing version** before creating new ones
5. **Document which version is the canonical one**

#### Examples of What We've Fixed:
- ✅ **My Symbols**: Found V2 service, deleted old basic service
- ✅ **Cryptometer**: Using complete library version
- ✅ **RiskMetric**: Using enhanced version with QA agent
- ✅ **KingFisher**: Using complete version with AI integration

#### Penalty for Breaking This Rule:
- **Wasted time** implementing duplicate functionality
- **User frustration** with inconsistent behavior
- **Code maintenance nightmare** with multiple versions
- **Potential bugs** from using wrong versions

---

## 📋 IMPLEMENTATION CHECKLIST

Before starting ANY implementation:

- [ ] Searched for existing implementations
- [ ] Found the BEST version available
- [ ] Verified it's being used in production
- [ ] Deleted old/duplicate versions
- [ ] Updated all imports to use correct version
- [ ] Tested the existing functionality
- [ ] Documented which version is canonical

---

## 🎯 CURRENT CANONICAL VERSIONS

### My Symbols Module
- **✅ CANONICAL**: `my_symbols_service_v2.py` (complete with all features)
- **❌ DELETED**: `my_symbols_service.py` (basic version)

### Cryptometer Module
- **✅ CANONICAL**: Library version with 17 endpoints
- **❌ ARCHIVED**: Old duplicate versions

### RiskMetric Module
- **✅ CANONICAL**: Enhanced version with QA agent
- **❌ ARCHIVED**: Old 25-point scoring versions

### KingFisher Module
- **✅ CANONICAL**: Complete version with AI integration
- **❌ ARCHIVED**: Old basic versions

---

**Remember: SEARCH FIRST, IMPLEMENT LAST!** 🔍
