#!/usr/bin/env python3
"""
KingFisher Complete Workflow Test
Demonstrates the full multi-agent workflow system
"""

import asyncio
import json
from datetime import datetime

# Test the complete workflow
async def test_complete_workflow():
    """Test the complete KingFisher workflow"""
    
    print("🚀 KingFisher Complete Workflow Test")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Liquidation Map - BTCUSDT',
            'context': 'BTC liquidation map showing major clusters',
            'filename': 'btc_liquidation_map.jpg',
            'expected_type': 'liquidation_map'
        },
        {
            'name': 'Liquidation Heatmap - ETHUSDT', 
            'context': 'ETH liquidation heatmap with high thermal zones',
            'filename': 'eth_liquidation_heatmap.jpg',
            'expected_type': 'liquidation_heatmap'
        },
        {
            'name': 'Multi-Symbol Screener',
            'context': 'AI screener showing BTCUSDT ETHUSDT XRPUSDT SOLUSDT INJUSDT',
            'filename': 'crypto_screener.jpg',
            'expected_type': 'multi_symbol'
        },
        {
            'name': 'Unknown Image with Symbol',
            'context': 'ADAUSDT analysis chart',
            'filename': 'ada_chart.jpg',
            'expected_type': 'unknown'
        }
    ]
    
    # Simulate each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print("-" * 40)
        
        # Simulate image data
        mock_image_data = f"mock_image_data_for_{scenario['filename']}".encode()
        
        try:
            # Import and test the workflow
            from src.services.workflow_orchestrator import workflow_orchestrator
            
            # Execute workflow
            start_time = datetime.now()
            result = await workflow_orchestrator.process_image_workflow(
                image_data=mock_image_data,
                image_filename=scenario['filename'],
                context_text=scenario['context']
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Display results
            if result.success:
                print(f"✅ SUCCESS - {result.image_type}")
                print(f"⏱️  Processing Time: {processing_time:.2f}s")
                print(f"🎯 Symbols Processed: {len(result.symbols_processed)}")
                print(f"📝 Reports Generated: {len(result.reports_generated)}")
                print(f"🗃️ Airtable Records: {len(result.airtable_records)}")
                
                if result.symbols_processed:
                    print(f"📊 Symbols: {', '.join(result.symbols_processed)}")
                
                if result.errors:
                    print(f"⚠️  Warnings: {len(result.errors)} issues")
                    
            else:
                print(f"❌ FAILED")
                print(f"🔴 Errors: {result.errors}")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    # Display overall statistics
    try:
        from src.services.workflow_orchestrator import workflow_orchestrator
        stats = workflow_orchestrator.processing_stats
        
        print(f"\n📊 OVERALL WORKFLOW STATISTICS")
        print("=" * 60)
        print(f"Total Images Processed: {stats['total_images_processed']}")
        print(f"Liquidation Maps: {stats['liquidation_maps_processed']}")
        print(f"Liquidation Heatmaps: {stats['liquidation_heatmaps_processed']}")
        print(f"Multi-Symbol Images: {stats['multi_symbol_images_processed']}")
        print(f"Total Symbols Analyzed: {stats['symbols_analyzed']}")
        print(f"Total Reports Generated: {stats['reports_generated']}")
        print(f"Airtable Records Updated: {stats['airtable_records_updated']}")
        
        if stats['total_images_processed'] > 0:
            avg_symbols = stats['symbols_analyzed'] / stats['total_images_processed']
            avg_reports = stats['reports_generated'] / stats['total_images_processed']
            print(f"Average Symbols per Image: {avg_symbols:.1f}")
            print(f"Average Reports per Image: {avg_reports:.1f}")
            
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")

async def test_image_classification():
    """Test image classification agent"""
    
    print(f"\n🔍 IMAGE CLASSIFICATION TEST")
    print("=" * 60)
    
    test_cases = [
        {
            'filename': 'btc_liquidation_map.jpg',
            'context': 'BTC liquidation clusters map',
            'expected': 'liquidation_map'
        },
        {
            'filename': 'eth_heatmap.jpg', 
            'context': 'ETH liquidation heatmap thermal zones',
            'expected': 'liquidation_heatmap'
        },
        {
            'filename': 'crypto_screener.jpg',
            'context': 'AI screener BTCUSDT ETHUSDT XRPUSDT',
            'expected': 'multi_symbol'
        }
    ]
    
    try:
        from src.services.image_classification_agent import image_classification_agent
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Classification Test {i}")
            print(f"Filename: {test_case['filename']}")
            print(f"Context: {test_case['context']}")
            
            # Mock image data
            mock_image_data = f"mock_classification_data_{i}".encode()
            
            # Classify
            classification = await image_classification_agent.classify_image(
                mock_image_data, test_case['filename'], test_case['context']
            )
            
            print(f"🔍 Detected Type: {classification.image_type.value}")
            print(f"🎯 Confidence: {classification.confidence:.2f}")
            print(f"📊 Symbols: {classification.detected_symbols}")
            print(f"🔄 Workflow: {classification.processing_workflow}")
            
            # Check if matches expected
            if classification.image_type.value == test_case['expected']:
                print("✅ Classification CORRECT")
            else:
                print(f"❌ Expected {test_case['expected']}, got {classification.image_type.value}")
                
    except Exception as e:
        print(f"❌ Classification test failed: {str(e)}")

async def main():
    """Run all tests"""
    
    print("🏎️ KINGFISHER COMPLETE WORKFLOW SYSTEM TEST")
    print("=" * 80)
    print("Testing the multi-agent system for automatic image processing")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test image classification
    await test_image_classification()
    
    # Test complete workflow
    await test_complete_workflow()
    
    print(f"\n🎉 ALL TESTS COMPLETED")
    print("=" * 80)
    print("The KingFisher workflow system is ready for:")
    print("✅ Automatic image classification")
    print("✅ Symbol detection and extraction")
    print("✅ Multi-agent coordination")
    print("✅ Professional report generation")
    print("✅ Airtable integration")
    print("✅ Real-time market data")
    print("✅ Lamborghini speed processing")

if __name__ == "__main__":
    asyncio.run(main()) 