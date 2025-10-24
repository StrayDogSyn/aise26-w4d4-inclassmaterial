"""
🎯 STRUCTLOG LOGGER MODULE
==========================
cSpell:words structlog levelno msecs ecommerce

This module uses structlog - a powerful structured logging library.

Structlog vs Custom Logger:
- Structlog: Production-grade, battle-tested, feature-rich
- Custom Logger: Educational, shows how logging works internally

Partner Discussion Points:
1. Why use a third-party library like structlog vs building our own?
2. What are the benefits of structured logging in production?
3. How does structlog make logs more searchable and analyzable?

Key Features:
- Automatic context binding (no manual extra={} needed)
- Thread-safe context management
- Beautiful console output with colors
- JSON output for log aggregation
- Performance optimized
- Rich ecosystem of processors
"""

import structlog
import sys
from pathlib import Path
from typing import Any, Dict
import logging.handlers

# ==============================================================================
# 📋 STRUCTLOG CONFIGURATION
# ==============================================================================

class StructlogConfig:
    """
    Structlog configuration settings.
    
    DISCUSSION: How is this different from our custom logger?
    Answer: Structlog uses "processors" - a pipeline of functions that
    transform log entries. Much more flexible than formatters!
    """
    
    # Log level
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # File settings
    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "structlog_ecommerce.log"
    
    # File rotation
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5
    
    # Colors for console output
    COLORS = {
        "debug": "\033[36m",      # Cyan
        "info": "\033[32m",       # Green
        "warning": "\033[33m",    # Yellow
        "error": "\033[31m",      # Red
        "critical": "\033[35m\033[1m",  # Magenta + Bold
        "reset": "\033[0m",
        "timestamp": "\033[90m",  # Gray
        "key": "\033[94m",        # Light Blue
        "value": "\033[97m",      # White
    }


def add_color_to_level(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processor that adds colors to log levels.
    
    DISCUSSION: What is a "processor" in structlog?
    Answer: A function that takes the log event dict and transforms it.
    Processors are chained together to build the final log message.
    """
    if sys.stderr.isatty():  # Only add colors if output is a terminal
        level = event_dict.get("level", "info")
        color = StructlogConfig.COLORS.get(level, "")
        reset = StructlogConfig.COLORS["reset"]
        
        # Add emoji based on level
        emojis = {
            "debug": "🔍",
            "info": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨",
        }
        emoji = emojis.get(level, "📝")
        
        # Color the level
        event_dict["level"] = f"{color}{emoji} {level.upper():<8}{reset}"
    
    return event_dict


def add_colored_timestamp(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processor that adds a colored timestamp.
    
    DISCUSSION: Why add timestamp in a processor vs in the formatter?
    Answer: Processors are composable. We can easily enable/disable
    or swap timestamp formats without changing other code.
    """
    if sys.stderr.isatty():
        timestamp = event_dict.get("timestamp", "")
        color = StructlogConfig.COLORS["timestamp"]
        reset = StructlogConfig.COLORS["reset"]
        event_dict["timestamp"] = f"{color}{timestamp}{reset}"
    
    return event_dict


def colorize_keys_and_values(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processor that colorizes context keys and values.
    
    DISCUSSION: How is this better than manual string formatting?
    Answer: Automatic! Every log gets colored context without extra code.
    Plus, colors are only added when outputting to terminal, not files.
    """
    if not sys.stderr.isatty():
        return event_dict
    
    key_color = StructlogConfig.COLORS["key"]
    value_color = StructlogConfig.COLORS["value"]
    reset = StructlogConfig.COLORS["reset"]
    
    # Color the event message
    if "event" in event_dict:
        event_dict["event"] = f"{value_color}{event_dict['event']}{reset}"
    
    return event_dict


# ==============================================================================
# 🔧 SETUP FUNCTION
# ==============================================================================

def setup_structlog(
    use_json: bool = False,
    log_to_console: bool = True,
    log_to_file: bool = True
) -> None:
    """
    Configure structlog with all processors and handlers.
    
    DISCUSSION: How does structlog configuration differ from logging module?
    Answer: Instead of handlers and formatters, structlog uses processors
    and a "logger factory". More flexible and composable!
    
    Args:
        use_json: If True, log files will be in JSON format
        log_to_console: If True, log to console with colors
        log_to_file: If True, log to rotating file
    """
    
    # Create log directory
    StructlogConfig.LOG_DIR.mkdir(exist_ok=True)
    
    # Set up standard library logging (structlog builds on top of it)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, StructlogConfig.LOG_LEVEL),
    )
    
    # Configure file handler with rotation
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            StructlogConfig.LOG_FILE,
            maxBytes=StructlogConfig.MAX_BYTES,
            backupCount=StructlogConfig.BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, StructlogConfig.LOG_LEVEL))
        logging.root.addHandler(file_handler)
    
    # Define processor chain
    # DISCUSSION: What's the benefit of a processor chain?
    # Answer: Each processor does ONE thing. Easy to add/remove/reorder.
    # This is the "Unix philosophy" - small, composable pieces.
    
    processors = [
        # Add log level to event dict
        structlog.stdlib.add_log_level,
        
        # Add logger name to event dict
        structlog.stdlib.add_logger_name,
        
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        
        # Add source code location (file, line, function)
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        
        # Stack info and exception formatting
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        
        # Add colors (custom processors)
        add_colored_timestamp,
        add_color_to_level,
        colorize_keys_and_values,
    ]
    
    # Add final renderer based on output format
    if use_json:
        # JSON for log aggregation systems
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=sys.stderr.isatty(),  # Only use colors in terminal
                exception_formatter=structlog.dev.plain_traceback,
            )
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ==============================================================================
# 🎯 GET LOGGER FUNCTION
# ==============================================================================

def get_logger(name: str = "ecommerce_api") -> structlog.stdlib.BoundLogger:
    """
    Get a configured structlog logger.
    
    DISCUSSION: How is this different from logging.getLogger()?
    Answer: Returns a structlog BoundLogger which supports:
    - Context binding: log = log.bind(user_id=123)
    - Method chaining
    - Type hints
    - Better performance
    
    Args:
        name: Logger name (default: ecommerce_api)
    
    Returns:
        Configured structlog logger
    
    Example:
        >>> log = get_logger()
        >>> log.info("User logged in", user_id=123, ip="192.168.1.1")
        >>> 
        >>> # Bind context for multiple logs
        >>> log = log.bind(request_id="abc-123")
        >>> log.info("Processing request")  # request_id automatically included
        >>> log.info("Request completed")   # request_id automatically included
    """
    return structlog.get_logger(name)


# ==============================================================================
# 🎨 DECORATORS (Compatible with custom logger)
# ==============================================================================

import time
import functools
import asyncio
from typing import Callable, Any

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    DISCUSSION: Why create a decorator-compatible version?
    Answer: So code can switch between custom logger and structlog
    without changing the application code!
    
    Works with both sync and async functions.
    """
    log = get_logger()
    
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        func_name = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            log.info(
                f"{func_name} completed successfully",
                function=func_name,
                execution_time=f"{duration:.4f}s",
                event="complete"
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            log.error(
                f"{func_name} failed",
                function=func_name,
                execution_time=f"{duration:.4f}s",
                error=str(e),
                event="error"
            )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        func_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            log.info(
                f"{func_name} completed successfully",
                function=func_name,
                execution_time=f"{duration:.4f}s",
                event="complete"
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            log.error(
                f"{func_name} failed",
                function=func_name,
                execution_time=f"{duration:.4f}s",
                error=str(e),
                event="error"
            )
            raise
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# ==============================================================================
# 🧪 TEST HARNESS
# ==============================================================================

if __name__ == "__main__":
    # Setup structlog
    setup_structlog(use_json=False, log_to_console=True, log_to_file=True)
    
    print("\n" + "=" * 80)
    print("🧪 Testing Structlog Logger")
    print("=" * 80 + "\n")
    
    # Get logger
    log = get_logger()
    
    # Test all log levels
    log.debug("Debug message - detailed troubleshooting", module="test", details="verbose")
    log.info("Application started", version="1.0.0", port=8000, environment="production")
    log.warning("Low stock alert", product="Laptop", stock=3, threshold=10)
    log.error("Database connection failed", host="localhost", port=5432, error="timeout")
    log.critical("System failure!", service="payment", impact="high", affected_users=1500)
    
    # Test context binding
    print("\n" + "-" * 80)
    print("Testing Context Binding:")
    print("-" * 80 + "\n")
    
    # Bind context to logger
    request_log = log.bind(request_id="abc-123-def", user_id=42)
    request_log.info("Request received", endpoint="/products", method="GET")
    request_log.info("Database query executed", query_time="0.05s")
    request_log.info("Response sent", status_code=200)
    
    # Test exception logging
    print("\n" + "-" * 80)
    print("Testing Exception Logging:")
    print("-" * 80 + "\n")
    
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        log.error("Division error occurred", operation="10/0", exc_info=True)
    
    print("\n" + "=" * 80)
    print("✅ Structlog test complete!")
    print(f"📁 Check log file: {StructlogConfig.LOG_FILE}")
    print("=" * 80 + "\n")
