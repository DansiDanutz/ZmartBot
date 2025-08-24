"""
Kingfisher Configuration Settings
Centralized configuration management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class KingfisherConfig:
    """Configuration manager for Kingfisher system"""
    
    # Default configuration
    DEFAULTS = {
        # API Keys
        'TELEGRAM_API_ID': os.getenv('TELEGRAM_API_ID', '26706005'),
        'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'AIRTABLE_API_KEY': os.getenv('AIRTABLE_API_KEY'),
        'AIRTABLE_BASE_ID': os.getenv('AIRTABLE_BASE_ID', 'appAs9sZH7OmtYaTJ'),
        'AIRTABLE_TABLE_NAME': os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        
        # Paths
        'BASE_DIR': Path(__file__).parent.parent.parent,
        'DOWNLOADS_DIR': 'downloads',
        'MD_REPORTS_DIR': 'downloads/MD Reports',
        'HISTORY_DIR': 'HistoryData',
        'LEARNING_DIR': 'learning_data',
        'MODELS_DIR': 'learning_data/models',
        
        # ML Settings
        'ML_ENABLED': True,
        'LEARNING_RATE': 0.1,
        'EXPLORATION_RATE': 0.2,
        'CONFIDENCE_THRESHOLD': 0.75,
        'MODEL_UPDATE_FREQUENCY': 10,  # Update models every N executions
        
        # Execution Settings
        'STEP_TIMEOUT': 300,  # 5 minutes
        'MONITOR_INTERVAL': 10,  # seconds
        'ADAPTIVE_SCHEDULING': True,
        'MAX_RETRIES': 3,
        
        # API Settings
        'API_HOST': '0.0.0.0',
        'API_PORT': 5555,
        'API_DEBUG': False,
        
        # Step Configuration
        'STEPS': {
            1: {
                'name': 'Monitor & Download Images',
                'script': 'STEP1-Monitoring-Images-And-download.py',
                'enabled': True,
                'trigger_interval': 300  # 5 minutes
            },
            2: {
                'name': 'Sort Images with AI',
                'script': 'STEP2-Sort-Images-With-AI.py',
                'enabled': True,
                'batch_size': 10
            },
            3: {
                'name': 'Remove Duplicates',
                'script': 'STEP3-Remove-Duplicates.py',
                'enabled': True
            },
            4: {
                'name': 'Analyze & Create Reports',
                'script': 'STEP4-Analyze-And-Create-Reports.py',
                'enabled': True,
                'max_tokens': 4000
            },
            5: {
                'name': 'Extract Liquidation Clusters',
                'script': 'STEP5-Extract-Liquidation-Clusters.py',
                'enabled': True,
                'min_distance_percentage': 2.0
            },
            6: {
                'name': 'Generate Professional Reports',
                'script': 'STEP6-Enhanced-Professional-Reports.py',
                'enabled': True,
                'report_interval': 1800  # 30 minutes
            }
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration
        
        Args:
            config_path: Path to JSON configuration file
        """
        self.config = self.DEFAULTS.copy()
        
        # Load from file if provided
        if config_path and Path(config_path).exists():
            self._load_from_file(config_path)
        
        # Create necessary directories
        self._create_directories()
    
    def _load_from_file(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                self.config.update(custom_config)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
    
    def _create_directories(self):
        """Create necessary directories"""
        base_dir = Path(self.config['BASE_DIR'])
        directories = [
            'DOWNLOADS_DIR',
            'MD_REPORTS_DIR',
            'HISTORY_DIR',
            'LEARNING_DIR',
            'MODELS_DIR'
        ]
        
        for dir_key in directories:
            dir_path = base_dir / self.config[dir_key]
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def get_step_config(self, step_num: int) -> Dict[str, Any]:
        """Get configuration for a specific step
        
        Args:
            step_num: Step number (1-6)
            
        Returns:
            Step configuration dictionary
        """
        return self.config['STEPS'].get(step_num, {})
    
    def save_to_file(self, file_path: str):
        """Save current configuration to file
        
        Args:
            file_path: Path to save configuration
        """
        try:
            # Convert Path objects to strings for JSON serialization
            config_to_save = {}
            for key, value in self.config.items():
                if isinstance(value, Path):
                    config_to_save[key] = str(value)
                else:
                    config_to_save[key] = value
            
            with open(file_path, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            print(f"Configuration saved to {file_path}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def validate(self) -> bool:
        """Validate configuration
        
        Returns:
            True if configuration is valid
        """
        required_keys = [
            'AIRTABLE_API_KEY',
            'AIRTABLE_BASE_ID',
            'OPENAI_API_KEY'
        ]
        
        for key in required_keys:
            if not self.config.get(key):
                print(f"Missing required configuration: {key}")
                return False
        
        return True
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation"""
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any):
        """Set configuration value using bracket notation"""
        self.config[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists"""
        return key in self.config
    
    def __repr__(self) -> str:
        """String representation"""
        return f"KingfisherConfig(keys={list(self.config.keys())})"


# Singleton instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> KingfisherConfig:
    """Get singleton configuration instance
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = KingfisherConfig(config_path)
    return _config_instance