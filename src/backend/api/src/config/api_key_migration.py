#!/usr/bin/env python3
"""
API Key Migration Script
Helps migrate services from hardcoded API keys to secure environment-based configuration
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeyMigrator:
    """Migrate hardcoded API keys to secure configuration"""
    
    def __init__(self):
        self.services_dir = Path(__file__).parent.parent / 'services'
        self.patterns = [
            (r'api_key\s*=\s*["\']([^"\']+)["\']', 'API key assignment'),
            (r'API_KEY\s*=\s*["\']([^"\']+)["\']', 'API key constant'),
            (r'["\']sk-[^"\']+["\']', 'OpenAI key pattern'),
            (r'["\'][\w]{32,}["\']', 'Long API key pattern')
        ]
    
    def scan_for_hardcoded_keys(self) -> List[Tuple[str, int, str, str]]:
        """
        Scan for hardcoded API keys in services
        
        Returns:
            List of (file_path, line_number, key_value, pattern_type)
        """
        findings = []
        
        for py_file in self.services_dir.glob('**/*.py'):
            try:
                with open(py_file, 'r') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, pattern_type in self.patterns:
                        matches = re.findall(pattern, line)
                        for match in matches:
                            # Skip placeholders and imports
                            if any(skip in match.lower() for skip in 
                                   ['your_', 'example', 'placeholder', 'import', 'from']):
                                continue
                            
                            # Skip short strings that are unlikely to be keys
                            if len(match) < 20:
                                continue
                            
                            findings.append((str(py_file), line_num, match, pattern_type))
            
            except Exception as e:
                logger.error(f"Error scanning {py_file}: {e}")
        
        return findings
    
    def generate_migration_code(self, service_name: str) -> str:
        """
        Generate migration code for a service
        
        Args:
            service_name: Name of the service to migrate
            
        Returns:
            Migration code template
        """
        return f'''
# Migration for {service_name}
# Replace hardcoded API key with secure configuration

# Old code (REMOVE):
# api_key = "your_hardcoded_key_here"

# New code (ADD):
from src.config.secure_config import get_api_key

# In __init__ or wherever you initialize the API key:
api_key = get_api_key('{service_name.lower()}')
if not api_key:
    raise ValueError(f"API key not configured for {service_name}")
'''
    
    def create_migration_report(self) -> str:
        """Create a report of all hardcoded keys found"""
        findings = self.scan_for_hardcoded_keys()
        
        if not findings:
            return "✅ No hardcoded API keys found!"
        
        report = ["⚠️ Found potential hardcoded API keys:\n"]
        
        for file_path, line_num, key_value, pattern_type in findings:
            # Mask the key value for security
            masked_key = key_value[:8] + "..." + key_value[-4:] if len(key_value) > 12 else "***"
            file_name = Path(file_path).name
            report.append(f"  📄 {file_name}:{line_num} - {pattern_type}: {masked_key}")
        
        report.append(f"\nTotal findings: {len(findings)}")
        report.append("\n📝 Migration steps:")
        report.append("1. Add API keys to .env file")
        report.append("2. Update services to use secure_config.get_api_key()")
        report.append("3. Remove hardcoded keys from code")
        report.append("4. Verify .env is in .gitignore")
        
        return "\n".join(report)

# Example usage patterns for different services
MIGRATION_EXAMPLES = {
    'cryptometer': '''
# Cryptometer Service Migration
from src.config.secure_config import get_cryptometer_key

class CryptometerService:
    def __init__(self):
        self.api_key = get_cryptometer_key()
        if not self.api_key:
            raise ValueError("Cryptometer API key not configured")
        self.base_url = "https://api.cryptometer.io"
''',
    
    'kucoin': '''
# KuCoin Service Migration
from src.config.secure_config import get_kucoin_credentials

class KuCoinService:
    def __init__(self):
        creds = get_kucoin_credentials()
        if not all([creds.get('api_key'), creds.get('secret'), creds.get('passphrase')]):
            raise ValueError("KuCoin credentials not fully configured")
        
        self.api_key = creds['api_key']
        self.secret = creds['secret']
        self.passphrase = creds['passphrase']
''',
    
    'openai': '''
# OpenAI Service Migration
from src.config.secure_config import get_openai_key
import openai

class AIAnalysisService:
    def __init__(self):
        api_key = get_openai_key()
        if not api_key:
            logger.warning("OpenAI API key not configured, AI features disabled")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
''',
    
    'binance': '''
# Binance Service Migration
from src.config.secure_config import get_binance_credentials

class BinanceService:
    def __init__(self):
        creds = get_binance_credentials()
        if not all([creds.get('api_key'), creds.get('secret')]):
            raise ValueError("Binance credentials not configured")
        
        self.api_key = creds['api_key']
        self.secret = creds['secret']
'''
}

def main():
    """Run the migration analysis"""
    migrator = APIKeyMigrator()
    report = migrator.create_migration_report()
    print(report)
    
    print("\n" + "="*50)
    print("Example Migration Patterns:")
    print("="*50)
    
    for service, example in MIGRATION_EXAMPLES.items():
        print(f"\n{service.upper()} Service:")
        print(example)

if __name__ == "__main__":
    main()