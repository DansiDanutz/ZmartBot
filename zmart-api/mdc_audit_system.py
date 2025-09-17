#!/usr/bin/env python3
"""
MDC Audit System - Comprehensive ZmartBot MDC File Analysis and Enhancement
Conducts full system audit and identifies missing Description, Triggers, and Requirements
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDCAuditSystem:
    def __init__(self, base_path: str = "/Users/dansidanutz/Desktop/ZmartBot"):
        self.base_path = Path(base_path)
        self.mdc_path = self.base_path / ".cursor" / "rules"
        self.audit_results = {}
        self.missing_sections = {}
        self.enhancement_queue = []
        
    def scan_all_mdc_files(self) -> Dict[str, Dict]:
        """Scan all MDC files in the system"""
        logger.info("🔍 Starting comprehensive MDC file scan...")
        
        if not self.mdc_path.exists():
            logger.error(f"MDC path not found: {self.mdc_path}")
            return {}
            
        mdc_files = list(self.mdc_path.glob("*.mdc"))
        logger.info(f"Found {len(mdc_files)} MDC files to audit")
        
        for mdc_file in mdc_files:
            try:
                with open(mdc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                analysis = self.analyze_mdc_file(mdc_file.name, content)
                self.audit_results[mdc_file.name] = analysis
                
                # Check for missing sections
                missing = self.check_missing_sections(content)
                if missing:
                    self.missing_sections[mdc_file.name] = missing
                    self.enhancement_queue.append({
                        'file': mdc_file.name,
                        'path': str(mdc_file),
                        'missing': missing,
                        'content': content
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {mdc_file.name}: {e}")
                
        return self.audit_results
    
    def analyze_mdc_file(self, filename: str, content: str) -> Dict:
        """Analyze individual MDC file for structure and completeness"""
        analysis = {
            'filename': filename,
            'size': len(content),
            'lines': len(content.split('\n')),
            'sections': {},
            'metadata': {},
            'quality_score': 0
        }
        
        # Extract metadata from header
        header_match = re.search(r'>\s*Type:\s*(\w+).*?Version:\s*([\d.]+).*?Owner:\s*(\w+)', content, re.DOTALL)
        if header_match:
            analysis['metadata'] = {
                'type': header_match.group(1),
                'version': header_match.group(2),
                'owner': header_match.group(3)
            }
            analysis['quality_score'] += 10
        
        # Check for standard sections
        sections_to_check = [
            'Purpose', 'Overview', 'Critical Functions', 'Architecture & Integration',
            'API Endpoints', 'Health & Readiness', 'Description', 'Triggers', 'Requirements'
        ]
        
        for section in sections_to_check:
            if re.search(rf'^#{1,3}\s*{section}', content, re.MULTILINE | re.IGNORECASE):
                analysis['sections'][section] = True
                analysis['quality_score'] += 5
            else:
                analysis['sections'][section] = False
        
        # Special scoring for critical sections
        if analysis['sections'].get('Description', False):
            analysis['quality_score'] += 10
        if analysis['sections'].get('Triggers', False):
            analysis['quality_score'] += 10
        if analysis['sections'].get('Requirements', False):
            analysis['quality_score'] += 10
            
        return analysis
    
    def check_missing_sections(self, content: str) -> List[str]:
        """Check for missing Description, Triggers, and Requirements sections"""
        missing = []
        
        required_sections = ['Description', 'Triggers', 'Requirements']
        
        for section in required_sections:
            # Look for various patterns of these sections
            patterns = [
                rf'^#{1,3}\s*{section}',
                rf'^#{1,3}\s*Service\s+{section}',
                rf'^#{1,3}\s*{section}\s+short',
                rf'^\*\*{section}\*\*:',
                rf'## {section}',
                rf'### {section}'
            ]
            
            found = False
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    found = True
                    break
                    
            if not found:
                missing.append(section)
        
        return missing
    
    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report"""
        total_files = len(self.audit_results)
        files_missing_sections = len(self.missing_sections)
        
        report = f"""
# 🔍 COMPREHENSIVE MDC AUDIT REPORT
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 AUDIT SUMMARY
- **Total MDC Files**: {total_files}
- **Files Missing Required Sections**: {files_missing_sections}
- **Enhancement Queue**: {len(self.enhancement_queue)} files need updates

## 🚨 MISSING SECTIONS ANALYSIS

"""
        
        # Missing sections breakdown
        missing_description = sum(1 for missing in self.missing_sections.values() if 'Description' in missing)
        missing_triggers = sum(1 for missing in self.missing_sections.values() if 'Triggers' in missing)
        missing_requirements = sum(1 for missing in self.missing_sections.values() if 'Requirements' in missing)
        
        report += f"""
### Missing Sections Count:
- **Description**: {missing_description} files missing
- **Triggers**: {missing_triggers} files missing  
- **Requirements**: {missing_requirements} files missing

### Files Requiring Enhancement:
"""
        
        for filename, missing in self.missing_sections.items():
            report += f"- **{filename}**: Missing {', '.join(missing)}\n"
        
        # Quality scores
        report += f"""

## 📈 QUALITY ANALYSIS

### Quality Score Distribution:
"""
        
        quality_scores = [result['quality_score'] for result in self.audit_results.values()]
        if quality_scores:
            avg_score = sum(quality_scores) / len(quality_scores)
            max_score = max(quality_scores)
            min_score = min(quality_scores)
            
            report += f"""
- **Average Quality Score**: {avg_score:.1f}/100
- **Highest Quality Score**: {max_score}/100
- **Lowest Quality Score**: {min_score}/100
"""
        
        # Service type breakdown
        service_types = {}
        for result in self.audit_results.values():
            service_type = result.get('metadata', {}).get('type', 'unknown')
            service_types[service_type] = service_types.get(service_type, 0) + 1
        
        report += f"""
### Service Type Distribution:
"""
        for service_type, count in sorted(service_types.items()):
            report += f"- **{service_type}**: {count} services\n"
        
        return report
    
    def save_audit_results(self):
        """Save audit results to files"""
        # Save JSON results
        results_file = self.base_path / "mdc_audit_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'audit_results': self.audit_results,
                'missing_sections': self.missing_sections,
                'enhancement_queue': len(self.enhancement_queue),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        # Save audit report
        report_file = self.base_path / "MDC_AUDIT_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(self.generate_audit_report())
        
        logger.info(f"✅ Audit results saved to {results_file}")
        logger.info(f"✅ Audit report saved to {report_file}")

class MDCEnhancementService:
    """Service to enhance MDC files with missing sections"""
    
    def __init__(self, audit_system: MDCAuditSystem):
        self.audit_system = audit_system
        
    def generate_description(self, filename: str, content: str) -> str:
        """Generate Description section based on file analysis"""
        # Extract service name from filename
        service_name = filename.replace('.mdc', '').replace('_', ' ').replace('-', ' ')
        
        # Try to extract purpose from existing content
        purpose_match = re.search(r'## Purpose\s*\n(.*?)(?=\n##|\n\n|$)', content, re.DOTALL | re.IGNORECASE)
        if purpose_match:
            purpose = purpose_match.group(1).strip()
            # Create concise description from purpose
            description = purpose.split('.')[0] + '.'
            if len(description) > 100:
                description = description[:97] + '...'
        else:
            # Generate generic description
            service_type = 'service'
            if 'backend' in filename.lower():
                service_type = 'backend service'
            elif 'agent' in filename.lower():
                service_type = 'agent'
            elif 'orchestration' in filename.lower():
                service_type = 'orchestration service'
            
            description = f"Core {service_type} component of the ZmartBot ecosystem providing essential functionality."
        
        return f"""
## Description
{description}
"""
    
    def generate_triggers(self, filename: str, content: str) -> str:
        """Generate Triggers section based on file analysis"""
        triggers = []
        
        # Analyze content for trigger patterns
        if 'API' in content or 'endpoint' in content.lower():
            triggers.append("API endpoint requests")
        if 'schedule' in content.lower() or 'cron' in content.lower():
            triggers.append("Scheduled execution")
        if 'file' in content.lower() and 'watch' in content.lower():
            triggers.append("File system changes")
        if 'database' in content.lower():
            triggers.append("Database events")
        if 'workflow' in content.lower():
            triggers.append("Workflow transitions")
        if 'health' in content.lower():
            triggers.append("Health check requests")
        
        # Default triggers if none detected
        if not triggers:
            if 'agent' in filename.lower():
                triggers = ["System events", "Automated processes", "External API calls"]
            elif 'service' in filename.lower():
                triggers = ["Service requests", "API calls", "System startup"]
            else:
                triggers = ["System initialization", "External requests", "Scheduled tasks"]
        
        triggers_text = '\n'.join([f"- **{trigger}**" for trigger in triggers[:3]])  # Limit to 3
        
        return f"""
## Triggers
{triggers_text}
"""
    
    def generate_requirements(self, filename: str, content: str) -> str:
        """Generate Requirements section based on file analysis"""
        requirements = []
        
        # Extract requirements from content analysis
        if 'port' in content.lower():
            requirements.append("Unique port assignment")
        if 'database' in content.lower():
            requirements.append("Database connectivity")
        if 'passport' in content.lower():
            requirements.append("Valid service passport")
        if 'mdc' in content.lower():
            requirements.append("Complete MDC documentation")
        if 'health' in content.lower():
            requirements.append("Health endpoint implementation")
        if 'orchestration' in content.lower():
            requirements.append("Master Orchestration integration")
        
        # Default requirements
        if not requirements:
            requirements = [
                "Service implementation complete",
                "Health monitoring configured",
                "Documentation updated"
            ]
        
        requirements_text = '\n'.join([f"- ✅ **{req}**" for req in requirements[:5]])  # Limit to 5
        
        return f"""
## Requirements
{requirements_text}
"""
    
    def enhance_mdc_file(self, file_info: Dict) -> bool:
        """Enhance single MDC file with missing sections"""
        try:
            content = file_info['content']
            missing = file_info['missing']
            filename = file_info['file']
            
            enhanced_content = content
            
            # Add missing sections
            if 'Description' in missing:
                description = self.generate_description(filename, content)
                # Insert after Purpose section or at beginning
                if '## Purpose' in content:
                    enhanced_content = re.sub(
                        r'(## Purpose.*?)(\n## [^#])',
                        r'\1' + description + r'\2',
                        enhanced_content,
                        flags=re.DOTALL
                    )
                else:
                    enhanced_content = description + '\n' + enhanced_content
            
            if 'Triggers' in missing:
                triggers = self.generate_triggers(filename, content)
                # Insert before Health & Readiness or at end
                if '## Health & Readiness' in enhanced_content:
                    enhanced_content = enhanced_content.replace('## Health & Readiness', triggers + '\n## Health & Readiness')
                else:
                    enhanced_content += '\n' + triggers
            
            if 'Requirements' in missing:
                requirements = self.generate_requirements(filename, content)
                # Insert before final sections or at end
                if '## Notes' in enhanced_content:
                    enhanced_content = enhanced_content.replace('## Notes', requirements + '\n## Notes')
                elif '---' in enhanced_content:
                    enhanced_content = enhanced_content.replace('---', requirements + '\n\n---')
                else:
                    enhanced_content += '\n' + requirements
            
            # Write enhanced content back to file
            with open(file_info['path'], 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            logger.info(f"✅ Enhanced {filename} - Added: {', '.join(missing)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enhance {file_info['file']}: {e}")
            return False

def main():
    """Main execution function"""
    logger.info("🚀 Starting ZmartBot MDC System Audit and Enhancement")
    
    # Initialize audit system
    audit_system = MDCAuditSystem()
    
    # Perform comprehensive scan
    logger.info("Phase 1: Comprehensive MDC File Scan")
    audit_results = audit_system.scan_all_mdc_files()
    
    # Save audit results
    audit_system.save_audit_results()
    
    # Initialize enhancement service
    enhancement_service = MDCEnhancementService(audit_system)
    
    # Enhance files with missing sections
    if audit_system.enhancement_queue:
        logger.info(f"Phase 2: Enhancing {len(audit_system.enhancement_queue)} files")
        
        enhanced_count = 0
        for file_info in audit_system.enhancement_queue:
            if enhancement_service.enhance_mdc_file(file_info):
                enhanced_count += 1
        
        logger.info(f"✅ Successfully enhanced {enhanced_count}/{len(audit_system.enhancement_queue)} files")
    else:
        logger.info("✅ All MDC files already have required sections!")
    
    # Generate final report
    print("\n" + "="*80)
    print("🎯 MDC AUDIT AND ENHANCEMENT COMPLETE")
    print("="*80)
    print(audit_system.generate_audit_report())
    
    return audit_results

if __name__ == "__main__":
    results = main()