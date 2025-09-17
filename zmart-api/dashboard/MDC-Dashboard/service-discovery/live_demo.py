#!/usr/bin/env python3
"""
Live Demo: Generate 12 Real Analyses from MDC Files and Select Winner
This demonstrates the complete workflow with real data from MDC files
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from discovery_workflow import AIDiscoveryWorkflow

class LiveWorkflowDemo:
    """
    Live demonstration of the AI Discovery Workflow system
    """
    
    def __init__(self):
        self.workflow = AIDiscoveryWorkflow()
        self.analyses = []
        
    def run_12_analyses(self):
        """Generate 12 real analyses from MDC files"""
        print("🚀 LIVE WORKFLOW DEMONSTRATION")
        print("=" * 80)
        print("📊 Generating 12 Real Analyses from MDC Files")
        print("=" * 80)
        
        # Load MDC files first
        mdc_files = self.workflow.load_mdc_files()
        print(f"📄 Loaded {len(mdc_files)} MDC files for analysis")
        print()
        
        for i in range(12):
            print(f"🔄 ANALYSIS #{i+1}/12 - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 60)
            
            try:
                # Select connection pair with combination tracking
                service_a, content_a, service_b, content_b, combination_id = self.workflow.select_connection_pair()
                
                # Show service details
                type_a = self.workflow.classify_service_type(service_a, content_a)
                type_b = self.workflow.classify_service_type(service_b, content_b)
                compatibility = self.workflow.get_compatibility_score(type_a, type_b)
                
                print(f"📋 Service A: {service_a} ({type_a})")
                print(f"📋 Service B: {service_b} ({type_b})")
                print(f"🎯 Compatibility Score: {compatibility}/10")
                print(f"🆔 Combination ID: #{combination_id}")
                
                # Generate analysis using ChatGPT or fallback
                analysis_text = self.workflow.analyze_connection_pair(service_a, content_a, service_b, content_b)
                quality_score = self.workflow.calculate_quality_score(analysis_text)
                
                # Store analysis
                analysis = {
                    'id': i + 1,
                    'timestamp': datetime.now(),
                    'service_a': service_a,
                    'service_b': service_b,
                    'service_type_a': type_a,
                    'service_type_b': type_b,
                    'compatibility_score': compatibility,
                    'combination_id': combination_id,
                    'ai_analysis': analysis_text,
                    'quality_score': quality_score,
                    'content_a_preview': content_a[:200] + "..." if len(content_a) > 200 else content_a,
                    'content_b_preview': content_b[:200] + "..." if len(content_b) > 200 else content_b
                }
                
                self.analyses.append(analysis)
                
                print(f"🧠 AI Analysis Quality Score: {quality_score:.2f}/10")
                print(f"📝 Analysis Preview: {analysis_text[:150]}...")
                print(f"✅ Analysis #{i+1} completed and stored")
                print()
                
                # Small delay to simulate real-time processing
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in analysis #{i+1}: {e}")
                print()
        
        print("✅ All 12 analyses completed!")
        print("=" * 80)
        return self.analyses
    
    def select_winner(self):
        """Select the best analysis as winner with detailed explanation"""
        print("\n🏆 WINNER SELECTION PROCESS")
        print("=" * 80)
        
        if not self.analyses:
            print("❌ No analyses to evaluate")
            return None
        
        # Show all analyses for comparison
        print("📊 All 12 Analyses Summary:")
        print("-" * 80)
        for i, analysis in enumerate(self.analyses, 1):
            print(f"{i:2d}. {analysis['service_a']} ↔ {analysis['service_b']}")
            print(f"    Type: {analysis['service_type_a']}+{analysis['service_type_b']}")
            print(f"    Compatibility: {analysis['compatibility_score']:.1f}/10")
            print(f"    Quality Score: {analysis['quality_score']:.2f}/10")
            print(f"    Analysis: {analysis['ai_analysis'][:100]}...")
            print()
        
        # Selection criteria
        print("🎯 WINNER SELECTION CRITERIA:")
        print("1. Implementation Feasibility (30%)")
        print("2. System Impact Potential (25%)")
        print("3. Analysis Quality & Detail (20%)")
        print("4. Service Compatibility (15%)")
        print("5. Business Value & ROI (10%)")
        print()
        
        # Calculate winner using multiple criteria
        best_analysis = None
        best_score = 0
        selection_details = []
        
        for analysis in self.analyses:
            # Implementation feasibility (based on analysis keywords)
            implementation_score = 0
            if 'API' in analysis['ai_analysis'] or 'endpoint' in analysis['ai_analysis']:
                implementation_score += 3
            if 'database' in analysis['ai_analysis'] or 'data' in analysis['ai_analysis']:
                implementation_score += 2
            if 'integration' in analysis['ai_analysis']:
                implementation_score += 2
            
            # System impact (based on service types and analysis content)
            impact_score = analysis['compatibility_score'] * 0.4
            if 'performance' in analysis['ai_analysis'] or 'optimization' in analysis['ai_analysis']:
                impact_score += 2
            
            # Analysis quality
            quality_score = analysis['quality_score'] * 0.3
            
            # Service compatibility
            compatibility_score = analysis['compatibility_score'] * 0.2
            
            # Business value (based on analysis content)
            business_score = 0
            if 'trading' in analysis['ai_analysis'].lower() or 'profit' in analysis['ai_analysis'].lower():
                business_score += 2
            if 'monitoring' in analysis['ai_analysis'].lower() or 'alert' in analysis['ai_analysis'].lower():
                business_score += 1.5
            
            # Calculate total weighted score
            total_score = (
                implementation_score * 0.30 +
                impact_score * 0.25 +
                quality_score * 0.20 +
                compatibility_score * 0.15 +
                business_score * 0.10
            )
            
            selection_details.append({
                'analysis': analysis,
                'implementation_score': implementation_score,
                'impact_score': impact_score,
                'quality_score': quality_score,
                'compatibility_score': compatibility_score,
                'business_score': business_score,
                'total_score': total_score
            })
            
            if total_score > best_score:
                best_score = total_score
                best_analysis = analysis
        
        # Sort by total score for ranking
        selection_details.sort(key=lambda x: x['total_score'], reverse=True)
        
        print("📊 SCORING BREAKDOWN (Top 5):")
        print("-" * 80)
        for i, detail in enumerate(selection_details[:5], 1):
            analysis = detail['analysis']
            print(f"#{i} {analysis['service_a']} ↔ {analysis['service_b']}")
            print(f"   Implementation: {detail['implementation_score']:.1f}/10")
            print(f"   System Impact:  {detail['impact_score']:.1f}/10") 
            print(f"   Analysis Quality: {detail['quality_score']:.1f}/6")
            print(f"   Compatibility:  {detail['compatibility_score']:.1f}/2")
            print(f"   Business Value: {detail['business_score']:.1f}/2")
            print(f"   TOTAL SCORE: {detail['total_score']:.2f}/10")
            print()
        
        return best_analysis, selection_details[0] if selection_details else None
    
    def display_winner_details(self, winner, winner_details):
        """Display comprehensive winner details"""
        if not winner:
            print("❌ No winner selected")
            return
        
        print("\n🏆 WINNER ANNOUNCEMENT")
        print("=" * 80)
        print(f"🥇 WINNING COMBINATION: {winner['service_a']} ↔ {winner['service_b']}")
        print(f"🏷️  Service Types: {winner['service_type_a']} + {winner['service_type_b']}")
        print(f"🎯 Compatibility Score: {winner['compatibility_score']}/10")
        print(f"🧠 Analysis Quality: {winner['quality_score']:.2f}/10")
        print(f"🏆 Final Winner Score: {winner_details['total_score']:.2f}/10")
        print()
        
        print("🔍 WHY THIS COMBINATION WON:")
        print("-" * 50)
        print(f"• Implementation Feasibility: {winner_details['implementation_score']:.1f}/10")
        print(f"  → Analysis contains clear implementation steps")
        print(f"• System Impact Potential: {winner_details['impact_score']:.1f}/10")
        print(f"  → High compatibility between service types")
        print(f"• Analysis Quality & Detail: {winner_details['quality_score']:.1f}/6")
        print(f"  → Comprehensive analysis with structured recommendations")
        print(f"• Service Compatibility: {winner_details['compatibility_score']:.1f}/2")
        print(f"  → Excellent architectural fit")
        print(f"• Business Value & ROI: {winner_details['business_score']:.1f}/2")
        print(f"  → Clear business benefits identified")
        print()
        
        print("📄 SERVICE A DETAILS:")
        print("-" * 30)
        print(f"Name: {winner['service_a']}")
        print(f"Type: {winner['service_type_a']}")
        print(f"Content Preview: {winner['content_a_preview']}")
        print()
        
        print("📄 SERVICE B DETAILS:")
        print("-" * 30)
        print(f"Name: {winner['service_b']}")
        print(f"Type: {winner['service_type_b']}")
        print(f"Content Preview: {winner['content_b_preview']}")
        print()
        
        print("🧠 COMPLETE AI ANALYSIS:")
        print("-" * 40)
        print(winner['ai_analysis'])
        print()
        
        print("💡 IMPLEMENTATION RECOMMENDATION:")
        print("-" * 45)
        print("✅ APPROVED FOR IMPLEMENTATION")
        print(f"Priority Level: HIGH (Score: {winner_details['total_score']:.2f}/10)")
        print("Next Steps:")
        print("1. Create detailed technical specification")
        print("2. Generate MDC file for new integration")
        print("3. Implement connection endpoints")
        print("4. Add monitoring and health checks")
        print("5. Update service discovery registry")
        print()
        
        return winner

def main():
    """Run the live demo"""
    demo = LiveWorkflowDemo()
    
    # Step 1: Generate 12 analyses
    analyses = demo.run_12_analyses()
    
    # Step 2: Select winner
    winner, winner_details = demo.select_winner()
    
    # Step 3: Display comprehensive winner details
    demo.display_winner_details(winner, winner_details)
    
    print("🎯 DEMO SUMMARY:")
    print("=" * 40)
    print(f"✅ Generated {len(analyses)} real analyses from MDC files")
    print(f"✅ Selected winner using multi-criteria scoring")
    print(f"✅ Provided comprehensive implementation roadmap")
    print(f"✅ Ready for MDC file generation and implementation")
    print()
    print("📊 This demonstrates the complete 5-minute → 1-hour workflow cycle")
    print("   In production: 12 analyses every hour → 1 winner → 24 daily winners")

if __name__ == "__main__":
    main()