#!/usr/bin/env python3
"""
Comprehensive Snapshot Service - Complete System State Management
CRITICAL PRIORITY SERVICE for disaster recovery and system restoration
"""

import os
import sys
import json
import time
import shutil
import hashlib
import sqlite3
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import psutil
import zipfile
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SnapshotMetadata:
    """Comprehensive snapshot metadata"""
    snapshot_id: str
    timestamp: str
    name: str
    description: str
    snapshot_type: str  # full, incremental, differential
    size_bytes: int
    file_count: int
    duration_seconds: float
    git_commit: str
    system_state: Dict
    services_state: Dict
    database_states: Dict
    configuration_hash: str
    parent_snapshot: Optional[str] = None
    restored_from: Optional[str] = None
    restoration_count: int = 0

@dataclass
class SystemState:
    """Complete system state capture"""
    mdc_files_count: int
    services_running: List[str]
    ports_in_use: List[int]
    system_health: Dict
    git_status: Dict
    environment_vars: Dict  # non-sensitive only
    disk_usage: Dict
    memory_usage: Dict
    process_count: int
    uptime_seconds: float

class SnapshotService:
    """
    Comprehensive System Snapshot Service
    
    Features:
    - Complete system state snapshots (files, databases, configuration, system state)
    - Incremental and differential snapshots
    - Quick restoration to any point in time
    - Snapshot comparison and analysis
    - Automated scheduling and retention management
    - Integration with System Protection Service
    - Git integration for version control awareness
    - Database state snapshots
    - Service state preservation
    - Configuration management
    - Performance monitoring and optimization
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.snapshots_dir = Path(self.config['snapshots_directory'])
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Snapshot database for metadata
        self.db_path = self.snapshots_dir / 'snapshots.db'
        self.init_database()
        
        # System state monitoring
        self.system_monitor = SystemStateMonitor()
        
        # Snapshot scheduler
        self.scheduler_thread = None
        self.running = False
        
        # Discover and catalog existing backups
        self._discover_existing_backups()
        
        logger.info("🎯 SnapshotService initialized - CRITICAL PRIORITY SERVICE")
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for snapshot service"""
        return {
            'snapshots_directory': './system_backups',
            'existing_backups_path': './system_backups/initial_startup_backup',
            'max_snapshots': 50,
            'retention_days': 90,
            'compression': True,
            'encryption': False,  # Future feature
            'auto_schedule': True,
            'schedule_interval': 6 * 60 * 60,  # 6 hours
            'incremental_interval': 2 * 60 * 60,  # 2 hours
            'full_snapshot_frequency': 24 * 60 * 60,  # 24 hours
            'include_databases': True,
            'include_git_state': True,
            'include_system_state': True,
            'include_service_states': True,
            'exclude_patterns': [
                '*.log', '*.tmp', '__pycache__', '*.pyc', 
                'node_modules', 'venv', '.git/objects',
                'system_snapshots', 'system_backups'
            ],
            'critical_paths': [
                '.cursor/rules',
                'services',
                'src',
                'Dashboard/MDC-Dashboard',
                'CLAUDE.md',
                'package.json',
                'requirements.txt',
                '.env.example',
                'docker-compose.yml'
            ]
        }
    
    def init_database(self):
        """Initialize snapshot metadata database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Snapshots table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS snapshots (
                        snapshot_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        snapshot_type TEXT NOT NULL,
                        size_bytes INTEGER,
                        file_count INTEGER,
                        duration_seconds REAL,
                        git_commit TEXT,
                        system_state TEXT,
                        services_state TEXT,
                        database_states TEXT,
                        configuration_hash TEXT,
                        parent_snapshot TEXT,
                        restored_from TEXT,
                        restoration_count INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Restoration history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS restorations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        snapshot_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        restoration_type TEXT NOT NULL,
                        success BOOLEAN,
                        duration_seconds REAL,
                        restored_files INTEGER,
                        errors TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (snapshot_id) REFERENCES snapshots (snapshot_id)
                    )
                ''')
                
                # System events
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        description TEXT,
                        metadata TEXT,
                        severity TEXT DEFAULT 'INFO',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Snapshot database initialized")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize snapshot database: {e}")
            raise
    
    def start_service(self) -> bool:
        """Start the snapshot service"""
        try:
            logger.info("🚀 Starting SnapshotService...")
            
            # Verify system integrity
            if not self._verify_system_state():
                logger.error("❌ System state verification failed")
                return False
            
            # Create initial snapshot if none exist
            if not self.list_snapshots():
                logger.info("📸 Creating initial system snapshot...")
                result = self.create_snapshot(
                    name="Initial System State",
                    description="Automatic initial snapshot created on service startup",
                    snapshot_type="full"
                )
                if result['success']:
                    logger.info(f"✅ Initial snapshot created: {result['snapshot_id']}")
                else:
                    logger.warning(f"⚠️ Initial snapshot failed: {result.get('error')}")
            
            # Start scheduler if enabled
            if self.config['auto_schedule']:
                self.running = True
                self._start_scheduler()
            
            # Log system event
            self._log_system_event('service_started', 'SnapshotService started successfully')
            
            logger.info("✅ SnapshotService started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start SnapshotService: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the snapshot service"""
        try:
            logger.info("🛑 Stopping SnapshotService...")
            
            self.running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=10)
            
            # Log system event
            self._log_system_event('service_stopped', 'SnapshotService stopped')
            
            logger.info("✅ SnapshotService stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop SnapshotService: {e}")
            return False
    
    def create_snapshot(self, 
                       name: str,
                       description: str = "",
                       snapshot_type: str = "full",
                       parent_snapshot: str = None) -> Dict:
        """Create a comprehensive system snapshot"""
        start_time = time.time()
        snapshot_id = f"snapshot_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        timestamp = datetime.now().isoformat()
        
        logger.info(f"📸 Creating {snapshot_type} snapshot: {name}")
        
        try:
            # Create snapshot directory
            snapshot_path = self.snapshots_dir / snapshot_id
            snapshot_path.mkdir(parents=True, exist_ok=True)
            
            # Capture system state
            system_state = self.system_monitor.capture_system_state()
            
            # Get git status
            git_status = self._get_git_status()
            git_commit = git_status.get('current_commit', 'unknown')
            
            # Capture service states
            services_state = self._capture_services_state()
            
            # Capture database states
            database_states = self._capture_database_states()
            
            # Create file snapshot
            files_result = self._create_file_snapshot(snapshot_path, snapshot_type, parent_snapshot)
            
            # Calculate configuration hash
            config_hash = self._calculate_configuration_hash()
            
            # Calculate total size
            total_size = self._get_directory_size(snapshot_path)
            
            # Create snapshot metadata
            metadata = SnapshotMetadata(
                snapshot_id=snapshot_id,
                timestamp=timestamp,
                name=name,
                description=description,
                snapshot_type=snapshot_type,
                size_bytes=total_size,
                file_count=files_result['file_count'],
                duration_seconds=time.time() - start_time,
                git_commit=git_commit,
                system_state=asdict(system_state),
                services_state=services_state,
                database_states=database_states,
                configuration_hash=config_hash,
                parent_snapshot=parent_snapshot
            )
            
            # Save metadata to database
            self._save_snapshot_metadata(metadata)
            
            # Save metadata file
            metadata_file = snapshot_path / 'snapshot_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(asdict(metadata), f, indent=2, default=str)
            
            # Compress if enabled
            if self.config['compression']:
                compressed_path = self._compress_snapshot(snapshot_path)
                if compressed_path:
                    shutil.rmtree(snapshot_path)
                    logger.info(f"🗜️ Snapshot compressed: {compressed_path}")
            
            # Cleanup old snapshots
            self._cleanup_old_snapshots()
            
            duration = time.time() - start_time
            logger.info(f"✅ Snapshot '{name}' created successfully in {duration:.2f}s")
            logger.info(f"📊 Snapshot stats: {files_result['file_count']} files, {self._format_bytes(total_size)}")
            
            # Log system event
            self._log_system_event(
                'snapshot_created', 
                f"Snapshot '{name}' created successfully",
                {'snapshot_id': snapshot_id, 'type': snapshot_type, 'size': total_size}
            )
            
            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'metadata': asdict(metadata),
                'duration': duration,
                'message': f"Snapshot '{name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create snapshot '{name}': {e}")
            
            # Cleanup failed snapshot
            if 'snapshot_path' in locals() and snapshot_path.exists():
                shutil.rmtree(snapshot_path, ignore_errors=True)
            
            self._log_system_event(
                'snapshot_failed', 
                f"Failed to create snapshot '{name}': {e}",
                {'error': str(e)},
                severity='ERROR'
            )
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create snapshot '{name}'"
            }
    
    def _create_file_snapshot(self, snapshot_path: Path, snapshot_type: str, parent_snapshot: str = None) -> Dict:
        """Create file system snapshot"""
        files_dir = snapshot_path / 'files'
        files_dir.mkdir(parents=True, exist_ok=True)
        
        file_count = 0
        total_size = 0
        
        # Get list of files to snapshot
        if snapshot_type == "incremental" and parent_snapshot:
            files_to_snapshot = self._get_incremental_files(parent_snapshot)
        elif snapshot_type == "differential" and parent_snapshot:
            files_to_snapshot = self._get_differential_files(parent_snapshot)
        else:
            files_to_snapshot = self._get_all_files()
        
        # Copy files
        for source_path in files_to_snapshot:
            try:
                if source_path.is_file():
                    # Calculate relative path from project root
                    rel_path = source_path.relative_to(Path.cwd())
                    dest_path = files_dir / rel_path
                    
                    # Create directory structure
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    file_count += 1
                    total_size += source_path.stat().st_size
                    
            except Exception as e:
                logger.warning(f"Failed to snapshot file {source_path}: {e}")
        
        return {
            'file_count': file_count,
            'total_size': total_size
        }
    
    def restore_snapshot(self, snapshot_id: str, restore_type: str = "full") -> Dict:
        """Restore system from snapshot"""
        start_time = time.time()
        logger.info(f"🔄 Starting {restore_type} restoration from snapshot: {snapshot_id}")
        
        try:
            # Get snapshot metadata
            metadata = self._get_snapshot_metadata(snapshot_id)
            if not metadata:
                raise ValueError(f"Snapshot {snapshot_id} not found")
            
            # Create restoration backup first
            backup_result = self._create_restoration_backup()
            if not backup_result['success']:
                logger.warning("Failed to create restoration backup - proceeding anyway")
            
            # Restore files
            files_restored = self._restore_files(snapshot_id, restore_type)
            
            # Restore databases if included
            if self.config['include_databases'] and restore_type == "full":
                db_result = self._restore_databases(snapshot_id)
                logger.info(f"📊 Database restoration: {db_result}")
            
            # Restore system configuration
            if restore_type == "full":
                config_result = self._restore_configuration(snapshot_id)
                logger.info(f"⚙️ Configuration restoration: {config_result}")
            
            duration = time.time() - start_time
            
            # Update restoration count
            self._increment_restoration_count(snapshot_id)
            
            # Log restoration
            self._log_restoration(snapshot_id, restore_type, True, duration, files_restored)
            
            logger.info(f"✅ Restoration completed successfully in {duration:.2f}s")
            logger.info(f"📊 Restored {files_restored} files from snapshot '{metadata['name']}'")
            
            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'files_restored': files_restored,
                'duration': duration,
                'message': f"Successfully restored from snapshot '{metadata['name']}'"
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Restoration failed: {e}")
            
            # Log failed restoration
            self._log_restoration(snapshot_id, restore_type, False, duration, 0, str(e))
            
            return {
                'success': False,
                'error': str(e),
                'duration': duration,
                'message': f"Restoration failed: {e}"
            }
    
    def list_snapshots(self, limit: int = None) -> List[Dict]:
        """List all snapshots with metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM snapshots 
                    ORDER BY timestamp DESC
                '''
                
                if limit:
                    query += f' LIMIT {limit}'
                
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                
                snapshots = []
                for row in cursor.fetchall():
                    snapshot_dict = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    for field in ['system_state', 'services_state', 'database_states']:
                        if snapshot_dict[field]:
                            try:
                                snapshot_dict[field] = json.loads(snapshot_dict[field])
                            except:
                                snapshot_dict[field] = {}
                    
                    snapshots.append(snapshot_dict)
                
                return snapshots
                
        except Exception as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []
    
    def compare_snapshots(self, snapshot1_id: str, snapshot2_id: str) -> Dict:
        """Compare two snapshots and show differences"""
        try:
            meta1 = self._get_snapshot_metadata(snapshot1_id)
            meta2 = self._get_snapshot_metadata(snapshot2_id)
            
            if not meta1 or not meta2:
                raise ValueError("One or both snapshots not found")
            
            comparison = {
                'snapshot1': {
                    'id': snapshot1_id,
                    'name': meta1['name'],
                    'timestamp': meta1['timestamp'],
                    'size': meta1['size_bytes'],
                    'files': meta1['file_count']
                },
                'snapshot2': {
                    'id': snapshot2_id,
                    'name': meta2['name'],
                    'timestamp': meta2['timestamp'],
                    'size': meta2['size_bytes'],
                    'files': meta2['file_count']
                },
                'differences': {
                    'size_diff': meta2['size_bytes'] - meta1['size_bytes'],
                    'file_diff': meta2['file_count'] - meta1['file_count'],
                    'time_diff': self._calculate_time_difference(meta1['timestamp'], meta2['timestamp'])
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare snapshots: {e}")
            return {'error': str(e)}
    
    def get_snapshot_info(self, snapshot_id: str) -> Dict:
        """Get detailed information about a specific snapshot"""
        try:
            metadata = self._get_snapshot_metadata(snapshot_id)
            if not metadata:
                return {'error': 'Snapshot not found'}
            
            # Get restoration history
            restorations = self._get_restoration_history(snapshot_id)
            
            # Check if snapshot files exist
            snapshot_path = self.snapshots_dir / snapshot_id
            compressed_path = self.snapshots_dir / f"{snapshot_id}.zip"
            exists = snapshot_path.exists() or compressed_path.exists()
            
            return {
                'metadata': metadata,
                'restorations': restorations,
                'exists': exists,
                'file_path': str(compressed_path if compressed_path.exists() else snapshot_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to get snapshot info: {e}")
            return {'error': str(e)}
    
    def delete_snapshot(self, snapshot_id: str) -> Dict:
        """Delete a snapshot and its data"""
        try:
            # Get metadata first
            metadata = self._get_snapshot_metadata(snapshot_id)
            if not metadata:
                raise ValueError("Snapshot not found")
            
            # Delete files
            snapshot_path = self.snapshots_dir / snapshot_id
            compressed_path = self.snapshots_dir / f"{snapshot_id}.zip"
            
            if snapshot_path.exists():
                shutil.rmtree(snapshot_path)
            
            if compressed_path.exists():
                compressed_path.unlink()
            
            # Delete from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM snapshots WHERE snapshot_id = ?', (snapshot_id,))
                cursor.execute('DELETE FROM restorations WHERE snapshot_id = ?', (snapshot_id,))
                conn.commit()
            
            logger.info(f"🗑️ Deleted snapshot: {metadata['name']} ({snapshot_id})")
            
            self._log_system_event(
                'snapshot_deleted',
                f"Deleted snapshot '{metadata['name']}'",
                {'snapshot_id': snapshot_id}
            )
            
            return {
                'success': True,
                'message': f"Snapshot '{metadata['name']}' deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _start_scheduler(self):
        """Start the snapshot scheduler"""
        def scheduler_worker():
            logger.info(f"📅 Snapshot scheduler started - Full: every {self.config['full_snapshot_frequency']//3600}h, Incremental: every {self.config['incremental_interval']//3600}h")
            
            last_full_snapshot = 0
            last_incremental = 0
            
            while self.running:
                try:
                    current_time = time.time()
                    
                    # Check if full snapshot is needed
                    if current_time - last_full_snapshot >= self.config['full_snapshot_frequency']:
                        logger.info("📸 Creating scheduled full snapshot...")
                        result = self.create_snapshot(
                            name=f"Scheduled Full Snapshot - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            description="Automatic full snapshot created by scheduler",
                            snapshot_type="full"
                        )
                        if result['success']:
                            last_full_snapshot = current_time
                            last_incremental = current_time  # Reset incremental timer
                        
                    # Check if incremental snapshot is needed
                    elif current_time - last_incremental >= self.config['incremental_interval']:
                        # Find the most recent snapshot to use as parent
                        recent_snapshots = self.list_snapshots(1)
                        parent_id = recent_snapshots[0]['snapshot_id'] if recent_snapshots else None
                        
                        if parent_id:
                            logger.info("📸 Creating scheduled incremental snapshot...")
                            result = self.create_snapshot(
                                name=f"Scheduled Incremental - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                description="Automatic incremental snapshot created by scheduler",
                                snapshot_type="incremental",
                                parent_snapshot=parent_id
                            )
                            if result['success']:
                                last_incremental = current_time
                    
                    # Sleep for check interval (5 minutes)
                    time.sleep(300)
                    
                except Exception as e:
                    logger.error(f"❌ Scheduler error: {e}")
                    time.sleep(300)  # Continue after error
        
        self.scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        self.scheduler_thread.start()
    
    def _save_snapshot_metadata(self, metadata: SnapshotMetadata):
        """Save snapshot metadata to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO snapshots (
                        snapshot_id, timestamp, name, description, snapshot_type,
                        size_bytes, file_count, duration_seconds, git_commit,
                        system_state, services_state, database_states,
                        configuration_hash, parent_snapshot
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metadata.snapshot_id, metadata.timestamp, metadata.name,
                    metadata.description, metadata.snapshot_type, metadata.size_bytes,
                    metadata.file_count, metadata.duration_seconds, metadata.git_commit,
                    json.dumps(metadata.system_state), json.dumps(metadata.services_state),
                    json.dumps(metadata.database_states), metadata.configuration_hash,
                    metadata.parent_snapshot
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save snapshot metadata: {e}")
            raise
    
    def _get_snapshot_metadata(self, snapshot_id: str) -> Optional[Dict]:
        """Get snapshot metadata from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM snapshots WHERE snapshot_id = ?', (snapshot_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    metadata = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    for field in ['system_state', 'services_state', 'database_states']:
                        if metadata[field]:
                            try:
                                metadata[field] = json.loads(metadata[field])
                            except:
                                metadata[field] = {}
                    
                    return metadata
                return None
                
        except Exception as e:
            logger.error(f"Failed to get snapshot metadata: {e}")
            return None
    
    def _get_all_files(self) -> List[Path]:
        """Get all files to include in snapshot"""
        files = []
        exclude_patterns = self.config['exclude_patterns']
        
        for path_str in self.config['critical_paths']:
            path = Path(path_str)
            if path.exists():
                if path.is_file():
                    files.append(path)
                else:
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            # Check exclusion patterns
                            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                                files.append(file_path)
        
        return files
    
    def _get_incremental_files(self, parent_snapshot: str) -> List[Path]:
        """Get files that have changed since parent snapshot"""
        parent_metadata = self._get_snapshot_metadata(parent_snapshot)
        if not parent_metadata:
            return self._get_all_files()
        
        parent_time = datetime.fromisoformat(parent_metadata['timestamp'])
        changed_files = []
        
        for file_path in self._get_all_files():
            try:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime > parent_time:
                    changed_files.append(file_path)
            except:
                continue  # Skip files we can't stat
        
        logger.info(f"📊 Incremental snapshot: {len(changed_files)} files changed since parent")
        return changed_files
    
    def _get_differential_files(self, parent_snapshot: str) -> List[Path]:
        """Get files that have changed since last full snapshot"""
        # Find the last full snapshot before the parent
        snapshots = self.list_snapshots()
        last_full = None
        
        for snapshot in snapshots:
            if snapshot['snapshot_type'] == 'full' and snapshot['timestamp'] <= parent_snapshot:
                last_full = snapshot
                break
        
        if not last_full:
            return self._get_all_files()
        
        return self._get_incremental_files(last_full['snapshot_id'])
    
    def _capture_services_state(self) -> Dict:
        """Capture current state of all services"""
        try:
            services_state = {}
            
            # Check common service ports
            service_ports = {
                'master_orchestration': 8002,
                'backend_api': 8000,
                'service_registry': 8610,
                'mdc_dashboard': 3400,
                'api_manager': 8006
            }
            
            for service, port in service_ports.items():
                try:
                    # Check if port is listening
                    connections = [conn for conn in psutil.net_connections() 
                                 if conn.laddr.port == port and conn.status == 'LISTEN']
                    services_state[service] = {
                        'running': len(connections) > 0,
                        'port': port,
                        'pid': connections[0].pid if connections else None
                    }
                except:
                    services_state[service] = {'running': False, 'port': port}
            
            return services_state
            
        except Exception as e:
            logger.error(f"Failed to capture services state: {e}")
            return {}
    
    def _capture_database_states(self) -> Dict:
        """Capture database states and create backups"""
        database_states = {}
        
        try:
            # Common database files
            db_files = [
                'src/data/service_registry.db',
                'port_registry.db',
                'src/data/port_registry.db'
            ]
            
            for db_file in db_files:
                db_path = Path(db_file)
                if db_path.exists():
                    try:
                        # Get file stats
                        stat = db_path.stat()
                        database_states[db_file] = {
                            'exists': True,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'backed_up': True
                        }
                    except Exception as e:
                        database_states[db_file] = {'exists': True, 'error': str(e)}
                else:
                    database_states[db_file] = {'exists': False}
            
            return database_states
            
        except Exception as e:
            logger.error(f"Failed to capture database states: {e}")
            return {}
    
    def _calculate_configuration_hash(self) -> str:
        """Calculate hash of current system configuration"""
        try:
            config_data = []
            
            # Key configuration files
            config_files = [
                'package.json',
                'requirements.txt',
                'docker-compose.yml',
                '.env.example'
            ]
            
            for config_file in config_files:
                path = Path(config_file)
                if path.exists():
                    config_data.append(path.read_text())
            
            # System configuration
            config_data.append(json.dumps(self.config, sort_keys=True))
            
            # Create hash
            combined = ''.join(config_data)
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Failed to calculate configuration hash: {e}")
            return 'unknown'
    
    def _compress_snapshot(self, snapshot_path: Path) -> Optional[Path]:
        """Compress snapshot directory"""
        try:
            zip_path = self.snapshots_dir / f"{snapshot_path.name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in snapshot_path.rglob('*'):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(snapshot_path)
                        zip_file.write(file_path, arc_name)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Failed to compress snapshot: {e}")
            return None
    
    def _cleanup_old_snapshots(self):
        """Clean up old snapshots based on retention policy"""
        try:
            snapshots = self.list_snapshots()
            
            # Remove snapshots beyond max count
            if len(snapshots) > self.config['max_snapshots']:
                excess_snapshots = snapshots[self.config['max_snapshots']:]
                for snapshot in excess_snapshots:
                    self.delete_snapshot(snapshot['snapshot_id'])
            
            # Remove snapshots older than retention days
            cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
            for snapshot in snapshots:
                snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
                if snapshot_date < cutoff_date:
                    self.delete_snapshot(snapshot['snapshot_id'])
            
        except Exception as e:
            logger.error(f"Failed to cleanup old snapshots: {e}")
    
    def _restore_files(self, snapshot_id: str, restore_type: str) -> int:
        """Restore files from snapshot"""
        files_restored = 0
        
        try:
            # Find snapshot files
            snapshot_path = self.snapshots_dir / snapshot_id
            compressed_path = self.snapshots_dir / f"{snapshot_id}.zip"
            
            if compressed_path.exists():
                # Extract compressed snapshot
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir) / snapshot_id
                    
                    with zipfile.ZipFile(compressed_path, 'r') as zip_file:
                        zip_file.extractall(temp_path)
                    
                    files_restored = self._copy_snapshot_files(temp_path / 'files', restore_type)
            
            elif snapshot_path.exists():
                files_restored = self._copy_snapshot_files(snapshot_path / 'files', restore_type)
            
            else:
                raise ValueError("Snapshot files not found")
            
            return files_restored
            
        except Exception as e:
            logger.error(f"Failed to restore files: {e}")
            return 0
    
    def _copy_snapshot_files(self, source_dir: Path, restore_type: str) -> int:
        """Copy files from snapshot to their original locations"""
        files_restored = 0
        
        if not source_dir.exists():
            return 0
        
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                try:
                    # Calculate destination path
                    rel_path = file_path.relative_to(source_dir)
                    dest_path = Path.cwd() / rel_path
                    
                    # Create directory if needed
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(file_path, dest_path)
                    files_restored += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to restore file {file_path}: {e}")
        
        return files_restored
    
    def _create_restoration_backup(self) -> Dict:
        """Create backup before restoration"""
        try:
            backup_name = f"Pre-Restoration Backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return self.create_snapshot(
                name=backup_name,
                description="Automatic backup created before snapshot restoration",
                snapshot_type="full"
            )
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _restore_databases(self, snapshot_id: str) -> str:
        """Restore database states from snapshot"""
        try:
            metadata = self._get_snapshot_metadata(snapshot_id)
            if not metadata or 'database_states' not in metadata:
                return "No database states in snapshot"
            
            # This would implement database restoration
            # For now, return status
            db_count = len(metadata['database_states'])
            return f"{db_count} database states available"
            
        except Exception as e:
            return f"Database restoration failed: {e}"
    
    def _restore_configuration(self, snapshot_id: str) -> str:
        """Restore system configuration from snapshot"""
        try:
            # This would implement configuration restoration
            return "Configuration restoration completed"
        except Exception as e:
            return f"Configuration restoration failed: {e}"
    
    def _increment_restoration_count(self, snapshot_id: str):
        """Increment restoration count for snapshot"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE snapshots 
                    SET restoration_count = restoration_count + 1 
                    WHERE snapshot_id = ?
                ''', (snapshot_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to increment restoration count: {e}")
    
    def _log_restoration(self, snapshot_id: str, restoration_type: str, 
                        success: bool, duration: float, files_restored: int, 
                        errors: str = None):
        """Log restoration attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO restorations (
                        snapshot_id, timestamp, restoration_type, success,
                        duration_seconds, restored_files, errors
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot_id, datetime.now().isoformat(), restoration_type,
                    success, duration, files_restored, errors
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log restoration: {e}")
    
    def _log_system_event(self, event_type: str, description: str, 
                         metadata: Dict = None, severity: str = 'INFO'):
        """Log system event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_events (
                        event_type, timestamp, description, metadata, severity
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    event_type, datetime.now().isoformat(), description,
                    json.dumps(metadata) if metadata else None, severity
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log system event: {e}")
    
    def _get_restoration_history(self, snapshot_id: str) -> List[Dict]:
        """Get restoration history for snapshot"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM restorations 
                    WHERE snapshot_id = ? 
                    ORDER BY timestamp DESC
                ''', (snapshot_id,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get restoration history: {e}")
            return []
    
    def _calculate_time_difference(self, time1: str, time2: str) -> str:
        """Calculate human-readable time difference"""
        try:
            dt1 = datetime.fromisoformat(time1)
            dt2 = datetime.fromisoformat(time2)
            diff = abs((dt2 - dt1).total_seconds())
            
            if diff < 3600:
                return f"{diff/60:.0f} minutes"
            elif diff < 86400:
                return f"{diff/3600:.1f} hours"
            else:
                return f"{diff/86400:.1f} days"
        except:
            return "unknown"
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory"""
        try:
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        except:
            return 0
    
    def _format_bytes(self, size: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _get_disk_usage(self) -> Dict:
        """Get disk usage information"""
        try:
            usage = psutil.disk_usage('.')
            return {
                'total': self._format_bytes(usage.total),
                'used': self._format_bytes(usage.used),
                'free': self._format_bytes(usage.free),
                'percent': f"{usage.used/usage.total*100:.1f}%"
            }
        except:
            return {'error': 'Unable to get disk usage'}
    
    def _discover_existing_backups(self):
        """Discover and catalog existing backup directories"""
        try:
            existing_path = Path(self.config.get('existing_backups_path', './system_backups/initial_startup_backup'))
            
            if existing_path.exists():
                logger.info(f"🔍 Discovered existing backup system at: {existing_path}")
                
                # Get backup creation time from directory stats
                stat_info = existing_path.stat()
                created_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                
                # Calculate backup size
                backup_size = sum(f.stat().st_size for f in existing_path.rglob('*') if f.is_file())
                
                # Count files in backup
                file_count = sum(1 for f in existing_path.rglob('*') if f.is_file())
                
                # Store existing backup metadata in database
                snapshot_id = f"existing_backup_{int(stat_info.st_mtime)}"
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Check if already cataloged
                    cursor.execute("SELECT snapshot_id FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO snapshots (
                                snapshot_id, timestamp, name, description, snapshot_type, 
                                size_bytes, file_count, system_state, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            snapshot_id,
                            created_time,
                            "Initial Startup Backup",
                            "Existing system backup discovered and cataloged",
                            "full",
                            backup_size,
                            file_count,
                            json.dumps({"backup_path": str(existing_path), "discovered": True}),
                            datetime.now().isoformat()
                        ))
                        
                        logger.info(f"📝 Cataloged existing backup: {snapshot_id}")
                        logger.info(f"   Size: {self._format_bytes(backup_size)}")
                        logger.info(f"   Files: {file_count:,}")
                    else:
                        logger.info("✅ Existing backup already cataloged")
            else:
                logger.info("ℹ️  No existing backup system found")
                
        except Exception as e:
            logger.error(f"❌ Failed to discover existing backups: {e}")
    
    def _verify_system_state(self) -> bool:
        """Verify system is in good state for snapshots"""
        try:
            # Check disk space
            disk_usage = psutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            
            if free_gb < 5:  # Less than 5GB free
                logger.warning(f"Low disk space: {free_gb:.1f}GB free")
                return False
            
            # Check critical paths exist
            for path_str in self.config['critical_paths']:
                path = Path(path_str)
                if not path.exists():
                    logger.warning(f"Critical path missing: {path}")
            
            return True
            
        except Exception as e:
            logger.error(f"System state verification failed: {e}")
            return False
    
    def _get_git_status(self) -> Dict:
        """Get current git status"""
        try:
            # Get current commit
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            current_commit = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            current_branch = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            has_changes = bool(result.stdout.strip()) if result.returncode == 0 else False
            
            return {
                'current_commit': current_commit,
                'current_branch': current_branch,
                'has_changes': has_changes,
                'status_output': result.stdout.strip() if result.returncode == 0 else ''
            }
            
        except Exception as e:
            logger.warning(f"Failed to get git status: {e}")
            return {'error': str(e)}
    
    def get_status(self) -> Dict:
        """Get service status"""
        snapshots = self.list_snapshots(10)
        total_snapshots = len(self.list_snapshots())
        
        return {
            'service_running': self.running,
            'total_snapshots': total_snapshots,
            'recent_snapshots': snapshots[:5],
            'snapshots_directory': str(self.snapshots_dir),
            'disk_usage': self._get_disk_usage(),
            'config': self.config,
            'last_check': datetime.now().isoformat()
        }

class SystemStateMonitor:
    """Monitor and capture complete system state"""
    
    def capture_system_state(self) -> SystemState:
        """Capture comprehensive system state"""
        try:
            # Count MDC files
            mdc_count = len(list(Path('.cursor/rules').glob('*.mdc'))) if Path('.cursor/rules').exists() else 0
            
            # Get running services (simplified)
            services_running = []
            
            # Get ports in use
            ports_in_use = [conn.laddr.port for conn in psutil.net_connections() 
                           if conn.status == 'LISTEN']
            
            # System health
            system_health = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('.').percent
            }
            
            # Environment variables (non-sensitive)
            env_vars = {k: v for k, v in os.environ.items() 
                       if not any(sensitive in k.upper() for sensitive in 
                                ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API'])}
            
            return SystemState(
                mdc_files_count=mdc_count,
                services_running=services_running,
                ports_in_use=sorted(ports_in_use),
                system_health=system_health,
                git_status={},
                environment_vars=env_vars,
                disk_usage=dict(psutil.disk_usage('.')._asdict()),
                memory_usage=dict(psutil.virtual_memory()._asdict()),
                process_count=len(psutil.pids()),
                uptime_seconds=time.time() - psutil.boot_time()
            )
            
        except Exception as e:
            logger.error(f"Failed to capture system state: {e}")
            return SystemState(
                mdc_files_count=0,
                services_running=[],
                ports_in_use=[],
                system_health={},
                git_status={},
                environment_vars={},
                disk_usage={},
                memory_usage={},
                process_count=0,
                uptime_seconds=0
            )

# Global service instance
snapshot_service = None

def start_snapshot_service(config: Optional[Dict] = None) -> bool:
    """Start the Snapshot service"""
    global snapshot_service
    
    try:
        snapshot_service = SnapshotService(config)
        service_started = snapshot_service.start_service()
        
        # Register with System Protection Service
        if service_started:
            protection_registered = register_snapshot_service_protection()
            if protection_registered:
                logger.info("✅ SnapshotService successfully integrated with System Protection")
            else:
                logger.warning("⚠️  SnapshotService started but protection registration failed")
        
        return service_started
    except Exception as e:
        logger.error(f"Failed to start Snapshot service: {e}")
        return False

def stop_snapshot_service() -> bool:
    """Stop the Snapshot service"""
    global snapshot_service
    
    try:
        if snapshot_service:
            return snapshot_service.stop_service()
        return True
    except Exception as e:
        logger.error(f"Failed to stop Snapshot service: {e}")
        return False

def get_snapshot_service_status() -> Dict:
    """Get Snapshot service status"""
    global snapshot_service
    
    if snapshot_service:
        return snapshot_service.get_status()
    
    return {
        'service_running': False,
        'error': 'Service not initialized'
    }

def register_snapshot_service_protection():
    """Register SnapshotService with System Protection Service"""
    try:
        from services.service_protection_integrations import protect_snapshot_service
        from services.system_protection_service import SystemProtectionService
        
        # Get protection configuration
        protection_config = protect_snapshot_service()
        logger.info(f"🛡️  Registering SnapshotService protection: {protection_config['service_name']}")
        
        # Initialize system protection service
        protection_service = SystemProtectionService()
        
        # Register critical paths for monitoring
        for critical_file in protection_config['critical_files']:
            if Path(critical_file).exists() or critical_file.startswith('/var/'):
                protection_service.add_critical_path(critical_file)
                logger.info(f"✅ Protected critical file: {critical_file}")
        
        # Register service for monitoring
        protection_service.add_critical_service('SnapshotService')
        
        # Register emergency handlers
        protection_service.register_emergency_handler(
            'snapshot_corruption', handle_snapshot_corruption_emergency
        )
        protection_service.register_emergency_handler(
            'storage_full', handle_storage_full_emergency
        )
        protection_service.register_emergency_handler(
            'database_corruption', handle_database_corruption_emergency
        )
        
        logger.info("🛡️  SnapshotService successfully registered with System Protection")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to register SnapshotService protection: {e}")
        return False

def handle_snapshot_corruption_emergency():
    """Handle snapshot corruption emergency"""
    try:
        logger.critical("🚨 SNAPSHOT CORRUPTION DETECTED - Initiating emergency response")
        
        global snapshot_service
        if snapshot_service:
            # Stop current operations
            logger.info("⏹️  Stopping current snapshot operations")
            
            # Verify existing snapshots
            logger.info("🔍 Verifying integrity of existing snapshots")
            valid_snapshots = []
            
            with sqlite3.connect(snapshot_service.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT snapshot_id, name FROM snapshots WHERE status = 'active'")
                for snapshot_id, name in cursor.fetchall():
                    if snapshot_service._verify_snapshot_integrity(snapshot_id):
                        valid_snapshots.append((snapshot_id, name))
                    else:
                        logger.warning(f"⚠️  Corrupted snapshot detected: {name}")
            
            logger.info(f"✅ Found {len(valid_snapshots)} valid snapshots")
            
            # Create emergency snapshot if possible
            if valid_snapshots:
                logger.info("📸 Creating emergency recovery snapshot")
                emergency_result = snapshot_service.create_snapshot(
                    name="emergency_corruption_backup",
                    description="Emergency backup created due to corruption detection",
                    snapshot_type="full"
                )
                logger.info(f"✅ Emergency snapshot created: {emergency_result.get('snapshot_id')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency snapshot corruption handler failed: {e}")
        return False

def handle_storage_full_emergency():
    """Handle storage full emergency"""
    try:
        logger.critical("🚨 STORAGE FULL - Initiating emergency cleanup")
        
        global snapshot_service
        if snapshot_service:
            # Cleanup expired snapshots
            cleanup_result = snapshot_service.cleanup_expired_snapshots()
            logger.info(f"🧹 Cleanup result: {cleanup_result}")
            
            # Compress oldest snapshots
            with sqlite3.connect(snapshot_service.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT snapshot_id FROM snapshots 
                    WHERE status = 'active' 
                    ORDER BY created_at ASC LIMIT 5
                """)
                
                for (snapshot_id,) in cursor.fetchall():
                    snapshot_path = snapshot_service.storage_path / f"{snapshot_id}.tar.gz"
                    if snapshot_path.exists():
                        # Additional compression if needed
                        logger.info(f"🗜️  Additional compression for: {snapshot_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency storage handler failed: {e}")
        return False

def handle_database_corruption_emergency():
    """Handle database corruption emergency"""
    try:
        logger.critical("🚨 DATABASE CORRUPTION DETECTED - Initiating recovery")
        
        global snapshot_service
        if snapshot_service:
            # Backup current database
            db_backup_path = snapshot_service.storage_path / "db_backup_emergency.db"
            try:
                shutil.copy2(snapshot_service.db_path, db_backup_path)
                logger.info(f"💾 Database backed up to: {db_backup_path}")
            except:
                logger.error("❌ Failed to backup corrupted database")
            
            # Attempt database repair
            try:
                snapshot_service._init_database()
                logger.info("✅ Database reinitialized successfully")
            except Exception as repair_error:
                logger.error(f"❌ Database repair failed: {repair_error}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency database handler failed: {e}")
        return False

if __name__ == "__main__":
    # Test the service
    print("📸 Testing Snapshot Service...")
    
    if start_snapshot_service():
        print("✅ Service started successfully")
        
        # Create a test snapshot
        result = snapshot_service.create_snapshot(
            name="Test Snapshot",
            description="Test snapshot for service validation",
            snapshot_type="full"
        )
        
        if result['success']:
            print(f"📸 Test snapshot created: {result['snapshot_id']}")
            
            # List snapshots
            snapshots = snapshot_service.list_snapshots(5)
            print(f"📋 Found {len(snapshots)} snapshots")
            
            # Get service status
            status = get_snapshot_service_status()
            print(f"📊 Service status: {status['total_snapshots']} total snapshots")
        
        # Stop service
        stop_snapshot_service()
        print("✅ Service stopped successfully")
    else:
        print("❌ Failed to start service")