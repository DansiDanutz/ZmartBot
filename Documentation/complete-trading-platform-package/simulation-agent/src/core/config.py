"""
Simulation Agent - Core Configuration Module
==========================================

Professional configuration management for the Simulation Agent module.
Integrates seamlessly with ZmartBot, KingFisher, and Trade Strategy systems.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
import logging
from pathlib import Path

# System Integration Configuration
@dataclass
class SystemIntegrationConfig:
    """Configuration for integration with existing trading systems"""
    
    # Port Configuration (Zero Conflicts)
    simulation_api_port: int = 8300  # Simulation Agent API
    simulation_frontend_port: int = 3300  # Simulation Agent Frontend
    
    # Existing System Ports (Reference Only)
    zmartbot_api_port: int = 8000
    zmartbot_frontend_port: int = 3000
    kingfisher_api_port: int = 8100
    kingfisher_frontend_port: int = 3100
    trade_strategy_api_port: int = 8200
    trade_strategy_frontend_port: int = 3200
    
    # Shared Services
    postgres_port: int = 5432
    redis_port: int = 6379
    prometheus_port: int = 9090
    grafana_port: int = 3001
    
    # Database Configuration
    database_url: str = "postgresql://trading_user:trading_pass@localhost:5432/trading_platform"
    redis_url: str = "redis://localhost:6379/3"  # Use DB 3 for Simulation Agent
    redis_namespace: str = "sim:"  # Namespace prefix for Redis keys
    
    # API Integration URLs
    zmartbot_api_url: str = "http://localhost:8000"
    kingfisher_api_url: str = "http://localhost:8100"
    trade_strategy_api_url: str = "http://localhost:8200"

@dataclass
class DataSourceConfig:
    """Configuration for external data sources"""
    
    # Cryptometer API Configuration
    cryptometer_api_key: str = "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"
    cryptometer_base_url: str = "https://api.cryptometer.io/v1"
    cryptometer_rate_limit: int = 100  # requests per minute
    
    # RiskMetric Data Sources
    riskmetric_primary_sheet: str = "https://docs.google.com/spreadsheets/d/1F-0_I2zy7MIQ_thTF2g4oaTZNiv1aV4x/edit?usp=sharing"
    riskmetric_historical_sheet: str = "https://docs.google.com/spreadsheets/d/1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg/edit?usp=sharing"
    riskmetric_methodology_doc: str = "https://drive.google.com/file/d/1VsT_-aOKFyZwFi8vLm-lkj4ELLoh9PzK/view?usp=sharing"
    
    # KingFisher Data Configuration
    kingfisher_data_retention_days: int = 365
    kingfisher_screenshot_types: List[str] = field(default_factory=lambda: [
        "liquidation_clusters_map",
        "short_term_liquidation_ratio", 
        "long_term_liquidation_ratio",
        "toxic_order_flow",
        "rsi_heatmap",
        "leverage_market_balance"
    ])

@dataclass
class SimulationConfig:
    """Configuration for simulation engine parameters"""
    
    # Simulation Parameters
    default_lookback_days: int = 365  # Default historical analysis period
    min_data_points: int = 100  # Minimum data points for reliable analysis
    max_concurrent_simulations: int = 8  # Leverage M2 Pro 12-core CPU
    
    # Pattern Recognition Settings
    pattern_confidence_threshold: float = 0.65
    min_pattern_occurrences: int = 5
    pattern_similarity_threshold: float = 0.80
    
    # Win Ratio Analysis
    min_trades_for_analysis: int = 30
    confidence_interval: float = 0.95
    risk_free_rate: float = 0.02  # 2% annual risk-free rate
    
    # Position Analysis
    long_position_analysis: bool = True
    short_position_analysis: bool = True
    position_size_percentages: List[float] = field(default_factory=lambda: [1.0, 2.0, 4.0, 8.0])
    leverage_options: List[int] = field(default_factory=lambda: [1, 2, 5, 10, 20])
    
    # Market Condition Categories
    market_conditions: List[str] = field(default_factory=lambda: [
        "trending_up",
        "trending_down", 
        "ranging",
        "high_volatility",
        "low_volatility",
        "breakout",
        "breakdown"
    ])

@dataclass
class AnalysisConfig:
    """Configuration for analysis algorithms and methods"""
    
    # Machine Learning Parameters
    ml_model_types: List[str] = field(default_factory=lambda: [
        "random_forest",
        "gradient_boosting",
        "neural_network",
        "svm"
    ])
    
    # Feature Engineering
    technical_indicators: List[str] = field(default_factory=lambda: [
        "rsi", "macd", "bollinger_bands", "stochastic",
        "williams_r", "cci", "atr", "adx", "obv", "mfi"
    ])
    
    # Custom Indicators (Based on KingFisher Data)
    custom_indicators: List[str] = field(default_factory=lambda: [
        "liquidation_pressure_index",
        "market_balance_ratio",
        "price_position_index", 
        "toxic_order_flow_intensity",
        "rsi_position_factor"
    ])
    
    # Statistical Analysis
    statistical_tests: List[str] = field(default_factory=lambda: [
        "t_test",
        "chi_square",
        "kolmogorov_smirnov",
        "mann_whitney_u"
    ])
    
    # Performance Metrics
    performance_metrics: List[str] = field(default_factory=lambda: [
        "win_ratio",
        "profit_factor",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "calmar_ratio",
        "information_ratio"
    ])

@dataclass
class ReportingConfig:
    """Configuration for professional reporting system"""
    
    # Report Types
    report_types: List[str] = field(default_factory=lambda: [
        "executive_summary",
        "detailed_analysis",
        "technical_report",
        "risk_assessment",
        "performance_attribution"
    ])
    
    # Visualization Settings
    chart_types: List[str] = field(default_factory=lambda: [
        "candlestick",
        "line_chart",
        "heatmap",
        "scatter_plot",
        "histogram",
        "box_plot",
        "correlation_matrix"
    ])
    
    # Export Formats
    export_formats: List[str] = field(default_factory=lambda: [
        "pdf",
        "html",
        "json",
        "csv",
        "excel"
    ])
    
    # Professional Styling
    brand_colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#1f2937",
        "secondary": "#3b82f6", 
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#06b6d4"
    })

@dataclass
class MacOptimizationConfig:
    """Mac Mini 2025 M2 Pro specific optimizations"""
    
    # Apple Silicon Optimizations
    use_apple_silicon_optimizations: bool = True
    cpu_cores: int = 12  # M2 Pro CPU cores
    gpu_cores: int = 19  # M2 Pro GPU cores
    unified_memory_gb: int = 16
    
    # Performance Settings
    max_memory_usage_gb: int = 12  # Leave 4GB for system
    parallel_processing_workers: int = 8
    async_io_workers: int = 4
    
    # Storage Optimization
    use_ssd_optimizations: bool = True
    cache_size_mb: int = 2048
    temp_storage_path: str = "/tmp/simulation_agent"
    
    # Monitoring and Logging
    enable_performance_monitoring: bool = True
    log_level: str = "INFO"
    log_rotation_size_mb: int = 100
    log_retention_days: int = 30

class SimulationAgentConfig:
    """Main configuration class for Simulation Agent"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.system_integration = SystemIntegrationConfig()
        self.data_sources = DataSourceConfig()
        self.simulation = SimulationConfig()
        self.analysis = AnalysisConfig()
        self.reporting = ReportingConfig()
        self.mac_optimization = MacOptimizationConfig()
        
        # Load environment-specific overrides
        self._load_environment_config()
        
        # Setup logging
        self._setup_logging()
    
    def _load_environment_config(self):
        """Load environment-specific configuration overrides"""
        
        if self.environment == "production":
            self.mac_optimization.log_level = "WARNING"
            self.simulation.max_concurrent_simulations = 6  # Conservative for production
            self.mac_optimization.max_memory_usage_gb = 10  # More conservative
            
        elif self.environment == "testing":
            self.mac_optimization.log_level = "DEBUG"
            self.simulation.default_lookback_days = 30  # Faster testing
            self.simulation.min_trades_for_analysis = 10  # Lower threshold for testing
            
        # Load from environment variables
        if os.getenv("SIMULATION_API_PORT"):
            self.system_integration.simulation_api_port = int(os.getenv("SIMULATION_API_PORT"))
            
        if os.getenv("CRYPTOMETER_API_KEY"):
            self.data_sources.cryptometer_api_key = os.getenv("CRYPTOMETER_API_KEY")
            
        if os.getenv("DATABASE_URL"):
            self.system_integration.database_url = os.getenv("DATABASE_URL")
            
        if os.getenv("REDIS_URL"):
            self.system_integration.redis_url = os.getenv("REDIS_URL")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=getattr(logging, self.mac_optimization.log_level),
            format=log_format,
            handlers=[
                logging.FileHandler(f"logs/simulation_agent_{self.environment}.log"),
                logging.StreamHandler()
            ]
        )
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration for SQLAlchemy"""
        
        return {
            "url": self.system_integration.database_url,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "echo": self.environment == "development"
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        
        return {
            "url": self.system_integration.redis_url,
            "decode_responses": True,
            "max_connections": 50,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get FastAPI configuration"""
        
        return {
            "title": "Simulation Agent API",
            "description": "Professional Trading Pattern Analysis and Win Ratio Simulation",
            "version": "1.0.0",
            "host": "0.0.0.0",
            "port": self.system_integration.simulation_api_port,
            "workers": self.mac_optimization.parallel_processing_workers,
            "reload": self.environment == "development",
            "access_log": self.environment != "production"
        }
    
    def get_integration_urls(self) -> Dict[str, str]:
        """Get URLs for system integration"""
        
        return {
            "zmartbot": self.system_integration.zmartbot_api_url,
            "kingfisher": self.system_integration.kingfisher_api_url,
            "trade_strategy": self.system_integration.trade_strategy_api_url,
            "prometheus": f"http://localhost:{self.system_integration.prometheus_port}",
            "grafana": f"http://localhost:{self.system_integration.grafana_port}"
        }
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        
        errors = []
        
        # Check port conflicts
        used_ports = [
            self.system_integration.zmartbot_api_port,
            self.system_integration.kingfisher_api_port,
            self.system_integration.trade_strategy_api_port
        ]
        
        if self.system_integration.simulation_api_port in used_ports:
            errors.append(f"Simulation API port {self.system_integration.simulation_api_port} conflicts with existing systems")
        
        # Check required API keys
        if not self.data_sources.cryptometer_api_key or self.data_sources.cryptometer_api_key == "your_api_key_here":
            errors.append("Cryptometer API key is required")
        
        # Check memory allocation
        if self.mac_optimization.max_memory_usage_gb > self.mac_optimization.unified_memory_gb:
            errors.append(f"Max memory usage ({self.mac_optimization.max_memory_usage_gb}GB) exceeds available memory ({self.mac_optimization.unified_memory_gb}GB)")
        
        # Check CPU allocation
        if self.mac_optimization.parallel_processing_workers > self.mac_optimization.cpu_cores:
            errors.append(f"Parallel workers ({self.mac_optimization.parallel_processing_workers}) exceeds CPU cores ({self.mac_optimization.cpu_cores})")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        
        return {
            "environment": self.environment,
            "system_integration": self.system_integration.__dict__,
            "data_sources": self.data_sources.__dict__,
            "simulation": self.simulation.__dict__,
            "analysis": self.analysis.__dict__,
            "reporting": self.reporting.__dict__,
            "mac_optimization": self.mac_optimization.__dict__
        }

# Global configuration instance
config = SimulationAgentConfig(environment=os.getenv("ENVIRONMENT", "development"))

# Validate configuration on import
config_errors = config.validate_config()
if config_errors:
    logger = logging.getLogger(__name__)
    for error in config_errors:
        logger.error(f"Configuration Error: {error}")
    
    if config.environment == "production":
        raise ValueError(f"Configuration validation failed: {config_errors}")

# Export commonly used configurations
DATABASE_CONFIG = config.get_database_config()
REDIS_CONFIG = config.get_redis_config()
API_CONFIG = config.get_api_config()
INTEGRATION_URLS = config.get_integration_urls()

# System Information for Cursor AI Development
CURSOR_AI_INFO = {
    "module_name": "Simulation Agent",
    "version": "1.0.0",
    "api_port": config.system_integration.simulation_api_port,
    "frontend_port": config.system_integration.simulation_frontend_port,
    "main_endpoints": [
        f"http://localhost:{config.system_integration.simulation_api_port}/docs",
        f"http://localhost:{config.system_integration.simulation_api_port}/health",
        f"http://localhost:{config.system_integration.simulation_api_port}/api/v1/simulation/analyze",
        f"http://localhost:{config.system_integration.simulation_frontend_port}"
    ],
    "integration_status": "Zero conflicts with existing systems",
    "mac_optimization": "Optimized for Mac Mini 2025 M2 Pro"
}

if __name__ == "__main__":
    # Configuration validation and info display
    print("🎯 Simulation Agent Configuration")
    print("=" * 50)
    print(f"Environment: {config.environment}")
    print(f"API Port: {config.system_integration.simulation_api_port}")
    print(f"Frontend Port: {config.system_integration.simulation_frontend_port}")
    print(f"Database: {config.system_integration.database_url}")
    print(f"Redis: {config.system_integration.redis_url}")
    print(f"Mac Optimization: {'Enabled' if config.mac_optimization.use_apple_silicon_optimizations else 'Disabled'}")
    
    errors = config.validate_config()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration Valid - Ready for Cursor AI Development!")

