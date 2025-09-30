#!/usr/bin/env python3
"""
Test script to verify Airtable API fix
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.airtable_service import AirtableService

async def test_airtable_fix():
    """Test the Airtable API fix"""
    print("🧪 Testing Airtable API fix...")
    
    service = AirtableService()
    
    # Test connection
    print("1. Testing connection...")
    connection_result = await service.test_connection()
    print(f"   Connection test: {'✅ PASSED' if connection_result else '❌ FAILED'}")
    
    # Test getting recent analyses
    print("2. Testing get_recent_analyses...")
    try:
        analyses = await service.get_recent_analyses(limit=5)
        print(f"   Get analyses: ✅ PASSED (found {len(analyses)} records)")
    except Exception as e:
        print(f"   Get analyses: ❌ FAILED - {e}")
    
    # Test getting symbol summaries
    print("3. Testing get_symbol_summaries...")
    try:
        summaries = await service.get_symbol_summaries()
        print(f"   Get summaries: ✅ PASSED (found {len(summaries)} records)")
    except Exception as e:
        print(f"   Get summaries: ❌ FAILED - {e}")
    
    print("\n🎯 Airtable API fix test completed!")

if __name__ == "__main__":
    asyncio.run(test_airtable_fix()) 