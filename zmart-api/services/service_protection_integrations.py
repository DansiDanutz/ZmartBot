#!/usr/bin/env python3
"""
Service Protection Integrations
Comprehensive protection functions for all ZmartBot services
"""

def protect_master_orchestration():
    """Master Orchestration Agent - CRITICAL PRIORITY"""
    return {
        'service_name': 'MasterOrchestrationAgent',
        'port': 8002,
        'protection_level': 'MAXIMUM',
        'critical_files': [
            'src/orchestration/orchestration_server.py',
            'src/data/service_registry.db',
            'port_registry.db',
            '.cursor/rules/MasterOrchestrationAgent.mdc'
        ],
        'file_protection': {
            'integrity_monitoring': True,
            'read_only_enforcement': True,
            'backup_frequency': '30min',
            'sha256_validation': True
        },
        'process_protection': {
            'auto_restart': True,
            'health_monitoring': True,
            'pid_tracking': True,
            'resource_monitoring': True
        },
        'port_protection': {
            'port_reservation': True,
            'conflict_prevention': True,
            'access_control': True
        },
        'database_protection': {
            'backup_frequency': '15min',
            'integrity_checks': True,
            'transaction_monitoring': True
        },
        'security_scanning': True,
        'emergency_procedures': [
            'immediate_backup',
            'service_restart',
            'database_recovery',
            'port_reallocation'
        ]
    }

def protect_backend_api():
    """Backend API Server - CRITICAL PRIORITY"""
    return {
        'service_name': 'Backend',
        'port': 8000,
        'protection_level': 'MAXIMUM',
        'critical_files': [
            'run_dev.py',
            'src/main.py',
            'src/routes/',
            'src/services/',
            'src/config/',
            '.cursor/rules/Backend.mdc'
        ],
        'file_protection': {
            'integrity_monitoring': True,
            'read_only_enforcement': True,
            'backup_frequency': '1hour',
            'cryptographic_hashing': True
        },
        'process_protection': {
            'auto_restart': True,
            'health_monitoring': True,
            'api_endpoint_monitoring': True
        },
        'api_protection': {
            'rate_limiting': True,
            'auth_validation': True,
            'input_sanitization': True,
            'endpoint_monitoring': True
        },
        'database_protection': True,
        'external_api_protection': True,
        'security_scanning': True
    }

def protect_api_keys_manager():
    """API Keys Manager - MAXIMUM SECURITY"""
    return {
        'service_name': 'API-Manager',
        'port': 8006,
        'protection_level': 'MAXIMUM',
        'security_level': 'CLASSIFIED',
        'critical_files': [
            'services/api_keys_manager.py',
            '.cursor/rules/API-Manager.mdc',
            '.cursor/rules/api-keys-manager-service.mdc'
        ],
        'file_protection': {
            'integrity_monitoring': True,
            'read_only_enforcement': True,
            'backup_frequency': '30min',
            'encryption_validation': True
        },
        'security_protection': {
            'encrypted_storage_validation': True,
            'access_control_monitoring': True,
            'audit_logging': True,
            'key_rotation_monitoring': True,
            'secret_scanning': True
        },
        'compliance_requirements': ['GDPR', 'SOC2', 'PCI-DSS'],
        'emergency_procedures': [
            'immediate_key_rotation',
            'access_revocation',
            'security_audit',
            'encrypted_backup'
        ]
    }

def protect_service_registry():
    """Service Registry - CRITICAL INFRASTRUCTURE"""
    return {
        'service_name': 'ServiceRegistry',
        'port': 8610,
        'protection_level': 'CRITICAL',
        'critical_files': [
            'src/data/service_registry.db',
            '.cursor/rules/ServiceRegistry.mdc'
        ],
        'database_protection': {
            'backup_frequency': '15min',
            'integrity_checks': True,
            'transaction_monitoring': True,
            'consistency_validation': True
        },
        'process_protection': {
            'auto_restart': True,
            'health_monitoring': True,
            'registry_consistency_checks': True
        },
        'service_discovery_protection': True,
        'emergency_procedures': [
            'registry_backup',
            'service_reregistration',
            'consistency_recovery'
        ]
    }

def protect_mysymbols_database():
    """MySymbols Database - TRADING DATA PROTECTION"""
    return {
        'service_name': 'MySymbolsDatabase',
        'database_file': 'src/data/my_symbols.db',
        'protection_level': 'HIGH',
        'critical_files': [
            'src/data/my_symbols.db',
            '.cursor/rules/MySymbolsDatabase.mdc',
            '.cursor/rules/MySymbols.mdc'
        ],
        'database_protection': {
            'backup_frequency': '15min',
            'integrity_checks': True,
            'transaction_monitoring': True,
            'symbol_validation': True
        },
        'trading_protection': {
            'max_symbols_enforcement': 10,
            'symbol_validation_rules': True,
            'trading_pair_validation': True
        },
        'emergency_procedures': [
            'database_backup',
            'symbol_validation',
            'trading_halt_if_corrupted'
        ]
    }

def protect_binance_service():
    """Binance Service - EXTERNAL API PROTECTION"""
    return {
        'service_name': 'BinanceServices',
        'protection_level': 'HIGH',
        'critical_files': [
            '.cursor/rules/BinanceServices.mdc'
        ],
        'external_api_protection': {
            'api_key_security': True,
            'rate_limit_protection': True,
            'trading_validation': True,
            'balance_monitoring': True
        },
        'security_protection': {
            'secret_scanning': True,
            'credential_encryption': True,
            'access_logging': True
        },
        'trading_protection': {
            'order_validation': True,
            'balance_checks': True,
            'rate_limit_compliance': True
        }
    }

def protect_kucoin_service():
    """KuCoin Service - MULTI-ACCOUNT PROTECTION"""
    return {
        'service_name': 'KuCoinService',
        'protection_level': 'HIGH',
        'critical_files': [
            '.cursor/rules/KuCoinService.mdc'
        ],
        'external_api_protection': {
            'multi_account_protection': True,
            'api_key_security': True,
            'rate_limit_protection': True
        },
        'trading_protection': {
            'account_separation': True,
            'order_validation': True,
            'balance_monitoring': True
        },
        'security_protection': {
            'credential_encryption': True,
            'access_control': True,
            'audit_logging': True
        }
    }

def protect_cryptometer_service():
    """Cryptometer Service - MARKET DATA PROTECTION"""
    return {
        'service_name': 'CryptometerService',
        'protection_level': 'MEDIUM',
        'critical_files': [
            '.cursor/rules/CryptometerService.mdc'
        ],
        'data_protection': {
            'data_validation': True,
            'cache_protection': True,
            'integrity_checks': True
        },
        'performance_protection': {
            'response_monitoring': True,
            'cache_optimization': True,
            'data_freshness_validation': True
        }
    }

def protect_indicators_system():
    """21 Indicators System - CALCULATION PROTECTION"""
    return {
        'service_name': '21indicators',
        'protection_level': 'HIGH',
        'critical_files': [
            '.cursor/rules/21indicators.mdc',
            '.cursor/rules/21indicatorsDatabase.mdc'
        ],
        'calculation_protection': {
            'algorithm_integrity': True,
            'data_validation': True,
            'performance_monitoring': True
        },
        'database_protection': {
            'historical_data_backup': True,
            'calculation_result_validation': True
        }
    }

def protect_alerts_systems():
    """Alert Systems Protection"""
    return {
        'live_alerts': {
            'service_name': 'LiveAlerts',
            'protection_level': 'MEDIUM',
            'critical_files': ['.cursor/rules/LiveAlerts.mdc'],
            'alert_protection': {
                'false_alert_prevention': True,
                'notification_security': True,
                'alert_history_protection': True
            }
        },
        'whale_alerts': {
            'service_name': 'WhaleAlerts', 
            'protection_level': 'MEDIUM',
            'critical_files': ['.cursor/rules/WhaleAlerts.mdc'],
            'whale_detection_protection': True
        },
        'messi_alerts': {
            'service_name': 'MessiAlerts',
            'protection_level': 'MEDIUM', 
            'critical_files': ['.cursor/rules/MessiAlerts.mdc'],
            'custom_alert_protection': True
        }
    }

def protect_security_services():
    """Security Services Protection"""
    return {
        'security_scan_service': {
            'service_name': 'SecurityScanService',
            'protection_level': 'CRITICAL',
            'critical_files': ['.cursor/rules/SecurityScanService.mdc'],
            'security_protection': {
                'secret_detection_integrity': True,
                'vulnerability_scan_protection': True,
                'compliance_monitoring': True
            }
        },
        'process_reaper': {
            'service_name': 'ProcessReaper',
            'protection_level': 'CRITICAL',
            'critical_files': ['.cursor/rules/ProcessReaper.mdc'],
            'process_protection': {
                'virus_detection': True,
                'unauthorized_process_prevention': True,
                'system_integrity_maintenance': True
            }
        }
    }

def protect_infrastructure_services():
    """Infrastructure Services Protection"""
    return {
        'port_manager': {
            'service_name': 'PortManager',
            'protection_level': 'HIGH',
            'critical_files': [
                '.cursor/rules/PortManager.mdc',
                '.cursor/rules/PortManagerDatabase.mdc'
            ],
            'port_protection': {
                'port_conflict_prevention': True,
                'port_allocation_monitoring': True,
                'database_protection': True
            }
        },
        'health_check_service': {
            'service_name': 'HealthCheckService',
            'protection_level': 'MEDIUM',
            'critical_files': ['.cursor/rules/HealthCheckService.mdc'],
            'health_monitoring_protection': True
        }
    }

def protect_optimization_claude_service():
    """Protection configuration for OptimizationClaude Service"""
    return {
        'service_name': 'OptimizationClaude',
        'protection_level': 'HIGH',
        'critical_files': [
            'services/optimization_claude_service.py',
            'CLAUDE.md',
            'data/optimization_history.json',
            '.cursor/rules/OptimizationClaude.mdc'
        ],
        'monitoring_requirements': {
            'performance_tracking': True,
            'file_integrity': True,
            'backup_validation': True,
            'adaptive_scheduling': True
        },
        'dependencies': [
            'SystemProtectionService',
            'MDC-Dashboard',
            'Context Management'
        ],
        'health_endpoints': [
            '/api/optimization/status',
            '/api/optimization/metrics',
            '/api/optimization/history'
        ],
        'emergency_procedures': [
            'backup_claude_md_before_optimization',
            'verify_system_integrity',
            'rollback_failed_optimization',
            'restore_optimization_history'
        ],
        'protection_features': {
            'file_backup': True,
            'content_validation': True,
            'performance_monitoring': True,
            'error_recovery': True,
            'rate_limiting': True
        }
    }

def protect_snapshot_service():
    """Protection configuration for Snapshot Service - CRITICAL DISASTER RECOVERY"""
    return {
        'service_name': 'SnapshotService',
        'port': 8085,
        'protection_level': 'CRITICAL',
        'security_level': 'HIGH',
        'critical_files': [
            'services/snapshot_service.py',
            '/var/snapshots/zmartbot/',
            '/var/lib/zmartbot/snapshots.db',
            '.cursor/rules/SnapshotService.mdc'
        ],
        'file_protection': {
            'integrity_monitoring': True,
            'read_only_enforcement': False,  # Needs write access for snapshots
            'backup_frequency': '30min',
            'cryptographic_hashing': True,
            'tamper_detection': True,
            'chain_of_custody': True
        },
        'process_protection': {
            'auto_restart': True,
            'health_monitoring': True,
            'resource_monitoring': True,
            'memory_leak_detection': True,
            'deadlock_detection': True
        },
        'database_protection': {
            'backup_frequency': '15min',
            'integrity_checks': True,
            'transaction_monitoring': True,
            'corruption_detection': True,
            'automated_recovery': True
        },
        'storage_protection': {
            'disk_space_monitoring': True,
            'quota_enforcement': True,
            'compression_validation': True,
            'corruption_scanning': True,
            'cleanup_automation': True
        },
        'disaster_recovery': {
            'automated_snapshots': True,
            'restoration_validation': True,
            'integrity_verification': True,
            'emergency_recovery': True,
            'cross_validation': True
        },
        'security_features': {
            'encryption_at_rest': True,
            'access_control': True,
            'audit_logging': True,
            'permission_validation': True
        },
        'monitoring_requirements': {
            'performance_tracking': True,
            'storage_utilization': True,
            'operation_success_rates': True,
            'restoration_timing': True,
            'compression_efficiency': True
        },
        'dependencies': [
            'SystemProtectionService',
            'DatabaseService',
            'FileSystemMonitor'
        ],
        'emergency_procedures': [
            'immediate_backup',
            'corruption_quarantine',
            'storage_cleanup',
            'emergency_restoration',
            'integrity_validation'
        ],
        'compliance_requirements': {
            'retention_policy': True,
            'audit_trail': True,
            'disaster_recovery_testing': True,
            'backup_validation': True
        }
    }

# Main protection registration function
def register_all_service_protections():
    """Register all services with the System Protection Service"""
    
    protection_configs = [
        protect_master_orchestration(),
        protect_backend_api(),
        protect_api_keys_manager(),
        protect_service_registry(),
        protect_mysymbols_database(),
        protect_binance_service(),
        protect_kucoin_service(),
        protect_cryptometer_service(),
        protect_indicators_system(),
        protect_optimization_claude_service(),
        protect_snapshot_service(),
    ]
    
    # Add alert systems
    alert_configs = protect_alerts_systems()
    for alert_config in alert_configs.values():
        protection_configs.append(alert_config)
    
    # Add security services
    security_configs = protect_security_services()
    for security_config in security_configs.values():
        protection_configs.append(security_config)
    
    # Add infrastructure services
    infra_configs = protect_infrastructure_services()
    for infra_config in infra_configs.values():
        protection_configs.append(infra_config)
    
    return protection_configs

if __name__ == "__main__":
    # Display all protection configurations
    configs = register_all_service_protections()
    
    print("🛡️  ZmartBot Service Protection Registry")
    print("=" * 50)
    
    for config in configs:
        service_name = config['service_name']
        protection_level = config['protection_level']
        critical_files_count = len(config.get('critical_files', []))
        
        print(f"Service: {service_name}")
        print(f"  Protection Level: {protection_level}")
        print(f"  Critical Files: {critical_files_count}")
        print(f"  Port: {config.get('port', 'N/A')}")
        print("-" * 30)