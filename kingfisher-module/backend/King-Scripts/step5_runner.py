#!/usr/bin/env python3
"""
STEP-5 Plugin Runner - Normalized Pipeline Architecture
Replaces multiple STEP-5 variants with a single configurable plugin system
"""

import os
import sys
import json
import logging
import importlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

@dataclass
class ProcessingContext:
    """Context passed between plugins"""
    symbol: Optional[str] = None
    image_path: Optional[str] = None
    analysis_data: Dict[str, Any] = None
    market_data: Dict[str, Any] = None
    liquidation_clusters: List[Dict[str, Any]] = None
    processing_metadata: Dict[str, Any] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.analysis_data is None:
            self.analysis_data = {}
        if self.market_data is None:
            self.market_data = {}
        if self.liquidation_clusters is None:
            self.liquidation_clusters = []
        if self.processing_metadata is None:
            self.processing_metadata = {
                "start_time": datetime.now().isoformat(),
                "plugin_results": {}
            }
        if self.errors is None:
            self.errors = []

class BasePlugin:
    """Base class for all STEP-5 plugins"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate that context has required data for this plugin"""
        return True
        
    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Execute plugin logic - must be implemented by subclasses"""
        raise NotImplementedError(f"Plugin {self.name} must implement run() method")
    
    def on_error(self, context: ProcessingContext, error: Exception) -> ProcessingContext:
        """Handle plugin errors"""
        error_msg = f"{self.name}: {str(error)}"
        context.errors.append(error_msg)
        logger.error(f"Plugin error: {error_msg}")
        return context

class Step5PluginRunner:
    """Main plugin runner for STEP-5 processing"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.plugins: List[BasePlugin] = []
        self.config = self._load_config(config_path)
        self._initialize_plugins()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load plugin configuration"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
        
        # Default configuration
        return {
            "plugins": [
                {
                    "name": "symbol_update",
                    "enabled": True,
                    "config": {
                        "update_airtable": True,
                        "validate_symbol": True
                    }
                },
                {
                    "name": "extract_liq_clusters", 
                    "enabled": True,
                    "config": {
                        "cluster_threshold": 0.8,
                        "max_clusters": 10
                    }
                },
                {
                    "name": "real_market_price",
                    "enabled": True,
                    "config": {
                        "price_sources": ["binance", "kucoin"],
                        "timeout": 30
                    }
                },
                {
                    "name": "finalize",
                    "enabled": True,
                    "config": {
                        "generate_summary": True,
                        "cleanup_temp": True
                    }
                }
            ],
            "global_config": {
                "max_retries": 3,
                "timeout_per_plugin": 300,
                "continue_on_error": True
            }
        }
    
    def _initialize_plugins(self):
        """Initialize plugins based on configuration"""
        plugins_dir = Path(__file__).parent / "plugins"
        
        for plugin_config in self.config.get("plugins", []):
            if not plugin_config.get("enabled", True):
                logger.info(f"Skipping disabled plugin: {plugin_config['name']}")
                continue
            
            try:
                plugin_name = plugin_config["name"]
                plugin_file = plugins_dir / f"{plugin_name}.py"
                
                if not plugin_file.exists():
                    logger.error(f"Plugin file not found: {plugin_file}")
                    continue
                
                # Import plugin module dynamically
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_name}", 
                    plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get plugin class (assumes class name is PascalCase of plugin name)
                class_name = ''.join(word.capitalize() for word in plugin_name.split('_')) + 'Plugin'
                
                if hasattr(module, class_name):
                    plugin_class = getattr(module, class_name)
                    plugin_instance = plugin_class(plugin_config.get("config", {}))
                    self.plugins.append(plugin_instance)
                    logger.info(f"✅ Loaded plugin: {plugin_name}")
                else:
                    logger.error(f"Plugin class {class_name} not found in {plugin_file}")
                
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_config['name']}: {e}")
    
    def run_pipeline(self, context: ProcessingContext) -> ProcessingContext:
        """Execute the complete STEP-5 pipeline"""
        logger.info(f"🚀 Starting STEP-5 pipeline with {len(self.plugins)} plugins")
        
        start_time = datetime.now()
        context.processing_metadata["pipeline_start"] = start_time.isoformat()
        
        for i, plugin in enumerate(self.plugins):
            plugin_start = datetime.now()
            logger.info(f"🔧 Running plugin {i+1}/{len(self.plugins)}: {plugin.name}")
            
            try:
                # Validate context for this plugin
                if not plugin.validate_context(context):
                    logger.warning(f"Context validation failed for plugin {plugin.name}")
                    if not self.config.get("global_config", {}).get("continue_on_error", True):
                        break
                    continue
                
                # Run the plugin
                context = plugin.run(context)
                
                # Record plugin execution
                plugin_duration = (datetime.now() - plugin_start).total_seconds()
                context.processing_metadata["plugin_results"][plugin.name] = {
                    "success": True,
                    "duration_seconds": plugin_duration,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"✅ Plugin {plugin.name} completed in {plugin_duration:.2f}s")
                
            except Exception as e:
                # Handle plugin error
                context = plugin.on_error(context, e)
                
                plugin_duration = (datetime.now() - plugin_start).total_seconds()
                context.processing_metadata["plugin_results"][plugin.name] = {
                    "success": False,
                    "error": str(e),
                    "duration_seconds": plugin_duration,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.error(f"❌ Plugin {plugin.name} failed after {plugin_duration:.2f}s: {e}")
                
                # Stop pipeline if configured to do so
                if not self.config.get("global_config", {}).get("continue_on_error", True):
                    logger.error("Stopping pipeline due to plugin failure")
                    break
        
        # Finalize context
        total_duration = (datetime.now() - start_time).total_seconds()
        context.processing_metadata["pipeline_end"] = datetime.now().isoformat()
        context.processing_metadata["total_duration_seconds"] = total_duration
        
        logger.info(f"🎯 STEP-5 pipeline completed in {total_duration:.2f}s")
        logger.info(f"📊 Results: {len([r for r in context.processing_metadata['plugin_results'].values() if r['success']])} success, {len(context.errors)} errors")
        
        return context
    
    def run_single_plugin(self, plugin_name: str, context: ProcessingContext) -> ProcessingContext:
        """Run a single plugin by name"""
        plugin = next((p for p in self.plugins if p.name == plugin_name), None)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        
        logger.info(f"🔧 Running single plugin: {plugin_name}")
        
        try:
            if not plugin.validate_context(context):
                raise ValueError(f"Context validation failed for plugin {plugin_name}")
            
            context = plugin.run(context)
            logger.info(f"✅ Plugin {plugin_name} completed successfully")
            
        except Exception as e:
            context = plugin.on_error(context, e)
            logger.error(f"❌ Plugin {plugin_name} failed: {e}")
        
        return context


def main():
    """Command line interface for STEP-5 plugin runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="STEP-5 Plugin Runner for KingFisher")
    parser.add_argument("--config", help="Path to plugin configuration file")
    parser.add_argument("--plugin", help="Run single plugin by name")
    parser.add_argument("--symbol", help="Symbol to process")
    parser.add_argument("--image", help="Image path to process")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize runner
    runner = Step5PluginRunner(args.config)
    
    # Create context
    context = ProcessingContext(
        symbol=args.symbol,
        image_path=args.image
    )
    
    # Run pipeline or single plugin
    if args.plugin:
        context = runner.run_single_plugin(args.plugin, context)
    else:
        context = runner.run_pipeline(context)
    
    # Output results
    print(f"\n🎯 STEP-5 Processing Complete")
    print(f"📊 Context: {asdict(context)}")
    
    if context.errors:
        print(f"❌ Errors encountered: {len(context.errors)}")
        for error in context.errors:
            print(f"   - {error}")
        sys.exit(1)
    else:
        print("✅ All plugins executed successfully")


if __name__ == "__main__":
    main()