import logging
import os
from datetime import datetime
from pathlib import Path
import json

class CustomJSONFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'logger_name': record.name
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
            
        return json.dumps(log_entry)

def setup_logger(
    name: str = "career_ai_companion",
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = None,
    console_output: bool = True,
    json_format: bool = True
) -> logging.Logger:
    """
    Set up a comprehensive logger for the application
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        log_file: Custom log file name (optional)
        console_output: Whether to output to console
        json_format: Whether to use JSON formatting
    
    Returns:
        Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(exist_ok=True)
    
    # Set up logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    if json_format:
        formatter = CustomJSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # File handler
    if log_file is None:
        log_file = f"career_ai_{datetime.now().strftime('%Y%m%d')}.log"
    
    file_handler = logging.FileHandler(log_dir_path / log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors)
    error_file = f"career_ai_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(log_dir_path / error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Use simpler format for console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Logger '{name}' initialized with level {log_level}")
    logger.info(f"Log files location: {log_dir_path.absolute()}")
    
    return logger

def get_logger(name: str = "career_ai_companion") -> logging.Logger:
    """Get an existing logger or create a new one with default settings"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger = setup_logger(name)
    return logger

# Context manager for request logging
class RequestLogger:
    def __init__(self, logger: logging.Logger, endpoint: str, request_data: dict = None):
        self.logger = logger
        self.endpoint = endpoint
        self.request_data = request_data
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            f"Request started: {self.endpoint}",
            extra={
                'endpoint': self.endpoint,
                'request_data': self.request_data
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                f"Request completed successfully: {self.endpoint} (Duration: {duration:.2f}s)",
                extra={'endpoint': self.endpoint, 'duration': duration}
            )
        else:
            self.logger.error(
                f"Request failed: {self.endpoint} (Duration: {duration:.2f}s) - {exc_val}",
                extra={'endpoint': self.endpoint, 'duration': duration},
                exc_info=True
            )
        
        return False  # Don't suppress exceptions