#!/usr/bin/env python3
"""
Auto-Update Master Orchestration Agent MDC
Automatically updates MasterOrchestrationAgent.mdc with knowledge of all registered services
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path

class MasterOrchestrationUpdater:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.mdc_file = self.project_root.parent / ".cursor" / "rules" / "MasterOrchestrationAgent.mdc"
        self.service_registry_db = self.project_root / "src" / "data" / "service_registry.db"
        
    def get_all_services(self):
        """Get all registered services from the database"""
        try:
            conn = sqlite3.connect(self.service_registry_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, kind, port, status 
                FROM service_registry 
                ORDER BY service_name
            """)
            
            services = cursor.fetchall()
            conn.close()
            
            return services
        except Exception as e:
            print(f"Error getting services: {e}")
            return []
    
    def categorize_services(self, services):
        """Categorize services by type"""
        categories = {
            'backend': [],
            'frontend': [],
            'worker': [],
            'orchestration': [],
            'internal_api': [],
            'other': []
        }
        
        for service_name, kind, port, status in services:
            if kind in categories:
                categories[kind].append({
                    'name': service_name,
                    'port': port,
                    'status': status
                })
            else:
                categories['other'].append({
                    'name': service_name,
                    'port': port,
                    'status': status
                })
        
        return categories
    
    def generate_dependency_mapping(self, services):
        """Generate dependency mapping based on service types"""
        dependencies = []
        
        # Core orchestration dependencies
        orchestration_services = [s[0] for s in services if s[1] == 'orchestration']
        backend_services = [s[0] for s in services if s[1] == 'backend']
        frontend_services = [s[0] for s in services if s[1] == 'frontend']
        worker_services = [s[0] for s in services if s[1] == 'worker']
        
        # Orchestration manages all other services
        for service_type, service_list in [('backend', backend_services), 
                                          ('frontend', frontend_services), 
                                          ('worker', worker_services)]:
            if service_list:
                for service in service_list:
                    if service != 'master-orchestration-agent':
                        dependencies.append(f"master-orchestration-agent → {service}")
        
        return dependencies
    
    def update_mdc_file(self):
        """Update the MasterOrchestrationAgent.mdc file with current service knowledge"""
        if not self.mdc_file.exists():
            print(f"MDC file not found: {self.mdc_file}")
            return False
        
        # Read current MDC file
        with open(self.mdc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get current services
        services = self.get_all_services()
        if not services:
            print("No services found in registry")
            return False
        
        # Categorize services
        categories = self.categorize_services(services)
        
        # Generate dependency mapping
        dependencies = self.generate_dependency_mapping(services)
        
        # Create new service knowledge section
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        service_knowledge = f"""## Self-Learning Service Knowledge
**Updated: {timestamp}**

### Currently Registered Services:"""
        
        for i, (service_name, kind, port, status) in enumerate(services, 1):
            service_knowledge += f"""
{i}. **{service_name}** ({kind}) - Port {port} - Status: {status}"""
        
        service_knowledge += f"""

### Service Categories:"""
        
        for category, service_list in categories.items():
            if service_list:
                service_names = [s['name'] for s in service_list]
                service_knowledge += f"""
- **{category.title()} Services**: {', '.join(service_names)}"""
        
        service_knowledge += f"""

### Dependency Mapping:"""
        
        for dep in dependencies:
            service_knowledge += f"""
- {dep}"""
        
        # Update the MDC file content
        # Find the existing service knowledge section and replace it
        pattern = r'## Self-Learning Service Knowledge.*?(?=## Known Issues|## Status)'
        
        if re.search(pattern, content, re.DOTALL):
            # Replace existing section
            new_content = re.sub(pattern, service_knowledge, content, flags=re.DOTALL)
        else:
            # Insert before Known Issues section
            pattern = r'(## Known Issues)'
            new_content = re.sub(pattern, f'{service_knowledge}\n\n\\1', content)
        
        # Update changelog
        changelog_pattern = r'(## Changelog.*?)(\n---\n)'
        new_changelog_entry = f"""## Changelog
- 1.0.0 (2025-08-24): Initial orchestration service with service lifecycle management
- 1.0.1 (2025-08-24): Merged with MasterOrchestrationAgent, added self-learning service knowledge
- 1.0.2 ({datetime.now().strftime("%Y-%m-%d")}): Auto-updated service knowledge - {len(services)} services registered

---
*Generated by MDCAgent (gpt5) on {timestamp}; input sha256-auto-update-{len(services)}-services; context: service_registry.db, auto_update.py.*"""
        
        if re.search(changelog_pattern, new_content, re.DOTALL):
            new_content = re.sub(changelog_pattern, new_changelog_entry, new_content, flags=re.DOTALL)
        
        # Write updated content
        with open(self.mdc_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Master Orchestration Agent MDC updated with {len(services)} services")
        print(f"📅 Last updated: {timestamp}")
        return True

def main():
    updater = MasterOrchestrationUpdater()
    success = updater.update_mdc_file()
    
    if success:
        print("🎯 Master Orchestration Agent self-learning knowledge updated successfully!")
    else:
        print("❌ Failed to update Master Orchestration Agent")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
