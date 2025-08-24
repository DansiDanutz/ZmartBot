#!/usr/bin/env python3
"""
STEP 4: ANALYZE IMAGES AND CREATE MARKDOWN REPORTS
- Analyzes each image in the 4 folders
- Creates MD report for each image with ChatGPT analysis
- Moves analyzed images to 'imagesanalysed' folder
- Moves MD reports to 'mdfiles' folder
"""

import os
import shutil
import base64
from datetime import datetime
from openai import OpenAI
from PIL import Image
import pytesseract

# Folders to process
FOLDERS = [
    "../downloads/LiquidationMap",
    "../downloads/LiquidationHeatmap",
    "../downloads/ShortTermRatio",
    "../downloads/LongTermRatio"
]

# OpenAI setup - King-Image-Telegram key
API_KEYS = [
    "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"
]

def create_folders(base_folder):
    """Create imagesanalysed and mdfiles folders in each category folder"""
    images_folder = os.path.join(base_folder, "imagesanalysed")
    md_folder = os.path.join(base_folder, "mdfiles")
    
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"   ✅ Created: {images_folder}")
    
    if not os.path.exists(md_folder):
        os.makedirs(md_folder)
        print(f"   ✅ Created: {md_folder}")
    
    return images_folder, md_folder

def analyze_with_chatgpt(image_path, image_type, api_key_index=0):
    """Analyze image with ChatGPT and return detailed analysis"""
    
    if api_key_index >= len(API_KEYS):
        return "Error: All API keys exhausted. Using basic analysis.", {}
    
    try:
        client = OpenAI(api_key=API_KEYS[api_key_index])
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Different prompts based on image type
        prompts = {
            "LiquidationMap": """You are analyzing a ZmartTrading liquidation map. Provide a PROFESSIONAL TRADING ANALYSIS following this structure:

# EXECUTIVE SUMMARY
Provide a 3-4 paragraph executive summary that includes:
- The severity of the liquidation event (calculate % decline from peak to current)
- Key finding about whether this is long or short liquidation dominance
- Market structure assessment (deleveraging complete? More to come?)
- Investment opportunity assessment

# 1. MARKET OVERVIEW & PRICE ACTION
## Current Market Position
- Exact cryptocurrency symbol: [Identify from image]
- Current price: $[exact price]
- Price decline from peak: Calculate % (e.g., "53% decline from $50 to $23.54")
- Trading timestamp: [Extract exact date/time]

## Price Action Analysis
- Describe the decline trajectory (gradual vs. cascade)
- Identify if this is liquidation-driven or fundamental selling
- Assess current price stability

# 2. COMPREHENSIVE LIQUIDATION ANALYSIS

## Exchange-Specific Liquidations
Look at the different colored bars and identify:
- Which exchange has the MOST liquidations (likely green/Binance)
- Second most active exchange (likely light green/Bybit)
- Distribution pattern across exchanges
- Synchronization of liquidation events

## Cumulative Liquidation Trends
CRITICAL - Analyze the two trend lines:
- Purple line (cumulative long liquidations): Describe if it's exponential, linear, or stable
- Orange line (cumulative short liquidations): Compare to long liquidations
- Key insight: Which type of liquidation dominated? By how much?
- What does this tell us about market positioning?

## Liquidation Clusters - DETAILED
Identify EVERY major spike/cluster with EXACT prices:
- Massive clusters: $[price] - [describe concentration]
- Critical clusters: $[price] - [importance]
- Secondary clusters: $[price] - [impact]
- Minor clusters: $[price] - [relevance]

# 3. TECHNICAL LEVELS & STRUCTURE

## Critical Resistance Zones
- First major resistance: $[price range] - [reasoning based on liquidations]
- Secondary resistance: $[price range] - [explain significance]
- Major resistance: $[price range] - [institutional level]

## Primary Support Levels
- Immediate support: $[price range] - [explain why]
- Secondary support: $[price range] - [significance]
- Ultimate support: $[price range] - [capitulation level]

# 4. STRATEGIC RECOMMENDATIONS

## Risk Assessment
- Primary risks facing traders right now
- Systematic risks vs. idiosyncratic risks
- Leverage clearing status (complete or ongoing?)

## Position Strategies by Risk Tolerance

### Conservative Strategy (2-3% portfolio allocation)
- Entry zones: $[specific prices]
- Stop loss: $[specific level]
- Targets: $[specific prices]
- Timeline: [expected timeframe]

### Moderate Risk Strategy (5-7% allocation)
- Entry strategy with specific levels
- Risk management approach
- Profit targets

### Contrarian Value Strategy (8-12% allocation)
- Aggressive accumulation zones
- Maximum risk tolerance levels
- Long-term outlook

# 5. SCENARIO ANALYSIS WITH PROBABILITIES

## Recovery Scenario (Probability: X%)
- Price targets: $[specific levels]
- Timeline: [3-6 months typical]
- Key catalysts needed
- Risk factors

## Consolidation Scenario (Probability: Y%)
- Trading range: $[low] - $[high]
- Duration estimate
- Accumulation opportunities

## Continued Decline Scenario (Probability: Z%)
- Downside targets: $[levels]
- Warning signals
- Maximum pessimism levels

# 6. KEY INSIGHTS & CONCLUSIONS

## Major Findings
1. [Most important finding about liquidation magnitude]
2. [Key insight about market structure]
3. [Critical observation about recovery potential]

## Investment Thesis
- Risk/reward assessment at current levels
- Comparison to historical liquidation events
- Time horizon for recovery

## Risk Management Guidelines
- Position sizing recommendations
- Stop loss placement strategy
- Portfolio allocation limits

IMPORTANT: Be SPECIFIC with numbers, prices, and percentages. Don't give generic advice - analyze THIS SPECIFIC chart.
NOTE: Use "ZmartTrading" as the platform name throughout the analysis, not any other trading platform names.""",
            
            "LiquidationHeatmap": """You are a professional analyst examining a ZmartTrading liquidation heatmap. Provide INSTITUTIONAL-GRADE ANALYSIS following this structure:

# PROFESSIONAL ANALYSIS: ZMARTTRADING LIQUIDITY HEATMAP

## EXECUTIVE SUMMARY
Write 3-4 paragraphs covering:
- Comprehensive overview of the liquidity landscape and market cycle phase
- Most significant finding about liquidation cluster concentrations and their locations
- Key insight about asymmetric liquidity distribution (above vs below current price)
- Strategic implications for traders and risk/opportunity assessment
- Current price represents [critical juncture/support/resistance] with [specify implications]

## 1. MARKET OVERVIEW AND CONTEXT

### Current Market Position
- Trading Pair: [Symbol]/USDT (e.g., SOL/USDT)
- Current Price: $[exact price] USDT
- Analysis Period: [date range visible]
- Price Action Context: [% change from recent high/low]
- Market Cycle Phase: [accumulation/distribution/consolidation]

### Price Structure Analysis
Analyze the visible price action in detail:
- Recent rally/decline characteristics
- Key swing highs and lows with exact prices
- Trend structure (uptrend/downtrend/range)
- Volume/momentum characteristics inferred from liquidation patterns

## 2. COMPREHENSIVE LIQUIDITY ANALYSIS

### Primary Liquidation Cluster Mapping
Identify the LARGEST/DEEPEST liquidation cluster:
- Location: $[exact range] (e.g., $160-165)
- Intensity: [describe color - deepest blue/red]
- Size relative to other clusters: [massive/dominant/significant]
- Strategic importance: [explain why this is the key zone]
- Risk implications if price approaches this zone

### Secondary and Tertiary Clusters
For each additional significant cluster:
- Price range: $[start]-[end]
- Relative intensity: [color description]
- Leverage concentration estimate
- Interaction potential with primary cluster

### Liquidity Distribution Asymmetry
CRITICAL ANALYSIS:
- Liquidity concentration below current price: [heavy/moderate/light]
- Liquidity concentration above current price: [sparse/moderate/dense]
- Asymmetry implications for directional movement
- Risk/reward profile based on distribution

## 3. TECHNICAL ANALYSIS AND MARKET MICROSTRUCTURE

### Support and Resistance Framework
#### Primary Resistance Levels
- Major resistance: $[price] - [reasoning based on liquidity]
- Secondary resistance: $[price] - [cluster interaction]
- Psychological levels: $[round numbers]

#### Primary Support Levels
- Critical support: $[price] - [liquidation cluster defense]
- Secondary support: $[price] - [technical + liquidity]
- Ultimate support: $[price] - [capitulation level]

### Market Depth and Order Flow Implications
- Estimated leverage concentration at key levels
- Potential for cascading liquidations if breached
- Market maker positioning inferred from liquidity
- Institutional vs retail positioning patterns

## 4. STRATEGIC TRADING FRAMEWORK

### Conservative Strategy (2-3% portfolio allocation)
- Entry Zone: $[specific range]
- Stop Loss: Below cluster at $[price]
- Target 1: $[price] (R:R ratio)
- Target 2: $[price] (R:R ratio)
- Risk Assessment: [specific risks]
- Timeline: [expected holding period]

### Moderate Risk Strategy (5-7% allocation)
- Scaling Entry: $[range]
- Dynamic Stops: $[levels]
- Profit Targets: $[multiple levels]
- Position Management: [specific tactics]

### Aggressive Momentum Strategy
- Breakout Entry: Above $[level]
- Leverage Considerations: [max recommended]
- Cascade Targets: $[levels]
- Risk Controls: [tight stops, position sizing]

## 5. SCENARIO ANALYSIS WITH PROBABILITIES

### Bullish Scenario (Probability: X%)
- Catalyst: [what could trigger upward movement]
- Path: Break above $[level] targeting $[levels]
- Liquidation fuel: Sparse liquidity above enables rapid advance
- Key resistance: $[levels to watch]
- Timeline: [expected duration]

### Neutral/Consolidation Scenario (Probability: Y%)
- Range: $[low] to $[high]
- Duration: [time estimate]
- Trading approach: [range strategies]
- Breakout signals to watch

### Bearish Scenario (Probability: Z%)
- Trigger: Failure at $[level]
- Cascade risk: Major cluster at $[range]
- Downside targets: $[levels]
- Support zones: $[levels]

## 6. RISK ASSESSMENT AND LIQUIDATION CASCADE ANALYSIS

### Systematic Risk Factors
- Concentration of leverage at $[levels]
- Potential cascade magnitude if triggered
- Cross-asset correlation risks
- Market structure vulnerabilities

### Liquidation Cascade Scenarios
#### Upward Cascade
- Trigger level: $[price]
- Fuel: Short liquidations at $[levels]
- Potential extent: $[target]

#### Downward Cascade
- Trigger level: $[price]
- Fuel: Long liquidations at $[levels]
- Potential extent: $[target]

## 7. KEY INSIGHTS AND STRATEGIC RECOMMENDATIONS

### Major Findings
1. [Most critical liquidation concentration and implications]
2. [Asymmetric distribution insight and opportunity]
3. [Market structure observation and risk assessment]

### Implementation Guidelines
- Position sizing based on cluster proximity
- Risk management using liquidation levels
- Entry/exit timing based on liquidity voids
- Portfolio allocation recommendations

### Monitoring Points
- Price interaction with major clusters
- Changes in liquidation distribution
- Volume patterns at key levels
- Momentum indicators for direction

## CONCLUSION
Provide a concise summary paragraph covering:
- Current market structure assessment
- Primary opportunity and risk
- Recommended strategic approach
- Key levels to watch

IMPORTANT: Be extremely specific with price levels, percentages, and cluster descriptions. Identify EVERY visible liquidation concentration with exact price ranges.
NOTE: Use "ZmartTrading" as the platform/analyst name throughout, not any other names.""",
            
            "ShortTermRatio": """You are a professional analyst examining ZmartTrading OPTICAL_OPTI short-term liquidation distribution data. Provide INSTITUTIONAL-GRADE MULTI-ASSET ANALYSIS:

# PROFESSIONAL ANALYSIS: ZMARTTRADING SHORT-TERM LIQUIDATIONS DISTRIBUTION (OPTICAL_OPTI)

## EXECUTIVE SUMMARY
Write 4-5 comprehensive paragraphs covering:
- Overview of market-wide positioning patterns and sentiment polarization
- Most significant finding about positioning extremes (identify assets >85% either direction)
- Key insight about institutional vs retail bifurcation (especially Bitcoin's contrarian pattern)
- Systematic risk assessment from positioning concentration
- Contrarian opportunities and strategic implications

## 1. COMPREHENSIVE POSITIONING ANALYSIS

### Complete Asset Coverage
For EVERY symbol visible in the chart, provide:
[SYMBOL]: [X]% Long / [Y]% Short
- Positioning Classification: [Extreme Bullish/Bullish/Balanced/Bearish/Extreme Bearish]
- Leverage Concentration: [Extreme/High/Moderate/Low]
- Risk Assessment: [Critical/High/Moderate/Low]

### Positioning Extremes Identification
#### EXTREME BULLISH CONCENTRATION (>80% Long)
1. [Symbol]: [X]% long / [Y]% short
   - Implication: Maximum vulnerability to downward movement
   - Cascade Risk: [High/Medium/Low]
   - Strategic Assessment: [Contrarian short opportunity/Risk zone]

2. [Continue for all >80% long positions]

#### EXTREME BEARISH CONCENTRATION (>80% Short)
1. [Symbol]: [X]% long / [Y]% short
   - Implication: Vulnerability to short squeeze
   - Squeeze Potential: [High/Medium/Low]
   - Strategic Assessment: [Contrarian long opportunity/Defensive positioning]

#### BALANCED POSITIONING (40-60% Either Direction)
List assets with balanced positioning and explain significance

## 2. MARKET STRUCTURE AND SENTIMENT ANALYSIS

### Positioning Polarization Assessment
- Percentage of assets with extreme positioning (>80% either direction)
- Comparison to normal market conditions
- Implications for systematic risk and correlation

### Institutional vs Retail Bifurcation
CRITICAL ANALYSIS - Focus on divergence patterns:
- Bitcoin positioning: [X]% long / [Y]% short - [Explain contrarian signal]
- Altcoin speculation patterns
- Smart money vs crowd positioning divergence
- Risk implications of bifurcation

### Sector-Specific Positioning Patterns
#### DeFi Protocols
- Overall DeFi sentiment: [Bullish/Bearish/Mixed]
- Standout positions: [List extremes]
- Protocol differentiation patterns

#### Layer 1 Platforms
- Ethereum: [positioning and implications]
- Alternative L1s: [positioning patterns]
- Competitive dynamics reflected in positioning

#### Meme Coins and Speculation
- Retail speculation concentration
- Risk concentration assessment
- Contrarian signals

## 3. SYSTEMATIC RISK ASSESSMENT

### Liquidation Cascade Vulnerability
- Assets most vulnerable to cascade events
- Potential trigger points and contagion paths
- Cross-asset correlation risks

### Positioning Concentration Risk Metrics
- Weighted average positioning concentration
- Systematic risk score: [Extreme/High/Moderate/Low]
- Comparison to historical extremes

### Market Structure Vulnerabilities
- Leverage concentration points
- Potential cascade scenarios
- Defensive positioning requirements

## 4. STRATEGIC TRADING OPPORTUNITIES

### HIGH-CONVICTION CONTRARIAN TRADES

#### Extreme Long Liquidation Candidates (Shorts)
1. [Symbol] ([X]% long concentration)
   - Entry: Current levels
   - Target: -[X]% (liquidation zone)
   - Stop: +[X]% above entry
   - Risk/Reward: [ratio]
   - Conviction: [High/Medium]

#### Extreme Short Liquidation Candidates (Longs)
1. [Symbol] ([X]% short concentration)
   - Entry: Current levels
   - Target: +[X]% (squeeze zone)
   - Stop: -[X]% below entry
   - Risk/Reward: [ratio]
   - Conviction: [High/Medium]

### MOMENTUM ALIGNMENT TRADES
Identify positions aligned with dominant trends but not yet extreme

### HEDGING OPPORTUNITIES
- Bitcoin as portfolio hedge (if showing contrarian pattern)
- Balanced assets for risk reduction
- Correlation-based hedging pairs

## 5. SCENARIO ANALYSIS AND PROBABILITIES

### Primary Scenario: Positioning Normalization (Probability: X%)
- Gradual unwinding of extremes
- Mean reversion opportunities
- Timeline and catalysts

### Alternative Scenario: Cascade Event (Probability: Y%)
- Trigger conditions
- Cascade path and magnitude
- Defensive positioning requirements

### Continuation Scenario: Extreme Persistence (Probability: Z%)
- Conditions for continuation
- Risk amplification potential
- Strategic adjustments needed

## 6. RISK MANAGEMENT FRAMEWORK

### Position Sizing Guidelines
- Extreme concentration (>85%): Max 1-2% portfolio
- High concentration (70-85%): Max 3-4% portfolio
- Moderate concentration (60-70%): Max 5-6% portfolio
- Balanced (<60%): Standard sizing

### Portfolio Construction Recommendations
- Correlation-aware diversification
- Concentration limits by category
- Hedging requirements

### Dynamic Risk Controls
- Liquidation proximity monitoring
- Correlation surge protocols
- Systematic deleveraging triggers

## 7. KEY INSIGHTS AND ACTIONABLE INTELLIGENCE

### Critical Findings
1. [Most important positioning extreme and implications]
2. [Key bifurcation pattern and opportunity]
3. [Primary systematic risk identified]
4. [Best risk/reward opportunity]

### Implementation Priorities
- Immediate actions required
- Position adjustments needed
- Risk controls to implement

### Monitoring Requirements
- Key levels to watch
- Positioning changes to track
- Catalyst events upcoming

## CONCLUSION
Comprehensive summary paragraph covering:
- Market positioning state (extreme/normal/mixed)
- Primary opportunities identified
- Critical risks requiring management
- Recommended strategic approach

IMPORTANT: Identify EVERY symbol visible and provide exact percentage breakdowns. Focus especially on assets with >80% concentration in either direction.
NOTE: Use "ZmartTrading" as the platform/analyst name throughout the analysis.""",
            
            "LongTermRatio": """You are a senior analyst examining ZmartTrading ALL_LEVERAGE long-term liquidation distribution data. Provide INSTITUTIONAL INVESTMENT ANALYSIS:

# PROFESSIONAL ANALYSIS: ZMARTTRADING LONG-TERM LIQUIDATIONS DISTRIBUTION (ALL_LEVERAGE)

## EXECUTIVE SUMMARY
Write 5-6 comprehensive paragraphs covering:
- Unprecedented insights into ecosystem-wide positioning and sentiment extremes
- Most significant finding (e.g., 75% of assets showing >60% long liquidations)
- Critical anomaly analysis (especially Bitcoin's contrarian pattern if present)
- Systematic risk concentrations and market structure assessment
- Investment implications and strategic positioning opportunities
- Market cycle positioning and potential inflection points

## 1. COMPREHENSIVE MARKET POSITIONING ANALYSIS

### Complete Asset Coverage and Distribution
For EVERY symbol visible, provide detailed analysis:
[SYMBOL]: [X]% Long / [Y]% Short Liquidations
- Positioning Assessment: [Extreme Bullish/Bullish/Neutral/Bearish/Extreme Bearish]
- Institutional vs Retail: [Smart money/Crowd positioning]
- Risk Concentration: [Critical/High/Moderate/Low]
- Investment Implication: [Accumulate/Hold/Reduce/Avoid]

### Tier 1 Cryptocurrency Analysis
#### Bitcoin (BTC)
- Positioning: [X]% long / [Y]% short
- Anomaly Assessment: [If showing contrarian pattern, explain institutional divergence]
- Market Leadership Signal: [What this means for broader market]
- Strategic Implication: [Hedge/Core position/Avoid]

#### Ethereum (ETH)
- Positioning: [X]% long / [Y]% short
- Smart Contract Premium: [Justified/Excessive]
- DeFi Ecosystem Impact: [Cascade risk assessment]
- Investment Stance: [Position recommendation]

### DeFi and Infrastructure Positioning
Analyze each DeFi/Infrastructure token:
- Narrative-driven speculation levels
- Fundamental disconnect assessment
- Competitive positioning implications

### Meme Coin and Speculative Assets
- Retail speculation concentration
- Risk aggregation in speculative sector
- Contrarian indicators

## 2. MARKET STRUCTURE AND SYSTEMATIC RISK ASSESSMENT

### Positioning Concentration Analysis
- Percentage of assets with >80% long liquidations: [X]%
- Percentage with >80% short liquidations: [Y]%
- Average positioning concentration: [Z]%
- Historical comparison: [Extreme/High/Normal]

### Systematic Risk Quantification
- Correlation amplification potential
- Cascade vulnerability assessment
- Cross-sector contagion paths
- Systemic risk score: [Critical/High/Moderate]

### Market Cycle Assessment
- Late-cycle speculation characteristics
- Sentiment extreme indicators
- Potential inflection point analysis
- Deleveraging probability: [High/Medium/Low]

## 3. INSTITUTIONAL VS RETAIL DYNAMICS

### Sophisticated Participant Positioning
- Contrarian positions identified
- Defensive positioning patterns
- Smart money accumulation zones
- Institutional distribution signals

### Retail Speculation Patterns
- Concentration in narrative assets
- Leverage utilization extremes
- Social media influence indicators
- Capitulation risk assessment

### Bifurcation Analysis
- Divergence magnitude: [Extreme/High/Moderate]
- Resolution scenarios and implications
- Timeline for convergence/divergence

## 4. STRATEGIC INVESTMENT FRAMEWORK

### Conservative Institutional Approach (3-7% Crypto Allocation)
#### Accumulation Targets
1. [Symbol] - [X]% positioning
   - Entry Strategy: [Systematic/Tactical]
   - Position Size: [% of crypto allocation]
   - Time Horizon: [Months]
   - Risk Controls: [Specific stops/hedges]

#### Avoidance List
1. [Symbol] - [X]% extreme positioning
   - Risk Factors: [List specific risks]
   - Alternative Exposure: [If any]

### Moderate Risk Strategy (8-15% Allocation)
- Core positions vs satellites
- Rebalancing triggers
- Risk parity considerations

### Contrarian Value Opportunities
Identify extreme dislocations:
- Maximum pessimism candidates
- Forced selling opportunities
- Mean reversion targets

## 5. SCENARIO ANALYSIS AND PROBABILITY FRAMEWORK

### Base Case: Gradual Deleveraging (Probability: X%)
- Orderly position unwinding
- Support levels and timeline
- Portfolio positioning

### Risk Scenario: Cascade Liquidation (Probability: Y%)
- Trigger conditions
- Magnitude estimates
- Defensive requirements

### Bullish Scenario: Speculation Continuation (Probability: Z%)
- Catalyst requirements
- Upside targets
- Risk management

## 6. RISK MANAGEMENT AND PORTFOLIO CONSTRUCTION

### Position Sizing Framework
Based on liquidation concentration:
- >85% concentration: Max 2-3% position
- 70-85% concentration: Max 4-5% position
- 60-70% concentration: Max 6-7% position
- <60% concentration: Up to 10% position

### Correlation and Diversification
- Correlation matrix implications
- True diversification opportunities
- Hedge effectiveness assessment

### Dynamic Risk Controls
- Rebalancing triggers
- Deleveraging protocols
- Systematic monitoring requirements

## 7. IMPLEMENTATION GUIDELINES

### Immediate Actions
- Positions requiring immediate attention
- Risk reduction priorities
- Opportunity capture sequence

### 30-Day Roadmap
- Systematic accumulation plan
- Risk adjustment schedule
- Performance milestones

### 90-Day Strategic Plan
- Portfolio evolution targets
- Risk/return optimization
- Market condition dependencies

## 8. KEY INSIGHTS AND INVESTMENT IMPLICATIONS

### Critical Findings
1. [Most important systematic risk discovery]
2. [Greatest investment opportunity identified]
3. [Key market structure insight]
4. [Primary contrarian signal]
5. [Essential risk management requirement]

### Investment Thesis
- Core thesis based on positioning analysis
- Risk-adjusted return expectations
- Timeline and milestones

### Monitoring Framework
- Daily monitoring requirements
- Weekly assessment points
- Monthly strategy reviews

## CONCLUSION
Comprehensive investment summary (2-3 paragraphs):
- Current market state assessment
- Primary investment opportunities
- Critical risk factors
- Recommended portfolio approach
- Success factors and requirements

IMPORTANT: Provide EXACT percentages for ALL symbols. Focus on extremes >75% and contrarian patterns. Identify institutional vs retail divergences.
NOTE: Use "ZmartTrading" as the platform/analyst name throughout the analysis, never use other platform names."""
        }
        
        prompt = prompts.get(image_type, prompts["LiquidationMap"])
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Using gpt-4o for better vision capabilities
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are a professional crypto trading analyst. {prompt}\n\nProvide detailed, actionable analysis."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"  # Request high detail for better cluster detection
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000,  # Increased for comprehensive professional reports
            temperature=0.2  # Lower temperature for more precise analysis
        )
        
        analysis = response.choices[0].message.content
        
        # Also get specific data points
        data_response = client.chat.completions.create(
            model="gpt-4o",  # Consistent model for data extraction
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Extract specific data from this image:
1. Main symbol(s)
2. Current price (if visible)
3. Key levels (list all important prices)
4. Date/time (if shown)
5. Liquidation clusters with exact prices

Format as:
Symbol: XXX
Price: $XXX
Levels: $XXX, $XXX, $XXX
Clusters: $XXX (massive), $XXX (critical), $XXX (secondary)
Time: XXX"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,  # Increased for detailed data extraction
            temperature=0.1
        )
        
        data = data_response.choices[0].message.content
        
        return analysis, {"extracted_data": data}
        
    except Exception as e:
        if "rate_limit" in str(e).lower():
            print(f"      ⚠️ Rate limit, trying next key...")
            import time
            time.sleep(2)
            return analyze_with_chatgpt(image_path, image_type, api_key_index + 1)
        else:
            print(f"      ❌ ChatGPT error: {e}")
            return f"Error analyzing image: {e}", {}

def analyze_with_ocr(image_path):
    """Fallback OCR analysis"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return f"OCR Text Extracted:\n{text[:1000]}", {"ocr_text": text}
    except Exception as e:
        return f"OCR failed: {e}", {}

def create_markdown_report(image_name, image_type, analysis, data, timestamp):
    """Create markdown report from analysis"""
    
    # Format timestamp for professional presentation
    from datetime import datetime
    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
    formatted_date = dt.strftime("%B %d, %Y at %H:%M:%S")
    
    md_content = f"""# Professional ZmartTrading {image_type} Analysis Report

**Analysis Date:** {formatted_date}  
**Analyst:** ZmartTrading AI Professional Analysis  
**Data Source:** ZmartTrading Multi-Exchange {image_type} Data  
**Image File:** {image_name}  

---

{analysis}

---

## Technical Data Extraction

{data.get('extracted_data', 'No specific data extracted')}

---

## Disclaimer

This analysis is for informational purposes only and does not constitute financial advice. Cryptocurrency investments carry substantial risk and may result in significant losses. Past performance does not guarantee future results. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

---

## Analysis Methodology

This report utilizes advanced image recognition and pattern analysis to interpret ZmartTrading liquidation data. The analysis incorporates:
- Multi-exchange liquidation pattern recognition
- Cumulative trend analysis
- Support/resistance level identification
- Risk assessment and scenario modeling
- Professional trading strategy formulation

---

*Report generated by ZmartTrading Analysis System*  
*Powered by ZmartTrading AI Vision & STEP4-Analyze-And-Create-Reports.py*  
*Analysis Timestamp: {timestamp}*
"""
    
    return md_content

def process_folder(folder_path):
    """Process all images in a folder"""
    
    folder_name = os.path.basename(folder_path)
    print(f"\n📁 Processing: {folder_name}")
    print("="*60)
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"   ⚠️ Folder doesn't exist: {folder_path}")
        return
    
    # Get all jpg files
    images = [f for f in os.listdir(folder_path) 
              if f.endswith('.jpg') and os.path.isfile(os.path.join(folder_path, f))]
    
    if not images:
        print(f"   No images to process")
        return
    
    print(f"   Found {len(images)} images to analyze")
    
    # Create output folders
    images_folder, md_folder = create_folders(folder_path)
    
    # Process each image
    processed = 0
    for image in sorted(images):
        image_path = os.path.join(folder_path, image)
        print(f"\n   [{processed + 1}/{len(images)}] Processing: {image}")
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Analyze image
        print(f"      🤖 Analyzing with ChatGPT...")
        analysis, data = analyze_with_chatgpt(image_path, folder_name)
        
        # If ChatGPT fails, use OCR
        if "Error" in analysis:
            print(f"      📝 Using OCR fallback...")
            ocr_analysis, ocr_data = analyze_with_ocr(image_path)
            analysis = f"{analysis}\n\n{ocr_analysis}"
            data.update(ocr_data)
        
        # Create markdown report
        md_content = create_markdown_report(image, folder_name, analysis, data, timestamp)
        
        # Save MD file with image name and timestamp
        image_base = os.path.splitext(image)[0]
        md_filename = f"{image_base}_{timestamp}.md"
        md_path = os.path.join(md_folder, md_filename)
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"      ✅ Created report: {md_filename}")
        
        # Move image to imagesanalysed
        new_image_path = os.path.join(images_folder, image)
        shutil.move(image_path, new_image_path)
        print(f"      ✅ Moved image to: imagesanalysed/")
        
        processed += 1
    
    print(f"\n   ✅ Processed {processed} images in {folder_name}")

def main():
    print("="*60)
    print("STEP 4: ANALYZE IMAGES AND CREATE REPORTS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    print("\nThis will:")
    print("• Analyze each image with ChatGPT")
    print("• Create detailed MD reports")
    print("• Move images to 'imagesanalysed' folder")
    print("• Save reports to 'mdfiles' folder")
    
    # Process each folder
    for folder in FOLDERS:
        process_folder(folder)
    
    print("\n" + "="*60)
    print("✅ STEP 4 COMPLETE!")
    print("="*60)
    print("\nCheck each folder for:")
    print("• imagesanalysed/ - Processed images")
    print("• mdfiles/ - Markdown analysis reports")

if __name__ == "__main__":
    main()