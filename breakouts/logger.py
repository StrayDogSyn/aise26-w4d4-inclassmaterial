"""
🎯 BREAKOUT 2 - STRUCTURED LOGGING MODULE
==========================================
cSpell:words ecommerce levelno msecs

This is a production-quality logging module for the E-commerce API.

Partner Discussion Points:
1. Why create a custom logger instead of using print()?
2. What is "structured logging" and why is it important?
3. How does this logger prevent other libraries from cluttering our logs?

Key Features:
- Structured logging with JSON support
- File rotation to prevent disk space issues
- Color-coded console output for readability
- Request ID tracking for distributed tracing
- Performance metrics (execution time tracking)
"""

import logging
import logging.handlers
import sys
import json
import time
import functools
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


# ==============================================================================
# 📋 LOGGER CONFIGURATION
# ==============================================================================

class LogConfig:
    """
    Centralized logging configuration.
    
    DISCUSSION: Why use a class for configuration instead of global variables?
    Answer: Easier to test, override, and maintain. Can create different configs
    for dev/staging/production environments.
    """
    
    # Logger name - IMPORTANT: Use a specific name, not root logger!
    # DISCUSSION: Why not use root logger?
    # Answer: Root logger affects ALL libraries (FastAPI, uvicorn, etc.)
    # Using a specific name keeps our logs separate and clean.
    LOGGER_NAME = "ecommerce_api"
    
    # Log level - Controls what gets logged
    # DEBUG: Everything (use in development)
    # INFO: Normal operations (use in production)
    # WARNING: Something unexpected but handled
    # ERROR: Something broke but app still runs
    # CRITICAL: System failure, immediate attention needed
    LOG_LEVEL = logging.INFO
    
    # File settings
    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "ecommerce.log"
    
    # File rotation settings
    # DISCUSSION: Why rotate log files?
    # Answer: Prevent disk space issues. A busy API can generate gigabytes of logs!
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
    BACKUP_COUNT = 5  # Keep 5 old files (total: 50 MB max)
    
    # Log format for file output
    # DISCUSSION: What information should every log line contain?
    # Answer: Timestamp, level, logger name, function name, line number, and message
    FILE_FORMAT = (
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(funcName)s:%(lineno)d | "
        "%(message)s"
    )
    
    # Date format
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==============================================================================
# 🎨 CUSTOM FORMATTERS
# ==============================================================================

class ColoredFormatter(logging.Formatter):
    """
    Formatter that adds ANSI color codes to console output for better readability.
    
    DISCUSSION: Why use colors in logs?
    Answer: Quickly identify log levels at a glance. Errors jump out in red,
    warnings in yellow, making debugging faster and less stressful!
    
    Colors work in most modern terminals (Windows 10+, macOS, Linux).
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m\033[1m',  # Magenta + Bold
    }
    
    # Special colors for different parts of the log
    TIMESTAMP_COLOR = '\033[90m'      # Gray
    FUNCTION_COLOR = '\033[94m'       # Light Blue
    MESSAGE_COLOR = '\033[97m'        # White
    CONTEXT_COLOR = '\033[96m'        # Cyan
    RESET = '\033[0m'                 # Reset all colors
    
    # Emojis for visual indicators
    EMOJI = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and emojis."""
        # Get color for this log level
        level_color = self.COLORS.get(record.levelname, self.RESET)
        emoji = self.EMOJI.get(record.levelname, '📝')
        
        # Format timestamp in gray
        timestamp = self.formatTime(record, LogConfig.DATE_FORMAT)
        colored_timestamp = f"{self.TIMESTAMP_COLOR}{timestamp}{self.RESET}"
        
        # Format level with color and emoji
        colored_level = f"{level_color}{emoji} {record.levelname:<8}{self.RESET}"
        
        # Format function name in light blue
        colored_function = f"{self.FUNCTION_COLOR}{record.funcName}:{record.lineno}{self.RESET}"
        
        # Format message in white (or level color for errors)
        message_color = level_color if record.levelname in ['ERROR', 'CRITICAL'] else self.MESSAGE_COLOR
        colored_message = f"{message_color}{record.getMessage()}{self.RESET}"
        
        # Build the log line
        log_line = (
            f"{colored_timestamp} | "
            f"{colored_level} | "
            f"{record.name} | "
            f"{colored_function} | "
            f"{colored_message}"
        )
        
        # Add extra context fields in cyan
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'message', 'pathname', 
                          'process', 'processName', 'relativeCreated', 
                          'thread', 'threadName', 'exc_info', 'exc_text',
                          'stack_info', 'asctime']:
                extra_fields[key] = value
        
        if extra_fields:
            context_json = json.dumps(extra_fields, indent=2)
            colored_context = f"{self.CONTEXT_COLOR}{context_json}{self.RESET}"
            log_line += f"\n  💡 Context: {colored_context}"
        
        # Add exception info in red if present
        if record.exc_info:
            exception_text = self.formatException(record.exc_info)
            log_line += f"\n{self.COLORS['ERROR']}  🔥 Exception:\n{exception_text}{self.RESET}"
        
        return log_line


class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs logs in a structured format with extra context.
    
    DISCUSSION: What is "structured logging"?
    Answer: Instead of plain text like "User logged in", we log:
    {"event": "user_login", "user_id": 123, "timestamp": "..."}
    
    This makes logs machine-readable for analysis and alerting!
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with extra context fields.
        
        DISCUSSION: What is record.extra used for?
        Answer: We can pass extra fields like request_id, user_id, etc.
        Example: logger.info("User logged in", extra={"user_id": 123})
        """
        # Start with base format
        base_message = super().format(record)
        
        # Add extra context if present
        # DISCUSSION: Why check hasattr instead of just accessing?
        # Answer: Not all log records have extra fields. Prevents AttributeError.
        extra_fields = {}
        for key, value in record.__dict__.items():
            # Skip standard logging fields
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'message', 'pathname', 
                          'process', 'processName', 'relativeCreated', 
                          'thread', 'threadName', 'exc_info', 'exc_text',
                          'stack_info', 'asctime']:
                extra_fields[key] = value
        
        # Add extra fields to message if any exist
        if extra_fields:
            base_message += f" | Context: {json.dumps(extra_fields)}"
        
        return base_message


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs logs as JSON for log aggregation systems.
    
    DISCUSSION: When would you use JSON format instead of text?
    Answer: When sending logs to ELK stack, Splunk, CloudWatch, Datadog, etc.
    JSON is easy to parse, search, and analyze at scale.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_data and key not in ['name', 'msg', 'args', 
                                                    'created', 'filename', 
                                                    'funcName', 'levelname', 
                                                    'levelno', 'lineno', 
                                                    'module', 'msecs', 'message']:
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# ==============================================================================
# 🔧 LOGGER SETUP
# ==============================================================================

def setup_ecommerce_logger(
    use_json: bool = False,
    log_to_console: bool = True,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Set up the e-commerce API logger.
    
    DISCUSSION: Why is this function needed?
    Answer: Centralizes logger configuration. Call once at app startup,
    use everywhere else. Ensures consistent logging across the application.
    
    Args:
        use_json: If True, use JSON format for file logs
        log_to_console: If True, log to console (stdout)
        log_to_file: If True, log to rotating file
    
    Returns:
        Configured logger instance
    
    IMPORTANT: Only call this ONCE at application startup!
    """
    # Get logger with our specific name
    # DISCUSSION: Why use getLogger(name) instead of creating new logger?
    # Answer: Python's logging system is singleton-based. Same name = same instance.
    logger = logging.getLogger(LogConfig.LOGGER_NAME)
    logger.setLevel(LogConfig.LOG_LEVEL)
    
    # CRITICAL: Prevent propagation to root logger
    # DISCUSSION: What happens if we don't set this?
    # Answer: Logs will also go to root logger, causing duplicate logs from
    # other libraries (uvicorn, FastAPI, etc.). Very messy!
    logger.propagate = False
    
    # Remove existing handlers (prevents duplicate handlers if called multiple times)
    logger.handlers.clear()
    
    # === Console Handler ===
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LogConfig.LOG_LEVEL)
        
        # Use colored formatter for console (better readability!)
        console_formatter = ColoredFormatter(
            LogConfig.FILE_FORMAT,
            datefmt=LogConfig.DATE_FORMAT
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # === File Handler with Rotation ===
    if log_to_file:
        # Create log directory if it doesn't exist
        LogConfig.LOG_DIR.mkdir(exist_ok=True)
        
        # DISCUSSION: Why use RotatingFileHandler instead of FileHandler?
        # Answer: Prevents log files from growing indefinitely.
        # When file reaches MAX_BYTES, it rotates to .log.1, .log.2, etc.
        file_handler = logging.handlers.RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(LogConfig.LOG_LEVEL)
        
        # Choose formatter based on use_json flag
        if use_json:
            file_formatter = JSONFormatter()
        else:
            file_formatter = StructuredFormatter(
                LogConfig.FILE_FORMAT,
                datefmt=LogConfig.DATE_FORMAT
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get the e-commerce API logger.
    
    DISCUSSION: Why have this separate from setup_ecommerce_logger()?
    Answer: setup_ecommerce_logger() is called once at startup.
    get_logger() is called in every file that needs to log.
    
    Usage in other files:
        from logger import get_logger
        logger = get_logger()
        logger.info("Something happened")
    
    Returns:
        The configured e-commerce logger instance
    """
    return logging.getLogger(LogConfig.LOGGER_NAME)


# ==============================================================================
# 🎯 DECORATORS FOR PERFORMANCE TRACKING
# ==============================================================================

def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    DISCUSSION: Why use a decorator instead of timing code in each function?
    Answer: DRY principle (Don't Repeat Yourself). Add @log_execution_time
    to any function and automatically get performance metrics!
    
    This is especially useful for:
    - Database queries
    - External API calls
    - File operations
    - Any potentially slow operation
    
    Usage:
        @log_execution_time
        async def get_products():
            # Your code here
            pass
    """
    logger = get_logger()
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        function_name = func.__name__
        
        # Log function entry (DEBUG level - detailed info)
        logger.debug(
            f"Executing {function_name}",
            extra={"function": function_name, "event": "start"}
        )
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Calculate execution time
            elapsed_time = time.perf_counter() - start_time
            
            # Log successful completion
            logger.info(
                f"{function_name} completed successfully",
                extra={
                    "function": function_name,
                    "execution_time": f"{elapsed_time:.4f}s",
                    "event": "complete"
                }
            )
            
            # DISCUSSION: When should we warn about slow operations?
            # Answer: Define thresholds based on your SLAs (Service Level Agreements)
            # For this demo, we'll warn if any operation takes > 1 second
            if elapsed_time > 1.0:
                logger.warning(
                    f"{function_name} took longer than expected",
                    extra={
                        "function": function_name,
                        "execution_time": f"{elapsed_time:.4f}s",
                        "threshold": "1.0s",
                        "action_needed": "Consider optimization"
                    }
                )
            
            return result
            
        except Exception as e:
            # Calculate time even for failures
            elapsed_time = time.perf_counter() - start_time
            
            # Log the error with context
            logger.error(
                f"{function_name} failed",
                extra={
                    "function": function_name,
                    "execution_time": f"{elapsed_time:.4f}s",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "event": "error"
                },
                exc_info=True  # Include stack trace
            )
            
            # Re-raise the exception so it's handled normally
            raise
    
    return wrapper


# ==============================================================================
# 🧪 TEST THE LOGGER
# ==============================================================================

if __name__ == "__main__":
    """
    Test the logger to ensure it works correctly.
    Run this file directly: python logger.py
    
    DISCUSSION: Why test the logger separately?
    Answer: Ensure logging works before integrating into the API.
    Makes debugging easier!
    """
    print("🧪 Testing E-commerce Logger...\n")
    
    # Setup logger
    test_logger = setup_ecommerce_logger(use_json=False)
    
    # Test all log levels
    test_logger.debug("This is a DEBUG message - detailed technical info")
    test_logger.info("This is an INFO message - normal operation")
    test_logger.warning("This is a WARNING message - something unexpected")
    test_logger.error("This is an ERROR message - something broke")
    test_logger.critical("This is a CRITICAL message - system failure!")
    
    # Test structured logging with context
    test_logger.info(
        "User logged in",
        extra={
            "user_id": 123,
            "email": "john@example.com",
            "ip_address": "192.168.1.100"
        }
    )
    
    # Test execution time decorator
    @log_execution_time
    async def slow_operation():
        """Simulate a slow operation."""
        import asyncio
        await asyncio.sleep(0.5)
        return "Done!"
    
    # Run the decorated function
    import asyncio
    result = asyncio.run(slow_operation())
    
    print("\n✅ Logger test complete!")
    print(f"📁 Check the log file at: {LogConfig.LOG_FILE}")
    print("\n💡 Partner Discussion:")
    print("   1. Look at the console output - notice the structured format?")
    print("   2. Open logs/ecommerce.log - compare with console output")
    print("   3. Discuss: Why do we log to both console AND file?")
    print("   4. Try changing LOG_LEVEL to DEBUG and run again")
