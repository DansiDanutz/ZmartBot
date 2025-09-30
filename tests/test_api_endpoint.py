#!/usr/bin/env python3
"""
Quick API Endpoint Test
======================

Simple test to demonstrate the new professional analysis API endpoints
"""

import requests
import json
from datetime import datetime

def test_professional_analysis_api():
    """Test the new professional analysis API"""
    base_url = "http://localhost:8001/api/v1"
    
    print("🚀 Testing Professional Analysis API Endpoints")
    print("=" * 60)
    
    # Test 1: Get analysis status
    print("\n📊 TEST 1: System Status")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/analysis/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            ai_models = data.get('system_status', {}).get('ai_capabilities', {}).get('available_models', 0)
            print(f"✅ AI Models Available: {ai_models}")
            print(f"✅ Professional Reports: {data.get('system_status', {}).get('professional_reports', {}).get('executive_summary', False)}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    
    # Test 2: Get available formats
    print("\n📋 TEST 2: Available Formats")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/analysis/formats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            formats = data.get('available_formats', {})
            print(f"✅ Executive Summary: {len(formats.get('executive_summary', {}).get('sections', []))} sections")
            print(f"✅ Comprehensive Analysis: {len(formats.get('comprehensive_analysis', {}).get('sections', []))} sections")
            print(f"✅ Template Based On: {data.get('template_based_on', 'N/A')}")
        else:
            print(f"❌ Formats check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 API Endpoint Tests Completed")
    print("Note: Full analysis endpoints require longer processing time")
    print("Use the backend server and call:")
    print("  GET /api/v1/analysis/BTC-USDT/executive")
    print("  GET /api/v1/analysis/ETH-USDT/comprehensive")
    print("=" * 60)

if __name__ == "__main__":
    test_professional_analysis_api()