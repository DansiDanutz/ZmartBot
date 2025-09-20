#!/usr/bin/env python3
"""
Log Rotation Manager for ZmartBot System
Handles automatic log rotation, compression, and cleanup for all system logs.
"""

import os
import gzip
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json
from dataclasses import dataclass

@dataclass
class LogFile:
    """Represents a log file with its rotation settings"""
    path: str
    max_size_mb: int = 10
    max_files: int = 5
    compress: bool = True
    enabled: bool = True

class LogRotationManager:
    """Manages log rotation for the ZmartBot system"""
    
    def __init__(self, config_path: str = "log_rotation_config.json"):
        self.config_path = Path(config_path)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Load configuration
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load log rotation configuration"""
        default_config = {
            "log_files": [
                {
                    "path": "logs/mdc_dashboard_8090.log",
                    "max_size_mb": 5,
                    "max_files": 3,
                    "compress": True,
                    "enabled": True
                },
                {
                    "path": "logs/mdc_dashboard.log", 
                    "max_size_mb": 5,
                    "max_files": 3,
                    "compress": True,
                    "enabled": True
                },
                {
                    "path": "logs/cryptometer-service.log",
                    "max_size_mb": 10,
                    "max_files": 5,
                    "compress": True,
                    "enabled": True
                },
                {
                    "path": "logs/background_optimization_agent.log",
                    "max_size_mb": 2,
                    "max_files": 3,
                    "compress": True,
                    "enabled": True
                },
                {
                    "path": "logs/system_optimization.log",
                    "max_size_mb": 5,
                    "max_files": 3,
                    "compress": True,
                    "enabled": True
                }
            ],
            "global_settings": {
                "check_interval_minutes": 60,
                "cleanup_old_logs_days": 30,
                "backup_dir": "logs/backups"
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded log rotation config from {self.config_path}")
                return config
            except Exception as e:
                self.logger.error(f"Error loading config: {e}, using defaults")
        else:
            # Create default config file
            self.save_config(default_config)
            self.logger.info(f"Created default config at {self.config_path}")
            
        return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in MB"""
        try:
            return file_path.stat().st_size / (1024 * 1024)
        except FileNotFoundError:
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting file size for {file_path}: {e}")
            return 0.0
    
    def rotate_log_file(self, log_file_config: Dict) -> bool:
        """Rotate a single log file"""
        try:
            log_path = Path(log_file_config["path"])
            max_size_mb = log_file_config["max_size_mb"]
            max_files = log_file_config["max_files"]
            compress = log_file_config["compress"]
            
            if not log_path.exists():
                return True  # Nothing to rotate
            
            current_size_mb = self.get_file_size_mb(log_path)
            
            if current_size_mb < max_size_mb:
                return True  # File not large enough to rotate
            
            self.logger.info(f"Rotating log file: {log_path} (size: {current_size_mb:.2f}MB)")
            
            # Create backup directory
            backup_dir = Path(self.config["global_settings"]["backup_dir"])
            backup_dir.mkdir(exist_ok=True)
            
            # Rotate existing files
            for i in range(max_files - 1, 0, -1):
                old_file = backup_dir / f"{log_path.stem}.{i}"
                if compress and i > 1:
                    old_file = backup_dir / f"{log_path.stem}.{i}.gz"
                new_file = backup_dir / f"{log_path.stem}.{i + 1}"
                if compress and i > 0:
                    new_file = backup_dir / f"{log_path.stem}.{i + 1}.gz"
                
                if old_file.exists():
                    if i == max_files - 1:
                        # Remove oldest file
                        old_file.unlink()
                    else:
                        shutil.move(str(old_file), str(new_file))
            
            # Move current log to .1
            current_backup = backup_dir / f"{log_path.stem}.1"
            shutil.move(str(log_path), str(current_backup))
            
            # Compress if enabled
            if compress:
                with open(current_backup, 'rb') as f_in:
                    with gzip.open(f"{current_backup}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                current_backup.unlink()  # Remove uncompressed file
            
            # Create new empty log file
            log_path.touch()
            
            self.logger.info(f"Successfully rotated {log_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rotating log file {log_file_config['path']}: {e}")
            return False
    
    def cleanup_old_logs(self):
        """Clean up old log files based on retention policy"""
        try:
            backup_dir = Path(self.config["global_settings"]["backup_dir"])
            cleanup_days = self.config["global_settings"]["cleanup_old_logs_days"]
            cutoff_date = datetime.now() - timedelta(days=cleanup_days)
            
            if not backup_dir.exists():
                return
            
            cleaned_count = 0
            for log_file in backup_dir.iterdir():
                if log_file.is_file():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        cleaned_count += 1
                        self.logger.info(f"Cleaned up old log: {log_file}")
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old log files")
                
        except Exception as e:
            self.logger.error(f"Error during log cleanup: {e}")
    
    def rotate_all_logs(self) -> Dict[str, bool]:
        """Rotate all configured log files"""
        results = {}
        
        for log_file_config in self.config["log_files"]:
            if log_file_config.get("enabled", True):
                log_path = log_file_config["path"]
                results[log_path] = self.rotate_log_file(log_file_config)
            else:
                results[log_file_config["path"]] = True  # Skip disabled files
        
        # Cleanup old logs
        self.cleanup_old_logs()
        
        return results
    
    def get_log_status(self) -> Dict[str, Dict]:
        """Get status of all log files"""
        status = {}
        
        for log_file_config in self.config["log_files"]:
            log_path = Path(log_file_config["path"])
            status[log_file_config["path"]] = {
                "exists": log_file_config["path"],
                "size_mb": self.get_file_size_mb(log_path),
                "max_size_mb": log_file_config["max_size_mb"],
                "needs_rotation": self.get_file_size_mb(log_path) >= log_file_config["max_size_mb"],
                "enabled": log_file_config.get("enabled", True)
            }
        
        return status
    
    def create_rotation_report(self) -> str:
        """Create a detailed rotation report"""
        status = self.get_log_status()
        report = []
        
        report.append("=" * 60)
        report.append("ZmartBot Log Rotation Status Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for log_path, info in status.items():
            report.append(f"Log File: {log_path}")
            report.append(f"  Size: {info['size_mb']:.2f}MB / {info['max_size_mb']}MB")
            report.append(f"  Status: {'NEEDS ROTATION' if info['needs_rotation'] else 'OK'}")
            report.append(f"  Enabled: {info['enabled']}")
            report.append("")
        
        # Check backup directory
        backup_dir = Path(self.config["global_settings"]["backup_dir"])
        if backup_dir.exists():
            backup_files = list(backup_dir.iterdir())
            report.append(f"Backup Directory: {backup_dir}")
            report.append(f"  Files: {len(backup_files)}")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Log Rotation Manager")
    parser.add_argument("--rotate", action="store_true", help="Rotate all log files")
    parser.add_argument("--status", action="store_true", help="Show log status")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--config", default="log_rotation_config.json", help="Config file path")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = LogRotationManager(args.config)
    
    if args.rotate:
        print("🔄 Rotating log files...")
        results = manager.rotate_all_logs()
        for log_path, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {log_path}")
    
    if args.status:
        print("📊 Log file status:")
        status = manager.get_log_status()
        for log_path, info in status.items():
            size_status = "🔴" if info['needs_rotation'] else "🟢"
            print(f"{size_status} {log_path}: {info['size_mb']:.2f}MB / {info['max_size_mb']}MB")
    
    if args.report:
        print(manager.create_rotation_report())
    
    if not any([args.rotate, args.status, args.report]):
        # Default: show status
        print("📊 Log file status:")
        status = manager.get_log_status()
        for log_path, info in status.items():
            size_status = "🔴" if info['needs_rotation'] else "🟢"
            print(f"{size_status} {log_path}: {info['size_mb']:.2f}MB / {info['max_size_mb']}MB")

if __name__ == "__main__":
    main()
