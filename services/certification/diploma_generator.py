#!/usr/bin/env python3
"""
ZmartBot Certification Diploma Generator
Generates professional certification diplomas for certified services
"""

import os
import hashlib
import base64
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser
from typing import Dict, Any

class CertificationDiplomaGenerator:
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(os.path.dirname(__file__)) / 'diplomas'
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_diploma(self, service_data: Dict[str, Any]) -> str:
        """
        Generate a certification diploma for a service
        
        Args:
            service_data: Dictionary containing service certification information
            
        Returns:
            Path to the generated diploma HTML file
        """
        # Load template
        template_path = self.templates_dir / 'certification_diploma_template.html'
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Generate diploma data
        diploma_data = self._prepare_diploma_data(service_data)
        
        # Replace template variables
        diploma_html = self._replace_template_variables(template_content, diploma_data)
        
        # Save diploma
        diploma_filename = f"diploma_{diploma_data['service_name_safe']}_{diploma_data['certificate_id']}.html"
        diploma_path = self.output_dir / diploma_filename
        
        with open(diploma_path, 'w', encoding='utf-8') as f:
            f.write(diploma_html)
            
        return str(diploma_path)
    
    def _prepare_diploma_data(self, service_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare and validate diploma data"""
        current_time = datetime.now()
        
        # Default values
        defaults = {
            'service_name': service_data.get('service_name', 'Unknown Service'),
            'certificate_id': service_data.get('cert_id', self._generate_cert_id()),
            'service_port': str(service_data.get('port', 'N/A')),
            'certificate_type': service_data.get('certificate_type', 'Standard'),
            'security_level': service_data.get('security_level', 'Production'),
            'compliance_score': str(service_data.get('compliance_score', 95)),
            'issue_date': service_data.get('issue_date', current_time.strftime('%B %d, %Y')),
            'expiry_date': service_data.get('expiry_date', 
                                         (current_time + timedelta(days=365)).strftime('%B %d, %Y')),
            'certification_date': service_data.get('certification_date', 
                                                 current_time.strftime('%Y-%m-%d %H:%M:%S'))
        }
        
        # Generate security features
        security_data = f"{defaults['service_name']}-{defaults['certificate_id']}-{defaults['issue_date']}"
        security_hash = hashlib.sha256(security_data.encode()).hexdigest()[:16].upper()
        
        defaults.update({
            'security_hash': security_hash,
            'verification_url': f"https://zmartbot.verify/{defaults['certificate_id']}",
            'service_name_safe': defaults['service_name'].replace(' ', '_').replace('-', '_').lower()
        })
        
        return defaults
    
    def _generate_cert_id(self) -> str:
        """Generate a unique certificate ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = base64.urlsafe_b64encode(os.urandom(6)).decode().rstrip('=')
        return f"CERT-{timestamp}-{random_part}"
    
    def _replace_template_variables(self, template: str, data: Dict[str, str]) -> str:
        """Replace template variables with actual data"""
        for key, value in data.items():
            placeholder = f"{{{{{key.upper()}}}}}"
            template = template.replace(placeholder, str(value))
        
        return template
    
    def generate_and_open_diploma(self, service_data: Dict[str, Any]) -> str:
        """Generate diploma and open it in the default browser"""
        diploma_path = self.generate_diploma(service_data)
        
        try:
            webbrowser.open(f'file://{os.path.abspath(diploma_path)}')
        except Exception as e:
            print(f"Could not open browser: {e}")
        
        return diploma_path
    
    def get_diploma_preview_data(self) -> Dict[str, Any]:
        """Get sample data for diploma preview"""
        return {
            'service_name': 'Authentication Service',
            'cert_id': 'CERT-20250828-ABC123',
            'port': 8443,
            'certificate_type': 'Security Compliance',
            'security_level': 'Enterprise',
            'compliance_score': 98,
            'issue_date': 'August 28, 2025',
            'expiry_date': 'August 28, 2026',
            'certification_date': '2025-08-28 15:30:00'
        }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ZmartBot Service Certification Diploma')
    parser.add_argument('--service-name', help='Service name (not required for preview)')
    parser.add_argument('--cert-id', help='Certificate ID (auto-generated if not provided)')
    parser.add_argument('--port', type=int, help='Service port')
    parser.add_argument('--certificate-type', default='Standard', help='Certificate type')
    parser.add_argument('--security-level', default='Production', help='Security level')
    parser.add_argument('--compliance-score', type=int, default=95, help='Compliance score (0-100)')
    parser.add_argument('--preview', action='store_true', help='Generate preview diploma')
    parser.add_argument('--open', action='store_true', help='Open diploma in browser after generation')
    
    args = parser.parse_args()
    
    generator = CertificationDiplomaGenerator()
    
    if args.preview:
        service_data = generator.get_diploma_preview_data()
        print("Generating preview diploma...")
    else:
        if not args.service_name:
            print("❌ Error: --service-name is required when not using --preview")
            return 1
            
        service_data = {
            'service_name': args.service_name,
            'cert_id': args.cert_id,
            'port': args.port,
            'certificate_type': args.certificate_type,
            'security_level': args.security_level,
            'compliance_score': args.compliance_score
        }
        # Remove None values
        service_data = {k: v for k, v in service_data.items() if v is not None}
    
    try:
        if args.open:
            diploma_path = generator.generate_and_open_diploma(service_data)
        else:
            diploma_path = generator.generate_diploma(service_data)
        
        print(f"✅ Diploma generated successfully: {diploma_path}")
        
    except Exception as e:
        print(f"❌ Error generating diploma: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())