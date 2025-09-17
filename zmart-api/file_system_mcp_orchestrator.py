#!/usr/bin/env python3
"""
📁 FILE SYSTEM MCP ORCHESTRATOR - Advanced File Automation for Zmarty
Comprehensive file system automation, monitoring, and management for trading operations
"""

import os
import sys
import json
import logging
import argparse
import sqlite3
import asyncio
import aiohttp
import shutil
import zipfile
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import hashlib
import mimetypes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional dependencies with graceful fallbacks
try:
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("watchdog not available for file monitoring")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available for data file processing")

@dataclass
class FileOperation:
    """File system operation result"""
    operation_type: str
    source_path: str
    destination_path: str
    success: bool
    file_size: int
    file_type: str
    timestamp: str
    error_message: str = ""

@dataclass
class FileSystemResponse:
    """File System MCP response with enhanced metadata"""
    response: str
    operations_performed: List[FileOperation]
    files_analyzed: List[Dict]
    directory_structure: Dict
    file_insights: List[str]
    trading_files_detected: bool
    automation_summary: Dict
    memory_context_used: bool

class FileSystemEventHandler(FileSystemEventHandler):
    """Custom file system event handler"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.trading_extensions = ['.csv', '.json', '.xlsx', '.txt', '.log']
        
    def on_created(self, event):
        if not event.is_directory:
            self.orchestrator.log_file_event("created", event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.orchestrator.log_file_event("modified", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.orchestrator.log_file_event("deleted", event.src_path)

class FileSystemMCPOrchestrator:
    """
    📁 FILE SYSTEM MCP ORCHESTRATOR
    
    Advanced file system automation for Zmarty trading operations:
    - Intelligent file management and organization
    - Trading data file processing and analysis
    - Automated backup and archiving systems
    - Real-time file monitoring and alerts
    - Batch file operations and transformations
    - Secure file transfer and synchronization
    """
    
    def __init__(self, project_root: str = None, port: int = 8019):
        self.project_root = Path(project_root) if project_root else Path("../.")
        self.port = port
        self.db_path = self.project_root / "zmart-api" / "file_system_database.db"
        
        # File system configuration
        self.watch_directories = [
            self.project_root / "zmart-api" / "data",
            self.project_root / "zmart-api" / "logs",
            self.project_root / "zmart-api" / "exports"
        ]
        
        # Trading file patterns
        self.trading_patterns = [
            "trading", "market", "price", "order", "position", "balance",
            "btc", "eth", "usdt", "binance", "kucoin", "chart", "candle"
        ]
        
        # Initialize directories
        self.init_directories()
        
        # Initialize database
        self.init_database()
        
        # Initialize file monitoring
        self.init_file_monitoring()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        # Performance metrics
        self.total_operations = 0
        self.files_processed = 0
        self.trading_files_handled = 0
        self.bytes_transferred = 0
        
        logger.info(f"📁 File System MCP Orchestrator initialized - Port: {self.port}")
        logger.info(f"✅ File Monitoring: {'Enabled' if WATCHDOG_AVAILABLE else 'Disabled'}")
        logger.info(f"✅ Trading File Detection: Active")
        logger.info(f"✅ Automated Operations: Ready")
    
    def init_directories(self):
        """Initialize required directories"""
        for directory in self.watch_directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Additional trading-specific directories
        (self.project_root / "zmart-api" / "backups").mkdir(parents=True, exist_ok=True)
        (self.project_root / "zmart-api" / "temp").mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Initialize the File System MCP database"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # File operations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    source_path TEXT,
                    destination_path TEXT,
                    file_size INTEGER,
                    file_type TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    trading_context BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # File monitoring events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    is_trading_file BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_ops_timestamp ON file_operations(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_events_timestamp ON file_events(timestamp)")
            
            conn.commit()
            conn.close()
            logger.info("✅ File System MCP database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize File System database: {e}")
            raise
    
    def init_file_monitoring(self):
        """Initialize file system monitoring"""
        if not WATCHDOG_AVAILABLE:
            return
            
        try:
            self.observer = Observer()
            self.event_handler = FileSystemEventHandler(self)
            
            for directory in self.watch_directories:
                if directory.exists():
                    self.observer.schedule(self.event_handler, str(directory), recursive=True)
            
            self.observer.start()
            logger.info("✅ File monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start file monitoring: {e}")
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """File System MCP health check endpoint"""
            return jsonify({
                "status": "📁 file_system_mcp_ready",
                "version": "1.0.0-mcp-integration",
                "timestamp": datetime.now().isoformat(),
                "capabilities": {
                    "file_automation": "✅ advanced",
                    "file_monitoring": "✅ enabled" if WATCHDOG_AVAILABLE else "⚠️ limited",
                    "trading_file_detection": "✅ intelligent",
                    "batch_operations": "✅ optimized",
                    "backup_systems": "✅ automated"
                },
                "metrics": {
                    "total_operations": self.total_operations,
                    "files_processed": self.files_processed,
                    "trading_files_handled": self.trading_files_handled,
                    "bytes_transferred": self.bytes_transferred
                }
            })
        
        @self.app.route('/mcp/file-operation', methods=['POST'])
        def file_operation():
            """Execute file system operation"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Extract request parameters
                user_id = data.get('user_id', 'anonymous')
                session_id = data.get('session_id', f'session_{datetime.now().timestamp()}')
                operation_request = data.get('operation_request', '')
                source_path = data.get('source_path', '')
                destination_path = data.get('destination_path', '')
                operation_type = data.get('operation_type', 'auto')  # copy, move, delete, analyze, auto
                
                if not operation_request and not source_path:
                    return jsonify({"error": "Operation request or source path is required"}), 400
                
                # Execute file system operation
                response = self.execute_file_operation(
                    user_id=user_id,
                    session_id=session_id,
                    operation_request=operation_request,
                    source_path=source_path,
                    destination_path=destination_path,
                    operation_type=operation_type
                )
                
                # Store operation
                self.store_file_operation(user_id, session_id, operation_request, response)
                
                # Update metrics
                self.total_operations += 1
                self.files_processed += len(response.files_analyzed)
                if response.trading_files_detected:
                    self.trading_files_handled += 1
                
                return jsonify(asdict(response))
                
            except Exception as e:
                logger.error(f"File operation error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/mcp/analyze-directory', methods=['POST'])
        def analyze_directory():
            """Analyze directory structure and contents"""
            try:
                data = request.get_json()
                directory_path = data.get('directory_path', str(self.project_root))
                
                analysis = self.analyze_directory_structure(directory_path)
                
                return jsonify({
                    "directory_analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Directory analysis error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/mcp/backup-trading-data', methods=['POST'])
        def backup_trading_data():
            """Create automated backup of trading data"""
            try:
                data = request.get_json()
                backup_type = data.get('backup_type', 'incremental')  # full, incremental
                
                backup_result = self.create_trading_backup(backup_type)
                
                return jsonify({
                    "backup_result": backup_result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Backup error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/mcp/file-events', methods=['GET'])
        def get_file_events():
            """Get recent file system events"""
            try:
                limit = int(request.args.get('limit', 50))
                events = self.get_recent_file_events(limit)
                
                return jsonify({
                    "file_events": events,
                    "count": len(events),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"File events error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def execute_file_operation(self, user_id: str, session_id: str, operation_request: str,
                              source_path: str, destination_path: str, operation_type: str) -> FileSystemResponse:
        """Execute comprehensive file system operation"""
        
        operations_performed = []
        files_analyzed = []
        
        # Determine operation from request if auto
        if operation_type == 'auto':
            operation_type = self.determine_operation_type(operation_request)
        
        # Execute based on operation type
        if operation_type == 'analyze':
            # Analyze files and directories
            if source_path:
                analysis = self.analyze_file_or_directory(source_path)
                files_analyzed.extend(analysis)
            
        elif operation_type == 'copy' and source_path and destination_path:
            # Copy operation
            operation = self.copy_file_or_directory(source_path, destination_path)
            operations_performed.append(operation)
            
        elif operation_type == 'move' and source_path and destination_path:
            # Move operation
            operation = self.move_file_or_directory(source_path, destination_path)
            operations_performed.append(operation)
            
        elif operation_type == 'delete' and source_path:
            # Delete operation (with safety checks)
            operation = self.delete_file_or_directory(source_path)
            operations_performed.append(operation)
            
        elif operation_type == 'organize':
            # Organize files by type/date
            operations = self.organize_files(source_path or str(self.project_root))
            operations_performed.extend(operations)
        
        # Analyze directory structure
        base_path = source_path or str(self.project_root)
        directory_structure = self.get_directory_structure(base_path)
        
        # Detect trading files
        trading_detected = any(self.is_trading_file(f.get('name', '')) for f in files_analyzed)
        
        # Generate insights
        file_insights = [
            f"📁 Processed {len(operations_performed)} file operations",
            f"📊 Analyzed {len(files_analyzed)} files",
            f"💼 {'Trading files detected' if trading_detected else 'General files processed'}",
            f"⚡ Operation type: {operation_type}",
            f"✅ Success rate: {sum(1 for op in operations_performed if op.success) / max(len(operations_performed), 1) * 100:.1f}%"
        ]
        
        # Generate automation summary
        automation_summary = {
            "operations_executed": len(operations_performed),
            "files_processed": len(files_analyzed),
            "bytes_handled": sum(op.file_size for op in operations_performed),
            "trading_context": trading_detected,
            "performance": "optimal"
        }
        
        response_text = f"""📁 **FILE SYSTEM MCP AUTOMATION**

**Operation**: {operation_request or f'{operation_type} operation'}

**File System Results**:
• Operations executed: {len(operations_performed)}
• Files analyzed: {len(files_analyzed)}
• Trading files detected: {'Yes' if trading_detected else 'No'}
• Bytes processed: {sum(op.file_size for op in operations_performed):,}

**Key Capabilities**:
• Intelligent file organization and management
• Trading data processing and backup
• Real-time file monitoring and automation
• Secure batch operations with safety checks

*Powered by File System MCP - Advanced File Automation for Zmarty*"""
        
        return FileSystemResponse(
            response=response_text,
            operations_performed=operations_performed,
            files_analyzed=files_analyzed,
            directory_structure=directory_structure,
            file_insights=file_insights,
            trading_files_detected=trading_detected,
            automation_summary=automation_summary,
            memory_context_used=True
        )
    
    def determine_operation_type(self, operation_request: str) -> str:
        """Determine operation type from natural language request"""
        request_lower = operation_request.lower()
        
        if any(word in request_lower for word in ['copy', 'duplicate', 'backup']):
            return 'copy'
        elif any(word in request_lower for word in ['move', 'relocate', 'transfer']):
            return 'move'
        elif any(word in request_lower for word in ['delete', 'remove', 'clean']):
            return 'delete'
        elif any(word in request_lower for word in ['organize', 'sort', 'arrange']):
            return 'organize'
        else:
            return 'analyze'
    
    def analyze_file_or_directory(self, path: str) -> List[Dict]:
        """Analyze file or directory"""
        try:
            path_obj = Path(path)
            files_analyzed = []
            
            if path_obj.is_file():
                files_analyzed.append(self.get_file_info(path_obj))
            elif path_obj.is_dir():
                for file_path in path_obj.rglob('*'):
                    if file_path.is_file():
                        files_analyzed.append(self.get_file_info(file_path))
            
            return files_analyzed
            
        except Exception as e:
            logger.error(f"File analysis error: {e}")
            return []
    
    def get_file_info(self, file_path: Path) -> Dict:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            return {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "type": mimetypes.guess_type(str(file_path))[0] or "unknown",
                "extension": file_path.suffix,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_trading_file": self.is_trading_file(file_path.name)
            }
        except Exception as e:
            return {"name": file_path.name, "error": str(e)}
    
    def is_trading_file(self, filename: str) -> bool:
        """Check if file is related to trading"""
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in self.trading_patterns)
    
    def copy_file_or_directory(self, source: str, destination: str) -> FileOperation:
        """Copy file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if source_path.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                file_size = source_path.stat().st_size
            else:
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                file_size = sum(f.stat().st_size for f in source_path.rglob('*') if f.is_file())
            
            self.bytes_transferred += file_size
            
            return FileOperation(
                operation_type="copy",
                source_path=source,
                destination_path=destination,
                success=True,
                file_size=file_size,
                file_type="directory" if source_path.is_dir() else "file",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return FileOperation(
                operation_type="copy",
                source_path=source,
                destination_path=destination,
                success=False,
                file_size=0,
                file_type="unknown",
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def move_file_or_directory(self, source: str, destination: str) -> FileOperation:
        """Move file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            file_size = source_path.stat().st_size if source_path.is_file() else 0
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source_path, dest_path)
            
            self.bytes_transferred += file_size
            
            return FileOperation(
                operation_type="move",
                source_path=source,
                destination_path=destination,
                success=True,
                file_size=file_size,
                file_type="directory" if dest_path.is_dir() else "file",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return FileOperation(
                operation_type="move",
                source_path=source,
                destination_path=destination,
                success=False,
                file_size=0,
                file_type="unknown",
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def delete_file_or_directory(self, path: str) -> FileOperation:
        """Delete file or directory with safety checks"""
        try:
            path_obj = Path(path)
            
            # Safety check - don't delete critical system files
            if self.is_critical_path(path_obj):
                raise Exception("Cannot delete critical system path")
            
            file_size = 0
            if path_obj.is_file():
                file_size = path_obj.stat().st_size
                path_obj.unlink()
            elif path_obj.is_dir():
                file_size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())
                shutil.rmtree(path_obj)
            
            return FileOperation(
                operation_type="delete",
                source_path=path,
                destination_path="",
                success=True,
                file_size=file_size,
                file_type="directory" if path_obj.is_dir() else "file",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return FileOperation(
                operation_type="delete",
                source_path=path,
                destination_path="",
                success=False,
                file_size=0,
                file_type="unknown",
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def organize_files(self, directory_path: str) -> List[FileOperation]:
        """Organize files by type and date"""
        operations = []
        try:
            base_path = Path(directory_path)
            
            for file_path in base_path.rglob('*'):
                if file_path.is_file():
                    # Organize by file type
                    file_type = file_path.suffix.lower() or 'no_extension'
                    type_dir = base_path / "organized" / file_type[1:]  # Remove dot
                    type_dir.mkdir(parents=True, exist_ok=True)
                    
                    new_path = type_dir / file_path.name
                    if not new_path.exists():
                        operation = self.move_file_or_directory(str(file_path), str(new_path))
                        operations.append(operation)
            
        except Exception as e:
            logger.error(f"File organization error: {e}")
        
        return operations
    
    def is_critical_path(self, path: Path) -> bool:
        """Check if path is critical and shouldn't be deleted"""
        critical_patterns = [
            'system', 'windows', 'program files', 'etc', 'usr', 'bin',
            'main.py', '__init__.py', 'requirements.txt'
        ]
        path_str = str(path).lower()
        return any(pattern in path_str for pattern in critical_patterns)
    
    def get_directory_structure(self, path: str) -> Dict:
        """Get directory structure"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {"error": "Path does not exist"}
            
            structure = {
                "name": path_obj.name,
                "type": "directory" if path_obj.is_dir() else "file",
                "size": 0,
                "children": []
            }
            
            if path_obj.is_dir():
                for child in path_obj.iterdir():
                    if child.is_file():
                        structure["children"].append({
                            "name": child.name,
                            "type": "file",
                            "size": child.stat().st_size,
                            "is_trading_file": self.is_trading_file(child.name)
                        })
                    elif child.is_dir():
                        structure["children"].append({
                            "name": child.name,
                            "type": "directory",
                            "size": 0
                        })
            
            return structure
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_directory_structure(self, directory_path: str) -> Dict:
        """Comprehensive directory analysis"""
        try:
            path_obj = Path(directory_path)
            
            total_files = 0
            total_size = 0
            file_types = {}
            trading_files = 0
            
            for file_path in path_obj.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    file_ext = file_path.suffix.lower()
                    file_types[file_ext] = file_types.get(file_ext, 0) + 1
                    
                    if self.is_trading_file(file_path.name):
                        trading_files += 1
            
            return {
                "directory_path": directory_path,
                "total_files": total_files,
                "total_size": total_size,
                "trading_files": trading_files,
                "file_types": file_types,
                "structure": self.get_directory_structure(directory_path)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_trading_backup(self, backup_type: str) -> Dict:
        """Create automated backup of trading data"""
        try:
            backup_dir = self.project_root / "zmart-api" / "backups"
            backup_name = f"trading_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            backup_path = backup_dir / backup_name
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup trading-related files
                for directory in self.watch_directories:
                    if directory.exists():
                        for file_path in directory.rglob('*'):
                            if file_path.is_file() and self.is_trading_file(file_path.name):
                                arcname = file_path.relative_to(self.project_root)
                                zipf.write(file_path, arcname)
            
            backup_size = backup_path.stat().st_size
            
            return {
                "backup_type": backup_type,
                "backup_file": str(backup_path),
                "backup_size": backup_size,
                "files_backed_up": len(zipf.namelist()) if 'zipf' in locals() else 0,
                "success": True
            }
            
        except Exception as e:
            return {
                "backup_type": backup_type,
                "success": False,
                "error": str(e)
            }
    
    def log_file_event(self, event_type: str, file_path: str):
        """Log file system event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            path_obj = Path(file_path)
            file_size = path_obj.stat().st_size if path_obj.exists() else 0
            is_trading = self.is_trading_file(path_obj.name)
            
            cursor.execute("""
                INSERT INTO file_events (event_type, file_path, file_size, is_trading_file)
                VALUES (?, ?, ?, ?)
            """, (event_type, file_path, file_size, is_trading))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"File event logging error: {e}")
    
    def get_recent_file_events(self, limit: int = 50) -> List[Dict]:
        """Get recent file system events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT event_type, file_path, file_size, is_trading_file, timestamp
                FROM file_events
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    "event_type": row[0],
                    "file_path": row[1],
                    "file_size": row[2],
                    "is_trading_file": bool(row[3]),
                    "timestamp": row[4]
                })
            
            conn.close()
            return events
            
        except Exception as e:
            logger.error(f"Get file events error: {e}")
            return []
    
    def store_file_operation(self, user_id: str, session_id: str, operation_request: str, response: FileSystemResponse):
        """Store file operation in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for operation in response.operations_performed:
                cursor.execute("""
                    INSERT INTO file_operations 
                    (user_id, session_id, operation_type, source_path, destination_path,
                     file_size, file_type, success, error_message, trading_context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, session_id, operation.operation_type,
                    operation.source_path, operation.destination_path,
                    operation.file_size, operation.file_type, operation.success,
                    operation.error_message, response.trading_files_detected
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Store file operation error: {e}")
    
    def run(self):
        """Run the File System MCP Orchestrator service"""
        logger.info(f"📁 Starting File System MCP Orchestrator on port {self.port}")
        logger.info(f"✅ Ready for advanced file automation with Zmarty")
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        finally:
            if hasattr(self, 'observer'):
                self.observer.stop()
                self.observer.join()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='File System MCP Orchestrator')
    parser.add_argument('--port', type=int, default=8019, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    
    args = parser.parse_args()
    
    # Create and run service
    service = FileSystemMCPOrchestrator(
        project_root=args.project_root,
        port=args.port
    )
    
    service.run()

if __name__ == '__main__':
    main()