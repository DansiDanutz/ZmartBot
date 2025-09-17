#!/usr/bin/env python3
"""
Verify ALL Level 3 MDC files are present and properly updated
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

def main():
    print("🔍 VERIFYING ALL LEVEL 3 MDC FILES")
    print("=" * 60)
    
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    db_path = os.path.join(base_path, "src", "data", "service_registry.db")
    
    try:
        # Get all Level 3 services from database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, port, passport_id 
            FROM service_registry 
            WHERE certification_level = 3
            ORDER BY service_name
        """)
        
        level3_services = cursor.fetchall()
        conn.close()
        
        print(f"📋 Found {len(level3_services)} Level 3 services in database")
        print()
        
        missing_mdc = []
        outdated_mdc = []
        valid_mdc = []
        
        for service_name, port, passport_id in level3_services:
            mdc_path = os.path.join(base_path, ".cursor", "rules", f"{service_name}.mdc")
            yaml_path = os.path.join(base_path, f"{service_name}.yaml")
            
            # Check MDC file
            mdc_exists = os.path.exists(mdc_path)
            mdc_status = "✅" if mdc_exists else "❌"
            
            # Check YAML file  
            yaml_exists = os.path.exists(yaml_path)
            yaml_status = "✅" if yaml_exists else "❌"
            
            # Check file content quality if exists
            content_quality = "❓"
            if mdc_exists:
                try:
                    with open(mdc_path, 'r') as f:
                        content = f.read()
                    
                    # Check for comprehensive content
                    has_purpose = "## Purpose" in content
                    has_workflow = "## Workflow & Triggers" in content  
                    has_methodology = "## Methodology" in content
                    has_passport = passport_id in content if passport_id else False
                    has_port = str(port) in content if port else False
                    
                    quality_score = sum([has_purpose, has_workflow, has_methodology, has_passport, has_port])
                    
                    if quality_score >= 4:
                        content_quality = "✅ COMPLETE"
                        valid_mdc.append(service_name)
                    elif quality_score >= 2:
                        content_quality = "⚠️ PARTIAL"
                        outdated_mdc.append(service_name)
                    else:
                        content_quality = "❌ MINIMAL"
                        outdated_mdc.append(service_name)
                        
                except Exception as e:
                    content_quality = f"❌ ERROR: {e}"
                    
            if not mdc_exists:
                missing_mdc.append(service_name)
            
            print(f"{service_name:<30} MDC: {mdc_status} YAML: {yaml_status} Content: {content_quality}")
        
        print()
        print("📊 SUMMARY REPORT")
        print("=" * 60)
        print(f"✅ Valid MDC files:     {len(valid_mdc)}")
        print(f"⚠️ Outdated MDC files:  {len(outdated_mdc)}")
        print(f"❌ Missing MDC files:   {len(missing_mdc)}")
        print(f"📋 Total Level 3:       {len(level3_services)}")
        
        # Show details
        if missing_mdc:
            print(f"\n❌ MISSING MDC FILES ({len(missing_mdc)}):")
            for service in missing_mdc:
                print(f"   • {service}")
        
        if outdated_mdc:
            print(f"\n⚠️ OUTDATED MDC FILES ({len(outdated_mdc)}):")
            for service in outdated_mdc:
                print(f"   • {service}")
        
        # Calculate completion percentage
        completion_rate = (len(valid_mdc) / len(level3_services)) * 100
        print(f"\n🎯 MDC COMPLETION RATE: {completion_rate:.1f}%")
        
        if completion_rate == 100:
            print("🏆 ALL LEVEL 3 SERVICES HAVE COMPLETE MDC FILES!")
        elif completion_rate >= 90:
            print("✅ MDC files are mostly complete")
        elif completion_rate >= 70:
            print("⚠️ MDC files need some updates")
        else:
            print("❌ MDC files require significant work")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()