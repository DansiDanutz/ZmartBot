#!/usr/bin/env python3
"""
Logger Utility
Centralized logging configuration for the ZmartBot system
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

class ZmartBotLogger:
    """Centralized logger for ZmartBot system"""
    
    def __init__(self, name: str = "zmartbot", level: str = "INFO"):
        self.name = name
        self.level = getattr(logging, level.upper())
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup centralized logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # File handler with rotation
        log_file = os.path.join(logs_dir, f"{self.name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger"""
        return self.logger

# Global logger instance
_global_logger = None

def get_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """Get a logger instance"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = ZmartBotLogger(name or "zmartbot", level)
    
    return _global_logger.get_logger()

def setup_logging(level: str = "INFO"):
    """Setup global logging configuration"""
    global _global_logger
    _global_logger = ZmartBotLogger("zmartbot", level)
    return _global_logger.get_logger()