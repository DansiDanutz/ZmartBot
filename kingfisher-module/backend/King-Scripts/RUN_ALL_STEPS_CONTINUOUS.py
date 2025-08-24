#!/usr/bin/env python3
"""
MASTER SCRIPT: RUNS ALL 5 STEPS CONTINUOUSLY
- STEP 1: Download new images from Telegram
- STEP 2: Sort images into categories using AI
- STEP 3: Remove duplicate images
- STEP 4: Analyze images and create MD reports
- STEP 5: Extract liquidation clusters and update Airtable
- Repeats every 5 minutes
"""

import subprocess
import time
from datetime import datetime, timedelta
import os
import sys

def run_step(step_name, script_name, args=None):
    """Run a single step script"""
    print(f"\n{'='*60}")
    print(f"Running {step_name}")
    print(f"{'='*60}")
    
    try:
        cmd = ['python', script_name]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {step_name} completed successfully")
            if result.stdout:
                # Show key output lines
                lines = result.stdout.strip().split('\n')
                for line in lines[-10:]:  # Show last 10 lines
                    if '✅' in line or 'Found' in line or 'Processing' in line:
                        print(f"   {line.strip()}")
        else:
            print(f"⚠️ {step_name} had issues:")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {step_name}: {e}")
        return False

def run_all_steps():
    """Run all 5 steps in sequence"""
    print(f"\n{'='*70}")
    print(f"KINGFISHER AUTOMATION - FULL PIPELINE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    success_count = 0
    
    # STEP 1: Download images from Telegram
    if run_step("STEP 1: Download Telegram Images", "STEP1-Monitoring-Images-And-download.py"):
        success_count += 1
        time.sleep(2)
    
    # STEP 2: Sort images with AI
    if run_step("STEP 2: Sort Images with AI", "STEP2-Sort-Images-With-AI.py"):
        success_count += 1
        time.sleep(2)
    
    # STEP 3: Remove duplicates
    if run_step("STEP 3: Remove Duplicates", "STEP3-Remove-Duplicates.py"):
        success_count += 1
        time.sleep(2)
    
    # STEP 4: Analyze and create reports
    if run_step("STEP 4: Analyze and Create Reports", "STEP4-Analyze-And-Create-Reports.py"):
        success_count += 1
        time.sleep(2)
    
    # STEP 5: Extract clusters and update Airtable
    if run_step("STEP 5: Extract Liquidation Clusters", "STEP5-Extract-Liquidation-Clusters.py", ["--once"]):
        success_count += 1
    
    print(f"\n{'='*70}")
    print(f"PIPELINE COMPLETE: {success_count}/5 steps successful")
    print(f"{'='*70}")
    
    return success_count == 5

def main():
    """Main continuous loop"""
    print("\n" + "="*70)
    print("KINGFISHER CONTINUOUS AUTOMATION SYSTEM")
    print("="*70)
    print("\nThis will run all 5 steps every 5 minutes:")
    print("1. Download new Telegram images")
    print("2. Sort images into categories")
    print("3. Remove duplicates")
    print("4. Analyze and create MD reports")
    print("5. Update Airtable with liquidation clusters")
    print("\nPress Ctrl+C to stop\n")
    
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    update_interval = 300  # 5 minutes
    
    try:
        while True:
            start_time = datetime.now()
            
            # Run all steps
            success = run_all_steps()
            
            # Calculate next run time
            next_run = start_time + timedelta(seconds=update_interval)
            
            print(f"\n⏰ Next pipeline run at {next_run.strftime('%H:%M:%S')}")
            print("Press Ctrl+C to stop")
            
            # Wait for next cycle with countdown
            while datetime.now() < next_run:
                remaining = (next_run - datetime.now()).total_seconds()
                if remaining > 0:
                    print(f"\r⏳ Next run in {int(remaining)} seconds...", end="", flush=True)
                time.sleep(1)
            
            print("\n")  # New line before next cycle
            
    except KeyboardInterrupt:
        print("\n\n👋 Automation stopped by user")
        print("="*70)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()