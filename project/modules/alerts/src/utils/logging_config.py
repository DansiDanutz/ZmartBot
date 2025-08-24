"""Logging configuration for the Symbol Alerts System."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config.settings import get_settings

settings = get_settings()


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
):
    """Setup logging configuration."""
    
    # Use settings defaults if not provided
    level = level or settings.logging.level
    log_file = log_file or settings.logging.file_path
    format_string = format_string or settings.logging.format
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=settings.logging.max_file_size,
            backupCount=settings.logging.backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("ccxt").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured - Level: {level}, File: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class StructuredLogger:
    """Structured logger for better log analysis."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.info(full_message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.warning(full_message)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.error(full_message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.debug(full_message)

