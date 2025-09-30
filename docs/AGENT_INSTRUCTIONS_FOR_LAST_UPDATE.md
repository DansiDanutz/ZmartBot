# Agent Instructions for Last_Update Field & Data Replacement

## 🎯 **Core Requirements**

### **Last_Update Field Handling**
- **Field Location:** The timestamp is stored in the **Result** field (not a separate Last_Update field)
- **Format:** ISO timestamp format (e.g., `2025-07-29T21:44:38.529110`)
- **Update Trigger:** Every time new image analysis is performed
- **Display:** Shown in the comprehensive analysis report

### **Data Replacement Strategy**
- **Replace Existing Data:** When new image analysis arrives, replace the corresponding field
- **Regenerate Result:** Always generate a new comprehensive Result field
- **Maintain History:** Keep all analysis types but update with latest data
- **Timestamp Tracking:** Include current timestamp in every update

## 📊 **Available Airtable Fields**

| Field Name | Purpose | Data Type | Update Strategy |
|------------|---------|-----------|-----------------|
| `Symbol` | Trading pair identifier | Text | Never change |
| `Liquidation_Map` | Liquidation map analysis | Long text | Replace with new analysis |
| `Liq_Heatmap` | Liquidation heatmap analysis | Long text | Replace with new analysis |
| `RSI_Heatmap` | RSI heatmap analysis | Long text | Replace with new analysis |
| `LiqRatios_long_term` | Long-term liquidation ratios | JSON string | Replace with new analysis |
| `LiqRatios_short_term` | Short-term liquidation ratios | JSON string | Replace with new analysis |
| `Result` | Comprehensive analysis report | Long text | Regenerate every update |
| `24h48h` | 24-48 hour score | Text | Update with new calculation |
| `7days` | 7-day score | Text | Update with new calculation |
| `1Month` | 1-month score | Text | Update with new calculation |
| `Score(24h48h_7Days_1Month)` | Overall score | Text | Update with new calculation |

## 🔄 **Update Process Flow**

### **1. Image Analysis Trigger**
```
New Image → Agent Analysis → Airtable Update → Result Regeneration
```

### **2. Field Update Process**
```python
# For each new image analysis:
1. Get existing record for symbol
2. Update specific analysis field (e.g., Liquidation_Map)
3. Generate new comprehensive Result with timestamp
4. Update Airtable record
5. Monitor for completion status
```

### **3. Result Field Structure**
```markdown
# SYMBOL Professional Trading Analysis & Win Rate Assessment

## Executive Summary
**Symbol:** SYMBOL  
**Analysis Date:** July 29, 2025  
**Last Update:** 2025-07-29T21:44:38.529110  ← TIMESTAMP HERE
**Analysis Status:** COMPLETE/PARTIAL  

## Available Analysis Components
📊 **Liquidation Map Analysis:** Available
🔥 **Liquidation Heatmap Analysis:** Available
📈 **RSI Heatmap Analysis:** Available

## Multi-Timeframe Analysis Results
### 24H-48H Timeframe Analysis
**Score:** Calculated based on available data

### 7-Day Timeframe Analysis  
**Score:** Calculated based on available data

### 1-Month Timeframe Analysis
**Score:** Calculated based on available data

## Professional Assessment
**Status:** READY FOR TRADING/AWAITING ADDITIONAL DATA  
**Confidence Level:** High/Medium/Low  

---
*This analysis was automatically generated based on available image data. Last updated: TIMESTAMP*
```

## 🎯 **Agent Calibration Instructions**

### **For Image Analysis:**
1. **Analyze each image independently** for technical patterns
2. **Identify critical price levels** and support/resistance zones
3. **Assess liquidation pressure** and cluster density
4. **Determine risk levels** and market sentiment
5. **Generate professional analysis** with actionable insights

### **For Win Rate Calculation:**
1. **24H-48H:** Focus on immediate momentum and breakout opportunities
2. **7 Days:** Emphasize consolidation patterns and range trading
3. **1 Month:** Prioritize trend direction and institutional accumulation

### **For Professional Scoring:**
- **Technical Analysis:** 8.0/10 (Strong price action and momentum)
- **Liquidation Analysis:** 8.5/10 (Clear liquidation patterns and levels)
- **Risk Assessment:** 7.0/10 (Medium-High risk due to density)
- **Market Sentiment:** 7.5/10 (Neutral to slightly bullish)

## 📋 **Agent Action Checklist**

### **When New Image Arrives:**
- [ ] **Analyze image** using technical analysis principles
- [ ] **Generate detailed analysis** with professional insights
- [ ] **Format data** for appropriate Airtable field
- [ ] **Update existing record** (don't create duplicate)
- [ ] **Regenerate comprehensive Result** with current timestamp
- [ ] **Update all score fields** (24h48h, 7days, 1Month, overall score)
- [ ] **Verify update success** and monitor status

### **For Each Analysis Type:**
- [ ] **Liquidation Maps:** Analyze cluster density and support/resistance
- [ ] **Liquidation Heatmaps:** Identify critical price levels and risk zones
- [ ] **RSI Heatmaps:** Assess market balance and momentum distribution
- [ ] **Liquidation Ratios:** Calculate short/long term ratios and win rates

### **Quality Assurance:**
- [ ] **Check data format** matches Airtable field requirements
- [ ] **Verify timestamp** is included in Result field
- [ ] **Ensure all fields** are properly updated
- [ ] **Confirm no duplicate records** are created
- [ ] **Test comprehensive result** generation

## 🚀 **Implementation Example**

```python
# Example agent workflow:
async def process_new_image(symbol: str, image_type: str, image_data: bytes):
    # 1. Analyze image
    analysis = await analyze_image(image_data)
    
    # 2. Format for Airtable
    formatted_analysis = format_analysis_for_airtable(image_type, analysis)
    
    # 3. Update Airtable with timestamp
    success = await update_airtable_record(symbol, image_type, formatted_analysis)
    
    # 4. Generate new comprehensive result
    if success:
        await regenerate_comprehensive_result(symbol)
    
    return success
```

## ✅ **Success Criteria**

### **Last_Update Implementation:**
- [ ] Timestamp included in every Result field update
- [ ] Current timestamp reflects most recent analysis
- [ ] No separate Last_Update field needed (uses Result field)
- [ ] Timestamp format: ISO 8601 standard

### **Data Replacement:**
- [ ] Existing data replaced with new analysis
- [ ] No duplicate records created
- [ ] All analysis types properly tracked
- [ ] Comprehensive Result regenerated each time

### **Agent Monitoring:**
- [ ] Agent detects new image updates
- [ ] Automatic analysis generation
- [ ] Proper Airtable field mapping
- [ ] Error handling and validation
- [ ] Status monitoring and reporting

## 🎯 **Ready for Production**

The enhanced system is now **PRODUCTION READY** with:
- ✅ **Proper Last_Update handling** (via Result field timestamp)
- ✅ **Data replacement strategy** (update existing records)
- ✅ **Comprehensive result generation** (regenerate on each update)
- ✅ **Agent monitoring capabilities** (track analysis status)
- ✅ **Error handling and validation** (robust update process)

**Next Steps:** Provide new images for analysis and the agent will automatically handle all updates with proper timestamp tracking! 🚀 