#!/usr/bin/env python3
"""
ZmartBot Achievements Service
Automated daily scanning and documentation of system achievements and implementations
"""

import os
import sys
import json
import time
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib
import subprocess

class AchievementsService:
    """
    Daily achievement scanning and documentation service for ZmartBot system
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cursor_rules_dir = self.project_root / ".cursor" / "rules"
        self.achievements_file = self.cursor_rules_dir / "achievements.mdc"
        self.achievements_db = self.project_root / "zmart-api" / "achievements.db"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Achievement patterns to detect
        self.achievement_patterns = {
            'completed': [
                r'Status.*?COMPLETED?',
                r'✅.*?COMPLETED?',
                r'PRODUCTION.*?READY',
                r'ACTIVE.*?SERVICE',
                r'SUCCESS.*?IMPLEMENTATION',
                r'Version.*?[2-9]\.\d+\.\d+',
                r'ENHANCED.*?PRODUCTION'
            ],
            'performance': [
                r'(\d+(?:\.\d+)?%).*?(?:compression|efficiency|reduction|improvement)',
                r'(\d+(?:\.\d+)?)ms.*?response.*?time',
                r'(\d+(?:\.\d+)?)x.*?(?:faster|improvement)',
                r'(\d+).*?(?:files|services|connections).*?processed'
            ],
            'features': [
                r'✅.*?([A-Z][^:]+):.*?([^\\n]+)',
                r'IMPLEMENTED.*?([A-Z][^:]+)',
                r'NEW.*?FEATURE.*?([A-Z][^:]+)',
                r'ADDED.*?([A-Z][^:]+)'
            ],
            'versions': [
                r'Version.*?(\d+\.\d+\.\d+)',
                r'> Type:.*?Version: (\d+\.\d+\.\d+)'
            ]
        }
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize achievements database"""
        try:
            with sqlite3.connect(str(self.achievements_db)) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        service_name TEXT NOT NULL,
                        achievement_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        impact_level TEXT DEFAULT 'medium',
                        metrics TEXT,
                        file_path TEXT,
                        version TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_date ON achievements(date)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_service ON achievements(service_name)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_type ON achievements(achievement_type)
                ''')
                
                conn.commit()
                self.logger.info("Achievements database initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def scan_mdc_files(self) -> List[Dict[str, Any]]:
        """Scan all MDC files for achievements and implementations"""
        achievements = []
        
        try:
            for mdc_file in self.cursor_rules_dir.glob("**/*.mdc"):
                if mdc_file.name.endswith('.backup'):
                    continue
                
                try:
                    with open(mdc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract basic info
                    file_achievements = self.extract_achievements_from_content(
                        content, str(mdc_file)
                    )
                    achievements.extend(file_achievements)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process {mdc_file}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scanning MDC files: {e}")
        
        return achievements
    
    def extract_achievements_from_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract achievements from MDC file content"""
        achievements = []
        service_name = Path(file_path).stem
        
        # Extract version info
        version_match = re.search(r'Version: (\d+\.\d+\.\d+)', content)
        version = version_match.group(1) if version_match else "1.0.0"
        
        # Detect completed implementations
        for pattern in self.achievement_patterns['completed']:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                achievements.append({
                    'service_name': service_name,
                    'achievement_type': 'implementation',
                    'title': f"{service_name} - Implementation Complete",
                    'description': f"Service implementation completed with status: {match}",
                    'impact_level': 'high',
                    'file_path': file_path,
                    'version': version,
                    'metrics': str(match)
                })
        
        # Extract performance metrics
        for pattern in self.achievement_patterns['performance']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                metric_value = match if isinstance(match, str) else str(match)
                achievements.append({
                    'service_name': service_name,
                    'achievement_type': 'performance',
                    'title': f"{service_name} - Performance Improvement",
                    'description': f"Performance metric achieved: {metric_value}",
                    'impact_level': 'medium',
                    'file_path': file_path,
                    'version': version,
                    'metrics': metric_value
                })
        
        # Extract feature implementations
        for pattern in self.achievement_patterns['features']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                feature_name = match[0] if isinstance(match, tuple) else str(match)
                feature_desc = match[1] if isinstance(match, tuple) and len(match) > 1 else ""
                achievements.append({
                    'service_name': service_name,
                    'achievement_type': 'feature',
                    'title': f"{service_name} - {feature_name}",
                    'description': feature_desc or f"Feature implemented: {feature_name}",
                    'impact_level': 'medium',
                    'file_path': file_path,
                    'version': version,
                    'metrics': feature_name
                })
        
        # Check for version upgrades (versions > 1.0.0 indicate achievements)
        if version and version != "1.0.0":
            achievements.append({
                'service_name': service_name,
                'achievement_type': 'version_upgrade',
                'title': f"{service_name} - Version Upgrade",
                'description': f"Service upgraded to version {version}",
                'impact_level': 'medium',
                'file_path': file_path,
                'version': version,
                'metrics': version
            })
        
        return achievements
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        metrics = {}
        
        try:
            # Count MDC files
            mdc_count = len(list(self.cursor_rules_dir.glob("**/*.mdc")))
            metrics['total_mdc_files'] = mdc_count
            
            # Count services with versions > 1.0.0
            enhanced_services = 0
            for mdc_file in self.cursor_rules_dir.glob("**/*.mdc"):
                try:
                    with open(mdc_file, 'r') as f:
                        content = f.read()
                    version_match = re.search(r'Version: (\d+)\.(\d+)\.(\d+)', content)
                    if version_match:
                        major, minor, patch = map(int, version_match.groups())
                        if major > 1 or minor > 0 or patch > 0:
                            enhanced_services += 1
                except:
                    continue
            
            metrics['enhanced_services'] = enhanced_services
            
            # Count production services
            production_services = 0
            for mdc_file in self.cursor_rules_dir.glob("**/*.mdc"):
                try:
                    with open(mdc_file, 'r') as f:
                        content = f.read()
                    if re.search(r'PRODUCTION|ACTIVE|COMPLETED', content, re.IGNORECASE):
                        production_services += 1
                except:
                    continue
            
            metrics['production_services'] = production_services
            
            # Get database metrics if available
            try:
                with sqlite3.connect(str(self.achievements_db)) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM achievements WHERE date = ?", 
                                        (datetime.now().date(),))
                    metrics['todays_achievements'] = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(DISTINCT service_name) FROM achievements")
                    metrics['services_with_achievements'] = cursor.fetchone()[0]
            except:
                metrics['todays_achievements'] = 0
                metrics['services_with_achievements'] = 0
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
        
        return metrics
    
    def store_achievements(self, achievements: List[Dict[str, Any]]) -> int:
        """Store achievements in database, avoiding duplicates"""
        stored_count = 0
        today = datetime.now().date()
        
        try:
            with sqlite3.connect(str(self.achievements_db)) as conn:
                for achievement in achievements:
                    # Check if similar achievement exists for today
                    cursor = conn.execute('''
                        SELECT COUNT(*) FROM achievements 
                        WHERE date = ? AND service_name = ? AND achievement_type = ? 
                        AND title = ?
                    ''', (
                        today,
                        achievement['service_name'],
                        achievement['achievement_type'],
                        achievement['title']
                    ))
                    
                    if cursor.fetchone()[0] == 0:  # Not exists, insert
                        conn.execute('''
                            INSERT INTO achievements (
                                date, service_name, achievement_type, title, 
                                description, impact_level, metrics, file_path, version
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            today,
                            achievement['service_name'],
                            achievement['achievement_type'],
                            achievement['title'],
                            achievement.get('description', ''),
                            achievement.get('impact_level', 'medium'),
                            achievement.get('metrics', ''),
                            achievement.get('file_path', ''),
                            achievement.get('version', '1.0.0')
                        ))
                        stored_count += 1
                
                conn.commit()
                self.logger.info(f"Stored {stored_count} new achievements")
        
        except Exception as e:
            self.logger.error(f"Error storing achievements: {e}")
        
        return stored_count
    
    def get_recent_achievements(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get achievements from the last N days"""
        achievements = []
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        try:
            with sqlite3.connect(str(self.achievements_db)) as conn:
                cursor = conn.execute('''
                    SELECT date, service_name, achievement_type, title, description, 
                           impact_level, metrics, version 
                    FROM achievements 
                    WHERE date >= ? 
                    ORDER BY date DESC, impact_level DESC
                ''', (cutoff_date,))
                
                for row in cursor.fetchall():
                    achievements.append({
                        'date': row[0],
                        'service_name': row[1],
                        'achievement_type': row[2],
                        'title': row[3],
                        'description': row[4],
                        'impact_level': row[5],
                        'metrics': row[6],
                        'version': row[7]
                    })
        
        except Exception as e:
            self.logger.error(f"Error getting recent achievements: {e}")
        
        return achievements
    
    def update_achievements_mdc(self):
        """Update the achievements.mdc file with latest discoveries"""
        try:
            # Get recent achievements
            recent_achievements = self.get_recent_achievements(days=30)
            system_metrics = self.get_system_metrics()
            
            # Group achievements by type and service
            grouped_achievements = {}
            for achievement in recent_achievements:
                service = achievement['service_name']
                if service not in grouped_achievements:
                    grouped_achievements[service] = []
                grouped_achievements[service].append(achievement)
            
            # Generate updated content
            updated_content = self.generate_achievements_mdc_content(
                grouped_achievements, system_metrics
            )
            
            # Write to file
            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.logger.info("Updated achievements.mdc file")
            
        except Exception as e:
            self.logger.error(f"Error updating achievements.mdc: {e}")
    
    def generate_achievements_mdc_content(self, grouped_achievements: Dict, metrics: Dict) -> str:
        """Generate the updated achievements MDC content"""
        content = f"""# achievements.mdc
> Type: system | Version: 1.1.0 | Owner: zmartbot | Port: None | Status: ACTIVE

## Purpose
Comprehensive ZmartBot System Achievements Tracker - Automated daily scanning and documentation of system accomplishments, implementations, and milestones across the entire ZmartBot ecosystem.

## Overview
The Achievements Service provides automated daily scanning and documentation of system improvements, new implementations, performance enhancements, and completed features across all {metrics.get('total_mdc_files', 211)}+ MDC files. This service maintains a complete historical record of system evolution and success metrics.

## 📊 CURRENT SYSTEM METRICS (As of {datetime.now().strftime('%Y-%m-%d')})

### System Overview:
- **Total MDC Files**: {metrics.get('total_mdc_files', 211)}
- **Enhanced Services**: {metrics.get('enhanced_services', 0)} (Version > 1.0.0)
- **Production Services**: {metrics.get('production_services', 0)}
- **Services with Achievements**: {metrics.get('services_with_achievements', 0)}
- **Today's New Achievements**: {metrics.get('todays_achievements', 0)}

## 🏆 RECENT ACHIEVEMENTS (Last 30 Days)

"""
        
        # Add grouped achievements
        for service_name, achievements in sorted(grouped_achievements.items()):
            if achievements:  # Only add if there are achievements
                content += f"### 🎯 {service_name.replace('_', ' ').title()}\n\n"
                
                # Group by achievement type
                by_type = {}
                for achievement in achievements:
                    achievement_type = achievement['achievement_type']
                    if achievement_type not in by_type:
                        by_type[achievement_type] = []
                    by_type[achievement_type].append(achievement)
                
                for achievement_type, type_achievements in by_type.items():
                    content += f"#### {achievement_type.replace('_', ' ').title()} Achievements:\n"
                    for achievement in type_achievements[:3]:  # Limit to 3 per type
                        impact_icon = "🔥" if achievement['impact_level'] == 'high' else "⚡" if achievement['impact_level'] == 'medium' else "✅"
                        content += f"- {impact_icon} **{achievement['title']}**\n"
                        if achievement['description']:
                            content += f"  - {achievement['description']}\n"
                        if achievement['metrics']:
                            content += f"  - Metrics: {achievement['metrics']}\n"
                        if achievement['version'] and achievement['version'] != '1.0.0':
                            content += f"  - Version: {achievement['version']}\n"
                        content += f"  - Date: {achievement['date']}\n"
                    content += "\n"
                
                content += "---\n\n"
        
        # Add footer
        content += f"""
## 🔄 AUTOMATED DAILY SCANNING

### Service Features:
- **Daily Scanning**: Automated detection of new implementations and achievements
- **Pattern Recognition**: Advanced pattern matching for achievement detection  
- **Database Storage**: Persistent storage of all achievements with deduplication
- **MDC Integration**: Automatic updates to achievements.mdc file
- **Metrics Tracking**: System-wide performance and implementation metrics

### Achievement Categories Tracked:
- **Implementation**: Completed service implementations and deployments
- **Performance**: System performance improvements and optimizations
- **Feature**: New feature implementations and capabilities
- **Version Upgrade**: Service version updates and enhancements
- **Security**: Security implementations and compliance achievements
- **Integration**: Service integrations and connectivity achievements

### Next Scan: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')} at 00:00 UTC

---

**Generated**: {datetime.now().isoformat()}
**Service Status**: ACTIVE - Daily Automated Scanning
**Database**: {metrics.get('services_with_achievements', 0)} services tracked
**Last Update**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

---
description: Automated ZmartBot system achievements tracker with daily scanning
globs: ["**/*.mdc", "**/*.py", "**/*.js"]
alwaysApply: true
updated: "{datetime.now().strftime('%Y-%m-%d')}"
"""
        
        return content
    
    def run_daily_scan(self) -> Dict[str, Any]:
        """Run the daily achievements scan"""
        start_time = time.time()
        results = {
            'scan_date': datetime.now().date().isoformat(),
            'scan_time': datetime.now().isoformat(),
            'achievements_found': 0,
            'new_achievements_stored': 0,
            'files_processed': 0,
            'errors': [],
            'duration_seconds': 0
        }
        
        try:
            self.logger.info("Starting daily achievements scan")
            
            # Scan for achievements
            achievements = self.scan_mdc_files()
            results['achievements_found'] = len(achievements)
            results['files_processed'] = len(list(self.cursor_rules_dir.glob("**/*.mdc")))
            
            # Store new achievements
            stored_count = self.store_achievements(achievements)
            results['new_achievements_stored'] = stored_count
            
            # Update achievements MDC file
            self.update_achievements_mdc()
            
            results['duration_seconds'] = round(time.time() - start_time, 2)
            
            self.logger.info(
                f"Daily scan completed: {results['achievements_found']} achievements found, "
                f"{results['new_achievements_stored']} new achievements stored"
            )
            
        except Exception as e:
            error_msg = f"Error in daily scan: {e}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def get_achievement_summary(self) -> Dict[str, Any]:
        """Get a summary of all achievements"""
        try:
            with sqlite3.connect(str(self.achievements_db)) as conn:
                # Total achievements
                cursor = conn.execute("SELECT COUNT(*) FROM achievements")
                total_achievements = cursor.fetchone()[0]
                
                # Achievements by type
                cursor = conn.execute("""
                    SELECT achievement_type, COUNT(*) 
                    FROM achievements 
                    GROUP BY achievement_type 
                    ORDER BY COUNT(*) DESC
                """)
                by_type = dict(cursor.fetchall())
                
                # Achievements by impact level
                cursor = conn.execute("""
                    SELECT impact_level, COUNT(*) 
                    FROM achievements 
                    GROUP BY impact_level 
                    ORDER BY COUNT(*) DESC
                """)
                by_impact = dict(cursor.fetchall())
                
                # Recent activity (last 7 days)
                cutoff = (datetime.now() - timedelta(days=7)).date()
                cursor = conn.execute("""
                    SELECT COUNT(*) 
                    FROM achievements 
                    WHERE date >= ?
                """, (cutoff,))
                recent_activity = cursor.fetchone()[0]
                
                return {
                    'total_achievements': total_achievements,
                    'by_type': by_type,
                    'by_impact': by_impact,
                    'recent_activity': recent_activity,
                    'system_metrics': self.get_system_metrics()
                }
        
        except Exception as e:
            self.logger.error(f"Error getting achievement summary: {e}")
            return {}

def main():
    """Main entry point for Achievements Service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Achievements Service")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--scan", action="store_true", help="Run daily achievements scan")
    parser.add_argument("--summary", action="store_true", help="Show achievements summary")
    parser.add_argument("--recent", type=int, default=7, help="Show recent achievements (days)")
    parser.add_argument("--update-mdc", action="store_true", help="Update achievements.mdc file")
    
    args = parser.parse_args()
    
    service = AchievementsService(args.project_root)
    
    if args.scan:
        results = service.run_daily_scan()
        print(json.dumps(results, indent=2))
    
    elif args.summary:
        summary = service.get_achievement_summary()
        print(json.dumps(summary, indent=2))
    
    elif args.recent:
        achievements = service.get_recent_achievements(args.recent)
        for achievement in achievements:
            print(f"[{achievement['date']}] {achievement['title']}")
            if achievement['description']:
                print(f"  Description: {achievement['description']}")
            if achievement['metrics']:
                print(f"  Metrics: {achievement['metrics']}")
            print()
    
    elif args.update_mdc:
        service.update_achievements_mdc()
        print("achievements.mdc file updated")
    
    else:
        print("Use --help for available commands")

if __name__ == "__main__":
    main()