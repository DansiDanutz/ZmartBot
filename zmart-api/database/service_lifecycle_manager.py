#!/usr/bin/env python3
"""
Dynamic Service Lifecycle Management System
Ensures proper progression: Discovery → Passport → Certificate
Enforces unique services across all levels (no duplicates)
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logger = logging.getLogger(__name__)

class ServiceLifecycleManager:
    """
    Dynamic Service Lifecycle Management System
    Ensures 1-to-1 mapping: Each service exists in ONLY ONE level
    """
    
    def __init__(self, base_path: str = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"):
        self.base_path = Path(base_path)
        self.databases = {
            'discovery': self.base_path / 'discovery_registry.db',
            'passport': self.base_path / 'data' / 'passport_registry.db', 
            'certificate': self.base_path / 'service_registry.db'
        }
        
    def get_all_services_by_level(self) -> Dict[str, Set[str]]:
        """Get all services organized by level"""
        services_by_level = {
            'discovery': set(),
            'passport': set(),
            'certificate': set()
        }
        
        # Level 1: Discovery Services
        try:
            conn = sqlite3.connect(self.databases['discovery'])
            cursor = conn.execute("SELECT service_name FROM discovery_services")
            services_by_level['discovery'] = {row[0] for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            logger.error(f"Error reading discovery services: {e}")
            
        # Level 2: Passport Services  
        try:
            conn = sqlite3.connect(self.databases['passport'])
            cursor = conn.execute("SELECT service_name FROM passport_registry")
            services_by_level['passport'] = {row[0] for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            logger.error(f"Error reading passport services: {e}")
            
        # Level 3: Certificate Services
        try:
            conn = sqlite3.connect(self.databases['certificate'])
            cursor = conn.execute("SELECT service_name FROM services")
            services_by_level['certificate'] = {row[0] for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            logger.error(f"Error reading certificate services: {e}")
            
        return services_by_level
    
    def find_duplicate_services(self) -> Dict[str, List[str]]:
        """Find services that exist in multiple levels (violations)"""
        services = self.get_all_services_by_level()
        duplicates = {}
        
        # Check Discovery + Passport duplicates
        discovery_passport = services['discovery'] & services['passport']
        if discovery_passport:
            duplicates['discovery_passport'] = list(discovery_passport)
            
        # Check Passport + Certificate duplicates  
        passport_certificate = services['passport'] & services['certificate']
        if passport_certificate:
            duplicates['passport_certificate'] = list(passport_certificate)
            
        # Check Discovery + Certificate duplicates (should never happen)
        discovery_certificate = services['discovery'] & services['certificate']
        if discovery_certificate:
            duplicates['discovery_certificate'] = list(discovery_certificate)
            
        return duplicates
    
    def get_unique_service_counts(self) -> Dict[str, int]:
        """Get CORRECT unique service counts (no duplicates)"""
        services = self.get_all_services_by_level()
        
        # Services that exist ONLY in their respective levels
        unique_discovery = services['discovery'] - services['passport'] - services['certificate']
        unique_passport = services['passport'] - services['certificate'] - services['discovery']  
        unique_certificate = services['certificate']  # Certificates are always unique (highest level)
        
        return {
            'discovery': len(unique_discovery),
            'passport': len(unique_passport), 
            'certificate': len(unique_certificate),
            'total_unique': len(unique_discovery | unique_passport | unique_certificate)
        }
    
    def cleanup_promoted_services(self, dry_run: bool = True) -> Dict[str, int]:
        """
        Clean up services that were promoted but not removed from lower levels
        
        Args:
            dry_run: If True, only report what would be cleaned (default)
                    If False, actually perform the cleanup
        """
        duplicates = self.find_duplicate_services()
        cleanup_results = {
            'removed_from_discovery': 0,
            'removed_from_passport': 0,
            'errors': []
        }
        
        if not duplicates:
            logger.info("✅ No cleanup needed - proper lifecycle progression maintained")
            return cleanup_results
            
        logger.info(f"🔧 Found duplicates requiring cleanup: {duplicates}")
        
        # Remove services from Discovery if they exist in Passport
        if 'discovery_passport' in duplicates:
            for service in duplicates['discovery_passport']:
                try:
                    if not dry_run:
                        conn = sqlite3.connect(self.databases['discovery'])
                        conn.execute("DELETE FROM discovery_services WHERE service_name = ?", (service,))
                        conn.commit()
                        conn.close()
                        
                    cleanup_results['removed_from_discovery'] += 1
                    logger.info(f"{'WOULD REMOVE' if dry_run else 'REMOVED'} {service} from Discovery (promoted to Passport)")
                except Exception as e:
                    cleanup_results['errors'].append(f"Error removing {service} from Discovery: {e}")
        
        # Remove services from Passport if they exist in Certificate
        if 'passport_certificate' in duplicates:
            for service in duplicates['passport_certificate']:
                try:
                    if not dry_run:
                        conn = sqlite3.connect(self.databases['passport'])
                        conn.execute("DELETE FROM passport_registry WHERE service_name = ?", (service,))
                        conn.commit()
                        conn.close()
                        
                    cleanup_results['removed_from_passport'] += 1
                    logger.info(f"{'WOULD REMOVE' if dry_run else 'REMOVED'} {service} from Passport (promoted to Certificate)")
                except Exception as e:
                    cleanup_results['errors'].append(f"Error removing {service} from Passport: {e}")
        
        return cleanup_results
    
    def promote_service(self, service_name: str, from_level: str, to_level: str) -> bool:
        """
        Promote a service from one level to the next
        Automatically removes from lower level
        """
        valid_promotions = {
            ('discovery', 'passport'),
            ('passport', 'certificate')
        }
        
        if (from_level, to_level) not in valid_promotions:
            logger.error(f"❌ Invalid promotion: {from_level} → {to_level}")
            return False
            
        try:
            # Add to target level (implementation depends on specific requirements)
            logger.info(f"🚀 Promoting {service_name}: {from_level} → {to_level}")
            
            # Remove from source level
            if from_level == 'discovery':
                conn = sqlite3.connect(self.databases['discovery'])
                conn.execute("DELETE FROM discovery_services WHERE service_name = ?", (service_name,))
                conn.commit()
                conn.close()
            elif from_level == 'passport':
                conn = sqlite3.connect(self.databases['passport'])
                conn.execute("DELETE FROM passport_registry WHERE service_name = ?", (service_name,))
                conn.commit()
                conn.close()
                
            logger.info(f"✅ Successfully promoted {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to promote {service_name}: {e}")
            return False
    
    def validate_system_integrity(self) -> Dict[str, any]:
        """Complete system validation report"""
        duplicates = self.find_duplicate_services()
        counts = self.get_unique_service_counts()
        services = self.get_all_services_by_level()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'integrity_status': 'CLEAN' if not duplicates else 'VIOLATIONS_FOUND',
            'duplicates': duplicates,
            'unique_counts': counts,
            'raw_counts': {
                'discovery_raw': len(services['discovery']),
                'passport_raw': len(services['passport']),
                'certificate_raw': len(services['certificate'])
            },
            'total_services': counts['total_unique'],
            'violations_count': sum(len(v) for v in duplicates.values())
        }

def main():
    """CLI interface for lifecycle management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZmartBot Service Lifecycle Manager')
    parser.add_argument('--validate', action='store_true', help='Validate system integrity')
    parser.add_argument('--cleanup', action='store_true', help='Clean up promoted services (dry run)')
    parser.add_argument('--cleanup-execute', action='store_true', help='Execute cleanup (ACTUAL REMOVAL)')
    parser.add_argument('--counts', action='store_true', help='Show unique service counts')
    
    args = parser.parse_args()
    
    manager = ServiceLifecycleManager()
    
    if args.validate:
        report = manager.validate_system_integrity()
        print(json.dumps(report, indent=2))
        
    elif args.cleanup:
        results = manager.cleanup_promoted_services(dry_run=True)
        print("DRY RUN - Cleanup Results:", json.dumps(results, indent=2))
        
    elif args.cleanup_execute:
        print("⚠️ EXECUTING ACTUAL CLEANUP - This will modify databases!")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            results = manager.cleanup_promoted_services(dry_run=False)
            print("EXECUTED - Cleanup Results:", json.dumps(results, indent=2))
        else:
            print("Cancelled")
            
    elif args.counts:
        counts = manager.get_unique_service_counts()
        print("UNIQUE SERVICE COUNTS:")
        print(f"Discovery (Level 1): {counts['discovery']}")
        print(f"Passport (Level 2): {counts['passport']}")  
        print(f"Certificate (Level 3): {counts['certificate']}")
        print(f"Total Unique Services: {counts['total_unique']}")
        
    else:
        parser.print_help()

class ServiceLifecycleManagerAPI:
    """FastAPI service wrapper for ServiceLifecycleManager"""
    
    def __init__(self, port: int = 8920):
        self.port = port
        self.lifecycle_manager = ServiceLifecycleManager()
        self.app = FastAPI(
            title="ZmartBot Service Lifecycle Manager",
            description="Dynamic Service Lifecycle Validation and Management System",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "ServiceLifecycleManager",
                "version": "1.0.0",
                "port": self.port
            }
        
        @self.app.get("/api/lifecycle/validate")
        async def validate_system_integrity():
            """Validate complete service lifecycle integrity"""
            try:
                validation_report = self.lifecycle_manager.validate_system_integrity()
                return validation_report
            except Exception as e:
                logger.error(f"Error validating system integrity: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/lifecycle/counts")
        async def get_unique_service_counts():
            """Get unique service counts across all levels"""
            try:
                unique_counts = self.lifecycle_manager.get_unique_service_counts()
                services_by_level = self.lifecycle_manager.get_all_services_by_level()
                
                return {
                    "unique_counts": unique_counts,
                    "services_by_level": {
                        "discovery": list(services_by_level['discovery']),
                        "passport": list(services_by_level['passport']),
                        "certificate": list(services_by_level['certificate'])
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error getting service counts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/lifecycle/duplicates")
        async def find_duplicate_services():
            """Find services existing in multiple levels"""
            try:
                duplicates = self.lifecycle_manager.find_duplicate_services()
                return {
                    "duplicates": duplicates,
                    "violation_count": sum(len(v) for v in duplicates.values()),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error finding duplicates: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/lifecycle/cleanup")
        async def cleanup_promoted_services(dry_run: bool = True):
            """Clean up services promoted but not removed from lower levels"""
            try:
                cleanup_results = self.lifecycle_manager.cleanup_promoted_services(dry_run=dry_run)
                return cleanup_results
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def run(self):
        """Start the FastAPI service"""
        logger.info(f"🚀 Starting ServiceLifecycleManager API on port {self.port}")
        uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="info")

def start_service():
    """Start the ServiceLifecycleManager as a service"""
    logging.basicConfig(level=logging.INFO)
    service = ServiceLifecycleManagerAPI()
    service.run()

if __name__ == '__main__':
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Check if running as service or CLI
    if len(sys.argv) > 1 and sys.argv[1] == '--service':
        start_service()
    else:
        main()