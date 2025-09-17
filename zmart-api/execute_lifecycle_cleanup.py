#!/usr/bin/env python3
"""
Direct execution of ServiceLifecycleManager cleanup without interactive prompt
"""

import sys
from pathlib import Path

# Add database directory to path
sys.path.append(str(Path(__file__).parent / "database"))

from service_lifecycle_manager import ServiceLifecycleManager
import logging

def main():
    """Execute lifecycle cleanup directly"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🧹 Starting ServiceLifecycleManager cleanup...")
    
    # Initialize the lifecycle manager
    manager = ServiceLifecycleManager()
    
    # Get current violations
    duplicates = manager.find_duplicate_services()
    
    if not duplicates:
        logger.info("✅ No violations found - system is clean!")
        return True
    
    logger.info(f"🔧 Found {sum(len(v) for v in duplicates.values())} violations to clean:")
    for violation_type, services in duplicates.items():
        logger.info(f"  {violation_type}: {len(services)} services")
    
    # Execute cleanup
    logger.info("⚙️ Executing cleanup...")
    cleanup_results = manager.cleanup_promoted_services(dry_run=False)
    
    # Report results
    logger.info("📊 Cleanup Results:")
    logger.info(f"  Removed from discovery: {cleanup_results['removed_from_discovery']}")
    logger.info(f"  Removed from passport: {cleanup_results['removed_from_passport']}")
    
    if cleanup_results['errors']:
        logger.error(f"  Errors: {len(cleanup_results['errors'])}")
        for error in cleanup_results['errors']:
            logger.error(f"    - {error}")
        return False
    else:
        logger.info("  ✅ No errors!")
    
    # Validate cleanup
    logger.info("🔍 Validating cleanup results...")
    validation_report = manager.validate_system_integrity()
    
    if validation_report['integrity_status'] == 'CLEAN':
        logger.info("🎉 SUCCESS: System is now clean!")
        logger.info(f"Final unique service counts:")
        logger.info(f"  Discovery: {validation_report['unique_counts']['discovery']}")
        logger.info(f"  Passport: {validation_report['unique_counts']['passport']}")  
        logger.info(f"  Certificate: {validation_report['unique_counts']['certificate']}")
        logger.info(f"  Total unique: {validation_report['unique_counts']['total_unique']}")
        return True
    else:
        logger.warning("⚠️ Some violations remain:")
        remaining_duplicates = validation_report.get('duplicates', {})
        for violation_type, services in remaining_duplicates.items():
            logger.warning(f"  {violation_type}: {services}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)