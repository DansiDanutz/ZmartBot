#!/usr/bin/env python3
"""
KING ORCHESTRATION AGENT
Intelligent orchestrator for all KingFisher automation steps
Monitors triggers, manages execution flow, and provides API access
"""

import os
import sys
import time
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import threading
import queue
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import aiohttp
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Load environment variables
load_dotenv()

# Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appAs9sZH7OmtYaTJ')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher')

# Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'
MD_REPORTS_DIR = DOWNLOADS_DIR / 'MD Reports'
HISTORY_DIR = BASE_DIR / 'HistoryData'
MDFILES_DIR = BASE_DIR / 'mdfiles'
IMAGES_ANALYSED_DIR = BASE_DIR / 'imagesanalysed'

# Step scripts
STEP_SCRIPTS = {
    1: "STEP1-Monitoring-Images-And-download.py",
    2: "STEP2-Sort-Images-With-AI.py",
    3: "STEP3-Remove-Duplicates.py",
    4: "STEP4-Analyze-And-Create-Reports.py",
    5: "STEP5-Extract-Liquidation-Clusters.py",
    6: "STEP6-Enhanced-Professional-Reports.py"
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KingOrchestrator')


class StepStatus(Enum):
    """Status for each step execution"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class TriggerType(Enum):
    """Trigger types for step execution"""
    NEW_IMAGE = "new_image"
    SORTED_IMAGES = "sorted_images"
    DUPLICATES_REMOVED = "duplicates_removed"
    REPORTS_CREATED = "reports_created"
    CLUSTERS_EXTRACTED = "clusters_extracted"
    TIMER = "timer"
    MANUAL = "manual"


class ImageDownloadHandler(FileSystemEventHandler):
    """Monitor downloads folder for new images"""
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                logger.info(f"New image detected: {file_path.name}")
                self.orchestrator.trigger_step(1, TriggerType.NEW_IMAGE)


class KingOrchestrationAgent:
    """Main orchestration agent for KingFisher automation"""
    
    def __init__(self):
        self.step_status = {i: StepStatus.IDLE for i in range(1, 7)}
        self.last_execution = {i: None for i in range(1, 7)}
        self.execution_history = []
        self.is_running = False
        self.event_queue = queue.Queue()
        self.observer = None
        self.api_app = None
        self.api_thread = None
        
        # Ensure all directories exist
        self._create_directories()
        
        # Initialize step dependencies
        self.step_dependencies = {
            1: [],  # No dependencies - triggered by new images
            2: [1],  # Depends on Step 1 (images downloaded)
            3: [2],  # Depends on Step 2 (images sorted)
            4: [3],  # Depends on Step 3 (duplicates removed)
            5: [4],  # Depends on Step 4 (reports created)
            6: [5],  # Depends on Step 5 (clusters extracted)
        }
        
        # Step trigger conditions
        self.step_triggers = {
            1: self._check_step1_trigger,  # New images in Telegram
            2: self._check_step2_trigger,  # Images in downloads folder
            3: self._check_step3_trigger,  # Sorted images ready
            4: self._check_step4_trigger,  # Duplicates removed
            5: self._check_step5_trigger,  # MD files created
            6: self._check_step6_trigger,  # Airtable data updated
        }
        
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            DOWNLOADS_DIR,
            MD_REPORTS_DIR,
            HISTORY_DIR,
            MDFILES_DIR,
            IMAGES_ANALYSED_DIR,
            DOWNLOADS_DIR / 'LiquidationMap',
            DOWNLOADS_DIR / 'LiquidationHeatmap',
            DOWNLOADS_DIR / 'ShortTermRatio',
            DOWNLOADS_DIR / 'LongTermRatio',
        ]
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _check_step1_trigger(self) -> bool:
        """Check if Step 1 should run - downloads folder empty or manual trigger"""
        # Check if downloads folder is empty
        download_files = list(DOWNLOADS_DIR.glob('*.jpg')) + list(DOWNLOADS_DIR.glob('*.png'))
        
        # Run if folder was empty and now monitoring started
        if len(download_files) == 0:
            return True
        
        # Also check last execution time (run every 5 minutes)
        if self.last_execution[1]:
            time_diff = datetime.now() - self.last_execution[1]
            if time_diff > timedelta(minutes=5):
                return True
        
        return False
    
    def _check_step2_trigger(self) -> bool:
        """Check if Step 2 should run - new unsorted images exist"""
        # Check for images in downloads root that need sorting
        unsorted_images = []
        for img in DOWNLOADS_DIR.glob('*.jpg'):
            if not any(img.name in str(f) for f in 
                      (DOWNLOADS_DIR / 'LiquidationMap').glob('*.jpg')):
                unsorted_images.append(img)
        
        return len(unsorted_images) > 0
    
    def _check_step3_trigger(self) -> bool:
        """Check if Step 3 should run - sorted folders have potential duplicates"""
        folders = ['LiquidationMap', 'LiquidationHeatmap', 'ShortTermRatio', 'LongTermRatio']
        
        for folder in folders:
            folder_path = DOWNLOADS_DIR / folder
            if folder_path.exists():
                images = list(folder_path.glob('*.jpg'))
                if len(images) > 1:  # Potential duplicates if more than 1 image
                    return True
        
        return False
    
    def _check_step4_trigger(self) -> bool:
        """Check if Step 4 should run - unanalyzed images exist"""
        folders = ['LiquidationMap', 'LiquidationHeatmap']
        
        for folder in folders:
            folder_path = DOWNLOADS_DIR / folder
            if folder_path.exists():
                images = list(folder_path.glob('*.jpg'))
                # Check if images haven't been analyzed yet
                for img in images:
                    analyzed_path = IMAGES_ANALYSED_DIR / img.name
                    if not analyzed_path.exists():
                        return True
        
        return False
    
    def _check_step5_trigger(self) -> bool:
        """Check if Step 5 should run - new MD files exist"""
        md_files = list(MDFILES_DIR.glob('*.md'))
        
        # Check if there are MD files that haven't been processed
        for md_file in md_files:
            # Check if this MD file has been processed (moved to history)
            history_file = HISTORY_DIR / md_file.name
            if not history_file.exists():
                return True
        
        return False
    
    def _check_step6_trigger(self) -> bool:
        """Check if Step 6 should run - Airtable has data but no reports"""
        # Check last report generation time
        if self.last_execution[6]:
            time_diff = datetime.now() - self.last_execution[6]
            # Generate reports every 30 minutes if data exists
            if time_diff > timedelta(minutes=30):
                return True
        else:
            # Never run before, check if Airtable has data
            return True
        
        return False
    
    async def execute_step(self, step_num: int) -> bool:
        """Execute a specific step"""
        if step_num not in STEP_SCRIPTS:
            logger.error(f"Invalid step number: {step_num}")
            return False
        
        # Check dependencies
        for dep in self.step_dependencies[step_num]:
            if self.step_status[dep] not in [StepStatus.COMPLETED, StepStatus.IDLE]:
                logger.warning(f"Step {step_num} waiting for dependency: Step {dep}")
                return False
        
        # Update status
        self.step_status[step_num] = StepStatus.RUNNING
        script_name = STEP_SCRIPTS[step_num]
        script_path = BASE_DIR / script_name
        
        logger.info(f"Executing Step {step_num}: {script_name}")
        
        try:
            # Execute the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.step_status[step_num] = StepStatus.COMPLETED
                self.last_execution[step_num] = datetime.now()
                logger.info(f"Step {step_num} completed successfully")
                
                # Record in history
                self.execution_history.append({
                    'step': step_num,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                
                # Trigger next step if applicable
                self._trigger_next_step(step_num)
                return True
            else:
                self.step_status[step_num] = StepStatus.FAILED
                logger.error(f"Step {step_num} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.step_status[step_num] = StepStatus.FAILED
            logger.error(f"Step {step_num} timed out")
            return False
        except Exception as e:
            self.step_status[step_num] = StepStatus.FAILED
            logger.error(f"Step {step_num} error: {e}")
            return False
    
    def _trigger_next_step(self, completed_step: int):
        """Trigger the next step in the pipeline"""
        next_step = completed_step + 1
        if next_step <= 6:
            # Check if next step trigger conditions are met
            if self.step_triggers[next_step]():
                self.trigger_step(next_step, TriggerType.TIMER)
    
    def trigger_step(self, step_num: int, trigger_type: TriggerType):
        """Add step execution to queue"""
        self.event_queue.put({
            'step': step_num,
            'trigger': trigger_type,
            'timestamp': datetime.now()
        })
    
    async def monitor_triggers(self):
        """Continuously monitor for trigger conditions"""
        while self.is_running:
            try:
                # Check each step's trigger conditions
                for step_num in range(1, 7):
                    if self.step_status[step_num] == StepStatus.IDLE:
                        if self.step_triggers[step_num]():
                            logger.info(f"Trigger detected for Step {step_num}")
                            self.trigger_step(step_num, TriggerType.TIMER)
                
                # Process event queue
                while not self.event_queue.empty():
                    event = self.event_queue.get()
                    await self.execute_step(event['step'])
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    def start_file_monitoring(self):
        """Start monitoring downloads folder for new images"""
        self.observer = Observer()
        handler = ImageDownloadHandler(self)
        self.observer.schedule(handler, str(DOWNLOADS_DIR), recursive=False)
        self.observer.start()
        logger.info("File monitoring started")
    
    def stop_file_monitoring(self):
        """Stop file monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File monitoring stopped")
    
    def create_api(self):
        """Create Flask API for data access"""
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
                'service': 'King Orchestration Agent',
                'timestamp': datetime.now().isoformat()
            })
        
        @app.route('/status', methods=['GET'])
        def get_status():
            """Get current status of all steps"""
            status = {}
            for step_num in range(1, 7):
                status[f'step_{step_num}'] = {
                    'status': self.step_status[step_num].value,
                    'last_execution': self.last_execution[step_num].isoformat() 
                                     if self.last_execution[step_num] else None,
                    'script': STEP_SCRIPTS[step_num]
                }
            
            return jsonify({
                'steps': status,
                'is_running': self.is_running,
                'history_count': len(self.execution_history)
            })
        
        @app.route('/trigger/<int:step_num>', methods=['POST'])
        def trigger_step_api(step_num):
            """Manually trigger a step"""
            if step_num not in STEP_SCRIPTS:
                return jsonify({'error': 'Invalid step number'}), 400
            
            self.trigger_step(step_num, TriggerType.MANUAL)
            return jsonify({
                'message': f'Step {step_num} triggered',
                'step': STEP_SCRIPTS[step_num]
            })
        
        @app.route('/data/<symbol>', methods=['GET'])
        def get_symbol_data(symbol):
            """Get latest data for a symbol from Airtable"""
            return asyncio.run(self._fetch_symbol_data(symbol))
        
        @app.route('/reports/<symbol>', methods=['GET'])
        def get_symbol_reports(symbol):
            """Get latest report for a symbol"""
            # Find latest report for symbol
            today = datetime.now().strftime("%Y-%m-%d")
            report_dir = MD_REPORTS_DIR / today
            
            if report_dir.exists():
                reports = list(report_dir.glob(f'report_{symbol}_*.md'))
                if reports:
                    latest_report = max(reports, key=lambda x: x.stat().st_mtime)
                    with open(latest_report, 'r') as f:
                        content = f.read()
                    
                    return jsonify({
                        'symbol': symbol,
                        'report': content,
                        'file': latest_report.name,
                        'timestamp': datetime.fromtimestamp(
                            latest_report.stat().st_mtime
                        ).isoformat()
                    })
            
            return jsonify({'error': 'No report found'}), 404
        
        @app.route('/history', methods=['GET'])
        def get_history():
            """Get execution history"""
            return jsonify({
                'history': self.execution_history[-100:],  # Last 100 executions
                'total': len(self.execution_history)
            })
        
        @app.route('/restart', methods=['POST'])
        def restart_orchestration():
            """Restart the orchestration system"""
            self.reset_all_steps()
            return jsonify({'message': 'Orchestration restarted'})
        
        self.api_app = app
        return app
    
    async def _fetch_symbol_data(self, symbol: str):
        """Fetch symbol data from Airtable"""
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
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
                            return jsonify(data['records'][0]['fields'])
                    return jsonify({'error': 'Symbol not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def reset_all_steps(self):
        """Reset all steps to idle state"""
        for step_num in range(1, 7):
            self.step_status[step_num] = StepStatus.IDLE
        logger.info("All steps reset to IDLE")
    
    def start_api_server(self):
        """Start the Flask API server in a separate thread"""
        app = self.create_api()
        
        def run_server():
            app.run(host='0.0.0.0', port=5555, debug=False)
        
        self.api_thread = threading.Thread(target=run_server, daemon=True)
        self.api_thread.start()
        logger.info("API server started on port 5555")
    
    async def start(self):
        """Start the orchestration agent"""
        logger.info("Starting King Orchestration Agent...")
        self.is_running = True
        
        # Start file monitoring
        self.start_file_monitoring()
        
        # Start API server
        self.start_api_server()
        
        # Check initial state
        logger.info("Checking initial state...")
        download_files = list(DOWNLOADS_DIR.glob('*.jpg'))
        if len(download_files) == 0:
            logger.info("Downloads folder is empty - waiting for first image...")
        else:
            logger.info(f"Found {len(download_files)} existing images")
            # Trigger Step 2 to process existing images
            self.trigger_step(2, TriggerType.TIMER)
        
        # Start monitoring loop
        try:
            await self.monitor_triggers()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the orchestration agent"""
        self.is_running = False
        self.stop_file_monitoring()
        logger.info("King Orchestration Agent stopped")


async def main():
    """Main entry point"""
    orchestrator = KingOrchestrationAgent()
    
    print("\n" + "="*60)
    print(" KING ORCHESTRATION AGENT")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Automatic trigger-based step execution")
    print("  ✅ File monitoring for new images")
    print("  ✅ API endpoints for data access")
    print("  ✅ Status tracking and history")
    print("\nAPI Endpoints (http://localhost:5555):")
    print("  GET  /health           - Health check")
    print("  GET  /status           - Step status")
    print("  POST /trigger/<step>   - Manual trigger")
    print("  GET  /data/<symbol>    - Symbol data")
    print("  GET  /reports/<symbol> - Symbol reports")
    print("  GET  /history          - Execution history")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(main())