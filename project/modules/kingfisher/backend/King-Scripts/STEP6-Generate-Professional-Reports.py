#!/usr/bin/env python3
"""
STEP 6: Generate Professional Trading Reports
Combines all Airtable data into comprehensive professional reports
Extracts win rates and updates Airtable with timeframe analysis
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from dotenv import load_dotenv
import aiohttp
import pytz

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appAs9sZH7OmtYaTJ')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher')

# Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'
MD_REPORTS_DIR = DOWNLOADS_DIR / 'MD Reports'

# Ensure MD Reports directory exists
MD_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class ProfessionalReportGenerator:
    def __init__(self):
        self.openai_key = OPENAI_API_KEY
        self.airtable_key = AIRTABLE_API_KEY
        self.airtable_base = AIRTABLE_BASE_ID
        self.airtable_table = AIRTABLE_TABLE_NAME
        
    async def fetch_symbol_data_from_airtable(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch all data for a symbol from Airtable"""
        url = f"https://api.airtable.com/v0/{self.airtable_base}/{self.airtable_table}"
        headers = {
            "Authorization": f"Bearer {self.airtable_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "filterByFormula": f"{{Symbol}} = '{symbol}'",
            "maxRecords": 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['records']:
                            return data['records'][0]['fields']
                    return None
            except Exception as e:
                print(f"Error fetching Airtable data: {e}")
                return None
    
    async def generate_comprehensive_report(self, symbol: str, airtable_data: Dict[str, Any]) -> str:
        """Generate comprehensive professional report using ChatGPT"""
        
        # Prepare the context with all available data
        context = f"""
        Symbol: {symbol}
        Current Price: ${airtable_data.get('CurrentPrice', 'N/A')}
        
        Liquidation Map Analysis:
        {airtable_data.get('LiquidationMap', 'No liquidation map data available')}
        
        Liquidation Heatmap Analysis:
        {airtable_data.get('LiquidationHeatmap', 'No liquidation heatmap data available')}
        
        Short-Term Ratio (Optical/OPTI):
        {airtable_data.get('ShortTermRatio', 'No short-term ratio data available')}
        
        Long-Term Ratio (All Leverage):
        {airtable_data.get('LongTermRatio', 'No long-term ratio data available')}
        
        Liquidation Clusters:
        - Below Price Level 2: ${airtable_data.get('Liqcluster-2', 'N/A')}
        - Below Price Level 1: ${airtable_data.get('Liqcluster-1', 'N/A')}
        - Above Price Level 1: ${airtable_data.get('Liqcluster+1', 'N/A')}
        - Above Price Level 2: ${airtable_data.get('Liqcluster+2', 'N/A')}
        
        Last Updated: {airtable_data.get('LastUpdated', 'N/A')}
        """
        
        prompt = f"""
        You are Manus AI, a professional cryptocurrency trading analyst. Based on the following data from various sources, 
        create a comprehensive professional trading report similar to the example provided. 
        
        The report MUST include:
        1. Executive Summary
        2. Detailed methodology explanation
        3. Market Evolution Analysis
        4. CRITICAL: Win Rate Analysis with specific percentages for:
           - 24-hour win rate for long and short positions
           - 7-day win rate projection for long and short positions  
           - 1-month win rate projection for long and short positions
        5. Strategic Trading Recommendations
        6. Risk Assessment
        7. Professional summary tables
        
        Use the following reference style and depth (but adapt the content to the actual data):
        
        Reference Report Style:
        # Final ETH/USDT Trading Report: Third Major Market Reversal Analysis
        [Include executive summary, methodology, analysis sections similar to the reference]
        
        IMPORTANT: You MUST calculate and clearly state win rates based on liquidation data:
        - If short liquidations dominate (e.g., 80% shorts liquidated), long positions have 80% win rate
        - If long liquidations dominate (e.g., 70% longs liquidated), short positions have 70% win rate
        - Project 7-day and 1-month rates using weighted analysis of current and historical patterns
        
        Data to analyze:
        {context}
        
        Generate a report of similar depth and professionalism as the reference, ensuring all win rates are clearly stated with exact percentages.
        The report should be at least 4000 tokens and include detailed analysis sections.
        """
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are Manus AI, a professional cryptocurrency trading analyst creating institutional-grade reports."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        print(f"OpenAI API error: {response.status}")
                        return None
            except Exception as e:
                print(f"Error generating report: {e}")
                return None
    
    def extract_win_rates(self, report: str) -> Dict[str, Dict[str, float]]:
        """Extract win rates from the generated report"""
        win_rates = {
            "24h": {"long": 0.0, "short": 0.0},
            "7d": {"long": 0.0, "short": 0.0},
            "1m": {"long": 0.0, "short": 0.0}
        }
        
        # Patterns to match win rates in various formats
        patterns = [
            # Format: "24-hour win rate: 86.6%" or "Long positions: 86.6% win rate"
            r"24[\s-]?hour?.*?long.*?(\d+\.?\d*)%",
            r"24[\s-]?hour?.*?short.*?(\d+\.?\d*)%",
            r"7[\s-]?day.*?long.*?(\d+\.?\d*)%",
            r"7[\s-]?day.*?short.*?(\d+\.?\d*)%",
            r"1[\s-]?month.*?long.*?(\d+\.?\d*)%",
            r"1[\s-]?month.*?short.*?(\d+\.?\d*)%",
            # Alternative formats
            r"long.*?24[\s-]?hour?.*?(\d+\.?\d*)%",
            r"short.*?24[\s-]?hour?.*?(\d+\.?\d*)%",
            r"long.*?7[\s-]?day.*?(\d+\.?\d*)%",
            r"short.*?7[\s-]?day.*?(\d+\.?\d*)%",
            r"long.*?1[\s-]?month.*?(\d+\.?\d*)%",
            r"short.*?1[\s-]?month.*?(\d+\.?\d*)%",
        ]
        
        report_lower = report.lower()
        
        # Try to extract 24h rates
        for pattern in patterns[:2]:
            match = re.search(pattern, report_lower)
            if match:
                if "long" in pattern:
                    win_rates["24h"]["long"] = float(match.group(1))
                else:
                    win_rates["24h"]["short"] = float(match.group(1))
        
        # Try to extract 7d rates
        for pattern in patterns[2:4]:
            match = re.search(pattern, report_lower)
            if match:
                if "long" in pattern:
                    win_rates["7d"]["long"] = float(match.group(1))
                else:
                    win_rates["7d"]["short"] = float(match.group(1))
        
        # Try to extract 1m rates
        for pattern in patterns[4:6]:
            match = re.search(pattern, report_lower)
            if match:
                if "long" in pattern:
                    win_rates["1m"]["long"] = float(match.group(1))
                else:
                    win_rates["1m"]["short"] = float(match.group(1))
        
        # Also check for table format
        table_pattern = r"\|\s*(\d+[\s-]?(?:hour|day|month)s?)\s*\|\s*(\d+\.?\d*)%?\s*.*?\|\s*(\d+\.?\d*)%?"
        for match in re.finditer(table_pattern, report_lower):
            timeframe = match.group(1)
            long_rate = float(match.group(2))
            short_rate = float(match.group(3)) if match.group(3) else 100 - long_rate
            
            if "24" in timeframe or "hour" in timeframe:
                win_rates["24h"]["long"] = long_rate
                win_rates["24h"]["short"] = short_rate
            elif "7" in timeframe or "day" in timeframe:
                win_rates["7d"]["long"] = long_rate
                win_rates["7d"]["short"] = short_rate
            elif "1" in timeframe or "month" in timeframe:
                win_rates["1m"]["long"] = long_rate
                win_rates["1m"]["short"] = short_rate
        
        return win_rates
    
    async def update_airtable_win_rates(self, symbol: str, win_rates: Dict[str, Dict[str, float]]) -> bool:
        """Update Airtable with extracted win rates"""
        url = f"https://api.airtable.com/v0/{self.airtable_base}/{self.airtable_table}"
        headers = {
            "Authorization": f"Bearer {self.airtable_key}",
            "Content-Type": "application/json"
        }
        
        # First, get the record ID
        params = {
            "filterByFormula": f"{{Symbol}} = '{symbol}'",
            "maxRecords": 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get record ID
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        return False
                    data = await response.json()
                    if not data['records']:
                        return False
                    record_id = data['records'][0]['id']
                
                # Calculate SCORE as max(long_24h, short_24h)
                score = max(win_rates['24h']['long'], win_rates['24h']['short'])
                
                # Update record with win rates - Format: "X% Long/Y% Short"
                update_url = f"{url}/{record_id}"
                update_data = {
                    "fields": {
                        "WinRate_24h": f"{win_rates['24h']['long']:.0f}% Long/{win_rates['24h']['short']:.0f}% Short",
                        "WinRate_7d": f"{win_rates['7d']['long']:.0f}% Long/{win_rates['7d']['short']:.0f}% Short",
                        "WinRate_1m": f"{win_rates['1m']['long']:.0f}% Long/{win_rates['1m']['short']:.0f}% Short",
                        "Score": score,  # Add the calculated score
                        "ReportGenerated": datetime.now().isoformat(),
                    }
                }
                
                async with session.patch(update_url, headers=headers, json=update_data) as response:
                    return response.status == 200
                    
            except Exception as e:
                print(f"Error updating Airtable: {e}")
                return False
    
    def save_report(self, symbol: str, report: str) -> str:
        """Save report with proper folder structure"""
        # Create today's folder
        today = datetime.now()
        date_folder = today.strftime("%Y-%m-%d")
        day_folder = MD_REPORTS_DIR / date_folder
        day_folder.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = today.strftime("%Y%m%d_%H%M%S")
        filename = f"report_{symbol}_{timestamp}.md"
        filepath = day_folder / filename
        
        # Save the report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report saved: {filepath}")
        return str(filepath)
    
    async def process_symbol(self, symbol: str) -> bool:
        """Process a single symbol: generate report, extract rates, update Airtable"""
        print(f"\n📊 Processing {symbol}...")
        
        # Fetch data from Airtable
        print(f"  📥 Fetching Airtable data...")
        airtable_data = await self.fetch_symbol_data_from_airtable(symbol)
        
        if not airtable_data:
            print(f"  ❌ No data found for {symbol} in Airtable")
            return False
        
        # Generate comprehensive report
        print(f"  🤖 Generating professional report with ChatGPT...")
        report = await self.generate_comprehensive_report(symbol, airtable_data)
        
        if not report:
            print(f"  ❌ Failed to generate report for {symbol}")
            return False
        
        # Extract win rates
        print(f"  📈 Extracting win rates...")
        win_rates = self.extract_win_rates(report)
        
        # Calculate score
        score = max(win_rates['24h']['long'], win_rates['24h']['short'])
        
        print(f"  📊 Win Rates Extracted:")
        print(f"     SCORE: {score:.0f}")
        print(f"     24h: Long {win_rates['24h']['long']}% | Short {win_rates['24h']['short']}%")
        print(f"     7d:  Long {win_rates['7d']['long']}% | Short {win_rates['7d']['short']}%")
        print(f"     1m:  Long {win_rates['1m']['long']}% | Short {win_rates['1m']['short']}%")
        
        # Save report
        filepath = self.save_report(symbol, report)
        
        # Update Airtable with win rates
        print(f"  📤 Updating Airtable with win rates...")
        success = await self.update_airtable_win_rates(symbol, win_rates)
        
        if success:
            print(f"  ✅ Successfully processed {symbol}")
        else:
            print(f"  ⚠️ Report saved but failed to update Airtable")
        
        return success
    
    async def get_all_symbols(self) -> List[str]:
        """Get all symbols from Airtable"""
        url = f"https://api.airtable.com/v0/{self.airtable_base}/{self.airtable_table}"
        headers = {
            "Authorization": f"Bearer {self.airtable_key}",
            "Content-Type": "application/json"
        }
        
        symbols = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for record in data['records']:
                            if 'Symbol' in record['fields']:
                                symbols.append(record['fields']['Symbol'])
            except Exception as e:
                print(f"Error fetching symbols: {e}")
        
        return symbols
    
    async def run(self, symbol: Optional[str] = None):
        """Main execution method"""
        print("\n" + "="*60)
        print(" STEP 6: PROFESSIONAL REPORT GENERATION")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if symbol:
            # Process single symbol
            await self.process_symbol(symbol)
        else:
            # Process all symbols
            symbols = await self.get_all_symbols()
            print(f"\n📋 Found {len(symbols)} symbols to process")
            
            for sym in symbols:
                await self.process_symbol(sym)
                await asyncio.sleep(2)  # Rate limiting for API calls
        
        print("\n" + "="*60)
        print(" STEP 6 COMPLETE")
        print("="*60)

async def main():
    """Main entry point"""
    # Check for command line arguments
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    
    generator = ProfessionalReportGenerator()
    await generator.run(symbol)

if __name__ == "__main__":
    asyncio.run(main())